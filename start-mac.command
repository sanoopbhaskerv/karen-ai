#!/bin/bash
set -u
cd -- "$(dirname -- "$0")" || exit 1
if [ ! -x "$PWD/.venv/bin/python" ]; then
  echo 'Run bootstrap-mac.command first. See README.md / READMEMALAYALAM.md.'
  if [ -t 0 ]; then read -r -p 'Press Enter to close...' _karen_reply; fi
  exit 1
fi
echo 'Karen AI: keep this window open. Open http://localhost:8080 in your browser.'
echo 'Stop with Ctrl+C. Existing files and saved facts are kept.'
"$PWD/.venv/bin/python" "$PWD/app.py"
karen_exit=$?
if [ "$karen_exit" -ne 0 ] && [ -t 0 ]; then
  read -r -p 'Press Enter to close...' _karen_reply
fi
exit "$karen_exit"
