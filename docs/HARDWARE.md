# Hardware and firmware commissioning

No hardware is connected to the Mac during this work. The user is testing software first. This document verifies the **firmware pin mapping against the intended digital interfaces**; actual board/module silkscreen, solder joints, flash size, electrical connections and audio quality remain unverified.

## Intended parts and outstanding confirmations

| Part | Current information | Must confirm physically |
|---|---|---|
| ESP32 | Classic 38-pin CP2102/Micro-USB board; GPIO labels 14, 22, 25, 26, 27, 32, 33, 2 reported visible | Module marking is classic ESP32, USB data connection, actual flash size |
| Microphone | Shop label INMP441 | Actual breakout VDD/GND/SCK/WS/SD/L-R labels, soldered headers |
| Amplifier | **MAX98357A I2S**, still being sourced | Correct module, VIN/enable/gain instructions and soldered headers |
| Speaker | Latest box reportedly **4 ohms / 10 watts** | Driver's own impedance/power marking, two suitable speaker wires |
| Button | Momentary push button | Which legs are already connected internally; select legs shorted only while pressed |
| Power | USB power bank / Micro-USB data cable / Mac adapter | Stable 5 V, suitable current and safe supply arrangement |

PAM8403 is not selected; do not wire it to the digital I2S outputs. A MAX98357A is rated up to about 3.2 W into 4 ohms at 5 V, not 10 W. A genuinely 4-ohm/10-watt passive speaker is a compatible load at lower delivered power; the box is not proof of the driver specification. Start at the firmware's low output gain (0.35). Do not connect a speaker directly to GPIO.

## Wiring checked against firmware

Unplug power before assembly. Use the printed GPIO number, **not** a header position. Breakout pin order varies; read labels on the actual board. INMP441 silicon supply is 1.8–3.3 V; use 3.3 V here. Grounded L/R selects the left I2S channel, matching the sketch.

| Module pin | Connection |
|---|---|
| INMP441 VDD | ESP32 3V3 |
| INMP441 GND | Common GND |
| INMP441 SCK / BCLK | GPIO26 |
| INMP441 WS / LRCLK | GPIO25 |
| INMP441 SD | GPIO33 |
| INMP441 L/R | GND (left channel) |
| MAX98357A VIN | Suitable 5 V source, per breakout documentation |
| MAX98357A GND | Common GND |
| MAX98357A BCLK | GPIO27 |
| MAX98357A LRC / LRCLK | GPIO14 |
| MAX98357A DIN | GPIO22 |
| MAX98357A SD / EN | Enabled according to the actual breakout's instructions |
| Speaker terminals | MAX98357A SPK+ and SPK− only |
| Button | GPIO32 to GND; firmware enables internal pull-up |
| Optional status LED | GPIO2 only if a suitable onboard LED is confirmed |

Both speaker terminals are amplifier outputs: connect neither to ground. Do not supply the microphone or ESP32 signal pins with 5 V. Use short I2S wires. Keep the microphone opening unobstructed and away from the speaker. Confirm headers are soldered; loose pins pushed through unsoldered holes are unreliable.

For first board-only tests, power through Mac USB. Add amplifier power only after confirming the actual board/breakout power arrangement. Do not assume a clone board's VIN rail can supply the amplifier or tie external 5 V to USB power blindly. An independently powered amplifier needs common ground with ESP32, but no connection from its external 5 V rail to ESP32's 5 V rail during USB-powered tests. Later choose one suitable source or a verified isolated arrangement. Investigate brownouts before increasing volume.

## Reproducible compile on a Mac

Install Arduino CLI, then the tested core/library versions:

```bash
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli lib install 'ESP8266Audio@2.4.1'
./scripts/compile_firmware.sh
```

This Mac has an ignored CLI copy at `.tools/arduino-cli`, which the script finds automatically. The script compiles a temporary sketch with **example credentials**; it preserves any real `config.h` and never uploads. FQBN: `esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M`. This targets the described classic ESP32; selecting 4 MB for a build does not measure physical flash. Use Arduino-ESP32 3.x (ESP-IDF 5 standard I2S driver), not 2.x's legacy driver.

In Arduino IDE select ESP32 Dev Module, 4 MB flash **only once verified**, and No OTA (2 MB APP / roughly 2 MB filesystem). The firmware requires >=1.5 MB filesystem for WAV, multipart and MP3 files. Check the compiler size report before upload. LittleFS uses the filesystem partition; its first mount may format it.

## Step-by-step commissioning when hardware arrives

1. **Board only:** connect the Micro-USB data cable to the Mac. `arduino-cli board list` should show `/dev/cu.usbserial-*` or `/dev/cu.SLAB_USBtoUART`. If absent, check cable/data adapter and CP2102 driver before wiring peripherals. Use the Silicon Labs official driver only if needed.
2. **Identify flash:** use Espressif esptool (`python -m pip install esptool`, then `python -m esptool --port /dev/cu.<actual-port> flash-id`). Hold BOOT during connect if required. Record chip and detected flash capacity. Do not flash a 4 MB layout into a smaller device. Firmware also prints detected flash bytes at boot.
3. **Inspect parts:** read the microphone's actual pin labels and speaker-driver marking, check continuity/button legs, solder headers and speaker wires. Keep the amplifier disconnected until it is available and identified.
4. **Configure:** `test -f firmware/karen_ai/config.h || cp firmware/karen_ai/config.example.h firmware/karen_ai/config.h`. Edit only this ignored file: 2.4 GHz WiFi credentials and `SERVER_ORIGIN="http://<Mac-LAN-IP>:8080"`, no trailing slash. Keep `STATUS_LED=-1` unless GPIO2 LED is confirmed. No Gemini key belongs on the board.
5. **Compile/upload:** recheck board, flash and partition selections. Build and upload with Arduino IDE, or `arduino-cli compile --fqbn 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M' firmware/karen_ai` then `arduino-cli upload -p /dev/cu.<actual-port> --fqbn 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M' firmware/karen_ai`. Open Serial Monitor at 115200. Expect flash-size, WiFi and Ready messages.
6. **Button + microphone only:** wire the INMP441 and button from the table. Press once; speak during the five-second Recording message. Watch the request ID and backend logs. With no amplifier, capture/STT/server MP3 can be checked, but audible playback is still untested.
7. **Add MAX98357A + speaker:** power down, wire its digital pins and verified power source. Connect the speaker only to SPK+/SPK−. Power up at low gain and confirm one complete Malayalam response. Check supply stability and noise before adjusting gain.
8. **Tune input:** INMP441 uses 32-bit slots, converted to 16-bit with `MIC_SHIFT=16`. If too quiet, try 15 then 14; reduce gain if clipping. Check L/R=GND and soldering before software gain changes.
9. **Recovery:** disconnect WiFi/internet, check visible/serial failure, restore connectivity and press again only after inspecting the prior request ID. Check that late responses never create duplicate turns. Verify malformed WAV/JSON is never played as MP3.
10. **Endurance:** run ten consecutive physical turns. Check intelligibility, clipping, repeated I2S initialization, clean flash files, stable power and no resets. Repeat at the venue with the actual power bank/network.

## Local networking and HTTPS

A device cannot use the Mac's `localhost`. Both must join the same network; firewall/client isolation may block port 8080. Start Flask on the Mac, verify text chat, then test the Mac LAN URL from a phone before the device.

For cloud HTTPS, use the exact hostname and its valid trusted root CA PEM in `ROOT_CA`. Firmware synchronizes NTP before TLS, calls `setCACert`, and never `setInsecure`. Obtain the root through the certificate issuer/host documentation or trusted store; update it if the chain changes. Cloud TLS and NTP are not verified without the actual board and hostname.

The firmware sends an asynchronous multipart WAV request and polls `/requests/<id>`. Individual HTTP reads are 15 seconds (below HTTPClient's 16-bit limit), with a 160-second polling budget. A lost upload is retried at most once using the same ID. There are no automatic new conversation turns. MP3 responses require fixed `Content-Length`, `audio/mpeg` and <=512,000 bytes. The Flask response supplies these; preserve them at the proxy.

## Manufacturer references

- [TDK/InvenSense INMP441 datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [Analog Devices MAX98357A specifications](https://www.analog.com/en/products/max98357a.html)
- [Espressif DevKitC power guidance](https://docs.espressif.com/projects/esp-idf/en/v4.4/esp32/hw-reference/esp32/get-started-devkitc.html) — relevant guidance, not proof that this clone has the same circuitry
- [ESP-IDF standard I2S](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2s.html)
- [ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio)
