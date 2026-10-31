"""Execute the actual .cmd launchers on Windows, including paths with spaces.

Small stub entry points isolate native argument/cwd/exit-code behavior from
downloads and hardware. CI separately runs the real bootstrap and HTTP server.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import venv

import pytest

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Native Windows cmd.exe launcher checks')
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def launcher_project(tmp_path_factory):
    root = tmp_path_factory.mktemp('launchers') / 'Karen project with spaces'
    root.mkdir()
    venv.EnvBuilder(with_pip=False).create(root / '.venv')
    (root / 'scripts').mkdir()
    stub = ('import json, os, pathlib, sys\n'
            'pathlib.Path("launcher-result.json").write_text(json.dumps({'
            '"args": sys.argv[1:], "cwd": os.getcwd(), "python": sys.executable, '
            '"utf8": os.getenv("PYTHONUTF8")}), encoding="utf-8")\n'
            'sys.exit(int(os.getenv("KAREN_LAUNCHER_TEST_EXIT", "0")))\n')
    for script in ('scripts/bootstrap.py', 'scripts/doctor.py', 'app.py'):
        (root / script).write_text(stub, encoding='utf-8')
    for launcher in ('bootstrap-windows.cmd', 'doctor-windows.cmd', 'start-windows.cmd'):
        shutil.copyfile(ROOT / launcher, root / launcher)
    return root


def run_launcher(root, launcher, arguments, cwd, exit_code=0):
    # /s /c requires a surrounding quote pair when the command path is quoted.
    # All test arguments are controlled strings without shell metacharacters.
    executable = subprocess.list2cmdline([os.environ.get('COMSPEC', 'cmd.exe')])
    argument_text = subprocess.list2cmdline(arguments)
    command = f'{executable} /d /s /c ""{root / launcher}" {argument_text}"'
    env = dict(os.environ, KAREN_LAUNCHER_TEST_EXIT=str(exit_code))
    result = subprocess.run(command, cwd=cwd, env=env, input='\n',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding='utf-8', errors='replace', timeout=60)
    recorded = json.loads((root / 'launcher-result.json').read_text(encoding='utf-8'))
    return result, recorded


@pytest.mark.parametrize('launcher, arguments', [
    ('bootstrap-windows.cmd', ['--controller', 'esp32_s3', '--marker', 'a value with spaces']),
    ('doctor-windows.cmd', ['--controller', 'esp32_s3', '--port', 'COM17', '--marker', 'a value with spaces']),
    ('start-windows.cmd', []),
])
def test_native_launchers_use_own_folder_and_forward_quoted_arguments(launcher_project, tmp_path, launcher, arguments):
    result, recorded = run_launcher(launcher_project, launcher, arguments, tmp_path)
    assert result.returncode == 0, result.stdout
    assert recorded['args'] == arguments
    assert Path(recorded['cwd']) == launcher_project
    assert Path(recorded['python']) == launcher_project / '.venv/Scripts/python.exe'
    assert recorded['utf8'] == '1'


@pytest.mark.parametrize('launcher', ['bootstrap-windows.cmd', 'doctor-windows.cmd'])
def test_native_setup_and_doctor_propagate_failure_exit_code(launcher_project, tmp_path, launcher):
    result, _ = run_launcher(launcher_project, launcher, ['--controller', 'esp32_s3'], tmp_path, exit_code=7)
    assert result.returncode == 7, result.stdout
