# Karen AI — Malayalam conversational assistant

**മലയാളത്തിലുള്ള എല്ലാ നിർദേശങ്ങൾക്കും:** [READMEMALAYALAM.md](READMEMALAYALAM.md)

Science exhibition assistant for Sreehari V, Class 9S, PKMMHSS Edarikode.

**Using Windows and the photographed HW678 / ESP32-S3 N16R8 board?** Start with [the Windows setup guide](docs/WINDOWS.md). Both it and the original classic ESP32 use the same backend.

ESP32 WAV → Flask → Google speech recognition (`ml-IN`) → Gemini → Malayalam gTTS (`ml`) MP3 → I2S speaker. The mobile dashboard provides text chat, five-second recording, memory editing and conversation reset. It intentionally has no login.

## Start on this Mac

```bash
cd /Users/sanoopbhaskerv/workspace/karen-ai
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://localhost:8080**. Keep Terminal open; stop with Control-C. If port 8080 is occupied, stop the previous server before starting another. For a fresh checkout, create a virtual environment with `python3 -m venv .venv`, then create `.env` only if it does not exist:

```bash
test -f .env || cp .env.example .env
```

Put your Gemini key in `.env` or the host's secret settings, never in firmware, screenshots or chat. The existing `.env` and `data/memory.txt` on this Mac were preserved. An ignored `.env.local` selects `gemini-3.5-flash-lite`, verified through **both** API model listing and real Malayalam generation on 28 October 2026. Setting precedence: shell environment → `.env.local` → `.env` → application defaults. Fresh checkouts use `.env.example`; `.env.local` is not published.

```dotenv
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
DEMO_MODE=0
PORT=8080
SECRET_KEY=replace_with_a_long_random_value
MEMORY_PATH=data/memory.txt
```

Python 3.14 works in the existing Mac environment. Docker targets Python 3.12. `requirements-lock.txt` records the original Python 3.12 environment; the bounded `requirements.txt` also permits Python's newer audio compatibility packages.

## Verify Gemini first

```bash
python scripts/diagnose_gemini.py --list-only
python scripts/diagnose_gemini.py
# Only select another exact ID after it appears in the listing:
python scripts/diagnose_gemini.py --model <listed-model-id>
```

Model listing proves metadata access; the separate inference test proves generation for the selected model. The diagnostic never updates saved facts or conversation. Gemini 1.5 is retired; a new key does not restore it. The original `gemini-3.8-flash` returned 504 deadlines at both 30 and 60 seconds, plus 503 high-demand responses. `gemini-3.5-flash-lite` returned a real Malayalam answer about Sreehari in 1.2 seconds with the same key. This establishes a working alternative, not the internal cause of Google's service failure.

Try `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?`, then a science question and a follow-up. Answers should be brief, natural Malayalam. The model can still make mistakes; inspect demonstration answers. Fixed Malayalam instructions remain separate from editable facts.

`GET /health` is a local process/configuration check. `configured: true` means a key is present. `gemini.status` starts `untested`, becomes `ready` after successful generation, or `degraded` after failure. It describes the last attempt, not a promise of future availability. Health checks never call Gemini.

Errors print sanitized operation/model/code/provider-code/attempt/elapsed-time fields in the Python console. Request completion logs include the request ID. No API key, prompt, saved facts or raw provider exception URL is logged. Common codes:

| Code | Action |
|---|---|
| `model_timeout` (often provider 504) | Model missed its deadline; check demand and run diagnostics |
| `model_unavailable` (often 503) | Temporary provider failure; bounded retry is automatic |
| `model_not_found` (404) | List models and verify a supported exact ID |
| `model_auth` (401/403) | Check restrictions/project access in AI Studio |
| `model_quota` (429) | Check rate limits/quota/billing; no automatic quota retry |
| `model_network`, `stt_unavailable`, `tts_unavailable` | Check outbound internet/provider availability |
| `request_timeout` | Whole request expired; inspect its ID before a new turn |
| `busy` | Wait for the current operation, or cached-result capacity to expire |

HTTP 505 means HTTP Version Not Supported. The reproduced failure was 504, not 505.

## Dashboard, voice and permanent memory

Browser microphone access requires localhost or trusted HTTPS and microphone permission. On the Mac use **localhost**, not its LAN IP. A phone on the same WiFi can use `http://<Mac-LAN-IP>:8080` for text and memory; phone recording needs trusted HTTPS. The recorder captures five seconds, converts to mono PCM WAV and displays a playable MP3 response. Chrome software tests use synthesized Malayalam input; human microphone quality remains a separate acceptance step.

`data/memory.txt` holds editable permanent facts. Saving memory replaces it atomically and clears the shared conversation. New chat and restart clear RAM history. The last ten complete turns are shared across browser/device. Memory paths are relative to this project, not the terminal's working directory. An answer still running when memory/reset changes cannot restore the old conversation.

Offline interface demo: set `DEMO_MODE=1`, restart. Replies are labelled scripted; voice is disabled. Restore `DEMO_MODE=0` for live operation.

## Requests, timeouts and retries

Original routes remain: `/`, `/health`, `/update`, `/test_chat`, `/chat`, `/reset`. Added: `GET /requests/<request-id>`.

Browser and firmware send `Prefer: respond-async` and a unique `X-Request-ID`. The POST returns 202 with `Location`/`Retry-After` while processing; poll until JSON text, MP3 or a structured error arrives. A repeated POST with the **same ID and same question** reuses the pending/completed result. Reusing an ID for different input returns 409. Polling never creates a conversation turn. Results remain in RAM for ten minutes, up to 64 results (at most ~32 MB of audio); when full, new work waits for expiry. Restart clears history and this cache, so recovery is guaranteed only within the same server process and retention window.

| Layer | Budget |
|---|---|
| Google STT | 15-second socket operation timeout |
| Gemini | Two attempts maximum, 45 seconds each, one-second backoff; SDK retries disabled |
| gTTS | 5-second connect / 15-second read per segment |
| Whole operation | 140-second result deadline, including all speech segments |
| Browser | 15-second individual calls; 160-second overall polling budget |
| ESP32 | 10-second connect / 15-second read; 160-second polling budget |
| Synchronous clients / host | 150+ seconds |

Only transient Gemini failures are retried automatically; the same context is reused. Browser upload transport retries reuse the same ID. Firmware polls after an uncertain POST, and re-uploads with that ID at most once if the server has no record. The device stops after four transport failures. Neither client silently resubmits a completed question with a new ID. If a client gives up, inspect `/requests/<id>` before asking again.

One background provider worker runs at a time; other new requests return `busy`. The dashboard and health stay responsive. A provider thread already inside a third-party library cannot be forcibly cancelled: if it outlives the 140-second result deadline, it keeps the worker slot until it exits, and its late result cannot append history. For voice, history is committed only after MP3 synthesis succeeds. These limits deliberately avoid unbounded threads or a hidden request queue.

Synchronous integrations still work without `Prefer`. Upload a mono 16-bit PCM WAV, 0.1–15 seconds:

```bash
curl --fail-with-body --max-time 155 -F 'audio=@question.wav;type=audio/wav' \
  -H 'X-Request-ID: manual-unique-question-001' http://localhost:8080/chat -o reply.mp3
```

A successful reply is HTTP 200, `audio/mpeg`, `X-Karen-Result: ok`. `spoken-error` means an error apology was synthesized; `X-Karen-Error` identifies why. Invalid WAV returns JSON 400; failed TTS returns JSON 503. Never treat JSON or a spoken apology as a successful AI answer.

## Tests and firmware

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
node --check static/app.js
```

See [validation record](docs/VALIDATION.md) for real versus mocked checks. The optional live Chrome test requires Playwright (`npm install --prefix /tmp/karen-browser playwright`) and a speech fixture at `/tmp/karen-audio/question.wav`:

```bash
NODE_PATH=/tmp/karen-browser/node_modules node tests/browser.cjs
# Separate live memory-editor check using a temporary copy of saved facts:
NODE_PATH=/tmp/karen-browser/node_modules node tests/browser_memory.cjs
```

The shared firmware has two controller adapters. Set `KAREN_CONTROLLER` in `.env`, `.env.local` or the shell, or pass `--controller` to the build tool. Shell settings win over files; `--controller` wins over both.

| Value | Board | Build configuration |
|---|---|---|
| `esp32` (default) | Original classic 38-pin ESP32 | 4 MB target, original GPIO map |
| `esp32_s3` | Photographed HW678 / Sixspan S3-N16R8 | 16 MB target, octal PSRAM, separate safe GPIO map |

```powershell
# Windows PowerShell, from the project folder:
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py
```

```bash
# Mac/Linux:
KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py
# The original wrapper also works and defaults to esp32:
./scripts/compile_firmware.sh
```

Normal builds use example credentials and never upload. `--use-config` uses private `firmware/karen_ai/config.h`; `--upload --port <actual-port>` compiles that private configuration and uploads only after success. Temporary sketches/binaries are cleaned up. Selecting a controller changes the firmware chip target and pins **at build time**; changing Flask's environment cannot reprogram an already-flashed board. Arduino IDE selects the adapter from its board target instead of reading `.env`.

Both profiles keep INMP441 digital input and **MAX98357A** I2S output. No PAM8403/analog substitution was made. See [Windows setup](docs/WINDOWS.md), [both wiring maps and commissioning](docs/HARDWARE.md), and [exhibition checklist](docs/EXHIBITION.md). The supplied photos establish the S3 board's labels, not measured flash/PSRAM size or successful physical operation. Microphone/amplifier pinout, electrical connections and the speaker driver's actual 4-ohm/10-watt marking still need confirmation.

## Cloud later

Local validation comes first. Nothing is deployed by this change. The existing Docker configuration uses one worker and four threads; keep **one instance** because history/jobs are intentionally process-local. Use trusted HTTPS, a persistent disk for `MEMORY_PATH`, and at least 150-second proxy timeouts for synchronous clients. `.env`, `.env.local`, saved memory and firmware credentials are excluded from Git and the Docker build context.

```bash
docker build -t karen-ai .
docker volume create karen-memory
docker run --rm -p 8080:8080 --env-file .env \
  -e GEMINI_MODEL=gemini-3.5-flash-lite -e MEMORY_PATH=/app/data/memory.txt \
  -v karen-memory:/app/data karen-ai
```

No-login access is intentional. Anyone who reaches the dashboard can edit memory and use quota; use the exhibition network/restricted ingress. CSRF protects browser forms, not authentication. `/chat` supports the ESP32 without cookies. Back up permanent facts before redeploying; ephemeral hosting does not preserve runtime disk edits.

## References

- [Gemini troubleshooting](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [Google model shutdown record](https://firebase.google.com/docs/ai-logic/faq-and-troubleshooting)
- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) and [gTTS](https://gtts.readthedocs.io/)
- [HTTP status definitions](https://www.rfc-editor.org/rfc/rfc9110.html)
