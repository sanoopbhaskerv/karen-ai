# Validation record — 28 October 2026

## Verified on this Mac

- Original backend suite ran before changes: **18 passed**.
- Expanded backend suite: **36 passed**, including the original language/route/history/memory/WAV tests and regression coverage for retries, sanitized errors, request deduplication, concurrent duplicate requests, deadlines, responsive health/dashboard, reset/memory edits during inference, TTS/oversized-audio failure before history commit, and bounded result retention.
- Python source compilation, JavaScript syntax checks and Git whitespace checks passed.
- A separate isolated Chrome test saved a test fact through the memory editor, retrieved it via real Malayalam Gemini chat, reset the conversation, then restarted the temporary server and confirmed saved facts persisted with empty history. The real saved memory was never edited.
- Existing `.env` and `data/memory.txt` remain byte-for-byte unchanged (hashes compared before/after). The working model is selected through a new ignored `.env.local`; no key or saved memory was published.
- Existing key successfully listed models through `google-genai` with SDK retries disabled. The configured `gemini-3.8-flash` was listed, but inference returned 504 `DEADLINE_EXCEEDED` at a 30-second limit (~29 seconds) and again at a 60-second limit (~59 seconds). Another attempt returned 503 `UNAVAILABLE` / high demand. A longer timeout did not fix it.
- API-listed `gemini-3.5-flash-lite` returned a Malayalam answer about Sreehari with Karen's full instructions and existing saved facts in **1.2 seconds** using the same key. This proves a usable key/model combination; it does not establish Google's internal cause for 3.8 failures.
- Actual Flask `/test_chat`: creator question **200 / 1.42 seconds**; rain question **200 / 3.63 seconds**, both Malayalam. `/health` reported `gemini.status: ready` afterward.
- `python scripts/diagnose_gemini.py` successfully listed models and generated a Malayalam answer without altering saved memory/history.
- Actual multipart WAV → Google Malayalam STT → Gemini → gTTS MP3: **200 / ~4 seconds / `X-Karen-Result: ok`**. Output was 103,488 bytes; macOS `afinfo` recognized mono 24 kHz MP3, **12.936 seconds**.
- Chrome/Playwright at 390×844: actual Malayalam text, creator identity, recorder, downsampling/WAV upload, live STT/Gemini/gTTS and decoded MP3 playback all passed. The test deliberately lost the first accepted text POST response; the browser retried with the same request ID and recovered successfully. Audio decoded to 8.88–12.576 seconds across runs. No JavaScript runtime errors or horizontal overflow. Screenshot inspected at `/tmp/karen-audio/mobile-dashboard.png` (local temporary output, not a repository asset).

The speech input for software tests was synthesized Malayalam (`മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?`), converted to 16 kHz mono 16-bit PCM with macOS `afconvert` and fed to Chrome's fake microphone. These are **real provider requests**, but not a human-microphone/noise/physical-device test. MP3 decoding/playback was checked programmatically; listening quality still needs human acceptance.

Environment: the existing Mac Python 3.14.7 virtual environment; Flask 3.1.3, google-genai 2.33.0, SpeechRecognition 3.17.0, gTTS 2.5.4, pytest 9.2.0. Two upstream deprecation warnings occur under Python 3.14 (aifc compatibility package and typing internals). Tests pass.

## Firmware status

**Cross-compile passed** using `./scripts/compile_firmware.sh` on this Mac:

- Arduino CLI 1.5.2-rc.1, Espressif Arduino-ESP32 **3.3.12**, ESP8266Audio **2.4.1**.
- Target: `esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M` (classic ESP32 Dev Module, matching the reported chip family).
- Program: **1,201,296 bytes / 2,097,152 bytes (57%)**.
- Static RAM: **49,272 bytes / 327,680 bytes (15%)**, leaving 278,408 bytes before runtime allocations.
- Compiled the multipart upload, asynchronous polling, standard digital I2S microphone/MP3 playback and optional-LED code with example credentials. No analog-output substitution, flash upload or insecure TLS setting.
- A local ignored CLI copy is available at `.tools/arduino-cli`; the compile script finds it automatically. Core/library installations are in the normal Arduino data directories.

A cross-compile cannot measure board flash, runtime heap or prove physical operation. The 4 MB build selection remains a target assumption until the actual board is connected and queried.

## Pending physical / deployment acceptance

- No ESP32 or audio hardware is currently available to the Mac. Actual board/module markings, flash capacity, serial connection and upload are unverified.
- INMP441 breakout pinout, header soldering, button continuity and microphone gain/noise.
- MAX98357A still needs sourcing; verify the speaker driver's actual 4-ohm/10-watt marking and speaker wires.
- Human microphone capture and audible speaker quality, brownouts, power-bank behavior and ten-turn physical endurance.
- ESP32 WiFi, NTP, certificate validation and real network failure recovery.
- Cloud hosting, proxy behavior, persistent storage across redeploy and venue network.

The wiring table is checked against source and manufacturer interface requirements, not physically inspected. Follow `HARDWARE.md` step by step and complete `EXHIBITION.md` before calling the hardware exhibition-ready.
