#!/bin/bash
set -u
cd -- "$(dirname -- "$0")" || exit 1
if [ "$#" -gt 1 ]; then
  echo 'Usage: monitor-mac.command [serial-port]'
  exit 2
fi
case "${1:-}" in
  -h|--help)
    echo 'Usage: monitor-mac.command [serial-port]'
    echo 'Open the ESP32 Serial Monitor at 115200 baud and save redacted logs to .tools/serial.log.'
    echo 'Without a port argument, list ports and ask which one to open. Ctrl+C closes the monitor.'
    exit 0
    ;;
esac
if [ ! -x "$PWD/.venv/bin/python" ]; then
  echo 'Run bootstrap-mac.command first to install the project environment and board tools.'
  if [ -t 0 ]; then read -r -p 'Press Enter to close...' _karen_reply; fi
  exit 1
fi
karen_port="${1:-}"
if [ -z "$karen_port" ]; then
  "$PWD/.venv/bin/python" "$PWD/scripts/board.py" ports || exit $?
  if [ ! -t 0 ]; then
    echo 'Pass the actual serial port as an argument.'
    exit 2
  fi
  read -r -p 'Paste the ESP32 serial port shown above: ' karen_port
fi
if [ -z "$karen_port" ]; then
  echo 'No serial port selected.'
  exit 2
fi
echo 'Keep this window open for live ESP32 logs. Ctrl+C closes it; close it before firmware upload.'
"$PWD/.venv/bin/python" -u "$PWD/scripts/board.py" monitor --port "$karen_port" --log
karen_exit=$?
if [ "$karen_exit" -ne 0 ] && [ "$karen_exit" -ne 130 ] && [ -t 0 ]; then
  read -r -p 'Press Enter to close...' _karen_reply
fi
exit "$karen_exit"
