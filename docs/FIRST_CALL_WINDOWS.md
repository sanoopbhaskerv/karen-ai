# First wiring call: Windows + S3-N16R8

Use this guide together on the call. The student reads the printed labels and makes one connection at a time; the adult checks each stage before power is connected. **Begin with the laptop and a USB-only board. Add the microphone/button after upload and WiFi work.** The amplifier can wait until it is available.

The supported carrier is the previously photographed **HW678 / Sixspan S3-N16R8**, with USB-C sockets marked **COM** and **USB**. A similar module name does not prove the carrier layout. If his board's labels differ, stop and identify it before wiring. GPIO numbers below are printed signal labels, not positions counted along a header.

Firmware builds have been tested on the project owner's Mac. Native Windows launchers, computer-only setup and server health passed on a Windows runner. This student's laptop, board-tool installation/build, connected S3 and physical audio must still pass the checks below before calling the complete system ready.

## 1. Put everything on the table

- Windows laptop, charger, internet, a known USB **data** cable, and the S3 board.
- INMP441 microphone with soldered headers, short jumper wires, and a momentary button. An adult checks soldering and identifies button contacts with continuity mode while unpowered; four-leg buttons have internally joined pairs.
- For the later speaker stage: **MAX98357A I2S** amplifier, a passive speaker marked **4 Ω or higher**, suitable speaker wires, and a verified amplifier supply. A PAM8403 cannot substitute for this digital amplifier.
- A trusted 2.4 GHz WiFi network or hotspot that permits connected devices to reach each other. Keep the laptop connected and awake. The laptop runs the AI server throughout use.

Unplug USB and every external supply before moving wires. Use only low-voltage USB supplies. The adult handles soldering and amplifier power. Do not force the wide S3 board into a breadboard that shorts its rows; female jumper wires can connect directly to fitted headers. Breadboard power rails may be split: do not assume their full length is connected.

## 2. Get the current `main` files and set up the laptop

1. Sign into GitHub with the account that has access to [the private repository](https://github.com/sanoopbhaskerv/karen-ai/tree/main). Select **main → Code → Download ZIP**, then **Extract All** to a normal writable folder such as `Documents\karen-ai`. The owner can send the current main ZIP if access is unavailable. Do not send tokens or passwords on the call.
2. Open the folder containing `app.py`, `bootstrap-windows.cmd`, `scripts`, and `firmware`. Click File Explorer's address bar, type `powershell`, press Enter.
3. Existing Python **3.15** can be used directly; no downgrade is needed. For the version check below use `py -3.15 --version` when 3.15 is installed. If Python is not installed, install Python **3.14** from [Python's Windows downloads](https://www.python.org/downloads/windows/), including the launcher/PATH option. Reopen PowerShell. A working Python 3.12–3.15 is also supported. Do not copy a Mac `.venv` or `.tools` folder onto Windows.
4. Run one command at a time:

```powershell
Test-Path .\app.py
py -3.14 --version
.\bootstrap-windows.cmd --controller esp32_s3 --firmware --compile
```

**Go:** `True`, a supported Python version, and finally `SETUP COMPLETE`; the example build reports `Controller: esp32_s3` and succeeds. An existing supported Python installation can be found by the launcher even if the specific `py -3.14` command is unavailable. Setup creates the Python environment, downloads verified Arduino CLI/ESP32/audio tools and esptool, and compiles example firmware. Allow at least **8 GB free disk space** and time for several GB of downloads. Progress messages show that long steps are still running. This command does not upload firmware.

Setup preserves existing `.env`, `.env.local`, `config.h`, and saved memory. `--controller` does not rewrite an existing settings file; we explicitly select S3 in every board command below. On failure, read the last message and `.tools\bootstrap.log`, fix it, and rerun the same command. Do not continue past a failed build.

```powershell
.\doctor-windows.cmd --controller esp32_s3
```

Read every `PASS`, `WARN`, and `FAIL`. Fix `FAIL` before proceeding. Warnings about unconfigured WiFi/key, a stopped server, and unrequested chip checks are expected at this early stage. A successful computer preflight alone does not prove the board works.

## 3. Connect the bare board and measure its chip/flash

1. Leave the microphone, button, amplifier, and speaker disconnected.
2. Connect the board's USB-C socket labelled **COM** to the laptop. Use only this USB connection for power now.
3. Run:

```powershell
.\.venv\Scripts\python.exe scripts\board.py ports
```

Find the new port, for example `COM5`. Unplug/replug and list again if several ports appear. Windows **Device Manager → Ports (COM & LPT)** can help. The board name may be unknown even when its port works. If no port appears, first try another data cable/USB port; identify the USB-UART bridge before installing its manufacturer's driver. Do not guess CP210x versus CH34x from the S3 module name.

Replace `COM5` below with the actual port and keep using this PowerShell as **Window B — board**:

```powershell
$karenPort = 'COM5'
.\doctor-windows.cmd --controller esp32_s3 --port $karenPort --probe-chip
```

**Go:** the read-only probe identifies **ESP32-S3** and **16 MB flash**. Probing may reset the board, but does not erase or upload firmware. If either measurement differs, stop and tell the owner. This probe does not measure PSRAM; the firmware reports that after boot.

If connection times out, close every Serial Monitor. With only USB attached, hold **BOOT**, tap **RESET/EN**, release BOOT, and retry. Tap RESET afterward to boot normally. BOOT is for recovery; it is not the question button. Do not erase flash as a troubleshooting shortcut.

## 4. Get laptop chat and local networking working

1. The adult supplies the existing Gemini key privately. Open `.env` in Notepad, fill `GEMINI_API_KEY` if blank, and use `KAREN_CONTROLLER=esp32_s3`, `DEMO_MODE=0`, `PORT=8080`. Keep existing secrets and saved facts. Never display the key or put it in board firmware. Save as `.env`, not `.env.txt`. Existing `.env.local` and PowerShell environment values can override `.env`; investigate warnings instead of deleting them.
2. Open another PowerShell in the project folder as **Window A — server**:

```powershell
.\start-windows.cmd
```

3. Keep Window A open. In Chrome/Edge, open **http://localhost:8080**. Send `മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?` and confirm a real Malayalam answer. Click **Record a question**, allow the laptop microphone, speak during five seconds, and confirm a spoken reply. An apology or provider error is a failed test even if audio plays. Use [README troubleshooting](../README.md#16-if-something-goes-wrong) if needed.
4. In Window B, run `ipconfig`. Find **IPv4 Address under the active WiFi adapter**, for example `192.168.1.50`. Do not use Default Gateway, a VPN/virtual adapter, or `localhost` as the board's server address.
5. If Windows asks about firewall access, allow the Python server on this trusted **Private** network with adult help. Keep the firewall enabled. From a second device on the same WiFi, open `http://192.168.1.50:8080/health`, substituting the actual laptop address. This checks inbound reachability. The hotspot-providing phone itself may not be able to perform that test; use another client where possible.

Also check the address locally in Window B, using the actual IP:

```powershell
.\doctor-windows.cmd --controller esp32_s3 --server http://192.168.1.50:8080
```

**Go:** real laptop text/voice work and `/health` is reachable. A local doctor request cannot prove another device can get through the firewall. If the remote test fails, check the active network/IP, private-network firewall permission, and hotspot client isolation before changing firmware. A present key or a health response alone does not prove live AI inference.

## 5. Set board WiFi and upload with no external wires

In Window B:

```powershell
notepad firmware\karen_ai\config.h
```

Replace the three example values, retaining the quotes:

```cpp
#define WIFI_SSID "YOUR_2_4_GHZ_HOTSPOT"
#define WIFI_PASSWORD "YOUR_HOTSPOT_PASSWORD"
#define SERVER_ORIGIN "http://192.168.1.50:8080"
```

Use the real 2.4 GHz network/password and current laptop IP. Keep `http://`, port `:8080`, and no trailing `/`. For this local session keep `STATUS_LED=-1`, `RECORD_SECONDS=5`, `MIC_SHIFT=16`; keep the root-certificate block. Do not add classic ESP32 pin overrides. If old overrides already exist, ask the owner to remove them so the S3 defaults apply. The Gemini key belongs only in `.env`.

Save and close Notepad. Read the configuration warnings again, then upload:

```powershell
.\doctor-windows.cmd --controller esp32_s3 --port $karenPort --probe-chip
.\.venv\Scripts\python.exe scripts\firmware.py --controller esp32_s3 --upload --port $karenPort
.\.venv\Scripts\python.exe scripts\board.py monitor --port $karenPort --log
```

Upload replaces the board's firmware; do this only on the intended project board. A first LittleFS mount may initialize this application's filesystem. The upload compiles the private WiFi configuration, then flashes the explicit port. Keep the board still and connected until it finishes. Close the monitor with **Ctrl+C** before another upload/probe.

Once the monitor opens at **115200 baud**, tap RESET/EN if startup lines were missed. **Go:** `[BOOT]` shows `Controller: esp32_s3`, flash **16777216** bytes, PSRAM **8388608** bytes, microphone **4/5/6**, amplifier **16/17/18**, button **7**; then `[WIFI] Connected` and `[READY]`. If PSRAM is zero/wrong, boot repeats, or WiFi fails, stop here. `[READY]` by itself does not prove WiFi/server/audio success. Keep the monitor open for the next tests.

## 6. Power off, then wire the microphone and button

Unplug USB. Leave the amplifier disconnected. Read the actual microphone labels; do not copy a photo's left-to-right order. Connect each row, then have the adult check it:

| INMP441 printed label | S3 printed label |
|---|---|
| VDD | **3V3** |
| GND | GND |
| SCK / BCLK | **4** |
| WS / LRCLK | **5** |
| SD | **6** |
| L/R | **GND** |

Connect one verified button contact to **GPIO7**, the other to **GND**; the selected two contacts must be disconnected when released and connected only when pressed. The firmware supplies the input pull-up, so no 5 V or extra power wire goes to the button. If using a four-leg button, do not assume two arbitrarily chosen legs are the switch contacts.

**Never connect INMP441 VDD to 5 V.** Grounded L/R selects the left audio channel used by Karen. The [TDK microphone datasheet](https://product.tdk.com/system/files/dam/doc/product/sw_piezo/mic/mems-mic/data_sheet/inmp441.pdf) specifies the supply and channel selection. Keep wires short, the microphone hole clear, and the mic away from the eventual speaker.

Reconnect USB and open the same monitor command if needed. Keep Window A running. Press and release the question button **once**. Wait for `[MIC] Recording. Speak now.`, ask one short Malayalam question during the five seconds, and wait for completion. Expect `[MIC] Complete` with `samples=80000/80000`, changing nonzero signal measurements, then `[HTTP] Result: ok`. A zero/very-low-signal or clipping warning needs investigation. Match the request ID with Window A. `spoken-error` means the backend failed even when it generated an apology MP3. The firmware produces digital playback even without an amplifier, so `[PLAY] Decoder finished` cannot prove audible output.

Refresh **http://localhost:8080** on the laptop after the turn. The shared conversation shows the recognized question under **YOU** and the generated answer under **KAREN**. Check that it understood what he actually said; this makes the microphone test useful even without an amplifier.

**Go:** the server successfully recognizes the spoken question and generates the response; no repeated resets or recording failures. No amplifier means no sound from the board yet. If a request fails, inspect the existing request/error before pressing again; a turn can take over two minutes during network recovery. Do not repeatedly press while waiting.

## 7. Add the amplifier and speaker when ready

Unplug USB **and** amplifier power. The adult checks the exact MAX98357A breakout and power instructions first. A **separate regulated 5 V supply rated at least 1 A** is a practical starting choice for the amplifier alone; confirm its polarity and actual breakout limits. Keep the S3 USB powered. Join grounds, but **do not join that external 5 V rail to the USB-powered S3's 5 V/VIN rail**. Do not draw amplifier power from S3's 3V3 pin or assume a clone's USB/VIN rail has enough current.

| MAX98357A printed label | Connection |
|---|---|
| VIN | Verified amplifier 5 V supply positive |
| GND | Supply negative **and S3 GND** |
| BCLK | S3 **GPIO16** |
| LRC / WS | S3 **GPIO17** |
| DIN | S3 **GPIO18** |
| SD / EN, GAIN | Follow this breakout's instructions; confirm amplifier enabled, start with its default gain |
| SPK+ / OUT+ | One speaker wire |
| SPK− / OUT− | Other speaker wire |

Both speaker terminals are amplifier outputs: **neither goes to GND**. A 4 Ω / 10 W marking describes the speaker's rating; it does not make this amplifier deliver 10 W. [Analog Devices](https://www.analog.com/en/products/max98357a.html) specifies the digital amplifier, and [Adafruit's breakout guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts) explains power and bridge-connected speaker outputs. Other breakouts can use different SD/GAIN resistors; if its instructions are unknown, finish the microphone stage and postpone this wiring.

After the adult checks the connections, power up and try one complete question at the firmware's low playback gain. **Go:** an understandable Malayalam reply from the speaker, no heat, crackling, brownout/reboot or loose connections. Power down to investigate any problem before trying again. Finish with **ten consecutive turns**, then repeat on the intended exhibition network/power source. See [the exhibition checklist](EXHIBITION.md).

## Keep the useful debug information

| File/window | What it tells the owner |
|---|---|
| `.tools\bootstrap.log` | Timestamped installation/build steps and failures |
| `.tools\doctor.log` | Readiness checks, requested chip/flash and health results |
| `.tools\serial.log` | Timestamped board output when monitor runs with `--log` |
| Window A | Server/provider errors and request IDs |

For help, report the **stage number, last error, request ID, and actual COM port**. Logs are kept locally; review them before sharing because they can contain machine/network details. Do not share `.env`, `.env.local`, `config.h`, WiFi passwords, or API keys. Setup does not silently validate the AI key or upload firmware; the live chat and explicit upload above are separate checks.

The [Espressif S3 module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) documents N16R8 memory and reserved PSRAM pins. It does not establish the power circuitry or pin positions of a Sixspan carrier. This guide uses the repository's checked [S3 adapter](../firmware/karen_ai/controllers/esp32_s3.h) and the [full hardware notes](HARDWARE.md).
