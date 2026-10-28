# Karen AI — Malayalam conversational assistant

Created for Sreehari V's science-fair project at PKMMHSS Edarikode.

**Start here:** this is a runnable Flask backend, mobile dashboard and ESP32 reference firmware. It is not a hosted deployment. Live use requires a Gemini key, internet access, host configuration and hardware commissioning. The included offline demo is explicitly labelled and gives a fixed reply; it is not an AI substitute.

## What is included

- Malayalam STT (`ml-IN`), Gemini conversation, and Malayalam MP3 synthesis (`ml`).
- Mobile dashboard with text chat, browser microphone recording, audio player, persistent memory editor and conversation reset.
- Original routes: `/`, `/update`, `/test_chat`, `/chat`; additional `/reset` and `/health`.
- Atomic `memory.txt` updates and one shared, bounded conversation (last 10 turns). History resets on memory edits/server restart.
- Classic ESP32 firmware: button → 5-second WAV → multipart upload → MP3 download → speaker.
- Setup, wiring, acceptance checklist, automated tests, Docker and Replit run configuration.

## 1. Run the dashboard first

Use Python 3.12 (the tested version). In a terminal in this folder:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Windows: copy .env.example .env
```

Edit `.env`:

```dotenv
GEMINI_API_KEY=your_key_from_google_ai_studio
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=0
PORT=8080
SECRET_KEY=replace_with_a_long_random_value
MEMORY_PATH=data/memory.txt
```

Get your own Gemini key from https://aistudio.google.com/apikey and put it in the host's secret settings or `.env`, never in firmware or chat. Confirm the chosen model is enabled for your account; `GEMINI_MODEL` is configurable. The original Gemini 1.5 integration has been replaced with the `google-genai` SDK and the model used in Google's current text-generation example (checked 28 October 2026).

```bash
python app.py
```

Visit http://localhost:8080. Ask `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` and expect a brief Malayalam reply about Sreehari. Browser recording needs HTTPS or localhost and microphone permission. Text chat works without a microphone and the basic forms work without JavaScript.

To try the interface without a key, set `DEMO_MODE=1` and restart. Voice is disabled in demo mode. Return to `DEMO_MODE=0` for real use.

## 2. Host it

### Replit — exhibition workspace flow

1. Create a Python project and import these files, keeping the folder layout.
2. Install `requirements.txt` in its shell.
3. Set `GEMINI_API_KEY`, `GEMINI_MODEL`, `SECRET_KEY`, `DEMO_MODE=0` and `PORT=8080` in Secrets/environment settings.
4. Run `python app.py`. `.replit` includes the port mapping. Use the HTTPS URL Replit displays; do not append `:5000` to its public hostname.
5. Open `/health` and test text chat, memory editing and voice before connecting hardware.
6. Keep the manually started workspace running throughout the demonstration. Sleep/restart availability is host-dependent.

The requested `memory.txt` persists on the same disk. A published Replit app must not rely on runtime filesystem changes surviving republishing. Back up edited memory before redeploying. For durable hosting use a persistent disk (below), or implement a database/object-store memory adapter before using an ephemeral multi-instance host.

### Persistent deployment with Docker

```bash
docker build -t karen-ai .
docker volume create karen-memory
docker run --rm -p 8080:8080 --env-file .env \
  -e MEMORY_PATH=/app/data/memory.txt \
  -v karen-memory:/app/data karen-ai
```

Terminate HTTPS at your host/reverse proxy and allow at least 150 seconds for the voice endpoint. Use **one worker / one instance**, because the exhibition conversation is deliberately shared in process memory. For a non-Docker persistent host:

```bash
gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 4 --timeout 150 'app:create_app()'
```

No dashboard login is implemented, as explicitly requested. Anyone who can reach the app can view/change its memory and use its API quota. Use a controlled exhibition network or restricted ingress. The CSRF token protects browser form submissions; it is not authentication. `/chat` is intentionally accessible to the device without browser cookies. This is a single-exhibit application, not a multi-user public service.

## 3. Assemble and flash the ESP32

See [docs/HARDWARE.md](docs/HARDWARE.md) for the pin table and flashing sequence. The reference build uses a **classic ESP32, INMP441 I2S microphone, MAX98357A I2S amplifier and 8-ohm speaker**. The report's unspecified legacy sound sensor is not interchangeable with this I2S firmware. Confirm the actual module before wiring it.

Copy `firmware/karen_ai/config.example.h` to `config.h` in the same folder. Fill in the hotspot, password and exact server origin. For a cloud HTTPS URL, provide the matching trusted root CA PEM; certificate verification is never disabled. Flash with Arduino IDE using Arduino-ESP32 3.x and ESP8266Audio 2.x. The firmware has not been compiled or tested on physical hardware in this delivery; the acceptance steps are mandatory before exhibiting.

## 4. Verify

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests inject fake speech/model providers, so they do not consume API quota and do not prove real recognition or synthesis quality. See [docs/VALIDATION.md](docs/VALIDATION.md) and [docs/EXHIBITION.md](docs/EXHIBITION.md).

For a live device-style request, record a mono 16-bit PCM WAV, 0.1–15 seconds long:

```bash
curl --fail-with-body -X POST -F 'audio=@question.wav;type=audio/wav' \
  http://localhost:8080/chat -o reply.mp3
```

HTTP 200 with `audio/mpeg` is playable audio. `X-Karen-Result: spoken-error` means Karen is speaking a retry/error message; it is not a successful AI answer. Invalid uploads return JSON 400; a failed TTS provider returns JSON 503. Do not play JSON as MP3.

## Scope choices

The shared history follows the PRD and is capped to control context growth. Immutable Malayalam instructions are separate from editable identity facts. Audio is kept in server memory and never written to shared `input.wav`/`output.mp3` files, avoiding cross-request overwrite. Firmware buffers audio on flash so a standard ESP32 does not need PSRAM. Text output language/length is instructed, not mathematically guaranteed by the model.

Google Web Speech via SpeechRecognition and gTTS match the requested stack. They need internet and their availability/quotas are not controlled by this project. A recognition failure can be spoken only if TTS is reachable. A complete network outage cannot produce new cloud speech. The optional demo still supports a scripted text reply.

## Reference documentation

- Google Gemini generation and system instructions: https://ai.google.dev/gemini-api/docs/generate-content/text-generation
- Gemini lifecycle: https://ai.google.dev/gemini-api/docs/deprecations
- SpeechRecognition: https://github.com/Uberi/speech_recognition
- ESP-IDF I2S standard driver: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2s.html
- ESP8266Audio decoder and I2S output: https://github.com/earlephilhower/ESP8266Audio
- Replit deployment filesystem behavior: https://replit.com/blog/deployments-launch
