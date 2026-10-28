import json
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
