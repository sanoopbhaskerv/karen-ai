# Hardware and firmware commissioning

## Reference bill of materials

| Part | Specification / purpose |
|---|---|
| ESP32 DevKit | Classic ESP32-WROOM, 4 MB flash; no PSRAM required |
| INMP441 | I2S digital microphone, 3.3 V |
| MAX98357A breakout | I2S DAC/amplifier; power from suitable 5 V supply |
| Speaker | 8 ohm / 3 W, connected to amplifier outputs |
| Momentary button | GPIO32 to ground |
| USB power bank | Stable 5 V source with adequate current for board and amplifier |
| Wiring | Short jumper wires, common ground; suitable breadboard |

This build deliberately chooses a known digital microphone because the source report only names a legacy sound sensor. A module exposing only a digital threshold signal reports loudness, not a usable speech waveform. An analog audio microphone would require an ADC sampling implementation and its exact voltage range; it is not supported by this sketch.

## Wiring

Unplug power while wiring. Labels refer to ESP32 GPIO numbers, not physical header positions.

| Module pin | ESP32 / connection |
|---|---|
| INMP441 VDD | 3V3 (not 5 V) |
| INMP441 GND | GND |
| INMP441 SCK/BCLK | GPIO26 |
| INMP441 WS/LRCLK | GPIO25 |
| INMP441 SD | GPIO33 |
| INMP441 L/R | GND (left channel) |
| MAX98357A VIN | 5 V supply rail, subject to your breakout specification |
| MAX98357A GND | Common GND |
| MAX98357A BCLK | GPIO27 |
| MAX98357A LRC | GPIO14 |
| MAX98357A DIN | GPIO22 |
| MAX98357A SD/EN | Enabled per breakout documentation; many boards default enabled |
| Speaker + / − | Amplifier SPK+ / SPK− only |
| Button terminal 1 | GPIO32 |
| Button terminal 2 | GND |
| Status | Onboard GPIO2 LED where present |

Do not connect the speaker directly to an ESP32 GPIO. Neither speaker output should be tied to ground. Do not feed 5 V into an ESP32 signal pin. Use common ground; avoid powering the ESP32 simultaneously from conflicting 5 V supplies. Start with low speaker gain.

## Arduino setup

1. Install Arduino IDE and the **esp32 by Espressif Systems** board package, version 3.x (uses ESP-IDF 5.x).
2. Install **ESP8266Audio by Earle F. Philhower**, version 2.x (2.4.1 or newer). Do not combine the current audio library with Arduino-ESP32 2.x's legacy I2S driver.
3. Open `firmware/karen_ai/karen_ai.ino`.
4. Copy `config.example.h` to `config.h`. Set the 2.4 GHz hotspot credentials and the actual server origin without a trailing slash.
5. Select **ESP32 Dev Module**, your serial port, 4 MB flash, and a partition layout with at least 1.5 MB filesystem and enough app space. A typical "No OTA (2MB APP/2MB SPIFFS)" layout is appropriate; LittleFS uses that filesystem partition. If the binary will not fit, inspect the compiler report and select a compatible larger-flash board or layout.
6. Verify/compile, then upload. The first filesystem mount may format the app's filesystem. Open Serial Monitor at 115200 baud.
7. Press and release the button. Once the LED turns on / Serial says "Recording", speak for five seconds. Wait for upload, processing and playback. One interaction runs at a time.

## HTTPS trust

For local LAN testing, use `http://<computer-LAN-IP>:8080`. Both computer and ESP32 must be on the same network; client isolation/firewall rules can block access. A device cannot use your computer's `localhost` address.

For Replit/cloud, use `https://<exact-host>` and put the issuer's valid root CA PEM in `ROOT_CA` in `config.h`. Get the root through your hosting/certificate issuer documentation or a trusted certificate store. TLS needs a valid clock; firmware synchronizes NTP before the request. If a provider changes its certificate chain, update the CA. Do not work around failures with `setInsecure()`.

## Audio tuning and boundaries

The firmware captures 16 kHz, mono 16-bit PCM for five seconds (~160 KB). Multipart assembly and the reply also use LittleFS; allow at least 1.5 MB free. It removes the transient files after each turn. Frequent writes are acceptable for a demonstration; long-term continuous usage should use streaming buffers or suitable storage.

INMP441 input is converted from 32-bit slots with `MIC_SHIFT=16`. If speech is very quiet, try 15 then 14 and recheck for clipping. If audio clips, use 16 or 17. Keep the microphone away from the speaker. Output gain starts at 0.35. Listen before increasing it.

The firmware expects a known `Content-Length` and `audio/mpeg`, capped at 512,000 bytes. Flask supplies these. If a proxy strips the length or applies streaming transfer encoding, it must preserve a fixed-length audio response for this firmware.

There is no wake word, full-duplex listening, device heartbeat or display in this build. The button starts a fixed recording. A touchscreen sensor can replace the button only after adapting its signal logic and voltage safely.

The device HTTP read timeout is 60 seconds (within HTTPClient's 16-bit timeout limit). A slow cloud request may fail and require another button press. Watch the dashboard/server logs before retrying; automatic retries are deliberately avoided so they cannot silently duplicate AI turns.
