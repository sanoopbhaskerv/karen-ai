"""Register a private client profile and write one-time credentials to a private file."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from multitenant import ClientRegistry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', required=True)
    parser.add_argument('--profile', required=True, help='Private profile JSON file')
    parser.add_argument('--credentials', required=True, help='New private output JSON file')
    args = parser.parse_args()
    # Reserve output first so an existing credential file cannot be overwritten.
    output = Path(args.credentials)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        profile = json.loads(Path(args.profile).read_text())
        result = ClientRegistry(args.registry).register(profile)
        with os.fdopen(descriptor, 'w') as handle:
            descriptor = None
            json.dump(result, handle, indent=2)
        print('Client registered. Credentials saved privately to ' + str(output))
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
            output.unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    main()
