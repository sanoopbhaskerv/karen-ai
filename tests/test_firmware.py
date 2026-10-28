"""Build selection, private-config isolation and unsafe wiring regressions."""
from argparse import Namespace
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from scripts import firmware


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'Karen project with spaces'
    source = root / 'firmware' / 'karen_ai'
    shutil.copytree(firmware.ROOT / 'firmware' / 'karen_ai', source,
                    ignore=shutil.ignore_patterns('config.h'))
    (root / '.env').write_text('KAREN_CONTROLLER=esp32\n')
    return root


def args(**changes):
    return Namespace(**(dict(controller=None, use_config=False, upload=False, port=None) | changes))


def test_env_precedence_and_explicit_controller(project):
    (project / '.env.local').write_text('KAREN_CONTROLLER=esp32_s3\n')
    assert firmware.select_controller(firmware.settings_for(project, {})) == 'esp32_s3'
    settings = firmware.settings_for(project, {'KAREN_CONTROLLER': 'esp32'})
    assert firmware.select_controller(settings) == 'esp32'
    assert firmware.select_controller(settings, 'esp32_s3') == 'esp32_s3'
    assert firmware.select_controller({}) == 'esp32'


def test_unknown_controller_does_not_echo_the_supplied_value():
    with pytest.raises(ValueError) as exc:
        firmware.select_controller({'KAREN_CONTROLLER': 'accidentally-pasted-private-value'})
    assert 'accidentally-pasted-private-value' not in str(exc.value)


def test_default_compile_uses_examples_and_preserves_private_config(project, monkeypatch):
    private = project / 'firmware/karen_ai/config.h'
    private.write_text('private WiFi credentials must stay here')
    calls, snapshots = [], []
    monkeypatch.setattr(firmware, 'find_cli', lambda *_: r'C:\Program Files\Arduino CLI\arduino-cli.exe')
    def run(command, **kwargs):
        calls.append(command)
        assert not kwargs.get('shell')
        sketch = Path(command[-1])
        snapshots.append(sketch)
        assert 'YOUR_HOTSPOT_PASSWORD' in (sketch / 'config.h').read_text()
        assert (sketch / 'controllers/esp32_s3.h').is_file()
        return SimpleNamespace(returncode=0, stdout='compiled\n')
    monkeypatch.setattr(firmware.subprocess, 'run', run)
    assert firmware.build(args(), project, {}) == 0
    assert len(calls) == 1 and calls[0][1] == 'compile'
    assert calls[0][0] == r'C:\Program Files\Arduino CLI\arduino-cli.exe'
    assert private.read_text() == 'private WiFi credentials must stay here'
    assert not snapshots[0].exists()


def test_s3_upload_uses_private_config_and_exact_same_target(project, monkeypatch, capsys):
    private = project / 'firmware/karen_ai/config.h'
    content = '#define WIFI_SSID "private-network"\n#define WIFI_PASSWORD "private-password"\n'
    private.write_text(content)
    commands = []
    monkeypatch.setattr(firmware, 'find_cli', lambda *_: 'arduino-cli.exe')
    def run(command, **kwargs):
        commands.append(command)
        assert (Path(command[-1]) / 'config.h').read_text() == content
        return SimpleNamespace(returncode=0, stdout='private-password private-network\n')
    monkeypatch.setattr(firmware.subprocess, 'run', run)
    assert firmware.build(args(upload=True, port='COM7'), project, {'KAREN_CONTROLLER': 'esp32_s3'}) == 0
    assert [c[1] for c in commands] == ['compile', 'upload']
    assert commands[0][commands[0].index('--fqbn') + 1] == firmware.PROFILES['esp32_s3']
    assert commands[1][commands[1].index('--fqbn') + 1] == firmware.PROFILES['esp32_s3']
    assert commands[1][commands[1].index('--port') + 1] == 'COM7'
    assert private.read_text() == content
    output = capsys.readouterr().out
    assert 'private-password' not in output and 'private-network' not in output


@pytest.mark.parametrize('configuration', ['no_port', 'no_config', 'placeholders'])
def test_unsafe_upload_requests_stop_before_running_any_tool(project, monkeypatch, configuration):
    if configuration == 'placeholders':
        shutil.copyfile(project / 'firmware/karen_ai/config.example.h', project / 'firmware/karen_ai/config.h')
    monkeypatch.setattr(firmware.subprocess, 'run', lambda *_a, **_k: pytest.fail('Must not invoke a tool'))
    with pytest.raises(ValueError):
        firmware.build(args(upload=True, port=None if configuration == 'no_port' else 'COM5'), project, {})


def test_failed_compile_never_uploads(project, monkeypatch):
    (project / 'firmware/karen_ai/config.h').write_text('#define WIFI_SSID "network"\n#define WIFI_PASSWORD "password"\n')
    calls = []
    monkeypatch.setattr(firmware, 'find_cli', lambda *_: 'arduino-cli')
    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=7, stdout='compile failed\n')
    monkeypatch.setattr(firmware.subprocess, 'run', run)
    assert firmware.build(args(upload=True, port='COM5'), project, {}) == 7
    assert len(calls) == 1


def test_compiler_source_diagnostics_are_redacted():
    config = '#define WIFI_PASSWORD "my-password"\n#define WIFI_SSID "my-network"\n'
    output = '7 | #define WIFI_PASSWORD "my-password"\nexpansion my-password my-network api-secret\n'
    sanitized = firmware.redact_output(output, config, {'GEMINI_API_KEY': 'api-secret'})
    assert all(secret not in sanitized for secret in ('my-password', 'my-network', 'api-secret'))


@pytest.mark.parametrize('target, override, accepted', [
    ('CONFIG_IDF_TARGET_ESP32', '', True),
    ('CONFIG_IDF_TARGET_ESP32S3', '', True),
    ('CONFIG_IDF_TARGET_ESP32S3', '#define MIC_DATA 35\n', False),  # octal PSRAM
    ('CONFIG_IDF_TARGET_ESP32S3', '#define AMP_DATA 19\n', False),  # USB
    ('CONFIG_IDF_TARGET_ESP32S3', '#define MIC_DATA 4\n', False),   # overlaps BCLK
    ('CONFIG_IDF_TARGET_ESP32S3', '#define MIC_BCLK 26\n#define MIC_WS 25\n#define MIC_DATA 33\n', False),
    ('CONFIG_IDF_TARGET_ESP32', '#define AMP_DATA 6\n', False),    # flash bus
    (None, '', False),  # unsupported chip
])
def test_controller_compile_guards(tmp_path, target, override, accepted):
    compiler = shutil.which('c++')
    if not compiler:
        pytest.skip('Host C++ compiler unavailable; real ESP32 builds are separate')
    # Minimal GPIO macro shim: these tests exercise adapter reservation/collision
    # policy; the real cross-compiles additionally exercise the Espressif SDK.
    driver = tmp_path / 'driver'; driver.mkdir()
    (driver / 'gpio.h').write_text('#define GPIO_IS_VALID_GPIO(x) ((x)>=0 && (x)<=48)\n'
                                  '#define GPIO_IS_VALID_OUTPUT_GPIO(x) GPIO_IS_VALID_GPIO(x)\n')
    source = tmp_path / 'guard.cpp'
    source.write_text(override + '#include "controller.h"\n')
    command = [compiler, '-std=c++17', '-fsyntax-only', '-I', str(tmp_path),
               '-I', str(firmware.ROOT / 'firmware/karen_ai')]
    if target:
        command.append('-D' + target + '=1')
    result = subprocess.run(command + [str(source)], capture_output=True, text=True)
    assert (result.returncode == 0) == accepted, result.stderr
