# Validation record — latest check 31 October 2026

## Windows S3 first-call kit — 31 October 2026

- `main` was five commits behind remote main; the newest bootstrap branch was one further commit ahead. Main was fast-forwarded to include both histories. New work is on main at the owner's explicit request.
- Full local suite: **109 passed / 5 Windows-only tests skipped**, with the same two upstream Python 3.14 deprecation warnings. Added coverage for diagnostic decisions, exact chip/flash parsing, malformed/loopback firmware origins, actual-port selection, no implicit probe/AI/upload, health-response filtering, escaped WiFi secret redaction, persistent serial logs and monitor interruption/forced termination.
- Real Mac bootstrap with `--firmware --controller esp32_s3` installed esptool **5.6.0**, reused the existing matching Arduino packages, and passed `--check --firmware` and `pip check`. A second bootstrap preserved every existing `.env`, `.env.local`, `data/memory.txt` and `config.h` byte-for-byte, checked with before/after hashes.
- Both updated firmware example builds passed with Arduino-ESP32 **3.3.12** / ESP8266Audio **2.4.1**: S3 **1,191,479 program bytes / 47,364 static RAM bytes**; classic **1,205,960 program bytes / 49,272 static RAM bytes**. No board upload or private-config build.
- Actual doctor software/toolchain checks passed on the Mac. Chip identity and board network remain explicitly pending. Doctor `/health` was also exercised against a real temporary Flask server; no AI request or saved-memory edit occurred in that check.
- A fresh live Gemini diagnostic using the existing key and `gemini-3.5-flash-lite` succeeded with a Malayalam answer. This tests this Mac/key at this time, not the student's Windows credentials, browser microphone or controller audio.
- Python compilation, Git whitespace, local documentation links/fences and **34 matching English/Malayalam command/settings blocks** passed. The [first-call guide](FIRST_CALL_WINDOWS.md) gives exact Windows commands, staged S3 wiring, expected diagnostic output and recovery checks.
- [Native Windows run passed](https://github.com/sanoopbhaskerv/karen-ai/actions/runs/41178597065) on CPython **3.14.10**: **113 passed / 1 Mac-only test skipped**, including all five native launcher cases in a path with spaces. Real computer-only bootstrap, `--check`, and `start-windows.cmd` serving `/health` passed without a key or AI request. A further CI step verifies the official Windows Arduino CLI download/checksum/execution; its result is separate from this first run.
- No S3 is connected here: measured S3 flash/PSRAM, COM-driver operation, upload/boot, power, microphone and speaker acceptance still require the call. The existing ignored classic-board logs do not establish S3 readiness.

## Verified on this Mac — 28 October 2026

- Original backend suite ran before changes: **18 passed**.
- Before the bootstrap addition: **53 passed** (36 backend and 17 firmware build/adapter regressions), including the original language/route/history/memory/WAV tests and regression coverage for retries, sanitized errors, request deduplication, concurrent duplicate requests, deadlines, responsive health/dashboard, reset/memory edits during inference, TTS/oversized-audio failure before history commit, and bounded result retention.
- Python source compilation, JavaScript/shell syntax checks and Git whitespace checks passed. Firmware tests cover environment/argument precedence, Windows-style executable paths with spaces, default/private config isolation, failed-build upload prevention, missing-port/placeholder rejection, credential redaction, and compile-time rejection of reserved/overlapping/unsupported pins.
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

**Both cross-compiles passed** on this Mac with Arduino CLI 1.5.2-rc.1, Arduino-ESP32 **3.3.12**, ESP8266Audio **2.4.1**:

| Profile | Build command | Program / 2,097,152 bytes | Static RAM / 327,680 bytes |
|---|---|---|---|
| Classic `esp32` | `KAREN_CONTROLLER=esp32 .venv/bin/python scripts/firmware.py` | **1,201,536 bytes (57%)** | **49,272 bytes (15%)** |
| HW678 `esp32_s3` | `KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py` | **1,186,787 bytes (56%)** | **47,364 bytes (14%)** |

- Exact targets are in `scripts/firmware.py`: classic ESP32 / 4 MB, and ESP32-S3 / advertised 16 MB QIO flash / OPI PSRAM / COM UART / CDC disabled. Both use a 2 MB no-OTA app and roughly 2 MB filesystem. S3 flash beyond that layout is intentionally unused.
- The shared sketch compiled with both controller adapters, digital INMP441 input, MAX98357A I2S output, multipart upload, asynchronous polling, MP3 decoder and optional LED disabled. No analog substitution, insecure TLS setting or upload.
- A local ignored CLI copy is available at `.tools/arduino-cli`; the Python tool and compatibility shell wrapper find it automatically. Normal builds use example credentials in a temporary sketch; private config/settings are preserved.
- C++ regression checks reject S3 PSRAM/USB pins, old classic pin overrides on S3, overlapping signals, classic flash-bus pins and unsupported chip targets.
- User-supplied JPG and clearer IMG_1446/1447/1448 HEIC photos were inspected. They show **HW678**, **Sixspan S3-N16R8**, relevant GPIO labels, fitted headers, onboard RGB LED and separate **COM / USB** connectors. These are photographic observations, not electrical tests.

A cross-compile cannot measure board flash/PSRAM, runtime heap or prove physical operation. The 4 MB classic and 16 MB S3 selections must be confirmed on connected hardware. Windows startup/build/upload instructions are documented in `WINDOWS.md`; no Windows runtime or physical upload has been tested here.

## Pending physical / deployment acceptance

- Neither controller is connected to this Mac. S3 labels are visible in photos; measured capacities, USB bridge identification, serial operation, upload and boot remain unverified.
- INMP441 breakout pinout, header soldering, button continuity and microphone gain/noise.
- MAX98357A still needs sourcing; verify the speaker driver's actual 4-ohm/10-watt marking and speaker wires.
- Human microphone capture and audible speaker quality, brownouts, power-bank behavior and ten-turn physical endurance.
- ESP32 WiFi, NTP, certificate validation and real network failure recovery.
- Cloud hosting, proxy behavior, persistent storage across redeploy and venue network.

The wiring tables are checked against source, visible S3 header labels and manufacturer interface requirements; physical connections are not tested. Follow `HARDWARE.md` step by step and complete `EXHIBITION.md` before calling the hardware exhibition-ready.

## Bootstrap kit — 28 October 2026

- Full suite after bootstrap/serial-tool integration: **73 passed**, with two existing upstream Python 3.14 deprecation warnings.
- Added native Windows `.cmd` and Mac `.command` setup/start launchers. Setup itself is a shared Python standard-library script; Python 3.12–3.14 must be available first. It never requests/prints the Gemini key or uploads firmware.
- Real Mac in-place setup reused the existing Python environment, private settings and matching global Arduino core/audio library. Existing `.env`, `.env.local`, saved memory and firmware config hashes stayed unchanged.
- Fresh computer setup in a temporary project path containing spaces created a new `.venv`, installed dependencies, seeded missing settings, then passed a second run with all four private/saved files byte-for-byte preserved.
- The native Mac start launcher served real Flask `/health` from that fresh project on an isolated test port. It reported no configured key and untested Gemini; no AI request was made. The test server was stopped afterward.
- Downloaded the official Arduino CLI **1.5.1 Apple Silicon archive**, verified its pinned SHA-256, extracted/executed it, then ran the native bootstrap's firmware/example-compile path in the fresh project. It reused matching existing core/library packages and compiled S3 firmware: **1,186,787 bytes program / 47,364 bytes static RAM**. No upload or private WiFi build.
- Missing/different global board packages use a project-local SDK under `.tools/arduino`. This new isolated-install path was tested with controlled tool calls, not by repeating the multi-GB SDK download. The firmware and serial helpers use the same scoped SDK paths and reject copied OS/CPU metadata.
- Regression coverage includes create-only settings/session secrets, retained broken environments, default examples, isolated installs/resume paths, insufficient disk, checksum failure, executable-only ZIP extraction, log redaction, unmodified JSON parsing, CLI selection, architecture mismatches, no implicit upload and port-required monitoring.
- Python/shell syntax, dependency consistency, Markdown local links/fences, English/Malayalam code-block/wiring parity and Git whitespace were checked.
- Native Windows execution remains pending on the nephew's PC. Windows paths, archive handling and argument construction are covered by tests; `.cmd` behavior has been reviewed but was not run on Windows here. Physical board upload/audio remain pending as before.
