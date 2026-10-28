#!/bin/sh
set -eu
# Compatibility wrapper; Windows calls scripts/firmware.py directly.
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python_bin=${KAREN_PYTHON:-python3}
if [ -x "$root/.venv/bin/python" ] && [ -z "${KAREN_PYTHON:-}" ]; then
  python_bin="$root/.venv/bin/python"
fi
exec "$python_bin" "$root/scripts/firmware.py" "$@"
