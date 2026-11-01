# Karen AI — Mac instructions in English

Use **Terminal** on your Mac. The Windows PowerShell commands in the main
guide do not work unchanged in Terminal.

## 1. Open the project folder

For this Mac, run:

```bash
cd /Users/sanoopbhaskerv/workspace/karen-ai
```

If your project is elsewhere, type `cd ` (including the space), drag the
project folder from Finder into Terminal, then press Enter. Check the folder:

```bash
ls app.py scripts/board.py
```

Both filenames should appear. Run the remaining commands from this folder.
Copy commands without the surrounding Markdown fences or Terminal prompt.

## 2. Fix the monitor command

The command `.\.venv\Scripts\python.exe` describes a
Windows executable path. Mac uses `.venv/bin/python`. In zsh, unquoted
backslashes escape characters, which is why the error loses the slashes and
shows something like `..venvScriptspython.exe`.

First check the Mac environment:

```bash
.venv/bin/python --version
```

If this prints a Python version and board tools are already installed,
continue below. If the file is missing or Arduino CLI cannot start, use
Step 3, then return here.

Connect the board with a USB **data** cable. For the photographed HW678 /
Sixspan S3-N16R8 board, use the USB-C connector labelled **COM**. List ports:

```bash
.venv/bin/python scripts/board.py ports
```

Find the board's port beginning with `/dev/cu.`. It may look like
`/dev/cu.usbserial-0001`, `/dev/cu.SLAB_USBtoUART` or `/dev/cu.usbmodem101`.
These are examples; use the exact port printed on your Mac. If unsure,
compare the list with the board unplugged and plugged in.

Set the variable below, **replacing the example port** with your board's port:

```bash
karenPort='/dev/cu.usbserial-0001'
```

There must be **no spaces around `=`**. Then start the monitor:

```bash
.venv/bin/python scripts/board.py monitor --port "$karenPort" --log
```

This opens Serial Monitor at **115200 baud** and appends timestamped,
redacted output to `.tools/serial.log`. It watches the board; it does not
start the Karen server. If no boot messages appear, briefly press the
board's **RST** button while the monitor is open.

Press **Control+C** to stop monitoring and release the port. Close the
monitor before uploading firmware or probing the chip. Set `karenPort`
again when opening a new Terminal window, and recheck it after reconnecting
the board if the port changes.

## 3. Install missing Mac tools

Skip this step if your environment and board tools already work.

```bash
bash bootstrap-mac.command --firmware --controller esp32_s3
```

Use `--controller esp32` instead for the original classic ESP32. The launcher
finds a supported Python 3.12–3.15 installation, creates/reuses `.venv` and
prepares the Python packages and Arduino tools. If Python is missing, follow
the install link printed by the launcher, reopen Terminal and retry.

Keep internet connected and wait for **SETUP COMPLETE**. Board tools need
at least 8 GB free disk space. Existing `.env`, `.env.local`, saved memory
and `firmware/karen_ai/config.h` are preserved. Setup does not upload
firmware or validate the API key. Do not copy a Windows `.venv` onto a Mac;
see [bootstrap recovery](BOOTSTRAP.md#if-setup-stops) if setup reports a
foreign or broken environment.

After setup, return to Step 2. You do not need to activate `.venv` when
using its Python path directly.

## 4. Start the local Karen server when needed

If using the backend on this Mac, keep the project's existing private
settings. For a first setup, finish the key/settings stage in the
[English guide](../README.md#5-create-the-computers-settings-file), editing
the file locally on Mac with:

```bash
open -e .env
```

Start the server in **Terminal A**:

```bash
bash start-mac.command
```

Keep it open and visit [Karen on this Mac](http://localhost:8080) in your
browser (use your configured port if different). Test a typed question
before testing voice. If a Karen server is already running, use that server.

Open **Terminal B**, run the `cd` command from Step 1, then use Step 2 to
monitor the board. A board configured for a hosted backend uses that
backend; starting a local server does not change its saved server address.

## 5. Upload firmware only when you intend to update the board

Monitoring does not require a new upload. For a firmware update, first
follow [hardware commissioning](HARDWARE.md#step-by-step-commissioning)
to confirm the chip/flash, wiring and private WiFi/server configuration.
For a local backend, the board needs the Mac's reachable LAN address in
`SERVER_ORIGIN`; the board cannot use the Mac's `localhost`.

Stop Serial Monitor with Control+C. In the same Terminal where you set the
actual `karenPort`, compile the private configuration, then upload only if
compilation succeeds:

```bash
.venv/bin/python scripts/firmware.py --controller esp32_s3 --use-config
```

```bash
.venv/bin/python scripts/firmware.py --controller esp32_s3 --upload --port "$karenPort"
```

Use `--controller esp32` in both commands for the original classic board.
After a successful upload, reopen the monitor using Step 2. Check the
controller, measured memory, WiFi connection and Ready messages.

## Common Mac errors

| Error or symptom | What to do |
|---|---|
| `zsh: command not found: ..venvScriptspython.exe` | Use `.venv/bin/python` and `scripts/board.py`, with forward slashes. |
| `no such file or directory: .venv/bin/python` | Check Step 1, then run Mac setup in Step 3 if the environment is missing. |
| `can't open file ... scripts/board.py` | Open the project folder from Step 1. |
| Arduino CLI missing | Run Step 3 to install/verify board tools. |
| No board port appears | Check the data cable and COM connector; identify the USB-UART bridge before installing its manufacturer's driver. |
| Monitor requires `--port` or cannot open port | Set `karenPort` to the actual `/dev/cu...` port in this Terminal and quote `"$karenPort"`. Close other monitors using it. |
| No reply from Karen | Keep the configured backend reachable; inspect the serial log and server log. The monitor command alone does not run the backend. |

Windows uses `$karenPort = 'COM5'`; Mac uses `karenPort='/dev/cu...'`.
After assigning the correct Mac port, `"$karenPort"` reads its value.
