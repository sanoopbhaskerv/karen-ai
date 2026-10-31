import io
import json
from types import SimpleNamespace

import pytest

from scripts import doctor, firmware


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / 'Karen Windows project with spaces'
    (root / 'firmware/karen_ai').mkdir(parents=True)
    python = doctor.venv_python(root)
    python.parent.mkdir(parents=True)
    python.write_text('test interpreter')
    (root / '.env').write_text('KAREN_CONTROLLER=esp32_s3\nGEMINI_API_KEY=private-api-value\n')
    (root / 'firmware/karen_ai/config.h').write_text(
        '#define WIFI_SSID "private-network"\n#define WIFI_PASSWORD "private\\"password"\n'
        '#define SERVER_ORIGIN "http://192.168.1.23:8080"\n')
    monkeypatch.setattr(firmware, 'find_cli', lambda *_: 'C:/Arduino folder/arduino-cli.exe')
    monkeypatch.delenv('KAREN_CONTROLLER', raising=False)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    return root


def fake_tools(monkeypatch, *, flash='Chip type: ESP32-S3 (revision v0.2)\nDetected flash size: 16MB\n', ports=None, esptool=True):
    calls = []
    def run(command, **kwargs):
        calls.append((command, kwargs))
        if 'core' in command:
            output = json.dumps({'platforms': [{'id': doctor.CORE, 'installed_version': doctor.CORE_VERSION}]})
        elif 'lib' in command:
            output = json.dumps({'installed_libraries': [{'library': {'name': doctor.AUDIO, 'version': doctor.AUDIO_VERSION}}]})
        elif 'board' in command:
            output = json.dumps({'detected_ports': ports if ports is not None else [{'port': {'address': 'COM5', 'protocol': 'serial'}}]})
        elif 'esptool' in command:
            output = flash
        elif command[-1] == doctor.ESPTOOL_CHECK:
            return SimpleNamespace(returncode=0 if esptool else 1, stdout='5.1.0' if esptool else 'PackageNotFoundError: esptool')
        else:
            output = ''
        return SimpleNamespace(returncode=0, stdout=output)
    monkeypatch.setattr(doctor.subprocess, 'run', run)
    return calls


def test_default_checks_do_not_probe_upload_contact_ai_or_edit_settings(project, monkeypatch, capsys):
    paths = [project / '.env', project / 'firmware/karen_ai/config.h']
    originals = [x.read_bytes() for x in paths]
    calls = fake_tools(monkeypatch)
    monkeypatch.setattr(doctor.urllib.request, 'urlopen', lambda *_a, **_k: pytest.fail('No implicit network call'))
    assert doctor.main([], project) == 0
    output = capsys.readouterr().out
    assert '[PASS] Arduino toolchain' in output
    assert '[WARN] Chip/flash identity: Not measured' in output
    assert '[WARN] Backend network: Not checked' in output
    assert all('esptool' not in command and 'upload' not in command and 'erase-flash' not in command for command, _ in calls)
    assert [x.read_bytes() for x in paths] == originals
    assert (project / '.tools/doctor.log').is_file()


def test_probe_requires_an_explicit_port(project, monkeypatch):
    monkeypatch.setattr(doctor.subprocess, 'run', lambda *_a, **_k: pytest.fail('Must not choose a board'))
    with pytest.raises(SystemExit) as result:
        doctor.main(['--probe-chip'], project)
    assert result.value.code == 2


@pytest.mark.parametrize('chip, expected', [
    ('Chip type: ESP32-S3 (revision v0.2)\nDetected flash size: 16MB', True),
    ('Chip type: ESP32 (revision v3.0)\nDetected flash size: 16MB', False),
    ('Chip type: ESP32-S2\nDetected flash size: 16MB', False),
    ('Chip type: ESP32-S3\nDetected flash size: 8MB', False),
    ('Chip type: ESP32-S3\n', False),
])
def test_probe_rejects_wrong_chip_flash_and_ambiguous_results(project, monkeypatch, chip, expected):
    calls = fake_tools(monkeypatch, flash=chip)
    assert doctor.main(['--port', 'COM5', '--probe-chip'], project) == (0 if expected else 1)
    probe = [command for command, _ in calls if 'esptool' in command]
    assert probe == [[str(doctor.venv_python(project)), '-m', 'esptool', '--port', 'COM5', 'flash-id']]


def test_unknown_selected_port_fails(project, monkeypatch):
    calls = fake_tools(monkeypatch)
    assert doctor.main(['--port', 'COM999', '--probe-chip'], project) == 1
    assert all('esptool' not in command for command, _ in calls)


def test_windows_com_port_comparison_is_case_insensitive(project, monkeypatch):
    calls = fake_tools(monkeypatch)
    assert doctor.main(['--port', 'com5', '--probe-chip'], project) == 0
    assert any(command[-3:] == ['--port', 'COM5', 'flash-id'] for command, _ in calls)


@pytest.mark.parametrize('origin', [
    'http://localhost:8080', 'http://127.0.0.1:8080', 'http://127.0.0.2:8080',
    'http://0.0.0.0:8080', 'http://[::1]:8080', 'http://[::]:8080',
    'http://192.168.1.23:8080/', 'http://192.168.1.23:8080/path', 'invalid-origin',
])
def test_firmware_origin_warnings_do_not_claim_settings_ready(project, monkeypatch, capsys, origin):
    fake_tools(monkeypatch)
    path = project / 'firmware/karen_ai/config.h'
    path.write_text(path.read_text().replace('http://192.168.1.23:8080', origin))
    assert doctor.main([], project) == 0
    output = capsys.readouterr().out
    assert '[WARN] Firmware settings: SERVER_ORIGIN' in output
    assert '[PASS] Firmware settings' not in output


@pytest.mark.parametrize('origin', ['http://192.168.1.50:8080', 'http://192.168.1.100:8080'])
def test_legitimate_lan_ips_are_not_treated_as_placeholders(project, monkeypatch, capsys, origin):
    fake_tools(monkeypatch)
    path = project / 'firmware/karen_ai/config.h'
    path.write_text(path.read_text().replace('http://192.168.1.23:8080', origin))
    assert doctor.main([], project) == 0
    assert '[PASS] Firmware settings' in capsys.readouterr().out


def test_missing_esptool_warns_without_probe_and_blocks_requested_probe(project, monkeypatch, capsys):
    calls = fake_tools(monkeypatch, esptool=False)
    assert doctor.main([], project) == 0
    assert '[WARN] Chip probe tool' in capsys.readouterr().out
    assert doctor.main(['--port', 'COM5', '--probe-chip'], project) == 1
    assert '[FAIL] Chip probe tool' in capsys.readouterr().out
    assert all('esptool' not in command for command, _ in calls)


def test_tool_and_config_secrets_are_redacted_from_log_and_console(project, monkeypatch, capsys):
    doc = doctor.Doctor(project)
    secret_output = 'private-api-value private-network private\\"password private"password https://user:pass@example.com\n#define WIFI_PASSWORD "other-value"'
    monkeypatch.setattr(doctor.subprocess, 'run', lambda *_a, **_k: SimpleNamespace(returncode=1, stdout=secret_output))
    doc.run(['tool'])
    doc.write(secret_output)
    output = capsys.readouterr().out + doc.log.read_text()
    for value in ('private-api-value', 'private-network', 'private\\"password', 'private"password', 'other-value', 'user:pass'):
        assert value not in output


def test_missing_project_environment_is_a_clear_failure(tmp_path, capsys):
    assert doctor.main([], tmp_path) == 1
    assert '[FAIL] Project Python' in capsys.readouterr().out


@pytest.mark.parametrize('origin', [
    'http://user:secret@192.168.1.1:8080', 'http://host/?key=secret', 'file:///tmp/secrets',
    'http://host/path', 'http://host:invalid', 'http://host/#secret',
])
def test_health_rejects_credentials_and_non_origin_urls_without_contacting_them(project, monkeypatch, origin):
    monkeypatch.setattr(doctor.urllib.request, 'urlopen', lambda *_a, **_k: pytest.fail('Invalid URL must not be fetched'))
    doc = doctor.Doctor(project)
    doctor.check_health(doc, origin)
    assert doc.failures == 1
    assert 'secret' not in doc.log.read_text()


def test_health_only_requests_health_and_never_logs_response_secrets(project, monkeypatch, capsys):
    class Response(io.BytesIO):
        status = 200
    seen = []
    def fetch(request, **kwargs):
        seen.append(request.full_url)
        return Response(json.dumps({'status': 'ok', 'mode': 'live', 'configured': True,
                                   'gemini': {'status': 'ready', 'secret': 'untrusted-server-secret'}}).encode())
    monkeypatch.setattr(doctor.urllib.request, 'urlopen', fetch)
    doc = doctor.Doctor(project)
    doctor.check_health(doc, 'http://192.168.1.23:8080/')
    assert seen == ['http://192.168.1.23:8080/health']
    assert doc.failures == 0
    assert 'untrusted-server-secret' not in doc.log.read_text() + capsys.readouterr().out
