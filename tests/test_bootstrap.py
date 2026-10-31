import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import zipfile

import pytest

from scripts import bootstrap, toolchain


@pytest.mark.parametrize('version, accepted', [
    ((3, 11), False), ((3, 12), True), ((3, 14), True),
    ((3, 15), True), ((3, 16), False),
])
def test_supported_python_versions_reach_install_check(project, monkeypatch, version, accepted):
    monkeypatch.setattr(bootstrap, 'sys', SimpleNamespace(version_info=version))
    checked = []
    monkeypatch.setattr(bootstrap, 'check', lambda *_a: checked.append(True))
    assert bootstrap.main(['--check'], project) == (0 if accepted else 1)
    assert bool(checked) == accepted


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'Karen project with spaces'
    (root / 'firmware/karen_ai').mkdir(parents=True)
    (root / 'app.py').write_text('# test project\n')
    shutil.copyfile(bootstrap.ROOT / '.env.example', root / '.env.example')
    shutil.copyfile(bootstrap.ROOT / 'firmware/karen_ai/config.example.h', root / 'firmware/karen_ai/config.example.h')
    return root


def test_new_files_get_controller_and_secret_and_existing_files_are_never_replaced(project, capsys):
    bootstrap.prepare_files(project, 'esp32_s3')
    text = (project / '.env').read_text()
    assert 'KAREN_CONTROLLER=esp32_s3' in text
    secret = next(line.split('=', 1)[1] for line in text.splitlines() if line.startswith('SECRET_KEY='))
    assert len(secret) == 64
    originals = {'.env': text, '.env.local': 'GEMINI_MODEL=custom\n',
                 'data/memory.txt': 'Keep these saved facts', 'firmware/karen_ai/config.h': 'private wifi settings'}
    for name, content in originals.items():
        path = project / name; path.parent.mkdir(exist_ok=True, parents=True); path.write_text(content)
    bootstrap.prepare_files(project, 'esp32')
    assert all((project / name).read_text() == content for name, content in originals.items())
    assert secret not in capsys.readouterr().out


def test_broken_or_foreign_virtualenv_is_not_deleted_or_recreated(project, monkeypatch):
    (project / '.venv').mkdir()
    sentinel = project / '.venv/keep'; sentinel.write_text('leave me')
    monkeypatch.setattr(bootstrap, 'run', lambda *_a, **_k: pytest.fail('Do not overwrite environment'))
    with pytest.raises(bootstrap.SetupError, match='not replaced'):
        bootstrap.prepare_python(project)
    assert sentinel.read_text() == 'leave me'


def test_existing_environment_does_not_force_upgrade_or_recreate(project, monkeypatch):
    python = bootstrap.venv_python(project); python.parent.mkdir(parents=True); python.touch()
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda command, *_a, **_k: calls.append(command))
    assert bootstrap.prepare_python(project) == python
    assert not any('venv' in command for command in calls)
    assert not any('--upgrade' in command for command in calls)
    assert any(str(project / 'requirements.txt') in command for command in calls)


def test_windows_virtualenv_path(project, monkeypatch):
    monkeypatch.setattr(bootstrap, 'os', SimpleNamespace(name='nt'))
    assert bootstrap.venv_python(project) == project / '.venv/Scripts/python.exe'


def test_failure_output_and_log_hide_keys_wifi_and_url_passwords(project, monkeypatch, capsys):
    (project / '.env').write_text('GEMINI_API_KEY=private-ai-key\n')
    (project / 'firmware/karen_ai/config.h').write_text('#define WIFI_PASSWORD "private-wifi"\n')
    monkeypatch.setattr(bootstrap.subprocess, 'run', lambda *_a, **_k: SimpleNamespace(
        returncode=1, stdout='private-ai-key private-wifi https://user:password@example.com/packages\n'))
    with pytest.raises(bootstrap.SetupError):
        bootstrap.run(['fake'], project, 'Testing failure')
    output = capsys.readouterr().out + (project / '.tools/bootstrap.log').read_text()
    assert all(value not in output for value in ('private-ai-key', 'private-wifi', 'user:password'))


def test_matching_global_toolchain_is_reused_without_project_install(project, monkeypatch):
    monkeypatch.setattr(bootstrap, 'find_cli', lambda *_: Path('arduino-cli'))
    monkeypatch.setattr(bootstrap, 'toolchain_ready', lambda *_a, **_k: True)
    monkeypatch.setattr(bootstrap, 'run', lambda *_a, **_k: pytest.fail('Do not reinstall matching tools'))
    bootstrap.prepare_firmware(project)
    assert not (project / toolchain.LOCAL_MARKER).exists()


def test_project_cli_wins_over_path_but_explicit_setting_wins(project, monkeypatch):
    from scripts import firmware
    monkeypatch.delenv('ARDUINO_CLI', raising=False)
    local = project / '.tools' / ('arduino-cli.exe' if bootstrap.os.name == 'nt' else 'arduino-cli')
    local.parent.mkdir(); local.touch()
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: 'explicit-cli' if name == 'my-cli' else 'global-cli')
    assert bootstrap.find_cli(project) == local
    assert firmware.find_cli({}, project) == str(local)
    monkeypatch.setenv('ARDUINO_CLI', 'my-cli')
    assert str(bootstrap.find_cli(project)) == 'explicit-cli'
    assert firmware.find_cli({'ARDUINO_CLI': 'my-cli'}, project) == 'explicit-cli'


def test_missing_tools_install_in_project_scope_and_can_resume(project, monkeypatch):
    monkeypatch.setattr(bootstrap, 'find_cli', lambda *_: Path('arduino-cli'))
    results = iter([False, True])
    monkeypatch.setattr(bootstrap, 'toolchain_ready', lambda *_a, **_k: next(results))
    monkeypatch.setattr(bootstrap.shutil, 'disk_usage', lambda *_: SimpleNamespace(free=20 * 1024**3))
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda command, *_a, **kwargs: calls.append((command, kwargs['env'])))
    bootstrap.prepare_firmware(project)
    assert (project / toolchain.LOCAL_MARKER).is_file()
    assert any(f'{toolchain.CORE}@{toolchain.CORE_VERSION}' in command for command, _ in calls)
    assert any(f'{toolchain.AUDIO}@{toolchain.AUDIO_VERSION}' in command for command, _ in calls)
    assert all(env['ARDUINO_DIRECTORIES_DATA'] == str(project / '.tools/arduino/data') for _, env in calls)
    assert all('upload' not in command for command, _ in calls)


def test_low_disk_stops_board_install_without_changing_global_tools(project, monkeypatch):
    monkeypatch.setattr(bootstrap, 'find_cli', lambda *_: Path('arduino-cli'))
    monkeypatch.setattr(bootstrap, 'toolchain_ready', lambda *_a, **_k: False)
    monkeypatch.setattr(bootstrap.shutil, 'disk_usage', lambda *_: SimpleNamespace(free=1024))
    monkeypatch.setattr(bootstrap, 'run', lambda *_a, **_k: pytest.fail('Must not install with insufficient disk'))
    with pytest.raises(bootstrap.SetupError, match='8 GB'):
        bootstrap.prepare_firmware(project)
    assert not (project / toolchain.LOCAL_MARKER).exists()


def test_copied_project_toolchain_is_rejected_without_deleting_it(project):
    marker = project / toolchain.LOCAL_MARKER; marker.parent.mkdir(parents=True)
    content = json.dumps({'schema': 1, 'system': 'different operating system', 'machine': 'different cpu'})
    marker.write_text(content)
    with pytest.raises(toolchain.ToolchainError, match='different computer'):
        toolchain.arduino_environment(project)
    assert marker.read_text() == content


def test_private_value_matching_model_name_does_not_corrupt_json_checks(project, monkeypatch):
    (project / 'firmware/karen_ai/config.h').write_text('#define WIFI_SSID "esp32"\n')
    def run(command, **kwargs):
        result = {'platforms': [{'id': 'esp32:esp32', 'installed_version': '3.3.12'}]} if 'core' in command else {
            'installed_libraries': [{'library': {'name': 'ESP8266Audio', 'version': '2.4.1'}}]}
        return SimpleNamespace(returncode=0, stdout=json.dumps(result))
    monkeypatch.setattr(bootstrap.subprocess, 'run', run)
    assert bootstrap.toolchain_ready(Path('arduino-cli'), project)


def test_checksum_failure_never_installs_executable(project, monkeypatch):
    monkeypatch.setattr(bootstrap.platform, 'system', lambda: 'Darwin')
    monkeypatch.setattr(bootstrap.platform, 'machine', lambda: 'arm64')
    monkeypatch.setattr(bootstrap.urllib.request, 'urlopen', lambda *_a, **_k: io.BytesIO(b'corrupted download'))
    with pytest.raises(bootstrap.SetupError, match='checksum'):
        bootstrap.download_cli(project)
    assert not (project / '.tools/arduino-cli').exists()


def test_verified_windows_archive_extracts_only_executable(project, monkeypatch):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as package:
        package.writestr('nested/arduino-cli.exe', b'fake binary')
        package.writestr('../unexpected.txt', b'do not extract')
    data = archive.getvalue()
    monkeypatch.setattr(bootstrap.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(bootstrap.platform, 'machine', lambda: 'AMD64')
    monkeypatch.setattr(bootstrap, 'CLI_ASSETS', {('Windows', 'amd64'): ('Windows_64bit.zip', hashlib.sha256(data).hexdigest())})
    monkeypatch.setattr(bootstrap.urllib.request, 'urlopen', lambda *_a, **_k: io.BytesIO(data))
    target = bootstrap.download_cli(project)
    assert target.name == 'arduino-cli.exe' and target.read_bytes() == b'fake binary'
    assert not (project.parent / 'unexpected.txt').exists()
    assert not (project / 'nested').exists()


def test_check_does_not_create_settings_log_or_memory(project, monkeypatch):
    python = bootstrap.venv_python(project); python.parent.mkdir(parents=True); python.touch()
    (project / '.env').write_text('GEMINI_API_KEY=\n')
    before = sorted(str(path.relative_to(project)) for path in project.rglob('*'))
    monkeypatch.setattr(bootstrap.subprocess, 'run', lambda *_a, **_k: SimpleNamespace(returncode=0, stdout=''))
    assert bootstrap.main(['--check'], project) == 0
    after = sorted(str(path.relative_to(project)) for path in project.rglob('*'))
    assert before == after
    assert not (project / 'data/memory.txt').exists()


def test_compile_is_example_build_only_and_never_upload(project, monkeypatch):
    calls = []
    monkeypatch.setattr(bootstrap, 'prepare_python', lambda *_a: None)
    monkeypatch.setattr(bootstrap, 'prepare_files', lambda *_a: None)
    monkeypatch.setattr(bootstrap, 'prepare_firmware', lambda *_a: None)
    monkeypatch.setattr(bootstrap, 'prepare_board_python', lambda *_a: None)
    monkeypatch.setattr(bootstrap, 'run', lambda command, *_a, **_k: calls.append(command) or '')
    assert bootstrap.main(['--compile', '--controller', 'esp32_s3'], project) == 0
    assert len(calls) == 1
    assert calls[0][-2:] == ['--controller', 'esp32_s3']
    assert '--upload' not in calls[0] and '--use-config' not in calls[0]


def test_board_python_installs_identification_tools_without_flashing(project, monkeypatch):
    calls = []
    environments = []
    monkeypatch.setenv('PYYAML_FORCE_LIBYAML', '1')
    monkeypatch.setenv('KAREN_TEST_KEEP', 'keep-environment')
    def run(command, *_a, **kwargs):
        calls.append(command)
        environments.append(kwargs.get('env'))
    monkeypatch.setattr(bootstrap, 'run', run)
    bootstrap.prepare_board_python(project)
    assert calls[0][-2:] == ['-r', str(project / 'requirements-board.txt')]
    assert calls[1][-3:] == ['-m', 'esptool', 'version']
    assert not any('write-flash' in command or 'erase-flash' in command for command in calls)
    assert environments[0]['PYYAML_FORCE_LIBYAML'] == '0'
    assert environments[0]['KAREN_TEST_KEEP'] == 'keep-environment'
    assert bootstrap.os.environ['PYYAML_FORCE_LIBYAML'] == '1'
    assert environments[1] is None  # Installer choice stays scoped to pip.


def test_setup_log_records_timing_exit_and_sanitized_output(project, monkeypatch):
    (project / '.env').write_text('GEMINI_API_KEY=hidden-key\n')
    monkeypatch.setattr(bootstrap.subprocess, 'run', lambda *_a, **_k: SimpleNamespace(returncode=0, stdout='ok hidden-key'))
    bootstrap.run(['fake'], project, 'Checking fake tool')
    log = (project / '.tools/bootstrap.log').read_text()
    assert 'START Checking fake tool' in log
    assert 'END exit=0 elapsed=' in log
    assert 'hidden-key' not in log and '[REDACTED]' in log


def test_escaped_wifi_passwords_are_hidden_in_source_and_decoded_output(project):
    config = '#define WIFI_PASSWORD "private\\"password\\\\tail"\n'
    (project / 'firmware/karen_ai/config.h').write_text(config)
    source = 'private\\"password\\\\tail'
    decoded = 'private"password\\tail'
    output = bootstrap.sanitized(config + source + '\n' + decoded, bootstrap.private_values(project))
    assert source not in output and decoded not in output
    assert '[credential definition redacted]' in output


def test_mac_launcher_handles_spaces_and_other_working_directory(project):
    if bootstrap.os.name == 'nt' or not shutil.which('bash'):
        pytest.skip('Mac shell launcher requires a POSIX host')
    shutil.copyfile(bootstrap.ROOT / 'bootstrap-mac.command', project / 'bootstrap-mac.command')
    python = project / '.venv/bin/python'; python.parent.mkdir(parents=True)
    python.write_text('#!/bin/sh\nif [ "$1" = "-c" ]; then exit 0; fi\nprintf "%s\\n" "$PWD" "$@"\n')
    python.chmod(0o755)
    result = subprocess.run(['bash', str(project / 'bootstrap-mac.command'), '--check'],
                            cwd=project.parent, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0
    assert result.stdout.splitlines() == [str(project), str(project / 'scripts/bootstrap.py'), '--check']
