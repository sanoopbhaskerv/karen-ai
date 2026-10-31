"""Safe Windows/Mac setup. Python 3.12-3.15 is the only prerequisite.

No arguments: a short menu in a terminal, computer-only setup otherwise.
Existing private files and memory are never replaced. No live AI call or upload.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request
import zipfile

if __package__:
    from .toolchain import CORE, CORE_VERSION, AUDIO, AUDIO_VERSION, INDEX_URL, LOCAL_MARKER, arduino_environment, isolation_identity, ToolchainError, COMPILE_TIMEOUT_SECONDS
else:
    from toolchain import CORE, CORE_VERSION, AUDIO, AUDIO_VERSION, INDEX_URL, LOCAL_MARKER, arduino_environment, isolation_identity, ToolchainError, COMPILE_TIMEOUT_SECONDS

ROOT = Path(__file__).resolve().parents[1]
CLI_VERSION = '1.5.1'
# SHA-256 digests published on the official Arduino v1.5.1 release assets.
CLI_ASSETS = {
    ('Darwin', 'arm64'): ('macOS_ARM64.tar.gz', 'cb952e8c1621c95ef5f1d17831c945e3d0ec5973f89c557a7ec8feb9c4f7d4c9'),
    ('Darwin', 'x86_64'): ('macOS_64bit.tar.gz', 'c982e940027996bea9901050e95fae99c59c1dcfee54beedecaf28141e7bf2e7'),
    ('Windows', 'amd64'): ('Windows_64bit.zip', 'fabe42e0eb04d00e776a66178299ff95a46c623dbc260f997e58fd514853dd40'),
}


class SetupError(Exception):
    pass


def private_values(root):
    values = [v for k, v in os.environ.items() if v and any(x in k.upper() for x in ('KEY', 'TOKEN', 'PASSWORD', 'SECRET'))]
    for name in ('.env', '.env.local'):
        path = root / name
        if path.is_file():
            for line in path.read_text(encoding='utf-8').splitlines():
                key, separator, value = line.partition('=')
                if separator and any(x in key.upper() for x in ('KEY', 'TOKEN', 'PASSWORD', 'SECRET')):
                    values.append(value.strip().strip('\'"'))
    path = root / 'firmware/karen_ai/config.h'
    if path.is_file():
        for value in re.findall(r'^\s*#\s*define\s+WIFI_(?:SSID|PASSWORD)\s+"((?:\\.|[^"\\])*)"', path.read_text(encoding='utf-8'), re.M):
            values.extend((value, re.sub(r'\\(["\\])', r'\1', value)))
    return sorted({v for v in values if v}, key=len, reverse=True)


def sanitized(text, values):
    text = re.sub(r'^.*#\s*define\s+WIFI_(?:SSID|PASSWORD)\b.*$',
                  '[credential definition redacted]', text, flags=re.MULTILINE)
    text = re.sub(r'(https?://)[^\s/@]+:[^\s/@]+@', r'\1[REDACTED]@', text)
    for value in values:
        text = text.replace(value, '[REDACTED]')
    return text


def setup_log(root, message):
    path = root / '.tools/bootstrap.log'
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with path.open('a', encoding='utf-8') as handle:
        handle.write(f'[{stamp}] {message}\n')


def run(command, root, label, *, env=None, timeout=600, log=True):
    print(label, flush=True)
    values = private_values(root)
    started = time.monotonic()
    stopped = threading.Event()
    safe_label = sanitized(label, values)
    if log:
        setup_log(root, 'START ' + safe_label)

    def heartbeat():
        while not stopped.wait(20):
            message = f'Still working ({int(time.monotonic() - started)}s): {safe_label}'
            print(message, flush=True)
            if log:
                setup_log(root, message)

    worker = threading.Thread(target=heartbeat, daemon=True)
    worker.start()
    try:
        result = subprocess.run(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                errors='replace', timeout=timeout)
    except subprocess.TimeoutExpired:
        if log:
            setup_log(root, f'TIMEOUT after {int(time.monotonic() - started)}s: {safe_label}')
        raise SetupError('That step timed out. Check internet/the tool installation, then rerun setup.') from None
    finally:
        stopped.set()
        worker.join(timeout=1)
    output = sanitized(result.stdout or '', values)
    if log:
        setup_log(root, f'END exit={result.returncode} elapsed={time.monotonic() - started:.1f}s: {safe_label}\n{output}')
    if result.returncode:
        print('\n'.join(deque(output.splitlines(), maxlen=16)))
        raise SetupError('Step failed. Read the message above. Existing settings and memory were kept.')
    # Parsing callers need unmodified JSON. Only sanitized output reaches logs/UI.
    return result.stdout or ''


def prepare_board_python(root):
    python = venv_python(root)
    # PyYAML may have no wheel for a newly released Python. Its source build
    # otherwise attempts a C extension and fails on student Windows laptops.
    # esptool works with pure-Python YAML; scope this choice to this pip process.
    environment = dict(os.environ, PYYAML_FORCE_LIBYAML='0')
    run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
         '-r', str(root / 'requirements-board.txt')], root,
        'Installing board identification tools (PyYAML source builds use pure Python; no C compiler needed)...',
        env=environment)
    run([str(python), '-m', 'esptool', 'version'], root, 'Checking esptool version...', timeout=60)


def create_once(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, 'wb') as handle:
        handle.write(content)
    return True


def prepare_files(root, controller):
    # Only the NEW file gets a session secret and selected controller. Never edit
    # existing .env/.env.local, firmware credentials, data/memory.txt or sources.
    text = (root / '.env.example').read_text(encoding='utf-8')
    text = re.sub(r'^SECRET_KEY=.*$', 'SECRET_KEY=' + secrets.token_hex(32), text, flags=re.M)
    text = re.sub(r'^KAREN_CONTROLLER=.*$', 'KAREN_CONTROLLER=' + (controller or 'esp32_s3'), text, flags=re.M)
    created = create_once(root / '.env', text.encode('utf-8'))
    print(('Created' if created else 'Kept existing') + ' .env (contents hidden).')
    created = create_once(root / 'firmware/karen_ai/config.h', (root / 'firmware/karen_ai/config.example.h').read_bytes())
    print(('Created example' if created else 'Kept existing') + ' firmware/karen_ai/config.h.')


def venv_python(root):
    return root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def prepare_python(root, dev=False):
    python = venv_python(root)
    if (root / '.venv').exists():
        if not python.is_file():
            raise SetupError('Existing .venv is incomplete or from another operating system. It was not replaced. Ask the owner to move ONLY .venv aside and rerun setup.')
        try:
            run([str(python), '-c', 'import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))'],
                root, 'Checking existing Python environment...')
        except SetupError:
            raise SetupError('Existing .venv does not run a supported Python. It was kept. Ask the owner to move ONLY .venv aside, install Python 3.14, then rerun setup.') from None
    else:
        run([sys.executable, '-m', 'venv', str(root / '.venv')], root, 'Creating this computer\'s Python environment...')
    requirement = 'requirements-dev.txt' if dev else 'requirements.txt'
    run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(root / requirement)],
        root, 'Installing Python packages; this may take a few minutes...')
    run([str(python), '-m', 'pip', 'check'], root, 'Checking package dependencies...')
    return python


def find_cli(root):
    explicit = os.getenv('ARDUINO_CLI')
    if explicit:
        found = shutil.which(explicit)
        if not found:
            raise SetupError('ARDUINO_CLI is set but its executable was not found. Correct that setting first.')
        return Path(found)
    local = root / '.tools' / ('arduino-cli.exe' if os.name == 'nt' else 'arduino-cli')
    if local.is_file():
        return local
    found = shutil.which('arduino-cli')
    return Path(found) if found else None


def download_cli(root):
    system, machine = platform.system(), platform.machine().lower()
    if machine == 'aarch64' and system == 'Darwin':
        machine = 'arm64'
    asset = CLI_ASSETS.get((system, machine))
    if not asset:
        raise SetupError('Automatic Arduino download supports Intel/Apple Silicon Mac and x64 Windows. Install Arduino CLI manually for this computer architecture.')
    suffix, expected = asset
    archive_name = f'arduino-cli_{CLI_VERSION}_{suffix}'
    url = f'https://github.com/arduino/arduino-cli/releases/download/v{CLI_VERSION}/{archive_name}'
    tools = root / '.tools'; tools.mkdir(exist_ok=True)
    binary = 'arduino-cli.exe' if system == 'Windows' else 'arduino-cli'
    print('Downloading official Arduino CLI; verifying SHA-256...', flush=True)
    with tempfile.TemporaryDirectory(prefix='karen-cli-') as folder:
        archive = Path(folder) / archive_name
        request = urllib.request.Request(url, headers={'User-Agent': 'Karen-AI-bootstrap'})
        digest, total = hashlib.sha256(), 0
        with urllib.request.urlopen(request, timeout=30) as source, archive.open('wb') as target:
            while chunk := source.read(1024 * 1024):
                total += len(chunk)
                if total > 128 * 1024 * 1024:
                    raise SetupError('Arduino download exceeded the expected size limit.')
                digest.update(chunk); target.write(chunk)
        if digest.hexdigest() != expected:
            raise SetupError('Arduino download checksum failed. Nothing was installed. Rerun setup on a reliable connection.')
        # Extract only the executable; never extract arbitrary archive paths/links.
        if suffix.endswith('.zip'):
            with zipfile.ZipFile(archive) as package:
                matches = [m for m in package.infolist() if Path(m.filename).name == binary and not m.is_dir()]
                if len(matches) != 1 or matches[0].file_size > 128 * 1024 * 1024:
                    raise SetupError('Unexpected Arduino archive layout.')
                content = package.read(matches[0])
        else:
            with tarfile.open(archive) as package:
                matches = [m for m in package.getmembers() if Path(m.name).name == binary and m.isfile()]
                if len(matches) != 1 or matches[0].size > 128 * 1024 * 1024:
                    raise SetupError('Unexpected Arduino archive layout.')
                content = package.extractfile(matches[0]).read()
        target = tools / binary
        if create_once(target, content):
            target.chmod(0o755)
    return target


def toolchain_ready(cli, root, *, log=True):
    env = arduino_environment(root)
    try:
        cores = json.loads(run([str(cli), 'core', 'list', '--json'], root, 'Checking ESP32 core...', env=env, timeout=60, log=log))
        libraries = json.loads(run([str(cli), 'lib', 'list', '--json'], root, 'Checking audio library...', env=env, timeout=60, log=log))
        core_ok = any(p.get('id') == CORE and p.get('installed_version') == CORE_VERSION for p in cores.get('platforms', []))
        library_ok = any(p.get('library', {}).get('name') == AUDIO and p['library'].get('version') == AUDIO_VERSION
                         for p in libraries.get('installed_libraries', []))
        return core_ok and library_ok
    except (SetupError, json.JSONDecodeError):
        return False


def prepare_firmware(root):
    cli = find_cli(root) or download_cli(root)
    if toolchain_ready(cli, root):
        print('Matching ESP32 core and audio library already installed; keeping them.')
        return
    if shutil.disk_usage(root).free < 8 * 1024**3:
        raise SetupError('Board setup needs at least 8 GB free disk space. Computer chat setup can still be used. Free space, then rerun with --firmware.')
    # Avoid downgrading or replacing another project's global board/library setup.
    create_once(root / LOCAL_MARKER, json.dumps(isolation_identity()).encode('utf-8'))
    env = arduino_environment(root)
    for path in ('data', 'downloads', 'user'):
        (root / '.tools/arduino' / path).mkdir(parents=True, exist_ok=True)
    print('Installing a project-local board toolchain under .tools/arduino. This is a large download; allow several GB of disk space.', flush=True)
    run([str(cli), 'core', 'update-index', '--additional-urls', INDEX_URL], root, 'Downloading Arduino package indexes...', env=env, timeout=600)
    run([str(cli), 'core', 'install', f'{CORE}@{CORE_VERSION}', '--additional-urls', INDEX_URL], root,
        'Installing ESP32 support. On a slow connection this can take 20 minutes or more...', env=env, timeout=3600)
    run([str(cli), 'lib', 'install', f'{AUDIO}@{AUDIO_VERSION}'], root, 'Installing ESP8266Audio...', env=env, timeout=600)
    if not toolchain_ready(cli, root):
        raise SetupError('Arduino installation did not pass verification. Rerun setup; no firmware was uploaded.')


def check(root, firmware=False):
    python = venv_python(root)
    if not python.is_file():
        raise SetupError('Python environment missing. Run setup first.')
    run([str(python), '-c', 'import flask, dotenv, speech_recognition, gtts; from google import genai'],
        root, 'Checking backend imports (no AI request)...', timeout=60, log=False)
    probe = ('from importlib.metadata import version; from pathlib import Path; '
             'from packaging.requirements import Requirement; import sys; '
             'requirements=[Requirement(s.strip()) for s in Path(sys.argv[1]).read_text().splitlines() '
             'if s.strip() and not s.lstrip().startswith(("#","-"))]; '
             'bad=[r.name for r in requirements if version(r.name) not in r.specifier]; '
             'print("Missing/outdated packages: "+", ".join(bad)) if bad else None; sys.exit(bool(bad))')
    run([str(python), '-c', probe, str(root / 'requirements.txt')], root,
        'Checking runtime package versions...', timeout=60, log=False)
    if not (root / '.env').is_file():
        raise SetupError('.env is missing. Run setup first.')
    if firmware:
        run([str(python), '-m', 'esptool', 'version'], root,
            'Checking board identification tools...', timeout=60, log=False)
        cli = find_cli(root)
        if not cli or not toolchain_ready(cli, root, log=False):
            raise SetupError('Board tools incomplete. Run setup with --firmware.')
    print('Installation checks passed. This does NOT validate the Gemini key or physical hardware.')


def main(argv=None, root=ROOT):
    supplied = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware', action='store_true', help='Also install/verify the board toolchain')
    parser.add_argument('--controller', choices=('esp32', 'esp32_s3'), help='Select controller for a NEW .env and optional example build; existing settings are kept')
    parser.add_argument('--compile', action='store_true', help='Also build example firmware, never upload (implies --firmware)')
    parser.add_argument('--dev', action='store_true', help='Also install test dependencies')
    parser.add_argument('--check', action='store_true', help='Check installation without running setup or making AI requests')
    args = parser.parse_args(supplied)
    if args.check and (args.compile or args.dev):
        parser.error('--check cannot be combined with --compile or --dev')
    try:
        if not (3, 12) <= sys.version_info[:2] < (3, 16):
            raise SetupError('Use Python 3.12, 3.13, 3.14 or 3.15. See the English/Malayalam README.')
        if not (root / 'app.py').is_file():
            raise SetupError('Project files missing. Extract the complete project ZIP before running setup.')
        if not supplied and sys.stdin.isatty():
            print('Karen AI setup\n1. Computer chat only (recommended first)\n2. Computer + ESP32-S3 tools\n3. Computer + classic ESP32 tools')
            choice = input('Choose 1, 2 or 3 [1]: ').strip() or '1'
            if choice not in ('1', '2', '3'):
                raise SetupError('Choose 1, 2 or 3, then rerun setup.')
            args.firmware = choice != '1'
            args.controller = 'esp32' if choice == '3' else 'esp32_s3'
        if args.check:
            check(root, args.firmware)
            return 0
        setup_log(root, f'SESSION Python={platform.python_version()} OS={platform.system()} CPU={platform.machine()} controller={args.controller or "existing/default"}')
        prepare_python(root, args.dev)
        prepare_files(root, args.controller)
        if args.firmware or args.compile:
            prepare_board_python(root)
            prepare_firmware(root)
        if args.compile:
            command = [str(venv_python(root)), str(root / 'scripts/firmware.py')]
            if args.controller:
                command += ['--controller', args.controller]
            output = run(command, root, 'Compiling example firmware; no upload...', timeout=COMPILE_TIMEOUT_SECONDS + 120)
            print(sanitized(output, private_values(root)))
        launcher = 'start-windows.cmd' if os.name == 'nt' else 'start-mac.command'
        print(f'\nSETUP COMPLETE\n1. Add GEMINI_API_KEY locally in .env only if blank; keep an existing key. Never share it.\n2. Run {launcher}.\n3. Open http://localhost:8080 (default port) and test text chat first.\nFor the board, edit private config.h and follow Step 10 onward in the README.\nExisting .env/.env.local/config.h and saved memory were preserved.\nA setup check does not prove live AI or hardware works.\nSafe setup log: .tools/bootstrap.log')
        return 0
    except KeyboardInterrupt:
        print('\nSetup cancelled. Rerun it to continue; existing private files were kept.')
        return 130
    except (SetupError, OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as error:
        print('SETUP STOPPED: ' + (str(error) if isinstance(error, (SetupError, ToolchainError)) else 'Could not complete a download or access setup files. Check internet, available disk space and permissions, then rerun.'))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
