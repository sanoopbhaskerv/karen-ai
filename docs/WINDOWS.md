# Windows setup — HW678 / ESP32-S3 N16R8

The user's photos show an HW678 PCB with a Sixspan module marked **S3-N16R8**, two USB-C connectors labelled **COM** and **USB** on the back, and an onboard RGB LED. This guide selects the ESP32-S3 adapter. The original classic ESP32 remains supported.

The S3 build uses the advertised **16 MB flash / 8 MB octal PSRAM** configuration. A label is not a flash measurement: confirm with esptool and the boot log before commissioning. Cross-compilation passed on the Mac; these Windows commands and physical upload still need execution on the nephew's PC.

## 1. Get the updated source and start the backend

Use the updated project folder. While PR #1 is open, the updates are on `fix/gemini-diagnostics-and-commissioning`; `main` remains the original import. The repository is private, so use an authorized checkout or a source copy. Local `.env`, saved memory and WiFi configuration are deliberately absent from Git.

Install Python 3.12 from the official Python distribution. In PowerShell, open the project folder (replace the example path):

```powershell
Set-Location C:\Projects\karen-ai
if (-not (Test-Path .venv)) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set the Gemini key locally, keep `DEMO_MODE=0`, and select the controller:

```dotenv
GEMINI_MODEL=gemini-3.5-flash-lite
KAREN_CONTROLLER=esp32_s3
PORT=8080
```

Do not overwrite an existing `.env`, `.env.local`, `data/memory.txt` or `config.h`. Settings precedence is shell → `.env.local` → `.env`. The controller variable selects a **firmware build**, not the Gemini provider. Switching it requires rebuilding and uploading; restarting Flask cannot change firmware already on the board.

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_gemini.py
.\.venv\Scripts\python.exe app.py
```

Open **http://localhost:8080** in Chrome or Edge. Test Malayalam text first, then microphone permission and the five-second recorder. Python errors print in the same PowerShell window. Keep it open. Use another PowerShell window in the project folder for the remaining steps. Calling the virtual environment's Python directly avoids needing PowerShell activation scripts or execution-policy changes.

## 2. Install Arduino CLI, the core and audio library

Download the Windows Arduino CLI ZIP from the [official installation page](https://arduino.github.io/arduino-cli/latest/installation/). Extract `arduino-cli.exe` to `.tools\arduino-cli.exe` inside this project (create `.tools` if needed). This folder is ignored by Git. Alternatively, install the CLI on PATH or set `ARDUINO_CLI` to its full executable path.

```powershell
$karenArduinoCli = Join-Path (Get-Location) '.tools\arduino-cli.exe'
& $karenArduinoCli version
& $karenArduinoCli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
& $karenArduinoCli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
& $karenArduinoCli lib install 'ESP8266Audio@2.4.1'
```

The core download is large and includes support for other ESP32 variants. Wait for installation to complete.

## 3. Select and compile either controller

For the photographed board, use the `.env` value above or set a PowerShell variable:

```powershell
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py
```

For the original classic board:

```powershell
$env:KAREN_CONTROLLER = 'esp32'
.\.venv\Scripts\python.exe scripts\firmware.py
```

A shell variable overrides the `.env` value. `Remove-Item Env:KAREN_CONTROLLER` returns to file settings. `--controller esp32_s3` overrides both for one command. Unknown names fail rather than silently selecting another board.

Ordinary builds use **example credentials** in a temporary sketch and do not upload. The helper prints the selected controller/target, compiles, then removes temporary files. Existing private `config.h` is preserved. `--use-config` compiles the private configuration without uploading. Compiler output is scrubbed of WiFi credential definitions and known secret values.

## 4. Find the COM port and confirm the hardware

1. Connect only the controller, using a USB-C **data** cable in the connector labelled **COM** on the back. The other connector is native USB/USB-OTG. This profile uses the UART/COM connector for both upload and Serial Monitor; native USB CDC on boot is disabled.
2. Open Windows Device Manager → Ports (COM & LPT), or run:

   ```powershell
   & $karenArduinoCli board list
   ```

3. Record the actual port, for example **COM5**. It is not necessarily COM5 on this computer. If absent, first check the data cable. Identify the USB-UART bridge through its marking or Device Manager Hardware IDs before installing its manufacturer's driver; do not assume it uses the classic board's CP2102.
4. Verify flash using Espressif esptool, replacing COM5 with the actual port:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install esptool
   .\.venv\Scripts\python.exe -m esptool --port COM5 flash-id
   ```

   Expect an ESP32-S3 and 16 MB flash for this profile. If it reports something different, stop and reconcile the board configuration. Close Serial Monitor before flashing. If automatic bootloader entry fails, hold onboard **BOOT**, briefly press **RST**, start the operation and release BOOT when connecting. BOOT is not the external question button.

## 5. Configure private WiFi and the backend address

```powershell
if (-not (Test-Path firmware\karen_ai\config.h)) {
    Copy-Item firmware\karen_ai\config.example.h firmware\karen_ai\config.h
}
notepad firmware\karen_ai\config.h
```

Set `WIFI_SSID` and `WIFI_PASSWORD` for a 2.4 GHz network. Set `SERVER_ORIGIN` to the reachable backend computer, for example `http://192.168.1.50:8080`, without a trailing slash. Use `ipconfig` on the backend PC to find the active adapter's IPv4 address. The board cannot use the PC's `localhost`.

If the backend is on the Mac, use the Mac's LAN IP instead. The PC/Mac and board must share a reachable LAN. If Windows Firewall prompts, permit the Python server on the private exhibition network; it may need inbound TCP 8080 access. Do not disable the firewall globally.

Leave `STATUS_LED=-1`; the visible RGB LED cannot be controlled by plain GPIO on/off calls. Pin defaults are in the two controller adapters. If migrating an old classic `config.h` to S3, preserve WiFi/root-CA settings and remove the old `MIC_*`, `AMP_*` and `BUTTON_PIN` definitions so the adapter supplies the S3 defaults. Unsafe old pins are rejected at compile time.

The Gemini key belongs only on the backend, never in this firmware configuration.

## 6. Compile private configuration and upload deliberately

```powershell
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py --use-config
# Replace COM5 with the port actually listed for this board:
.\.venv\Scripts\python.exe scripts\firmware.py --upload --port COM5
& $karenArduinoCli monitor --port COM5 --config baudrate=115200
```

`--upload` always compiles the private configuration first. It requires an explicit port, refuses untouched example WiFi placeholders, and stops if compilation fails. No port is chosen automatically. The CLI checks the selected chip family during upload. Keep the controller disconnected from the amplifier during the first upload.

The boot log prints `Controller: esp32_s3`, measured flash/PSRAM bytes, selected pins, WiFi status and Ready. Expected advertised capacities are 16,777,216 flash bytes and 8,388,608 PSRAM bytes. Actual values, USB operation and successful boot are still unverified until tested on the device. The current no-OTA layout uses 2 MB app / roughly 2 MB filesystem; additional flash is intentionally unused.

## 7. Wire this S3 board

Power down before wiring. All numbers refer to GPIO labels, not header positions. These labels are visible in the supplied close-up photos.

| Signal | S3 GPIO / connection |
|---|---|
| INMP441 VDD, GND | 3V3, GND |
| INMP441 BCLK/SCK, WS, SD | **4, 5, 6** respectively |
| INMP441 L/R | GND (left channel) |
| MAX98357A BCLK, LRC/WS, DIN | **16, 17, 18** respectively |
| MAX98357A VIN, GND | Suitable 5 V source, common GND |
| External momentary question button | **7 to GND**; internal pull-up |
| Speaker | MAX98357A SPK+ / SPK− only |

Do not copy the classic board's 26/25/33/27/14/22/32 wiring to this S3. Do not use GPIO35–37: octal PSRAM occupies them on this module family. This adapter also avoids USB 19/20, flash signals, boot straps, serial-console pins and possible RGB pins. Confirm microphone/amplifier breakout labels and speaker marking separately; these photos only show the controller.

Complete the [hardware commissioning checklist](HARDWARE.md), including low-gain playback, power stability, network failure recovery and ten physical turns. The MAX98357A design is unchanged; no PAM8403 or analog-output conversion is involved.

## Arduino IDE alternative

The Python helper is the path that reads `KAREN_CONTROLLER`. Arduino IDE instead selects the adapter from Tools → Board:

| Setting | Photographed S3 board | Original classic board |
|---|---|---|
| Board | ESP32S3 Dev Module | ESP32 Dev Module |
| Flash | 16 MB, once verified | 4 MB, once verified |
| PSRAM | OPI PSRAM | Disabled / as actual module |
| Flash mode | QIO 80 MHz | Core default |
| Partition | No OTA (2 MB APP / 2 MB filesystem) | Same |
| USB CDC on boot | Disabled; use COM/UART connector | Not applicable |
| Upload speed | 115200 initially | 115200 initially |

Open `firmware/karen_ai/karen_ai.ino`, configure `config.h` and select the actual COM port. Never switch just the pin map while leaving the wrong chip target selected.

## References

- [Arduino CLI installation](https://arduino.github.io/arduino-cli/latest/installation/)
- [Espressif Arduino installation](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
- [ESP32-S3 DevKitC interface reference](https://docs.espressif.com/projects/esp-idf/en/v4.4.8/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html) — a reference design, not proof the HW678 clone has identical circuitry
- [Espressif S3 module datasheet / memory pin restrictions](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
