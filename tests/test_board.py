import json
import io
import subprocess
from pathlib import Path

import pytest

from scripts import board, toolchain


@pytest.mark.parametrize('arguments, expected', [
    (['ports'], ['board', 'list']),
    (['monitor', '--port', 'COM7'], ['monitor', '--port', 'COM7', '--config', 'baudrate=115200']),
])
def test_serial_commands_find_project_tools_without_shell_variables(tmp_path, monkeypatch, arguments, expected):
    marker = tmp_path / toolchain.LOCAL_MARKER
    marker.parent.mkdir(parents=True); marker.write_text(json.dumps(toolchain.isolation_identity()))
    monkeypatch.setattr(board, 'find_cli', lambda *_: 'arduino-cli.exe')
    calls = []
    monkeypatch.setattr(board.subprocess, 'call', lambda command, **kwargs: calls.append((command, kwargs)) or 0)
    assert board.main(arguments, tmp_path) == 0
    assert calls[0][0] == ['arduino-cli.exe'] + expected
    assert calls[0][1]['env']['ARDUINO_DIRECTORIES_DATA'] == str(tmp_path / '.tools/arduino/data')
    assert 'upload' not in calls[0][0]


def test_monitor_requires_explicit_port(monkeypatch):
    monkeypatch.setattr(board.subprocess, 'call', lambda *_a, **_k: pytest.fail('Must not guess a port'))
    with pytest.raises(SystemExit) as exc:
        board.main(['monitor'])
    assert exc.value.code == 2


def test_logged_monitor_redacts_secrets_and_keeps_original_config(tmp_path, monkeypatch, capsys):
    config = tmp_path / 'firmware/karen_ai/config.h'
    config.parent.mkdir(parents=True)
    original = '#define WIFI_SSID "private-network"\n#define WIFI_PASSWORD "private-pass"\n'
    config.write_text(original)
    class Process:
        stdout = io.StringIO('private-network private-pass private-key\n[READY] waiting\n')
        def wait(self, **kwargs): return 0
        def poll(self): return 0
    calls = []
    monkeypatch.setattr(board, 'find_cli', lambda *_: 'arduino-cli.exe')
    monkeypatch.setattr(board, 'settings_for', lambda *_: {'GEMINI_API_KEY': 'private-key'})
    monkeypatch.setattr(board.subprocess, 'Popen', lambda command, **kwargs: calls.append((command, kwargs)) or Process())
    assert board.main(['monitor', '--port', 'COM8', '--log'], tmp_path) == 0
    log = (tmp_path / '.tools/serial.log').read_text()
    output = log + capsys.readouterr().out
    assert '[READY] waiting' in log and 'Serial session ended.' in log
    assert all(value not in output for value in ('private-network', 'private-pass', 'private-key'))
    assert config.read_text() == original
    assert calls[0][0][calls[0][0].index('--port') + 1] == 'COM8'
    assert not calls[0][1].get('shell')


def test_logged_monitor_releases_port_after_interruption(tmp_path, monkeypatch):
    class Output:
        def __iter__(self): raise KeyboardInterrupt
        def close(self): pass
    class Process:
        stdout = Output()
        terminated = False
        def poll(self): return None
        def terminate(self): self.terminated = True
        def wait(self, **kwargs): return 0
    process = Process()
    monkeypatch.setattr(board, 'find_cli', lambda *_: 'arduino-cli.exe')
    monkeypatch.setattr(board.subprocess, 'Popen', lambda *_a, **_k: process)
    assert board.main(['monitor', '--port', 'COM8', '--log'], tmp_path) == 130
    assert process.terminated


def test_logged_monitor_kills_unresponsive_child_on_exit(tmp_path, monkeypatch):
    class Output:
        def __iter__(self): raise KeyboardInterrupt
        def close(self): pass
    class Process:
        stdout = Output()
        killed = False
        def poll(self): return None
        def terminate(self): pass
        def kill(self): self.killed = True
        def wait(self, **kwargs):
            if not self.killed:
                raise subprocess.TimeoutExpired('monitor', 5)
            return 0
    process = Process()
    monkeypatch.setattr(board, 'find_cli', lambda *_: 'arduino-cli.exe')
    monkeypatch.setattr(board.subprocess, 'Popen', lambda *_a, **_k: process)
    assert board.main(['monitor', '--port', 'COM8', '--log'], tmp_path) == 130
    assert process.killed
