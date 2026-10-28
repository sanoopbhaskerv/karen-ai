"""List ports or open Serial Monitor using Karen's selected Arduino toolchain."""
import argparse
import subprocess
from pathlib import Path

if __package__:
    from .firmware import find_cli, settings_for
    from .toolchain import arduino_environment
else:
    from firmware import find_cli, settings_for
    from toolchain import arduino_environment

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('ports', 'monitor'))
    parser.add_argument('--port', help='Actual serial port, for example COM5')
    args = parser.parse_args(argv)
    if args.action == 'monitor' and not args.port:
        parser.error('monitor requires --port; use ports to find the actual number')
    try:
        cli = find_cli(settings_for(root), root)
        command = [cli, 'board', 'list'] if args.action == 'ports' else [
            cli, 'monitor', '--port', args.port, '--config', 'baudrate=115200']
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
