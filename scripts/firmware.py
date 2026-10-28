"""Build/upload either Karen controller on Windows, macOS or Linux.

KAREN_CONTROLLER comes from shell > .env.local > .env > esp32.
Normal builds use example credentials. --upload requires a real config.h and port.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from dotenv import dotenv_values
if __package__:
    from .toolchain import arduino_environment
else:
    from toolchain import arduino_environment

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    'esp32': 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M,UploadSpeed=115200',
    'esp32_s3': ('esp32:esp32:esp32s3:PartitionScheme=no_ota,FlashSize=16M,FlashMode=qio,'
                 'PSRAM=opi,USBMode=hwcdc,CDCOnBoot=default,UploadMode=default,UploadSpeed=115200'),
}


def settings_for(root, environment=None):
    return {**dotenv_values(root / '.env', interpolate=False),
            **dotenv_values(root / '.env.local', interpolate=False),
            **(os.environ if environment is None else environment)}


def select_controller(settings, explicit=None):
    selected = explicit if explicit is not None else settings.get('KAREN_CONTROLLER', 'esp32')
    if selected not in PROFILES:
        raise ValueError('Unknown KAREN_CONTROLLER. Use esp32 or esp32_s3.')
    return selected


def find_cli(settings, root):
    configured = settings.get('ARDUINO_CLI')
    if configured:
        found = shutil.which(configured)
        if found:
            return found
        raise ValueError('ARDUINO_CLI does not point to an executable Arduino CLI.')
    local = root / '.tools' / ('arduino-cli.exe' if os.name == 'nt' else 'arduino-cli')
    if local.is_file():
        return str(local)
    found = shutil.which('arduino-cli')
    if found:
        return found
    raise ValueError('Install Arduino CLI and add it to PATH, or set ARDUINO_CLI to its executable path.')


def redact_output(output, config, settings):
    # Compile errors can quote config.h source. Hide credential definitions and
    # literal values, including escaped C++ strings; never use shell commands.
    output = re.sub(r'^.*#\s*define\s+(?:WIFI_SSID|WIFI_PASSWORD)\b.*$',
                    '[credential definition redacted]', output, flags=re.MULTILINE)
    values = [value for key, value in settings.items() if value and
              any(part in key.upper() for part in ('API_KEY', 'SECRET', 'TOKEN', 'PASSWORD'))]
    for name in ('WIFI_SSID', 'WIFI_PASSWORD'):
        match = re.search(r'^\s*#\s*define\s+' + name + r'\s+"((?:\\.|[^"\\])*)"', config, re.MULTILINE)
        if match:
            values.append(match.group(1))
            # The compiler may display either the source spelling or decoded value.
            values.append(re.sub(r'\\(["\\])', r'\1', match.group(1)))
    for value in sorted(set(values), key=len, reverse=True):
        if value:
            output = output.replace(value, '[REDACTED]')
    return output


def run_tool(command, config, settings, timeout, env=None):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding='utf-8', errors='replace', timeout=timeout, env=env)
    print(redact_output(result.stdout or '', config, settings), end='', flush=True)
    return result.returncode


def build(args, root=ROOT, environment=None):
    settings = settings_for(root, environment)
    controller = select_controller(settings, args.controller)
    if args.upload and not args.port:
        raise ValueError('--upload requires --port (for example COM5). No board is selected automatically.')
    source = root / 'firmware' / 'karen_ai'
    private = args.use_config or args.upload
    config_path = source / ('config.h' if private else 'config.example.h')
    if not config_path.is_file():
        raise ValueError('Create firmware/karen_ai/config.h from config.example.h and configure WiFi/server first.')
    config = config_path.read_text(encoding='utf-8')
    if args.upload and any(value in config for value in ('YOUR_2_4_GHZ_HOTSPOT', 'YOUR_HOTSPOT_PASSWORD')):
        raise ValueError('Replace the example WiFi placeholders in config.h before uploading.')
    cli = find_cli(settings, root)
    tool_environment = arduino_environment(root)
    fqbn = PROFILES[controller]
    print(f'Controller: {controller}\nTarget: {fqbn}\nCredentials: {"private config.h" if private else "example only"}', flush=True)
    with tempfile.TemporaryDirectory(prefix='karen-build-') as temporary:
        work = Path(temporary)
        sketch, artifacts = work / 'karen_ai', work / 'artifacts'
        shutil.copytree(source, sketch, ignore=shutil.ignore_patterns('config.h'))
        (sketch / 'config.h').write_text(config, encoding='utf-8')
        # Absolute argument lists work with spaces/Windows paths and do not invoke a shell.
        command = [cli, 'compile', '--fqbn', fqbn, '--build-path', str(work / 'build'),
                   '--output-dir', str(artifacts), str(sketch)]
        code = run_tool(command, config, settings, timeout=600, env=tool_environment)
        if code or not args.upload:
            return code
        print('Uploading to the explicitly selected port…', flush=True)
        return run_tool([cli, 'upload', '--fqbn', fqbn, '--input-dir', str(artifacts),
                         '--port', args.port, str(sketch)], config, settings, timeout=240, env=tool_environment)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', choices=PROFILES, help='Override KAREN_CONTROLLER for this command')
    parser.add_argument('--use-config', action='store_true', help='Compile with private config.h instead of example credentials')
    parser.add_argument('--upload', action='store_true', help='Build with private config.h, then upload to --port')
    parser.add_argument('--port', help='Explicit serial port, e.g. COM5 or /dev/cu.usbserial-…')
    args = parser.parse_args(argv)
    try:
        return build(args)
    except (ValueError, OSError) as exc:
        # File/config errors contain no secret values; unexpected subprocess
        # errors/tracebacks are deliberately not printed with captured output.
        # Report actionable validation errors, but keep OS exception paths concise.
        print(str(exc) if isinstance(exc, ValueError) else 'Could not run Arduino CLI or access firmware files. Check installation and permissions.')
        return 1
    except subprocess.TimeoutExpired:
        print('Arduino operation timed out. Check the toolchain/connection before retrying.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
