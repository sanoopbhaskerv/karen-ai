"""Shared, dependency-free Arduino toolchain paths and pinned versions."""
import os
import json
import platform

CORE = 'esp32:esp32'
CORE_VERSION = '3.3.12'
AUDIO = 'ESP8266Audio'
AUDIO_VERSION = '2.4.1'
INDEX_URL = 'https://espressif.github.io/arduino-esp32/package_esp32_index.json'
LOCAL_MARKER = '.tools/arduino/.karen-isolated'


class ToolchainError(ValueError):
    pass


def isolation_identity():
    return {'schema': 1, 'system': platform.system(), 'machine': platform.machine().lower()}


def arduino_environment(root, environment=None):
    env = dict(os.environ if environment is None else environment)
    if (root / LOCAL_MARKER).is_file():
        try:
            state = json.loads((root / LOCAL_MARKER).read_text(encoding='utf-8'))
        except (ValueError, OSError):
            raise ToolchainError('Project-local Arduino metadata is invalid. Keep your private files; ask the owner to move ONLY .tools/arduino aside, then rerun board setup.') from None
        if state != isolation_identity():
            raise ToolchainError('Project-local Arduino tools belong to a different computer architecture. They were kept. Ask the owner to move ONLY .tools/arduino aside and rerun board setup on this computer.')
        base = root / '.tools/arduino'
        env.update(ARDUINO_DIRECTORIES_DATA=str(base / 'data'),
                   ARDUINO_DIRECTORIES_DOWNLOADS=str(base / 'downloads'),
                   ARDUINO_DIRECTORIES_USER=str(base / 'user'))
    return env
