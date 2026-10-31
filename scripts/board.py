"""List ports or open Serial Monitor using Karen's selected Arduino toolchain."""
import argparse
from datetime import datetime, timezone
import subprocess
from pathlib import Path

if __package__:
    from .firmware import find_cli, settings_for, redact_output
    from .toolchain import arduino_environment
else:
    from firmware import find_cli, settings_for, redact_output
    from toolchain import arduino_environment

ROOT = Path(__file__).resolve().parents[1]


def logged_monitor(command, root, settings):
    """Stream safe serial output to the console and an ignored, timestamped log."""
    config_path = root / 'firmware/karen_ai/config.h'
    config = config_path.read_text(encoding='utf-8') if config_path.is_file() else ''
    path = root / '.tools/serial.log'
    path.parent.mkdir(parents=True, exist_ok=True)
    print('Serial log: .tools/serial.log. Ctrl+C closes the monitor; close it before uploading.', flush=True)
    with path.open('a', encoding='utf-8') as handle:
        def emit(line):
            safe = redact_output(line, config, settings)
            stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
            handle.write(f'[{stamp}] {safe.rstrip()}\n')
            handle.flush()
            print(safe, end='' if safe.endswith('\n') else '\n', flush=True)
        emit('Serial session started at 115200 baud.')
        process = subprocess.Popen(command, cwd=root, env=arduino_environment(root),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace', bufsize=1)
        try:
            for line in process.stdout:
                emit(line)
            return process.wait()
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            process.stdout.close()
            emit('Serial session ended.')


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('ports', 'monitor'))
    parser.add_argument('--port', help='Actual serial port, for example COM5')
    parser.add_argument('--log', action='store_true', help='Save redacted timestamped monitor output to .tools/serial.log')
    args = parser.parse_args(argv)
    if args.action == 'monitor' and not args.port:
        parser.error('monitor requires --port; use ports to find the actual number')
    if args.log and args.action != 'monitor':
        parser.error('--log is available with monitor only')
    try:
        settings = settings_for(root)
        cli = find_cli(settings, root)
        command = [cli, 'board', 'list'] if args.action == 'ports' else [
            cli, 'monitor', '--port', args.port, '--config', 'baudrate=115200']
        if args.log:
            return logged_monitor(command, root, settings)
        return subprocess.call(command, cwd=root, env=arduino_environment(root))
    except KeyboardInterrupt:
        print('\nSerial operation stopped.')
        return 130
    except ValueError as exc:
        print(str(exc))
        return 1
    except OSError:
        print('Could not start Arduino CLI. Run bootstrap with --firmware, then retry.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
