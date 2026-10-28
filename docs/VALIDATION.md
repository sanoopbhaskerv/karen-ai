# Validation record — 28 October 2026

## Completed

- Python 3.12 backend test suite: **18 passed**.
- Flask dashboard HTML renders and health endpoint responds.
- Text and form interactions, shared follow-up history, last-10-turn limit, and explicit reset.
- Memory update persists to disk, resets history, and survives app recreation.
- Failed model requests do not add incomplete conversation turns.
- CSRF validation on browser mutations and HTML escaping of user content.
- Invalid/empty text and memory handling.
- Multipart and raw WAV voice endpoints with injected providers.
- Invalid, truncated, too-long and oversized WAV upload rejection.
- Spoken recognition-error response and TTS failure JSON response.
- Explicit offline demo behavior and disabled voice in demo mode.
- Actual provider adapters checked with mocks: `ml-IN` recognition, `ml` synthesis, Gemini role ordering and Malayalam system instruction.
- Python source compilation and JavaScript syntax check.

The tests substitute provider results and fake MP3 bytes; they prove application behavior, not actual audio quality or provider availability. The installed environment is captured in `requirements-lock.txt` (including test dependencies). Use `pip install -r requirements-lock.txt` for the tested Python 3.12 package set, or the bounded `requirements.txt` for runtime installation.

## Not completed

- Live Gemini, Google speech recognition and gTTS requests: no user API key or live speech sample supplied.
- Real browser layout/interaction and microphone recording: Playwright was available but its Chromium downloads repeatedly returned invalid archives. JavaScript syntax was checked; visual and browser runtime checks are pending.
- ESP32 compile/upload: Arduino CLI was fetched, but board/library indexes could not be downloaded due to network/DNS restrictions. Source uses documented ESP-IDF 5 standard I2S interfaces and ESP8266Audio interfaces; compilation remains unverified.
- Physical microphone capture, speaker playback, WiFi/TLS connection, power draw and ten-turn endurance.
- Replit or other hosted deployment: account access, runtime secrets and deployment hostname were not supplied.
- Persistent storage across an actual host redeploy.

Run the live acceptance checklist in `EXHIBITION.md` before considering the complete system exhibition-ready. No claim of successful live end-to-end operation is made.
