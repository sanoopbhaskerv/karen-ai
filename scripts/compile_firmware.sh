#!/bin/sh
set -eu
# Compile with placeholder credentials in an isolated sketch, preserving config.h.
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
compiler=${ARDUINO_CLI:-arduino-cli}
if ! command -v "$compiler" >/dev/null 2>&1 && [ -x "$root/.tools/arduino-cli" ]; then
  compiler="$root/.tools/arduino-cli"
fi
sketch_dir=$(mktemp -d "${TMPDIR:-/tmp}/karen-compile.XXXXXX")
trap 'rm -rf "$sketch_dir"' EXIT HUP INT TERM
mkdir "$sketch_dir/karen_ai"
cp "$root/firmware/karen_ai/karen_ai.ino" "$sketch_dir/karen_ai/"
cp "$root/firmware/karen_ai/config.example.h" "$sketch_dir/karen_ai/config.h"
"$compiler" compile --fqbn 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M' "$sketch_dir/karen_ai"
