# Hardware and firmware commissioning

The firmware supports the original classic ESP32 and the nephew's photographed HW678 board, marked **Sixspan S3-N16R8**. The clearer IMG_1446/1447/1448 photos confirm the S3 signal labels used below, two USB-C ports labelled **COM** and **USB**, and an onboard RGB LED. They show fitted header pins/solder joints; electrical continuity and solder quality are not tested. Neither board is connected to this Mac, so measured flash/PSRAM size, upload and audio operation remain pending. For the nephew's PC, follow [Windows setup](WINDOWS.md).

## Intended parts and outstanding confirmations

| Part | Current information | Must confirm physically |
|---|---|---|
| Original ESP32 | Classic 38-pin CP2102/Micro-USB board; original GPIO map | Exact module, USB data connection and measured flash size |
| New ESP32-S3 | HW678 / Sixspan S3-N16R8; relevant GPIO and COM/USB labels visible in photos | Measured 16 MB flash / 8 MB PSRAM, USB-UART bridge identity, upload and boot |
| Microphone | Shop label INMP441 | Actual breakout VDD/GND/SCK/WS/SD/L-R labels, soldered headers |
| Amplifier | **MAX98357A I2S**, still being sourced | Correct module, VIN/enable/gain instructions and soldered headers |
| Speaker | Latest box reportedly **4 ohms / 10 watts** | Driver's own impedance/power marking, two suitable speaker wires |
| Button | Momentary push button | Which legs are already connected internally; select legs shorted only while pressed |
| Power | USB power bank / Micro-USB data cable / Mac adapter | Stable 5 V, suitable current and safe supply arrangement |

PAM8403 is not selected; do not wire it to the digital I2S outputs. A MAX98357A is rated up to about 3.2 W into 4 ohms at 5 V, not 10 W. A genuinely 4-ohm/10-watt passive speaker is a compatible load at lower delivered power; the box is not proof of the driver specification. Start at the firmware's low output gain (0.35). Do not connect a speaker directly to GPIO.

## Wiring checked against firmware

Unplug power before assembly. Use the printed GPIO number, **not** a header position. Breakout pin order varies; read labels on the actual board. INMP441 silicon supply is 1.8–3.3 V; use 3.3 V here. Grounded L/R selects the left I2S channel, matching the sketch.

| Module pin | Classic `esp32` | HW678 `esp32_s3` |
|---|---|---|
| INMP441 VDD | 3V3 | 3V3 |
| INMP441 GND | GND | GND |
| INMP441 SCK / BCLK | GPIO26 | **GPIO4** |
| INMP441 WS / LRCLK | GPIO25 | **GPIO5** |
| INMP441 SD | GPIO33 | **GPIO6** |
| INMP441 L/R | GND (left channel) | GND (left channel) |
| MAX98357A VIN | Suitable 5 V, per breakout | Suitable 5 V, per breakout |
| MAX98357A GND | Common GND | Common GND |
| MAX98357A BCLK | GPIO27 | **GPIO16** |
| MAX98357A LRC / WS | GPIO14 | **GPIO17** |
| MAX98357A DIN | GPIO22 | **GPIO18** |
| MAX98357A SD / EN | Per breakout instructions | Per breakout instructions |
| Speaker | SPK+ / SPK− only | SPK+ / SPK− only |
| External question button | GPIO32 to GND | **GPIO7 to GND** |
| Status LED | Disabled; optional confirmed GPIO2 LED | Disabled; onboard RGB needs a separate driver |

Do not reuse the classic pin map on the S3. The S3 adapter avoids flash/PSRAM pins (including GPIO35–37), native USB 19/20, serial-console pins, boot straps and possible onboard RGB pins. Compile-time checks reject reserved pins, overlapping signals and unsupported chips. Old classic pin overrides in `config.h` are preserved on disk but rejected if unsafe for the S3; remove those overrides to use the new adapter defaults. Never use onboard BOOT as the question button.

Both speaker terminals are amplifier outputs: connect neither to ground. Do not supply the microphone or ESP32 signal pins with 5 V. Use short I2S wires. Keep the microphone opening unobstructed and away from the speaker. Confirm headers are soldered; loose pins pushed through unsoldered holes are unreliable.

For first board-only tests, power through the computer's USB (the S3's COM connector). Add amplifier power only after confirming the actual board/breakout power arrangement. Do not assume a clone board's VIN rail can supply the amplifier or tie external 5 V to USB power blindly. An independently powered amplifier needs common ground with ESP32, but no connection from its external 5 V rail to ESP32's 5 V rail during USB-powered tests. Later choose one suitable source or a verified isolated arrangement. Investigate brownouts before increasing volume.

## Reproducible compile on a Mac

Install Arduino CLI, then the tested core/library versions:

```bash
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli lib install 'ESP8266Audio@2.4.1'
./scripts/compile_firmware.sh
# Build the photographed S3 instead:
KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py
```

This Mac has an ignored CLI copy at `.tools/arduino-cli`, which the script finds automatically. `KAREN_CONTROLLER` selects `esp32` (default) or `esp32_s3`, with shell → `.env.local` → `.env` precedence; `--controller` overrides them. Normal builds compile a temporary sketch with **example credentials**, preserve private `config.h` and never upload. `--use-config` compiles private credentials; `--upload --port <actual-port>` compiles and then uploads. See `scripts/firmware.py` for both exact FQBNs. Classic uses a 4 MB target; S3 uses advertised 16 MB flash/QIO and octal PSRAM, with UART upload at 115200. Target selection is not a physical flash measurement. Use Arduino-ESP32 3.x (ESP-IDF 5 standard I2S driver), not 2.x's legacy driver.

In Arduino IDE select **ESP32 Dev Module / 4 MB** for the classic board, or **ESP32S3 Dev Module / 16 MB / OPI PSRAM / USB CDC disabled** for this S3, once measured capacities are confirmed. The adapter follows the chip target automatically in IDE; IDE does not read `KAREN_CONTROLLER`. Both use No OTA (2 MB APP / roughly 2 MB filesystem); the S3's additional flash is currently unused. The firmware requires >=1.5 MB filesystem for WAV, multipart and MP3 files. LittleFS uses that partition; its first mount may format it.

## Step-by-step commissioning

1. **Board only:** classic uses Micro-USB; photographed S3 uses USB-C labelled **COM**. `arduino-cli board list` should show a serial port (`/dev/cu.*` on Mac, COM number on Windows). If absent, check the data cable and identify the actual USB-UART bridge before installing its manufacturer's driver. Do not assume the S3 shares the classic CP2102.
2. **Identify flash:** use Espressif esptool (`python -m pip install esptool`, then `python -m esptool --port <actual-port> flash-id`). Hold BOOT during connect if required. Record chip and detected flash capacity. Select `esp32` or `esp32_s3` to match; never use a larger flash target than the measured hardware. Firmware also prints measured flash and PSRAM bytes at boot.
3. **Inspect parts:** read the microphone's actual pin labels and speaker-driver marking, check continuity/button legs, solder headers and speaker wires. Keep the amplifier disconnected until it is available and identified.
4. **Configure:** copy `firmware/karen_ai/config.example.h` to `config.h` only if absent. Edit this ignored file: 2.4 GHz WiFi credentials and `SERVER_ORIGIN="http://<backend-LAN-IP>:8080"`, no trailing slash. Keep `STATUS_LED=-1`; S3's RGB LED is not a plain GPIO LED. No Gemini key belongs on the board. Use the selected adapter's pin map instead of old classic overrides on S3.
5. **Compile/upload:** set `KAREN_CONTROLLER` and recheck the measured board/flash. On Mac, use `.venv/bin/python scripts/firmware.py --use-config`, then `.venv/bin/python scripts/firmware.py --upload --port /dev/cu.<actual-port>`. Windows commands are in `WINDOWS.md`. The helper stops on compile failure and requires an explicit port/private configuration. Open Serial Monitor at 115200. Expect controller name, flash/PSRAM sizes, pin map, WiFi and Ready messages.
6. **Button + microphone only:** wire the INMP441 and button from the table. Press once; speak during the five-second Recording message. Watch the request ID and backend logs. With no amplifier, capture/STT/server MP3 can be checked, but audible playback is still untested.
7. **Add MAX98357A + speaker:** power down, wire its digital pins and verified power source. Connect the speaker only to SPK+/SPK−. Power up at low gain and confirm one complete Malayalam response. Check supply stability and noise before adjusting gain.
8. **Tune input:** INMP441 uses 32-bit slots, converted to 16-bit with `MIC_SHIFT=16`. If too quiet, try 15 then 14; reduce gain if clipping. Check L/R=GND and soldering before software gain changes.
9. **Recovery:** disconnect WiFi/internet, check visible/serial failure, restore connectivity and press again only after inspecting the prior request ID. Check that late responses never create duplicate turns. Verify malformed WAV/JSON is never played as MP3.
10. **Endurance:** run ten consecutive physical turns. Check intelligibility, clipping, repeated I2S initialization, clean flash files, stable power and no resets. Repeat at the venue with the actual power bank/network.

## Local networking and HTTPS

A device cannot use the backend computer's `localhost`. Both must share a reachable network; firewall/client isolation may block port 8080. Start Flask on the Mac or Windows PC, verify text chat, then test that computer's LAN URL from a phone before the device.

For cloud HTTPS, use the exact hostname and its valid trusted root CA PEM in `ROOT_CA`. Firmware synchronizes NTP before TLS, calls `setCACert`, and never `setInsecure`. Obtain the root through the certificate issuer/host documentation or trusted store; update it if the chain changes. Cloud TLS and NTP are not verified without the actual board and hostname.

The firmware sends an asynchronous multipart WAV request and polls `/requests/<id>`. Individual HTTP reads are 15 seconds (below HTTPClient's 16-bit limit), with a 160-second polling budget. A lost upload is retried at most once using the same ID. There are no automatic new conversation turns. MP3 responses require fixed `Content-Length`, `audio/mpeg` and <=512,000 bytes. The Flask response supplies these; preserve them at the proxy.

## Manufacturer references

- [TDK/InvenSense INMP441 datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [Analog Devices MAX98357A specifications](https://www.analog.com/en/products/max98357a.html)
- [Espressif DevKitC power guidance](https://docs.espressif.com/projects/esp-idf/en/v4.4/esp32/hw-reference/esp32/get-started-devkitc.html) — relevant guidance, not proof that this clone has the same circuitry
- [ESP-IDF standard I2S](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2s.html)
- [ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio)
- [Espressif S3 module memory/pin restrictions](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
