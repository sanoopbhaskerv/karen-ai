# OpenAI setup for Karen

Karen can use OpenAI for Malayalam speech recognition and answer generation while retaining the existing Google Malayalam voice. Both browser recording and the ESP32 keep the same WAV upload and MP3 reply protocol; changing the backend does not require another board upload.

## Credentials and API credits

Create a project API key under the personal OpenAI API organization receiving your credits. Store it only in the project's ignored `.env.local` or the server's private deployment settings. Do not put the key in firmware, Git, screenshots or chat. Eligible ChatGPT Pro/Business owners can claim an API-credit benefit by linking their API organization; check the current offer and expiry in [OpenAI's API-credit guide](https://developers.openai.com/api/docs/guides/chatgpt-api-credits).

The credits cover OpenAI transcription, answer-generation and billed web-search calls. Google MP3 synthesis remains the same service used by the original setup. OpenAI audio output was evaluated separately; it is not enabled in this Malayalam configuration.

## Select OpenAI

Set these nonsecret model/provider values in the existing private settings file, along with the securely provisioned key:

```dotenv
AI_PROVIDER=openai
OPENAI_MODEL=gpt-6-luna
OPENAI_STT_MODEL=gpt-transcribe
```

Restart the server after changing its environment. For Docker hosting, use the existing private `deploy/.env`, validate Compose without printing its resolved secrets, then rebuild only the app:

```bash
sudo docker compose config --quiet
sudo docker compose up --build --detach --no-deps app
```

The setup retains saved memory and existing cloud authentication. A server restart clears conversation history and the temporary request cache. The default provider remains `gemini` for existing installations; explicitly setting `AI_PROVIDER=gemini` selects the original provider again.

## Verify and interpret timings

`/health` reports `provider: openai`, the selected text model and `openai.status`. `configured: true` indicates key presence; `ready` describes the latest successful generation, not a guarantee for future requests. Health checks make no inference request.

Completed voice responses report `stt`, `openai` and `tts` in `Server-Timing`. The `openai` duration is text-answer generation; `tts` is Google Malayalam speech generation. Cached request results preserve their original audio and timings. Existing board firmware can play these replies and print total timing without modification; older timing parsers may omit the newly named `openai` metric. The server logs always include it with the request ID.

OpenAI requests have a 5-second connection timeout. Recognition retains a 20-second read timeout; answer requests allow 45 seconds because they can search the web. There is no implicit generation retry. A timeout returns a labeled spoken error rather than waiting for another long attempt. The existing overall job deadline, request deduplication, memory-revision guard and audio-size limits remain in place.

## Current information and sources

General answers can use the Responses API [web-search tool](https://developers.openai.com/api/docs/guides/tools-web-search). Recent-year questions and changing facts explicitly require search, while ordinary science questions let the model decide whether verification is useful. Each answer request supplies the current Indian date, so “last year” follows the actual calendar. A question about an award with several categories can ask which category the visitor means.

The configured model is retained, with at most two search/tool calls per answer. Search prefers official sources and supplies actual citation URLs. Source links appear under the answer and remain attached to that exact turn after refreshing the dashboard; they leave with the bounded conversation history or a reset. Voice replies use the answer text without citation markers or source URLs. The dashboard provides the corresponding links after refresh.

Answers are checked for mixed Indic scripts or English-only prose. If needed, one additional request rewrites the same facts into Malayalam, keeping proper names in Latin script and retaining the original sources. That formatting request has a 20-second read timeout and does not search again. An unsuccessful correction returns a labeled Malayalam error instead of publishing mixed-language text.

Creator/privacy replies and the checked Sasthramela extracts still run before general generation. Search failures remain labeled service errors. No answer should claim a current result was verified merely because the tool was available.

Tests use fake transports and isolated facts:

```bash
AI_PROVIDER=gemini .venv/bin/python -m pytest -q
```

On Windows PowerShell, set `$env:AI_PROVIDER = 'gemini'` before running the matching `.venv\Scripts\python.exe -m pytest -q` command. This selects the legacy baseline for tests even when private settings choose OpenAI.

Live timing varies with provider load, the question and network conditions. Compare the same short Malayalam question and measure first sound separately from reply duration. The board still records five seconds, uploads the WAV and downloads the complete MP3 before playback. Follow the [controller timing guide](CONTROLLER_LATENCY.md) to measure those stages.

## മലയാളത്തിൽ

ഈ configuration-ൽ ചോദ്യം തിരിച്ചറിയാനും മറുപടി തയ്യാറാക്കാനും OpenAI ഉപയോഗിക്കുന്നു. മലയാളം ശബ്ദമറുപടിക്ക് നിലവിലുള്ള Google voice നിലനിർത്തുന്നു. API key server-ൽ മാത്രം സൂക്ഷിക്കുക; `config.h`-ൽ ചേർക്കരുത്. Backend മാറ്റുന്നതിനായി board firmware വീണ്ടും upload ചെയ്യേണ്ടതില്ല.

`/health`-ൽ `provider: openai` പരിശോധിക്കുക. ചോദ്യം ചോദിച്ചശേഷം server logs-ൽ `stt`, `openai`, `tts` സമയങ്ങൾ കാണാം. പഴയ firmware-ൽ `openai` എന്ന പുതിയ timing പേര് കാണിക്കാത്തപ്പോഴും മറുപടി play ചെയ്യും. Credits-ന്റെ കാലാവധിയും balance-ഉം OpenAI Platform billing-ൽ പരിശോധിക്കണം.
