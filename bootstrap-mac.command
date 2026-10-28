#!/bin/bash
set -u
cd -- "$(dirname -- "$0")" || exit 1
karen_python=''
for candidate in "$PWD/.venv/bin/python" python3.14 python3.13 python3.12 python3; do
  if "$candidate" -c 'import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,15)))' >/dev/null 2>&1; then
    karen_python="$candidate"
    break
  fi
done
if [ -z "$karen_python" ]; then
  echo 'Python 3.12-3.14 was not found. Install Python 3.14 from:'
  echo 'https://www.python.org/downloads/macos/'
  echo 'Then reopen this file. See README.md / READMEMALAYALAM.md.'
  karen_exit=1
else
  "$karen_python" "$PWD/scripts/bootstrap.py" "$@"
  karen_exit=$?
fi
if [ -t 0 ] && [ "$#" -eq 0 ]; then
  read -r -p 'Press Enter to close this setup window...' _karen_reply
fi
exit "$karen_exit"
