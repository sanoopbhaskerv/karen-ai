"""Read-only Karen setup checks; optional chip probe resets the selected board.

No firmware upload, flash erase, AI request, firewall changes or private-file edits.
Run with this project's .venv Python after bootstrap. Logs: .tools/doctor.log.
"""
import argparse
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

if __package__:
    from .bootstrap import private_values, sanitized, venv_python
    from .toolchain import CORE, CORE_VERSION, AUDIO, AUDIO_VERSION, arduino_environment
else:
    from bootstrap import private_values, sanitized, venv_python
    from toolchain import CORE, CORE_VERSION, AUDIO, AUDIO_VERSION, arduino_environment

ROOT = Path(__file__).resolve().parents[1]
ESPTOOL_CHECK = ('from importlib.metadata import version; import sys; '
                 'v=version("esptool"); print(v); sys.exit(not (5 <= int(v.split(".")[0]) < 6))')


class Doctor:
    def __init__(self, root):
        self.root = root
        self.values = private_values(root)
        self.failures = 0
        self.warnings = 0
        self.log = root / '.tools/doctor.log'
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.config = ''
        path = root / 'firmware/karen_ai/config.h'
        if path.is_file():
            self.config = path.read_text(encoding='utf-8')
            # Hide both the C++ source spelling and decoded quoted/backslash
            # values; compiler/tool output can use either spelling.
            for match in re.finditer(r'^\s*#\s*define\s+WIFI_(?:SSID|PASSWORD)\s+"((?:\\.|[^"\\])*)"', self.config, re.M):
                value = match.group(1)
                self.values += [value, re.sub(r'\\(["\\])', r'\1', value)]
        self.values = sorted(set(self.values), key=len, reverse=True)
        self.write('\n=== Karen doctor ' + datetime.now(timezone.utc).isoformat() + ' ===')

    def write(self, message, *, console=True):
        safe = sanitized(str(message), self.values)
        safe = re.sub(r'^.*#\s*define\s+WIFI_(?:SSID|PASSWORD)\b.*$', '[credential definition redacted]', safe, flags=re.M)
        with self.log.open('a', encoding='utf-8') as handle:
            handle.write(safe + '\n')
        if console:
            print(safe, flush=True)

    def result(self, status, label, detail):
        self.failures += status == 'FAIL'
        self.warnings += status == 'WARN'
        self.write(f'[{status}] {label}: {detail}')

    def run(self, command, *, env=None, timeout=60):
        # Do not log command arguments: a configured executable path can contain
        # credentials. Capture tools before displaying any of their output.
        result = subprocess.run(command, cwd=self.root, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                errors='replace', timeout=timeout)
        self.write((result.stdout or '')[-60000:], console=False)
        return result


def define_value(config, name):
    match = re.search(r'^\s*#\s*define\s+' + name + r'\s+"((?:\\.|[^"\\])*)"', config, re.M)
    return match.group(1) if match else None


def validate_origin(value):
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
        raise ValueError('Use an http:// or https:// server origin with no login, path, query or fragment.')
    # Reading .port also validates malformed/invalid port syntax.
    parsed.port
    return value.rstrip('/')


def validate_firmware_origin(value):
    origin = validate_origin(value)
    if origin != value:
        raise ValueError('Firmware SERVER_ORIGIN must have no trailing slash.')
    hostname = urllib.parse.urlsplit(origin).hostname.lower().rstrip('.')
    if hostname == 'localhost' or hostname.endswith('.localhost'):
        raise ValueError('The board needs the backend computer LAN address, not localhost.')
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and (address.is_loopback or address.is_unspecified):
        raise ValueError('The board needs the backend computer LAN address, not a loopback/listen address.')
    return origin


def port_identity(value):
    return value.upper() if re.fullmatch(r'COM\d+', value, flags=re.I) else value


def check_health(doctor, origin):
    try:
        origin = validate_origin(origin)
        request = urllib.request.Request(origin + '/health', headers={'Accept': 'application/json'})
        with urllib.request.urlopen(request, timeout=8) as response:
            content = response.read(65537)
            if response.status != 200 or len(content) > 65536:
                raise ValueError('Unexpected health response.')
            health = json.loads(content)
        if not isinstance(health, dict) or health.get('status') != 'ok' or not isinstance(health.get('gemini'), dict):
            raise ValueError('Unexpected health response.')
        # Only print known status fields; never log arbitrary server response data.
        gemini = health['gemini']
        status = gemini.get('status')
        status = status if status in ('untested', 'ready', 'degraded', 'unconfigured') else 'unknown'
        doctor.result('PASS', 'Backend health', f'/health reachable; Gemini status={status}. No AI request made.')
        if health.get('mode') != 'live' or not health.get('configured'):
            doctor.result('WARN', 'Backend mode', 'Backend is in demo mode or has no configured key. Ask the owner to configure live mode before AI tests.')
        if status != 'ready':
            doctor.result('WARN', 'Live AI', 'Run scripts/diagnose_gemini.py and browser text/voice tests separately; health alone cannot validate a key.')
    except (OSError, ValueError, urllib.error.URLError):
        doctor.result('FAIL', 'Backend health', 'Could not read Karen /health. Start the server, check the LAN IPv4/port and trusted Private-network firewall rule. Firewall was not changed.')


def chip_matches(output, controller):
    chip = re.search(r'(?:Chip(?:\s+is|\s+type)?\s*:\s*|Detecting chip type[^\n]*?)(ESP32(?:-S3)?)(?=[\s(\r\n]|$)', output, re.I)
    flash = re.search(r'Detected flash size\s*:\s*(\d+)\s*MB', output, re.I)
    expected_chip, expected_mb = ('ESP32-S3', 16) if controller == 'esp32_s3' else ('ESP32', 4)
    return bool(chip and chip.group(1).upper() == expected_chip and flash and int(flash.group(1)) == expected_mb)


def check_chip(doctor, python, controller, port):
    doctor.write('Chip probe: close Serial Monitor first. The selected board may reset; no firmware or flash data is written.')
    try:
        result = doctor.run([str(python), '-m', 'esptool', '--port', port, 'flash-id'], timeout=45)
        if result.returncode:
            doctor.result('FAIL', 'Chip/flash probe', 'Probe failed. Check the COM port, data cable and closed Serial Monitor. Run board bootstrap to install esptool; see sanitized doctor.log for tool details.')
        elif not chip_matches(result.stdout or '', controller):
            doctor.result('FAIL', 'Chip/flash identity', 'Measured chip/flash did not match the selected profile or could not be parsed. Do not upload; ask the owner to inspect sanitized doctor.log.')
        else:
            expected = 'ESP32-S3 / 16 MB flash' if controller == 'esp32_s3' else 'ESP32 / 4 MB flash'
            doctor.result('PASS', 'Chip/flash identity', expected + '. PSRAM still needs the firmware boot log; this does not validate wiring.')
    except (OSError, subprocess.TimeoutExpired):
        doctor.result('FAIL', 'Chip/flash probe', 'Could not complete the probe. Check the selected port, cable and esptool installation; close Serial Monitor.')


def checks(doctor, args):
    root = doctor.root
    doctor.write(f'Computer: {platform.system()} {platform.machine()}; Python {platform.python_version()}; selected controller={args.controller}.')
    python = venv_python(root)
    if not python.is_file():
        doctor.result('FAIL', 'Project Python', 'Missing .venv for this operating system. Run bootstrap-windows.cmd first; do not copy a Mac .venv.')
        return
    if not (3, 12) <= sys.version_info[:2] < (3, 15):
        doctor.result('FAIL', 'Python version', 'Use Python 3.12–3.14 and rerun bootstrap.')
        return
    try:
        result = doctor.run([str(python), '-c', 'import flask, dotenv, speech_recognition, gtts; from google import genai'], timeout=30)
        if result.returncode:
            doctor.result('FAIL', 'Backend packages', 'Imports failed. Rerun bootstrap; details are in doctor.log.')
            return
        doctor.result('PASS', 'Backend packages', 'Required imports work; no AI call made.')
        if __package__:
            from .firmware import settings_for, find_cli
        else:
            from firmware import settings_for, find_cli
        settings = settings_for(root)
    except (OSError, subprocess.TimeoutExpired, ImportError):
        doctor.result('FAIL', 'Project environment', 'Run doctor with .venv Python after successful bootstrap.')
        return
    if not (root / '.env').is_file():
        doctor.result('FAIL', 'Computer settings', '.env missing. Rerun bootstrap to create missing settings.')
    else:
        doctor.result('PASS', 'Computer settings', '.env exists; private contents hidden.')
    if settings.get('KAREN_CONTROLLER', 'esp32') != args.controller:
        doctor.result('WARN', 'Controller setting', 'Effective .env/.env.local/shell selection differs from this check. Use --controller explicitly for firmware builds/uploads; ask the owner to align settings.')
    key = settings.get('GEMINI_API_KEY', '')
    if not key or key.startswith(('PASTE_', 'YOUR_')):
        doctor.result('WARN', 'Gemini key', 'A real key is not configured. The owner should set it locally before live text/voice tests; never share it in logs.')
    else:
        doctor.result('PASS', 'Gemini key', 'A value is configured; validity/quota/model access have not been tested.')
    config_ok = all(define_value(doctor.config, name) for name in ('WIFI_SSID', 'WIFI_PASSWORD', 'SERVER_ORIGIN'))
    if not config_ok or any(value in doctor.config for value in ('YOUR_2_4_GHZ_HOTSPOT', 'YOUR_HOTSPOT_PASSWORD')):
        doctor.result('WARN', 'Firmware settings', 'Private config.h is missing/incomplete or contains examples. Set the 2.4 GHz WiFi and backend LAN address locally before upload.')
    else:
        try:
            validate_firmware_origin(define_value(doctor.config, 'SERVER_ORIGIN'))
            doctor.result('PASS', 'Firmware settings', 'Required definitions and server origin format valid; actual WiFi credentials and reachability are untested.')
        except ValueError:
            doctor.result('WARN', 'Firmware settings', 'SERVER_ORIGIN must be http:// or https:// plus the backend LAN address/port, with no localhost, loopback, 0.0.0.0, trailing slash, path or login.')
    esptool_ok = False
    try:
        result = doctor.run([str(python), '-c', ESPTOOL_CHECK], timeout=30)
        esptool_ok = result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        pass
    if esptool_ok:
        doctor.result('PASS', 'Chip probe tool', 'esptool 5.x installed in the project environment.')
    else:
        doctor.result('FAIL' if args.probe_chip else 'WARN', 'Chip probe tool', 'esptool 5.x missing or unsupported. Rerun bootstrap-windows.cmd --firmware, or install requirements-board.txt with .venv Python.')
    selected_port = None
    try:
        cli = find_cli(settings, root)
        env = arduino_environment(root)
        core = doctor.run([cli, 'core', 'list', '--json'], env=env)
        audio = doctor.run([cli, 'lib', 'list', '--json'], env=env)
        cores = json.loads(core.stdout or '{}') if not core.returncode else {}
        libraries = json.loads(audio.stdout or '{}') if not audio.returncode else {}
        core_ok = any(x.get('id') == CORE and x.get('installed_version') == CORE_VERSION for x in cores.get('platforms', []))
        audio_ok = any(x.get('library', {}).get('name') == AUDIO and x['library'].get('version') == AUDIO_VERSION for x in libraries.get('installed_libraries', []))
        if core_ok and audio_ok:
            doctor.result('PASS', 'Arduino toolchain', f'ESP32 core {CORE_VERSION}; {AUDIO} {AUDIO_VERSION}.')
        else:
            doctor.result('FAIL', 'Arduino toolchain', 'Matching ESP32 core/audio library missing. Rerun bootstrap-windows.cmd --firmware --controller ' + args.controller)
        ports = doctor.run([cli, 'board', 'list', '--json'], env=env)
        if ports.returncode:
            doctor.result('FAIL', 'Serial ports', 'Could not enumerate ports. See doctor.log; check Arduino installation.')
        else:
            detected = json.loads(ports.stdout or '{}').get('detected_ports', [])
            addresses = [x.get('port', {}).get('address', '') for x in detected if x.get('port', {}).get('protocol') == 'serial']
            doctor.result('PASS' if addresses else 'WARN', 'Serial ports', ', '.join(addresses) if addresses else 'No serial ports found. Connect only the controller through its COM connector with a USB data cable.')
            if args.port:
                selected_port = next((value for value in addresses if port_identity(value) == port_identity(args.port)), None)
                if not selected_port:
                    doctor.result('FAIL', 'Selected port', 'The requested port is not listed. Compare ports before/after plugging the board in; do not guess a COM number.')
    except (ValueError, OSError, subprocess.TimeoutExpired, AttributeError, TypeError):
        doctor.result('FAIL', 'Arduino checks', 'Could not inspect the board tools. Rerun board bootstrap; see doctor.log. No upload attempted.')
    if args.probe_chip:
        if selected_port and esptool_ok:
            check_chip(doctor, python, args.controller, selected_port)
        else:
            doctor.result('WARN', 'Chip/flash identity', 'Probe skipped: resolve the selected-port/tool failure above first. The board was not accessed.')
    else:
        doctor.result('WARN', 'Chip/flash identity', 'Not measured. After USB-only connection, rerun with --port YOUR_ACTUAL_PORT --probe-chip before upload.')
    if args.server:
        check_health(doctor, args.server)
    else:
        doctor.result('WARN', 'Backend network', 'Not checked. Start the server and rerun with --server http://THE_COMPUTER_LAN_IPV4:8080. A PC health check does not prove the board can connect.')


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', choices=('esp32_s3', 'esp32'), default='esp32_s3')
    parser.add_argument('--port', help='Actual board serial port, for example COM5')
    parser.add_argument('--probe-chip', action='store_true', help='Read chip/flash identity on --port; may reset the board, never writes flash')
    parser.add_argument('--server', help='Backend origin, for example http://192.168.1.23:8080; request /health only')
    args = parser.parse_args(argv)
    if args.probe_chip and not args.port:
        parser.error('--probe-chip requires --port; no board is selected automatically')
    try:
        doctor = Doctor(root)
        checks(doctor, args)
        doctor.write(f'Checks finished: {doctor.failures} failure(s), {doctor.warnings} warning(s). Log: .tools/doctor.log')
        doctor.write('PASS applies only to the named software/read-only checks. Wiring, power, microphone, speaker and live AI still need the step-by-step call guide.')
        return 1 if doctor.failures else 0
    except KeyboardInterrupt:
        print('\nDoctor stopped; no upload or private-file changes were performed.')
        return 130
    except OSError:
        print('Doctor could not read project files or write .tools/doctor.log. Check folder permissions and rerun.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
