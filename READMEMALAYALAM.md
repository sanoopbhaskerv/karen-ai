# Karen AI — മലയാളത്തിലുള്ള ഉപയോഗനിർദേശങ്ങൾ

ശ്രീഹരി V, ക്ലാസ് 9S, PKMMHSS എടരിക്കോട് എന്നിവർക്കായി തയ്യാറാക്കിയ ശാസ്ത്രപ്രദർശന സഹായിയാണ് Karen AI.

ESP32 റെക്കോർഡ് ചെയ്യുന്ന WAV → Flask സർവർ → Google ശബ്ദതിരിച്ചറിയൽ (`ml-IN`) → Gemini → മലയാളം gTTS (`ml`) MP3 → I2S സ്പീക്കർ എന്ന ക്രമത്തിലാണ് പ്രവർത്തനം. മൊബൈൽ ഡാഷ്ബോർഡിൽ ടെക്സ്റ്റ് ചാറ്റ്, അഞ്ചു സെക്കൻഡ് ശബ്ദറെക്കോർഡിങ്, സ്ഥിരം ഓർമ്മ തിരുത്തൽ, സംഭാഷണം മായ്ക്കൽ എന്നിവ ലഭ്യമാണ്. ഡാഷ്ബോർഡിൽ ലോഗിൻ ഇല്ല.

[English README](README.md)യിലെ നിർദേശങ്ങളും [ഹാർഡ്‌വെയർ](docs/HARDWARE.md), [പ്രദർശന ഒരുക്കം](docs/EXHIBITION.md), [പരിശോധനാഫലം](docs/VALIDATION.md) എന്നീ രേഖകളിലെ വിവരങ്ങളും ഈ മലയാളം മാർഗനിർദേശത്തിൽ ഉൾപ്പെടുത്തിയിട്ടുണ്ട്. കമാൻഡുകൾ, ഫയൽപ്പേരുകൾ, ക്രമീകരണപ്പേരുകൾ, GPIO നമ്പറുകൾ എന്നിവ അതേപടി ഉപയോഗിക്കുക. താഴെപ്പറയുന്ന പരിശോധനാഫലങ്ങൾ 2026 ഒക്ടോബർ 28-ന് രേഖപ്പെടുത്തിയവയാണ്; പുതിയ പരിശോധന നടത്തിയെന്ന അവകാശവാദമല്ല.

## 1. ആദ്യം Mac-ൽ പ്രവർത്തിപ്പിക്കുക

പുതിയ checkout ആണെങ്കിൽ പ്രോജക്ട് ഫോൾഡറിൽ virtual environment ഉണ്ടാക്കുക:

```bash
cd /Users/sanoopbhaskerv/workspace/karen-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```

ഇതിനകം `.venv` ഉണ്ടെങ്കിൽ അത് വീണ്ടും സൃഷ്ടിക്കേണ്ടതില്ല. മറ്റൊരു കമ്പ്യൂട്ടറാണെങ്കിൽ `cd` കമാൻഡിൽ അവിടെയുള്ള പ്രോജക്ട് പാത്ത് നൽകുക. Windows PowerShell-ൽ environment പ്രവർത്തനക്ഷമമാക്കാൻ `.venv\Scripts\Activate.ps1` ഉപയോഗിക്കാം.

`.env`-ൽ ആവശ്യമായ മൂല്യങ്ങൾ നൽകുക:

```dotenv
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
DEMO_MODE=0
PORT=8080
SECRET_KEY=replace_with_a_long_random_value
MEMORY_PATH=data/memory.txt
```

സ്വന്തം Gemini API key [Google AI Studio](https://aistudio.google.com/apikey)-യിൽനിന്ന് എടുക്കുക. അത് `.env`-ലോ ഹോസ്റ്റിന്റെ secret ക്രമീകരണത്തിലോ മാത്രം സൂക്ഷിക്കുക. firmware, screenshot, chat എന്നിവയിൽ ചേർക്കരുത്. `SECRET_KEY`-യ്ക്ക് നീളമുള്ള യാദൃച്ഛിക മൂല്യം നൽകുക.

ക്രമീകരണങ്ങളുടെ മുൻഗണന: shell environment → `.env.local` → `.env` → ആപ്പിന്റെ അടിസ്ഥാന ക്രമീകരണം. ഈ Mac-ലെ നിലവിലുള്ള `.env`, `data/memory.txt` എന്നിവ സംരക്ഷിച്ചിട്ടുണ്ട്. Git അവഗണിക്കുന്ന `.env.local` ആണ് ഇവിടെ പരിശോധിച്ച `gemini-3.5-flash-lite` തിരഞ്ഞെടുക്കുന്നത്. പുതിയ checkout-ൽ `.env.example` ഉപയോഗിക്കുക; `.env.local` പ്രസിദ്ധീകരിക്കുന്നില്ല.

സർവർ തുടങ്ങാൻ:

```bash
python app.py
```

ബ്രൗസറിൽ **http://localhost:8080** തുറക്കുക. Terminal തുറന്നുവയ്ക്കുക; നിർത്താൻ Control-C അമർത്തുക. 8080 പോർട്ട് ഉപയോഗത്തിലാണെങ്കിൽ പഴയ സർവർ നിർത്തിയശേഷം വീണ്ടും തുടങ്ങുക.

നിലവിലുള്ള Mac environment-ൽ Python 3.14 പ്രവർത്തിക്കുന്നു. Docker Python 3.12 ഉപയോഗിക്കുന്നു. `requirements-lock.txt` ആദ്യം ഉപയോഗിച്ച Python 3.12 environment രേഖപ്പെടുത്തുന്നു; `requirements.txt` പുതിയ Python പതിപ്പുകളിലെ audio compatibility packages-നും അനുവദിക്കുന്നു.

## 2. Gemini ആദ്യം പരിശോധിക്കുക

```bash
python scripts/diagnose_gemini.py --list-only
python scripts/diagnose_gemini.py
```

മറ്റൊരു model തിരഞ്ഞെടുക്കണമെങ്കിൽ പട്ടികയിൽ കാണുന്ന കൃത്യമായ ID മാത്രം ഉപയോഗിക്കുക; താഴെയുള്ള placeholder മാറ്റണം:

```bash
python scripts/diagnose_gemini.py --model <listed-model-id>
```

Model പട്ടിക കിട്ടുന്നത് metadata access തെളിയിക്കുന്നു. മറുപടി സൃഷ്ടിക്കുന്ന വേറിട്ട പരിശോധനയാണ് inference പ്രവർത്തിക്കുന്നെന്ന് തെളിയിക്കുന്നത്. Diagnostic സ്ഥിരം ഓർമ്മയോ സംഭാഷണമോ മാറ്റുന്നില്ല.

രേഖപ്പെടുത്തിയ പരിശോധനയിൽ `gemini-3.8-flash` 30, 60 സെക്കൻഡ് പരിധികളിൽ 504 deadline പിശകുകളും മറ്റൊരു ശ്രമത്തിൽ 503 high-demand പിശകും നൽകി. അതേ key ഉപയോഗിച്ച് പട്ടികയിലുള്ള `gemini-3.5-flash-lite` ശ്രീഹരിയെക്കുറിച്ച് 1.2 സെക്കൻഡിൽ യഥാർഥ മലയാളം മറുപടി നൽകി. ഇത് പ്രവർത്തിക്കുന്ന മറ്റൊരു model ഉണ്ടെന്ന് തെളിയിക്കുന്നു; Google-ന്റെ ഉള്ളിലെ തകരാറിന്റെ കാരണം തെളിയിക്കുന്നില്ല. Gemini 1.5 വിരമിച്ചതാണ്; പുതിയ key ഉണ്ടാക്കിയാൽ അത് തിരിച്ചുകിട്ടില്ല.

`നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` എന്ന് ചോദിക്കുക. തുടർന്ന് ഒരു ശാസ്ത്രചോദ്യവും അതുമായി ബന്ധപ്പെട്ട തുടർചോദ്യവും ചോദിക്കുക. മറുപടികൾ ചെറുതും സ്വാഭാവികമായ മലയാളത്തിലുമാകണം. Model തെറ്റുകൾ വരുത്താം; പ്രദർശനത്തിൽ ഉപയോഗിക്കുന്ന മറുപടികൾ പരിശോധിക്കുക. സ്ഥിരമായ മലയാളം നിർദേശങ്ങൾ തിരുത്താവുന്ന വ്യക്തിവിവരങ്ങളിൽനിന്ന് വേർതിരിച്ചിരിക്കുന്നു.

### Health നിലയും പിശകുകളും

`GET /health` പ്രക്രിയയും ക്രമീകരണവും പരിശോധിക്കുന്നു; Gemini-യെ വിളിക്കുന്നില്ല. `configured: true` എന്നത് key നൽകിയിട്ടുണ്ടെന്നാണ്. `gemini.status` ആദ്യ generation-ന് മുമ്പ് `untested`, വിജയിച്ചാൽ `ready`, പരാജയപ്പെട്ടാൽ `degraded` ആയിരിക്കും. ഇത് അവസാന ശ്രമത്തിന്റെ നിലയാണ്; അടുത്ത ശ്രമത്തിന്റെ വിജയത്തിന് ഉറപ്പല്ല.

Python console-ൽ രഹസ്യവിവരങ്ങൾ നീക്കിയ operation/model/code/provider-code/attempt/elapsed-time വിവരങ്ങൾ ലഭിക്കും. Request completion log-ൽ request ID ഉണ്ടാകും. API key, prompt, saved facts, provider exception-ന്റെ അസംസ്കൃത URL എന്നിവ രേഖപ്പെടുത്തുന്നില്ല.

| കോഡ് | ചെയ്യേണ്ടത് |
|---|---|
| `model_timeout` / സാധാരണ 504 | Model സമയപരിധി കടന്നു; diagnostic നടത്തി നിലവിലെ model പരിശോധിക്കുക |
| `model_unavailable` / സാധാരണ 503 | താൽക്കാലിക provider പ്രശ്നം; പരിമിതമായ retry സ്വയമേവ നടക്കും |
| `model_not_found` / 404 | പട്ടികയിൽനിന്ന് പിന്തുണയുള്ള കൃത്യമായ model ID തിരഞ്ഞെടുക്കുക |
| `model_auth` / 401, 403 | AI Studio-യിലെ key നിയന്ത്രണങ്ങളും project access-ഉം പരിശോധിക്കുക |
| `model_quota` / 429 | Rate limit, quota, billing പരിശോധിക്കുക; quota പിശകിന് automatic retry ഇല്ല |
| `model_network`, `stt_unavailable`, `tts_unavailable` | Internet-ഉം provider ലഭ്യതയും പരിശോധിക്കുക |
| `request_timeout` | മുഴുവൻ request-ന്റെ സമയം കഴിഞ്ഞു; വീണ്ടും ചോദിക്കുന്നതിനുമുമ്പ് അതിന്റെ ID പരിശോധിക്കുക |
| `busy` | നിലവിലെ ജോലി തീരാനോ cached result-ുകളുടെ കാലാവധി കഴിയാനോ കാത്തിരിക്കുക |

HTTP 505 എന്നത് HTTP Version Not Supported ആണ്. ഇവിടെ ആവർത്തിച്ച് കണ്ടെത്തിയ പിശക് 504 ആയിരുന്നു.

## 3. ഡാഷ്ബോർഡ്, ശബ്ദം, സ്ഥിരം ഓർമ്മ

ബ്രൗസറിൽ മൈക്രോഫോൺ ഉപയോഗിക്കാൻ `localhost` അല്ലെങ്കിൽ വിശ്വസനീയമായ HTTPS-ഉം microphone permission-ഉം വേണം. Mac-ൽ അതിന്റെ LAN IP-യ്ക്ക് പകരം **localhost** ഉപയോഗിക്കുക. അതേ WiFi-യിലെ ഫോണിൽ `http://<Mac-LAN-IP>:8080` വഴി ടെക്സ്റ്റും ഓർമ്മ തിരുത്തലും ഉപയോഗിക്കാം. ഫോണിലെ recording-ന് വിശ്വസനീയ HTTPS വേണം.

Recorder അഞ്ചു സെക്കൻഡ് ശബ്ദം എടുത്ത് mono PCM WAV ആക്കുകയും മറുപടി കേൾക്കാവുന്ന MP3 ആയി കാണിക്കുകയും ചെയ്യുന്നു. Software പരിശോധനയിൽ ഉപയോഗിച്ചത് കൃത്രിമമായി സൃഷ്ടിച്ച മലയാളം ശബ്ദമാണ്; മനുഷ്യന്റെ ശബ്ദവും ചുറ്റുപാടിലെ ശബ്ദവും പ്രത്യേകം പരിശോധിക്കണം.

`data/memory.txt`-ലാണ് സ്ഥിരം വിവരങ്ങൾ. Save ചെയ്യുമ്പോൾ ഫയൽ സുരക്ഷിതമായി പകരംവയ്ക്കുകയും പങ്കിട്ട സംഭാഷണം മായ്ക്കുകയും ചെയ്യും. New chat അമർത്തിയാലും സർവർ വീണ്ടും തുടങ്ങിയാലും RAM-ലെ സംഭാഷണം മായും. അവസാനത്തെ പത്ത് പൂർണ്ണ ചോദ്യോത്തരങ്ങൾ browser/device എല്ലാവർക്കും പങ്കിട്ടതാണ്. Memory path പ്രോജക്ടിനെയാണ് അടിസ്ഥാനമാക്കുന്നത്; Terminal തുറന്നിരിക്കുന്ന ഫോൾഡറെയല്ല. Memory/reset മാറുമ്പോൾ നടക്കുകയായിരുന്ന പഴയ മറുപടിക്ക് പഴയ സംഭാഷണം തിരിച്ചുകൊണ്ടുവരാൻ കഴിയില്ല.

Internet ഇല്ലാതെ interface മാത്രം കാണിക്കാൻ `DEMO_MODE=1` ആക്കി സർവർ വീണ്ടും തുടങ്ങുക. മറുപടികൾ മുൻകൂട്ടി തയ്യാറാക്കിയതാണെന്ന് അടയാളപ്പെടുത്തും; voice പ്രവർത്തിക്കില്ല. യഥാർഥ ഉപയോഗത്തിന് `DEMO_MODE=0` ആക്കുക.

## 4. Request, സമയപരിധി, retry

നിലവിലുള്ള routes: `/`, `/health`, `/update`, `/test_chat`, `/chat`, `/reset`. Request നില അറിയാൻ `GET /requests/<request-id>` ഉപയോഗിക്കാം.

Browser-ഉം firmware-ഉം `Prefer: respond-async`, ഓരോ ചോദ്യത്തിനും വ്യത്യസ്തമായ `X-Request-ID` എന്നിവ അയക്കും. ജോലി നടക്കുമ്പോൾ POST-ന് 202-ഉം `Location`/`Retry-After` headers-ഉം ലഭിക്കും. തുടർന്ന് JSON text, MP3, അല്ലെങ്കിൽ വ്യക്തമായ error കിട്ടുന്നതുവരെ poll ചെയ്യും.

അതേ ID-യും അതേ ചോദ്യവും വീണ്ടും POST ചെയ്താൽ നിലവിലുള്ള pending/completed result ഉപയോഗിക്കും. അതേ ID മറ്റൊരു ചോദ്യത്തിന് ഉപയോഗിച്ചാൽ 409 ലഭിക്കും. Poll ചെയ്യുന്നത് പുതിയ സംഭാഷണം ഉണ്ടാക്കുന്നില്ല. Result-ുകൾ RAM-ൽ പത്ത് മിനിറ്റ് വരെ, പരമാവധി 64 എണ്ണം, audio ഏകദേശം 32 MB വരെ സൂക്ഷിക്കും. നിറഞ്ഞാൽ പഴയ result-ുകളുടെ കാലാവധി കഴിയണം. Restart ചെയ്താൽ സംഭാഷണവും cache-ഉം മായും; recovery അതേ server process-ലും retention കാലയളവിലും മാത്രമേ ഉറപ്പുള്ളൂ.

| ഘട്ടം | സമയപരിധി |
|---|---|
| Google STT | Socket operation-ന് 15 സെക്കൻഡ് |
| Gemini | പരമാവധി രണ്ട് ശ്രമം; ഓരോന്നും 45 സെക്കൻഡ്; ഇടയിൽ 1 സെക്കൻഡ്; SDK retries ഇല്ല |
| gTTS | ഓരോ segment-നും connect 5 / read 15 സെക്കൻഡ് |
| മുഴുവൻ operation | Speech segment-ുകൾ ഉൾപ്പെടെ 140 സെക്കൻഡ് |
| Browser | ഓരോ call-നും 15 സെക്കൻഡ്; മൊത്തം polling 160 സെക്കൻഡ് |
| ESP32 | Connect 10 / read 15 സെക്കൻഡ്; polling 160 സെക്കൻഡ് |
| Synchronous client / host | കുറഞ്ഞത് 150 സെക്കൻഡ് |

താൽക്കാലിക Gemini പിശകുകൾക്ക് മാത്രം അതേ context ഉപയോഗിച്ച് automatic retry നടക്കും. Browser upload retry-കളിൽ അതേ ID ഉപയോഗിക്കും. Firmware-ന് POST സ്വീകരിച്ചോ എന്ന് വ്യക്തമല്ലെങ്കിൽ ആദ്യം poll ചെയ്യും; സർവറിൽ record ഇല്ലെങ്കിൽ അതേ ID-യിൽ പരമാവധി ഒരിക്കൽ വീണ്ടും upload ചെയ്യും. നാല് transport പരാജയങ്ങൾക്ക് ശേഷം device നിർത്തും. പൂർത്തിയായ ചോദ്യത്തെ പുതിയ ID-യിൽ client സ്വയം വീണ്ടും അയയ്ക്കില്ല. Client നിർത്തിയാൽ വീണ്ടും ചോദിക്കുന്നതിനുമുമ്പ് `/requests/<id>` പരിശോധിക്കുക.

ഒരേസമയം ഒരു background provider worker മാത്രമാണ് പ്രവർത്തിക്കുന്നത്; മറ്റു പുതിയ requests-ന് `busy` ലഭിക്കും. Dashboard-ഉം health-ഉം പ്രതികരിക്കും. Third-party library-യിൽ പ്രവർത്തിക്കുന്ന thread ബലമായി നിർത്താനാവില്ല. അത് 140 സെക്കൻഡ് കടന്നാലും പുറത്തുവരുന്നതുവരെ worker slot കൈവശംവയ്ക്കും; വൈകിയ result history-യിൽ ചേരില്ല. Voice മറുപടി MP3 ആക്കുന്നതിൽ വിജയിച്ചശേഷം മാത്രമാണ് history ചേർക്കുന്നത്. പരിധിയില്ലാത്ത threads-ഉം മറഞ്ഞ request queue-ഉം ഒഴിവാക്കാനാണ് ഈ നിയന്ത്രണം.

`Prefer` ഇല്ലാത്ത synchronous client-ുകളും പ്രവർത്തിക്കും. 0.1–15 സെക്കൻഡ് ദൈർഘ്യമുള്ള mono 16-bit PCM WAV അയയ്ക്കാം. ഓരോ പുതിയ ചോദ്യത്തിനും പുതിയ ID നൽകുക:

```bash
curl --fail-with-body --max-time 155 -F 'audio=@question.wav;type=audio/wav' \
  -H 'X-Request-ID: manual-unique-question-001' http://localhost:8080/chat -o reply.mp3
```

വിജയിച്ചാൽ HTTP 200, `audio/mpeg`, `X-Karen-Result: ok` ലഭിക്കും. `spoken-error` എന്നത് പിശകിന്റെ ക്ഷമാപണ ശബ്ദമാണ്; വിജയിച്ച AI ഉത്തരം അല്ല. `X-Karen-Error` കാരണം കാണിക്കും. തെറ്റായ WAV-ന് JSON 400; TTS പരാജയത്തിന് JSON 503. JSON സ്പീക്കറിൽ MP3 ആയി play ചെയ്യരുത്.

## 5. ഹാർഡ്‌വെയർ തിരഞ്ഞെടുക്കൽ

ഈ രേഖയിലെ wiring classic 38-pin ESP32, INMP441, **MAX98357A I2S** എന്നിവയ്ക്കാണ്. മറ്റൊരു controller-ന്റെ pinout ആയി ഉപയോഗിക്കരുത്. രേഖപ്പെടുത്തിയ പരിശോധനാസമയത്ത് hardware Mac-ൽ ബന്ധിപ്പിച്ചിട്ടില്ല; യഥാർഥ pin labels, soldering, flash capacity, വൈദ്യുതബന്ധം, ശബ്ദനിലവാരം എന്നിവ നേരിട്ട് പരിശോധിച്ചിട്ടില്ല.

| ഭാഗം | ലഭ്യമായ വിവരം | നേരിട്ട് ഉറപ്പാക്കേണ്ടത് |
|---|---|---|
| ESP32 | Classic 38-pin CP2102 / Micro-USB board; 14, 22, 25, 26, 27, 32, 33, 2 GPIO labels കണ്ടതായി അറിയിച്ചിട്ടുണ്ട് | Module classic ESP32 ആണോ, USB data connection, flash capacity |
| Microphone | കടയിലെ label INMP441 | യഥാർഥ VDD/GND/SCK/WS/SD/L-R labels, solder ചെയ്ത headers |
| Amplifier | MAX98357A I2S വാങ്ങേണ്ടതുണ്ട് | ശരിയായ module, VIN/enable/gain നിർദേശങ്ങൾ, soldering |
| Speaker | പെട്ടിയിൽ 4 ohms / 10 watts എന്നാണ് അറിയിച്ചത് | Driver-ൽ തന്നെയുള്ള impedance/power marking, രണ്ട് അനുയോജ്യ wires |
| Button | Momentary push button | അമർത്തുമ്പോൾ മാത്രം short ആകുന്ന കാലുകൾ |
| Power | USB power bank / Micro-USB data cable / Mac adapter | സ്ഥിരമായ 5 V, ആവശ്യമായ current, സുരക്ഷിത supply ക്രമീകരണം |

PAM8403 ഈ firmware-നായി തിരഞ്ഞെടുത്തിട്ടില്ല; digital I2S output-ിൽ ബന്ധിപ്പിക്കരുത്. MAX98357A-യ്ക്ക് 5 V-ൽ 4-ohm load-ിലേക്ക് ഏകദേശം 3.2 W വരെയാണ്; 10 W നൽകില്ല. യഥാർഥ 4-ohm/10-watt passive speaker കുറഞ്ഞ power-ൽ ഉപയോഗിക്കാം; പെട്ടിയിലെ വിവരം മാത്രം ആശ്രയിക്കരുത്. Firmware output gain `0.35`-ൽ തുടങ്ങുക. Speaker നേരിട്ട് GPIO-യിൽ ബന്ധിപ്പിക്കരുത്.

### Wiring

ബന്ധിപ്പിക്കുന്നതിനുമുമ്പ് power വിച്ഛേദിക്കുക. Header-ലെ സ്ഥാനമല്ല, board-ൽ അച്ചടിച്ച **GPIO നമ്പർ** ഉപയോഗിക്കുക. Breakout-ുകളുടെ pin ക്രമം മാറാം. INMP441-ന് ഇവിടെ 3.3 V നൽകണം; silicon supply പരിധി 1.8–3.3 V ആണ്. L/R ground ചെയ്താൽ firmware പ്രതീക്ഷിക്കുന്ന ഇടത് I2S channel തിരഞ്ഞെടുക്കും.

| Module pin | ബന്ധിപ്പിക്കേണ്ടത് |
|---|---|
| INMP441 VDD | ESP32 3V3 |
| INMP441 GND | പൊതുവായ GND |
| INMP441 SCK / BCLK | GPIO26 |
| INMP441 WS / LRCLK | GPIO25 |
| INMP441 SD | GPIO33 |
| INMP441 L/R | GND — ഇടത് channel |
| MAX98357A VIN | Breakout നിർദേശപ്രകാരമുള്ള അനുയോജ്യ 5 V supply |
| MAX98357A GND | പൊതുവായ GND |
| MAX98357A BCLK | GPIO27 |
| MAX98357A LRC / LRCLK | GPIO14 |
| MAX98357A DIN | GPIO22 |
| MAX98357A SD / EN | യഥാർഥ breakout നിർദേശപ്രകാരം enable ചെയ്യുക |
| Speaker | MAX98357A SPK+, SPK− എന്നിവയിൽ മാത്രം |
| Button | GPIO32-നും GND-നും ഇടയിൽ; internal pull-up firmware പ്രവർത്തനക്ഷമമാക്കും |
| ഐച്ഛിക status LED | അനുയോജ്യ onboard LED ഉണ്ടെന്ന് ഉറപ്പാക്കിയാൽ മാത്രം GPIO2 |

Speaker-ന്റെ രണ്ടു terminal-ുകളും amplifier output ആണ്; ഒന്നും GND-യിൽ ചേർക്കരുത്. Microphone-നോ ESP32 signal pin-നോ 5 V നൽകരുത്. I2S wires ചെറുതാക്കുക. Microphone ദ്വാരം തുറന്നുവയ്ക്കുക; speaker-ൽനിന്ന് അകലം പാലിക്കുക. Headers solder ചെയ്യണം; solder ഇല്ലാതെ ദ്വാരത്തിൽ കുത്തിവച്ച pins വിശ്വസനീയമല്ല.

ആദ്യം board മാത്രം Mac USB വഴി പ്രവർത്തിപ്പിക്കുക. Board/breakout power ക്രമീകരണം ഉറപ്പാക്കിയശേഷം amplifier ചേർക്കുക. Clone board-ന്റെ VIN amplifier-ന് വേണ്ട current നൽകുമെന്ന് കരുതരുത്. USB power-ഉം പുറത്തുനിന്നുള്ള 5 V-ഉം പരിശോധിക്കാതെ കൂട്ടിച്ചേർക്കരുത്. വേറെ supply ഉപയോഗിക്കുന്ന amplifier-ന് ESP32-യുമായി common ground വേണം; USB പരീക്ഷണത്തിൽ ആ external 5 V rail ESP32 5 V rail-ൽ ചേർക്കരുത്. പിന്നീട് അനുയോജ്യമായ ഒരൊറ്റ supply അല്ലെങ്കിൽ പരിശോധിച്ച isolated ക്രമീകരണം തിരഞ്ഞെടുക്കുക. Volume കൂട്ടുന്നതിനുമുമ്പ് brownout കാരണം കണ്ടെത്തുക.

## 6. Firmware compile ചെയ്യുക

Arduino CLI install ചെയ്തശേഷം പരിശോധിച്ച core/library പതിപ്പുകൾ install ചെയ്യുക:

```bash
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli lib install 'ESP8266Audio@2.4.1'
./scripts/compile_firmware.sh
```

ഈ Mac-ൽ Git അവഗണിക്കുന്ന `.tools/arduino-cli` script സ്വയം കണ്ടെത്തും. Script example credentials ഉള്ള temporary sketch compile ചെയ്യുന്നു; യഥാർഥ `config.h` സംരക്ഷിക്കുന്നു; board-ിലേക്ക് upload ചെയ്യുന്നില്ല.

രേഖപ്പെടുത്തിയ classic ESP32 FQBN: `esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M`. Build-ൽ 4 MB തിരഞ്ഞെടുക്കുന്നത് board-ന്റെ യഥാർഥ flash അളക്കുന്നില്ല. Arduino-ESP32 3.x / ESP-IDF 5 standard I2S driver ഉപയോഗിക്കുക; 2.x legacy driver അല്ല.

Arduino IDE-ൽ ESP32 Dev Module തിരഞ്ഞെടുക്കുക. Flash യഥാർഥത്തിൽ 4 MB ആണെന്ന് ഉറപ്പാക്കിയാൽ മാത്രം ആ വലുപ്പം തിരഞ്ഞെടുക്കുക. Partition: No OTA — 2 MB APP / ഏകദേശം 2 MB filesystem. WAV, multipart, MP3 ഫയലുകൾക്കായി കുറഞ്ഞത് 1.5 MB filesystem വേണം. Upload-ന് മുമ്പ് compiler size report പരിശോധിക്കുക. LittleFS ആദ്യ mount-ൽ filesystem format ചെയ്തേക്കാം.

### Hardware ലഭിക്കുമ്പോൾ ക്രമമായി ചെയ്യേണ്ടത്

1. **Board മാത്രം:** Micro-USB data cable വഴി Mac-ൽ ബന്ധിപ്പിക്കുക. `arduino-cli board list`-ൽ `/dev/cu.usbserial-*` അല്ലെങ്കിൽ `/dev/cu.SLAB_USBtoUART` കാണണം. ഇല്ലെങ്കിൽ cable, adapter, CP2102 driver പരിശോധിക്കുക. ആവശ്യമെങ്കിൽ Silicon Labs-ന്റെ ഔദ്യോഗിക driver മാത്രം ഉപയോഗിക്കുക.
2. **Flash തിരിച്ചറിയുക:** `python -m pip install esptool` നടത്തിയശേഷം `python -m esptool --port /dev/cu.<actual-port> flash-id` ഉപയോഗിക്കുക. Placeholder യഥാർഥ port ആയി മാറ്റുക. ആവശ്യമെങ്കിൽ connect സമയത്ത് BOOT അമർത്തിപ്പിടിക്കുക. Chip-ഉം flash capacity-യും രേഖപ്പെടുത്തുക. ചെറിയ flash-ിലേക്ക് 4 MB layout upload ചെയ്യരുത്. Firmware boot-ൽ detected flash bytes കാണിക്കും.
3. **ഭാഗങ്ങൾ പരിശോധിക്കുക:** Microphone pin labels, speaker driver marking, button continuity, solder ചെയ്ത headers, speaker wires എന്നിവ പരിശോധിക്കുക. Amplifier തിരിച്ചറിയുന്നതുവരെ ബന്ധിപ്പിക്കരുത്.
4. **Credentials നൽകുക:** താഴെയുള്ള copy കമാൻഡ് ഉപയോഗിക്കുക. Git അവഗണിക്കുന്ന `config.h`-ൽ മാത്രം 2.4 GHz WiFi credentials-ഉം `SERVER_ORIGIN="http://<Mac-LAN-IP>:8080"`-ഉം നൽകുക. അവസാനം slash വേണ്ട. GPIO2 LED ഉറപ്പാക്കിയില്ലെങ്കിൽ `STATUS_LED=-1` നിലനിർത്തുക. Gemini key board-ിൽ ഇടരുത്.
5. **Compile/upload:** Board, flash, partition വീണ്ടും ഉറപ്പാക്കുക. താഴെയുള്ള കമാൻഡുകളോ Arduino IDE-യോ ഉപയോഗിക്കുക. Serial Monitor 115200-ൽ തുറക്കുക; flash-size, WiFi, Ready സന്ദേശങ്ങൾ പ്രതീക്ഷിക്കാം.
6. **Button + microphone:** പട്ടികപ്രകാരം INMP441-ഉം button-ഉം ബന്ധിപ്പിക്കുക. ഒരിക്കൽ അമർത്തി അഞ്ചു സെക്കൻഡ് Recording സമയത്ത് സംസാരിക്കുക. Request ID-യും backend log-ഉം നോക്കുക. Amplifier ഇല്ലാതെ capture/STT/server MP3 പരിശോധിക്കാം; കേൾക്കാവുന്ന playback പരിശോധിച്ചതായി കണക്കാക്കരുത്.
7. **Amplifier + speaker:** Power off ചെയ്തശേഷം MAX98357A digital pins-ഉം പരിശോധിച്ച supply-ഉം ബന്ധിപ്പിക്കുക. Speaker SPK+/SPK−-ൽ മാത്രം. കുറഞ്ഞ gain-ൽ ഒരു പൂർണ്ണ മലയാളം മറുപടി കേൾക്കുക. Gain കൂട്ടുന്നതിനുമുമ്പ് supply സ്ഥിരതയും noise-ഉം പരിശോധിക്കുക.
8. **Input ക്രമീകരിക്കുക:** INMP441 32-bit slots `MIC_SHIFT=16` ഉപയോഗിച്ച് 16-bit ആക്കുന്നു. ശബ്ദം തീരെ കുറവെങ്കിൽ 15, തുടർന്ന് 14 പരീക്ഷിക്കാം. Clipping ഉണ്ടെങ്കിൽ gain കുറയ്ക്കുക. Software gain മാറ്റുന്നതിനുമുമ്പ് L/R=GND-ഉം soldering-ഉം പരിശോധിക്കുക.
9. **Recovery:** WiFi/internet വിച്ഛേദിച്ച് പിശക് കാണിക്കുന്നുണ്ടോ പരിശോധിക്കുക. ബന്ധം തിരികെവന്നാൽ മുൻ request ID പരിശോധിച്ചശേഷം മാത്രം വീണ്ടും അമർത്തുക. വൈകിയ result duplicate turns ഉണ്ടാക്കരുത്; തെറ്റായ WAV/JSON MP3 ആയി play ചെയ്യരുത്.
10. **തുടർച്ചയായ പരീക്ഷണം:** പത്ത് physical turns നടത്തുക. വ്യക്തത, clipping, I2S വീണ്ടും തുടങ്ങൽ, temporary flash files നീക്കം, power സ്ഥിരത, reset ഇല്ലായ്മ എന്നിവ പരിശോധിക്കുക. യഥാർഥ power bank/network ഉപയോഗിച്ച് വേദിയിലും ആവർത്തിക്കുക.

```bash
test -f firmware/karen_ai/config.h || cp firmware/karen_ai/config.example.h firmware/karen_ai/config.h
arduino-cli compile --fqbn 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M' firmware/karen_ai
arduino-cli upload -p /dev/cu.<actual-port> --fqbn 'esp32:esp32:esp32:PartitionScheme=no_ota,FlashSize=4M' firmware/karen_ai
```

## 7. Local network-ഉം HTTPS-ഉം

Device-ന് Mac-ന്റെ `localhost` ഉപയോഗിക്കാനാവില്ല. രണ്ടും ഒരേ network-ൽ വേണം. Firewall/client isolation പോർട്ട് 8080 തടഞ്ഞേക്കാം. ആദ്യം Mac-ൽ Flask-ഉം text chat-ഉം പരിശോധിക്കുക; തുടർന്ന് ഫോണിൽ Mac LAN URL പരിശോധിച്ചശേഷം device ഉപയോഗിക്കുക.

Cloud HTTPS-ന് കൃത്യമായ hostname-ഉം അതിന്റെ വിശ്വസനീയ root CA PEM `ROOT_CA`-യിലും നൽകണം. Firmware TLS-ന് മുമ്പ് NTP സമയം നേടുകയും `setCACert` ഉപയോഗിക്കുകയും ചെയ്യുന്നു; `setInsecure` ഉപയോഗിക്കുന്നില്ല. Certificate issuer/host രേഖകളിൽനിന്നോ trusted store-ൽനിന്നോ root certificate നേടുക. Chain മാറിയാൽ പുതുക്കുക. യഥാർഥ board-ഉം hostname-ഉം ഇല്ലാതെ TLS/NTP പരിശോധിച്ചതായി കണക്കാക്കരുത്.

Firmware asynchronous multipart WAV അയച്ച് `/requests/<id>` poll ചെയ്യും. ഓരോ HTTP read-നും 15 സെക്കൻഡ്; മൊത്തം polling 160 സെക്കൻഡ്. നഷ്ടപ്പെട്ട upload അതേ ID-യിൽ പരമാവധി ഒരിക്കൽ retry ചെയ്യും. MP3-ന് സ്ഥിരമായ `Content-Length`, `audio/mpeg`, പരമാവധി 512,000 bytes വേണം. Flask നൽകുന്ന ഈ headers proxy-യിലും നിലനിർത്തുക.

## 8. Software പരിശോധനകൾ

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
node --check static/app.js
```

Backend tests fake providers ഉപയോഗിക്കുന്നു; അവ live speech/model നിലവാരം തെളിയിക്കുന്നില്ല. യഥാർഥവും mock ചെയ്തതുമായ പരിശോധനകളുടെ വ്യത്യാസത്തിന് [പരിശോധനാരേഖ](docs/VALIDATION.md) കാണുക.

ഐച്ഛിക live Chrome പരിശോധനയ്ക്ക് Playwright install ചെയ്യുക. `/tmp/karen-audio/question.wav`-ൽ speech fixture വേണം:

```bash
npm install --prefix /tmp/karen-browser playwright
NODE_PATH=/tmp/karen-browser/node_modules node tests/browser.cjs
NODE_PATH=/tmp/karen-browser/node_modules node tests/browser_memory.cjs
```

Memory editor പരിശോധിക്കുമ്പോൾ സ്ഥിരം വിവരങ്ങളുടെ temporary copy ഉപയോഗിക്കുക; യഥാർഥ saved facts test data കൊണ്ട് മാറ്റരുത്.

### 2026 ഒക്ടോബർ 28-ലെ രേഖപ്പെടുത്തിയ ഫലങ്ങൾ

- ആദ്യ backend suite: **18 passed**; വിപുലീകരിച്ച suite: **36 passed**. Language/routes/history/memory/WAV, retry, രഹസ്യവിവരങ്ങൾ നീക്കിയ errors, duplicate/concurrent requests, deadlines, responsive dashboard/health, inference സമയത്തെ reset/memory edit, TTS/oversized audio പരാജയത്തിന് മുമ്പ് history ചേർക്കാതിരിക്കൽ, result retention പരിധി എന്നിവ പരിശോധിച്ചു.
- Python compilation, JavaScript syntax, Git whitespace പരിശോധനകൾ വിജയിച്ചു.
- Temporary memory copy ഉപയോഗിച്ച Chrome പരിശോധനയിൽ fact save ചെയ്തു, live Malayalam chat-ൽ തിരിച്ചുപിടിച്ചു, reset ചെയ്തു, server restart-നുശേഷം fact നിലനിൽക്കുന്നതും history ശൂന്യമാകുന്നതും ഉറപ്പാക്കി. യഥാർഥ `.env`, `data/memory.txt` hashes മാറിയില്ല; key/saved facts പ്രസിദ്ധീകരിച്ചില്ല.
- SDK retries ഇല്ലാതെ യഥാർഥ key model പട്ടിക നൽകി. `gemini-3.8-flash` പട്ടികയിലുണ്ടായിട്ടും 30/60-second ശ്രമങ്ങളിൽ ഏകദേശം 29/59 സെക്കൻഡിൽ 504; മറ്റൊരു ശ്രമത്തിൽ 503. `gemini-3.5-flash-lite` അതേ key-യിൽ 1.2 സെക്കൻഡിൽ മലയാളം മറുപടി നൽകി.
- യഥാർഥ Flask `/test_chat`: creator ചോദ്യം **200 / 1.42 സെക്കൻഡ്**; മഴയെക്കുറിച്ചുള്ള ചോദ്യം **200 / 3.63 സെക്കൻഡ്**. തുടർന്ന് health `ready` ആയി. Diagnostic saved facts/history മാറ്റാതെ വിജയിച്ചു.
- WAV → Google STT → Gemini → gTTS: **200 / ഏകദേശം 4 സെക്കൻഡ് / `X-Karen-Result: ok`**. MP3 103,488 bytes; `afinfo` mono 24 kHz, 12.936-second audio ആയി തിരിച്ചറിഞ്ഞു.
- 390×844 Chrome/Playwright പരിശോധനയിൽ Malayalam text, creator identity, recorder, WAV upload, live providers, MP3 decoding/playback വിജയിച്ചു. ആദ്യം സ്വീകരിച്ച POST-ന്റെ response നഷ്ടപ്പെടുത്തിയിട്ടും അതേ ID-യിൽ recovery വിജയിച്ചു. Audio 8.88–12.576 സെക്കൻഡ്; JavaScript runtime error-ഉം horizontal overflow-ഉം ഉണ്ടായില്ല. Screenshot പരിശോധിച്ചത് `/tmp/karen-audio/mobile-dashboard.png`-ൽ; അത് repository asset അല്ല.
- Input `മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?` എന്ന synthesized speech, `afconvert` വഴി 16 kHz mono 16-bit PCM ആക്കി fake microphone-ൽ നൽകിയതാണ്. Provider calls യഥാർഥമാണ്; മനുഷ്യന്റെ microphone/noise പരിശോധനയല്ല. കേൾവിനിലവാരം മനുഷ്യൻ അംഗീകരിക്കണം.
- Environment: Python 3.14.7, Flask 3.1.3, google-genai 2.33.0, SpeechRecognition 3.17.0, gTTS 2.5.4, pytest 9.2.0. Python 3.14-ൽ aifc compatibility package/typing internals സംബന്ധിച്ച രണ്ട് upstream deprecation warnings ഉണ്ടായിരുന്നു; tests വിജയിച്ചു.
- Firmware cross-compile വിജയിച്ചു: Arduino CLI 1.5.2-rc.1, Arduino-ESP32 **3.3.12**, ESP8266Audio **2.4.1**, classic ESP32 / 4 MB / No OTA target. Program **1,201,296 / 2,097,152 bytes (57%)**; static RAM **49,272 / 327,680 bytes (15%)**; runtime allocation-ന് മുമ്പ് 278,408 bytes ശേഷിച്ചു.
- Example credentials ഉപയോഗിച്ച് multipart upload, async polling, standard digital I2S mic/MP3 playback, optional LED എന്നിവ compile ചെയ്തു. Board upload ചെയ്തിട്ടില്ല; insecure TLS ഉപയോഗിച്ചിട്ടില്ല. Compile വിജയിക്കുന്നത് flash capacity, runtime heap, യഥാർഥ hardware പ്രവർത്തനം എന്നിവ തെളിയിക്കുന്നില്ല.

ഇനിയും പരിശോധിക്കേണ്ടത്: board/module markings, flash, serial/upload, microphone pinout/soldering/gain/noise, button, MAX98357A ലഭ്യത, speaker marking/wires, മനുഷ്യശബ്ദം, speaker quality, brownout, power bank, പത്ത് physical turns, ESP32 WiFi/NTP/TLS/recovery, cloud proxy/storage, വേദിയിലെ network.

## 9. ശാസ്ത്രപ്രദർശനത്തിനുള്ള ഒരുക്കം

### പുറപ്പെടുന്നതിനുമുമ്പ്

- യഥാർഥ board-ൽ compile/upload ചെയ്ത് താഴെയുള്ള acceptance പരിശോധനകൾ പൂർത്തിയാക്കുക.
- Source ZIP, ഏറ്റവും പുതിയ memory text, hotspot credentials, deployment URL എന്നിവയുടെ copy സൂക്ഷിക്കുക.
- Phone-ഉം power bank-ഉം charge ചെയ്യുക. വേദിയിൽ 2.4 GHz hotspot-ഉം mobile data-യും പരിശോധിക്കുക.
- Gemini key/model/quota പരിശോധിക്കുക; key server-ൽ മാത്രം സൂക്ഷിക്കുക.
- Hosted process ഉറങ്ങുന്നില്ലെന്നും URL ലഭ്യമാണെന്നും ESP32 TLS പ്രവർത്തിക്കുന്നെന്നും restart-നുശേഷം സ്ഥിരം ഓർമ്മ നിലനിൽക്കുന്നെന്നും ഉറപ്പാക്കുക.

### നേരിട്ട് പരിശോധിക്കേണ്ട ക്രമം

1. `DEMO_MODE=0` ഉപയോഗിച്ച് server തുടങ്ങി dashboard തുറക്കുക. `/health`-ൽ live/configured-ഉം പ്രതീക്ഷിക്കുന്ന model-ഉം പരിശോധിക്കുക. ആദ്യ inference-ന് മുമ്പ് `untested` സ്വാഭാവികമാണ്. `python scripts/diagnose_gemini.py` നടത്തുക; model പട്ടിക മാത്രം inference തെളിയിക്കുന്നില്ല.
2. `നിന്റെ പേര് എന്താണ്?` എന്ന് ചോദിക്കുക; Karen എന്ന് മലയാളത്തിൽ തിരിച്ചറിയണം.
3. `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` എന്ന് ചോദിക്കുക; ശ്രീഹരി V / നൽകിയ സ്കൂൾവിവരങ്ങൾ പ്രതീക്ഷിക്കാം.
4. Memory തിരുത്തുന്നതിനുമുമ്പ് backup എടുക്കുക. അംഗീകരിച്ച യഥാർഥ fact ചേർത്ത് save ചെയ്ത് അതിനെക്കുറിച്ച് ചോദിക്കുക. പുതിയ fact-ഉം പുതിയ സംഭാഷണവും ഉറപ്പാക്കുക. യഥാർഥ facts test data കൊണ്ട് മാറ്റരുത്.
5. മുൻ മറുപടിയെ പരാമർശിക്കുന്ന തുടർചോദ്യം ചോദിച്ച് context പരിശോധിക്കുക. New chat അമർത്തി history മായുന്നെന്ന് ഉറപ്പാക്കുക.
6. Server restart ചെയ്യുക; പുതിയ സ്ഥിരം fact നിലനിൽക്കണം, session history ശൂന്യമാകണം.
7. Mac localhost-ൽ അഞ്ചു സെക്കൻഡ് മലയാളത്തിൽ സംസാരിച്ച് പൂർണ്ണ MP3 മറുപടി കേൾക്കുക. Permission/HTTPS പരിശോധിക്കുക. Phone LAN HTTP-ൽ സാധാരണ recording സാധ്യമല്ല.
8. ESP32 boot WiFi log പരിശോധിച്ച് button ഉപയോഗിച്ച് അതേ ചോദ്യം റെക്കോർഡ് ചെയ്യുക. Clipping ഇല്ലാത്ത പൂർണ്ണ മറുപടി കേൾക്കണം.
9. Mobile data വിച്ഛേദിച്ച് പിശക് വ്യക്തമായി കാണിക്കുന്നുണ്ടോ പരിശോധിക്കുക; connectivity തിരികെവന്നാൽ recovery പരിശോധിക്കുക. Internet ഇല്ലാത്തപ്പോൾ പുതിയ cloud speech പ്രതീക്ഷിക്കരുത്.
10. പത്ത് തുടർച്ചയായ hardware turns നടത്തി memory pressure, timeout, I2S വീണ്ടും തുടങ്ങൽ, flash cleanup എന്നിവ പരിശോധിക്കുക.

### പ്രദർശനത്തിൽ കാണിക്കാവുന്ന ക്രമം

നിർമാതാവിനെ പരിചയപ്പെടുത്തുക → Karen-നോട് ആരാണ് നിർമ്മിച്ചതെന്ന് ചോദിക്കുക → ശാസ്ത്രചോദ്യം → തുടർചോദ്യം → ഫോണിൽ ഒരു personality fact തിരുത്തുക → അതിനെക്കുറിച്ച് ചോദിക്കുക → ചെറിയ device audio കൈകാര്യം ചെയ്യുന്നതും cloud speech/reasoning ചെയ്യുന്നതും വിശദീകരിക്കുക.

Physical microphone/speaker പരാജയപ്പെട്ടാൽ dashboard text chat ഉപയോഗിക്കുക. Internet മുഴുവൻ നഷ്ടപ്പെട്ടാൽ scripted ആണെന്ന് വ്യക്തമാക്കിയ demo mode-ൽ interface കാണിക്കാം.

### സാധാരണ പ്രശ്നങ്ങളും പരിഹാരവും

| ലക്ഷണം | പരിശോധിക്കേണ്ടത് |
|---|---|
| Setup needed | Server key environment variable; തുടർന്ന് restart |
| AI unavailable | Python console stage/code/provider-code, health അവസാന inference, live diagnostic |
| 504 / `model_timeout` | നിലവിലെ model generation സമയപരിധി കടക്കുന്നുണ്ടോ പരിശോധിക്കുക |
| 503 / `model_unavailable` | താൽക്കാലിക provider/demand പ്രശ്നം; രണ്ട് പരിമിത ശ്രമങ്ങൾ നടന്നിട്ടുണ്ട് |
| 505 | HTTP version പിന്തുണയില്ല; 504-ൽനിന്ന് വ്യത്യസ്തം |
| Response നഷ്ടപ്പെട്ടു | പുതിയ ചോദ്യം അയയ്ക്കുന്നതിനുമുമ്പ് `/requests/<id>` പരിശോധിക്കുക |
| മലയാളം തിരിച്ചറിയുന്നില്ല | Mic channel, ശാന്തമായ സ്ഥലം, gain, mono 16-bit WAV |
| Mic ശൂന്യം / വികൃതം | INMP441 L/R=GND, clock pins, supply |
| Speaker ശബ്ദമില്ല | Amplifier enable/VIN/GND, speaker terminals, pin mapping |
| TLS failure | കൃത്യമായ hostname, root CA, NTP സമയം/connectivity |
| ESP32 brownout/reboot | Supply/current, amplifier wiring, decoupling |
| HTTP 400 | WAV format/duration, multipart field `audio` |
| HTTP 413 | Upload 2 MiB-നേക്കാൾ വലുതാണ് |
| MP3-യ്ക്ക് പകരം JSON | Status/dashboard-ൽ provider error പരിശോധിക്കുക; audio ആയി play ചെയ്യരുത് |
| Page expired | Server restart-നുശേഷം പുതിയ CSRF token-ന് browser refresh ചെയ്യുക |
| Publish ചെയ്തശേഷം memory നഷ്ടം | Ephemeral disk; backup restore ചെയ്യുക അല്ലെങ്കിൽ persistent disk ഉപയോഗിക്കുക |

## 10. പിന്നീട് Cloud-ൽ പ്രവർത്തിപ്പിക്കൽ

ആദ്യം local validation പൂർത്തിയാക്കുക. ഈ നിർദേശങ്ങൾ deployment നടത്തിയെന്നർഥമല്ല. നിലവിലെ Docker ക്രമീകരണം ഒരു worker-ഉം നാല് threads-ഉം ഉപയോഗിക്കുന്നു. History/jobs process-local ആയതിനാൽ **ഒരു instance മാത്രം** ഉപയോഗിക്കുക. വിശ്വസനീയ HTTPS, `MEMORY_PATH`-യ്ക്ക് persistent disk, synchronous client-ുകൾക്കായി കുറഞ്ഞത് 150-second proxy timeout എന്നിവ വേണം. `.env`, `.env.local`, saved memory, firmware credentials എന്നിവ Git-ലും Docker build context-ലും ഉൾപ്പെടുന്നില്ല.

```bash
docker build -t karen-ai .
docker volume create karen-memory
docker run --rm -p 8080:8080 --env-file .env \
  -e GEMINI_MODEL=gemini-3.5-flash-lite -e MEMORY_PATH=/app/data/memory.txt \
  -v karen-memory:/app/data karen-ai
```

Docker ഇല്ലാത്ത persistent host-ൽ:

```bash
gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 4 --timeout 150 'app:create_app()'
```

Replit workspace ഉപയോഗിക്കുന്നുവെങ്കിൽ:

1. Python project ഉണ്ടാക്കി folder ക്രമം നിലനിർത്തി files import ചെയ്യുക.
2. Shell-ൽ `python -m pip install -r requirements.txt` നടത്തുക.
3. Secrets/environment-ൽ `GEMINI_API_KEY`, `GEMINI_MODEL`, `SECRET_KEY`, `DEMO_MODE=0`, `PORT=8080` നൽകുക.
4. `python app.py` നടത്തുക. `.replit`-ൽ port mapping ഉണ്ട്. Replit കാണിക്കുന്ന HTTPS URL ഉപയോഗിക്കുക; public hostname-ന്റെ അവസാനം `:5000` ചേർക്കരുത്.
5. Hardware-ന് മുമ്പ് `/health`, text chat, memory, voice പരിശോധിക്കുക.
6. പ്രദർശനമുഴുവൻ workspace പ്രവർത്തിപ്പിച്ചുവയ്ക്കുക; sleep/restart ലഭ്യത host-നെ ആശ്രയിച്ചിരിക്കുന്നു.

Republish ചെയ്യുമ്പോൾ runtime disk-ലെ memory edits നിലനിൽക്കുമെന്ന് കരുതരുത്. Backup എടുക്കുക; durable hosting-ന് persistent disk വേണം. Ephemeral multi-instance host ഉപയോഗിക്കുന്നതിനുമുമ്പ് database/object-store memory adapter പോലുള്ള പരിഹാരം ആവശ്യമാണ്.

ലോഗിൻ ഇല്ലാത്തതിനാൽ dashboard-ൽ എത്തുന്ന ആർക്കും shared conversation കാണാനും memory തിരുത്താനും API quota ഉപയോഗിക്കാനും കഴിയും. നിയന്ത്രിത exhibition network/ingress ഉപയോഗിക്കുക. CSRF browser forms സംരക്ഷിക്കുന്നതാണ്; authentication അല്ല. `/chat` ESP32-യ്ക്ക് cookies ഇല്ലാതെ ലഭ്യമാണ്. പ്രദർശനം കഴിഞ്ഞാൽ app നിർത്തുകയോ പ്രവേശനം നിയന്ത്രിക്കുകയോ ചെയ്യുക.

Recorded speech Google recognition-ലേക്കും text/history/personality Gemini-യിലേക്കും മറുപടി gTTS-ലേക്കും അയക്കും. പ്രദർശനത്തിൽ സ്വകാര്യ വ്യക്തിവിവരങ്ങൾ ഒഴിവാക്കുക. Server audio ഉദ്ദേശപൂർവം സ്ഥിരമായി save ചെയ്യുന്നില്ല; firmware temporary files നീക്കും. Text history RAM-ലും തിരുത്താവുന്ന സ്ഥിരം facts disk-ലുമാണ്. Firmware flash-ൽ audio buffer ചെയ്യുന്നതിനാൽ സാധാരണ ESP32-യ്ക്ക് PSRAM ആവശ്യമില്ല. Model-നോട് മലയാളത്തിലും ചുരുക്കമായും മറുപടി നൽകാൻ നിർദേശിച്ചിട്ടുണ്ടെങ്കിലും അത് പൂർണ്ണമായി ഉറപ്പാക്കാനാവില്ല. Speech providers-ന് internet വേണം; അവയുടെ ലഭ്യതയും quota-യും ഈ പ്രോജക്ടിന്റെ നിയന്ത്രണത്തിലല്ല.

## 11. Windows PC-യും HW678 / ESP32-S3 N16R8 board-ഉം

പുതിയ Windows നിർദേശങ്ങളുടെ English പതിപ്പ് [docs/WINDOWS.md](docs/WINDOWS.md)-ലുണ്ട്. ചിത്രങ്ങളിൽ HW678 PCB, Sixspan **S3-N16R8** module, **COM**, **USB** എന്നിങ്ങനെ അടയാളപ്പെടുത്തിയ രണ്ട് USB-C ports, onboard RGB LED എന്നിവ കാണുന്നു. S3 profile 16 MB flash / 8 MB octal PSRAM ലക്ഷ്യമിടുന്നു; label മാത്രം capacity അളന്നതിന്റെ തെളിവല്ല. Mac cross-compile രേഖപ്പെടുത്തിയിട്ടുണ്ട്; Windows commands, physical upload എന്നിവ യഥാർഥ PC/board-ൽ പരിശോധിക്കണം.

### Windows-ൽ backend തുടങ്ങുക

പുതുക്കിയ source folder ഉപയോഗിക്കുക. Repository private ആണ്; അംഗീകൃത checkout/source copy വേണം. PR #1 തുറന്നിരിക്കുമ്പോൾ updates `fix/gemini-diagnostics-and-commissioning` branch-ലാണ്; merge കഴിഞ്ഞാൽ പുതുക്കിയ default branch ഉപയോഗിക്കാം. Git-ൽ സ്വകാര്യ `.env`, memory, WiFi configuration എന്നിവ ലഭിക്കില്ല. Python 3.12 ഔദ്യോഗിക distribution install ചെയ്യുക. PowerShell-ൽ ഉദാഹരണ path സ്വന്തം folder ആയി മാറ്റുക:

```powershell
Set-Location C:\Projects\karen-ai
if (-not (Test-Path .venv)) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Gemini key പ്രാദേശികമായി `.env`-ൽ നൽകുക. മുകളിലെ പൊതുവായ ക്രമീകരണങ്ങൾക്കൊപ്പം ഇവ നൽകുക:

```dotenv
GEMINI_MODEL=gemini-3.5-flash-lite
KAREN_CONTROLLER=esp32_s3
DEMO_MODE=0
PORT=8080
```

നിലവിലുള്ള `.env`, `.env.local`, `data/memory.txt`, `config.h` എന്നിവ overwrite ചെയ്യരുത്. മുൻഗണന shell → `.env.local` → `.env`; `--controller` നൽകിയാൽ അതിന് മുൻഗണന. `esp32` classic board-നും `esp32_s3` പുതിയ S3 board-നും. Controller മാറ്റം firmware build സമയത്താണ്; Flask restart ചെയ്താൽ board-ലെ firmware മാറില്ല. Rebuild/upload വേണം. അറിയാത്ത controller പേര് നൽകിയാൽ helper പിശക് കാണിക്കും.

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_gemini.py
.\.venv\Scripts\python.exe app.py
```

Chrome/Edge-ൽ **http://localhost:8080** തുറന്ന് മലയാളം text, തുടർന്ന് microphone permission/അഞ്ചു സെക്കൻഡ് recorder പരിശോധിക്കുക. Python പിശകുകൾ അതേ PowerShell-ൽ കാണാം; അത് തുറന്നുവയ്ക്കുക. ബാക്കി steps-ന് മറ്റൊരു PowerShell window ഉപയോഗിക്കുക. `.venv` Python നേരിട്ട് വിളിക്കുന്നതിനാൽ activation script/execution policy മാറ്റേണ്ടതില്ല.

### Arduino CLI install ചെയ്ത് controller തിരഞ്ഞെടുക്കുക

[ഔദ്യോഗിക Arduino CLI installation page](https://arduino.github.io/arduino-cli/latest/installation/)-ൽനിന്ന് Windows ZIP എടുത്ത് project-ലെ `.tools\arduino-cli.exe` ആയി extract ചെയ്യുക. `.tools` ഇല്ലെങ്കിൽ സൃഷ്ടിക്കുക; Git അത് അവഗണിക്കുന്നു. പകരം PATH-ൽ install ചെയ്യുകയോ `ARDUINO_CLI`-ൽ executable-ന്റെ പൂർണ്ണ path നൽകുകയോ ചെയ്യാം.

```powershell
$karenArduinoCli = Join-Path (Get-Location) '.tools\arduino-cli.exe'
& $karenArduinoCli version
& $karenArduinoCli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
& $karenArduinoCli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
& $karenArduinoCli lib install 'ESP8266Audio@2.4.1'
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py
```

Core download വലുതാണ്; പൂർത്തിയാകുന്നതുവരെ കാത്തിരിക്കുക. Classic board-ന് `$env:KAREN_CONTROLLER = 'esp32'` ആക്കി അതേ helper നടത്തുക. `Remove-Item Env:KAREN_CONTROLLER` shell override നീക്കും. ഒരു കമാൻഡിന് മാത്രം `--controller esp32_s3` ഉപയോഗിക്കാം.

Mac/Linux-ലും പുതിയ helper ഉപയോഗിക്കാം:

```bash
KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py
```

സാധാരണ build example credentials ഉപയോഗിക്കുന്നു; upload ചെയ്യില്ല. Temporary sketch/binary നീക്കും; private `config.h` സംരക്ഷിക്കും. `--use-config` private configuration compile ചെയ്യുന്നു. Compiler output-ൽ WiFi credential definitions/അറിയാവുന്ന secret values മറയ്ക്കുന്നു. പഴയ `./scripts/compile_firmware.sh` wrapper-ഉം ലഭ്യമാണ്; controller നൽകാത്തപ്പോൾ classic `esp32` ആണ് default.

### COM port കണ്ടെത്തി flash ഉറപ്പാക്കുക

1. ആദ്യം controller മാത്രം USB-C **data** cable വഴി പിന്നിൽ **COM** എന്ന് എഴുതിയ connector-ൽ ബന്ധിപ്പിക്കുക. മറ്റേത് native USB/USB-OTG ആണ്. ഈ profile upload/Serial Monitor-ന് COM/UART ഉപയോഗിക്കുന്നു; USB CDC on boot disabled ആണ്.
2. Device Manager → Ports (COM & LPT) അല്ലെങ്കിൽ താഴെയുള്ള board list ഉപയോഗിച്ച് യഥാർഥ port കണ്ടെത്തുക. COM5 ഉദാഹരണം മാത്രം. Port ഇല്ലെങ്കിൽ ആദ്യം cable പരിശോധിക്കുക. Bridge marking/Hardware IDs തിരിച്ചറിഞ്ഞശേഷം മാത്രം അനുയോജ്യ manufacturer driver install ചെയ്യുക; CP2102 ആണെന്ന് കരുതരുത്.
3. താഴെ COM5 സ്വന്തം port ആയി മാറ്റി flash പരിശോധിക്കുക. ESP32-S3 / 16 MB പ്രതീക്ഷിക്കുന്നു. വ്യത്യാസമുണ്ടെങ്കിൽ ശരിയായ board configuration ഉറപ്പാക്കിയശേഷം തുടരുക. Flash ചെയ്യുന്നതിനുമുമ്പ് Serial Monitor അടയ്ക്കുക. Bootloader സ്വയം പ്രവർത്തിച്ചില്ലെങ്കിൽ BOOT പിടിച്ച് RST ഒന്നു അമർത്തി operation തുടങ്ങി connecting സമയത്ത് BOOT വിടുക. BOOT ചോദ്യം ചോദിക്കാനുള്ള button അല്ല.

```powershell
& $karenArduinoCli board list
.\.venv\Scripts\python.exe -m pip install esptool
.\.venv\Scripts\python.exe -m esptool --port COM5 flash-id
```

### WiFi ക്രമീകരിച്ച് upload ചെയ്യുക

```powershell
if (-not (Test-Path firmware\karen_ai\config.h)) {
    Copy-Item firmware\karen_ai\config.example.h firmware\karen_ai\config.h
}
notepad firmware\karen_ai\config.h
```

`WIFI_SSID`, `WIFI_PASSWORD` എന്നിവയിൽ 2.4 GHz network നൽകുക. `SERVER_ORIGIN` ഉദാഹരണം `http://192.168.1.50:8080`; അവസാനം slash വേണ്ട. Backend PC-യിൽ `ipconfig` വഴി active adapter IPv4 കണ്ടെത്തുക. Backend Mac-ലാണെങ്കിൽ Mac LAN IP ഉപയോഗിക്കുക. Device-ന് PC-യുടെ `localhost` ഉപയോഗിക്കാനാവില്ല. Board-ഉം backend-ഉം പരസ്പരം എത്താവുന്ന LAN-ൽ വേണം. Windows Firewall ചോദിച്ചാൽ private exhibition network-ൽ Python server അനുവദിക്കുക; inbound TCP 8080 വേണ്ടിവന്നേക്കാം. Firewall മുഴുവനായി off ചെയ്യരുത്.

`STATUS_LED=-1` നിലനിർത്തുക; RGB LED-യ്ക്ക് പ്രത്യേക driver വേണം. Classic `config.h` S3-ലേക്ക് മാറ്റുമ്പോൾ WiFi/root CA സംരക്ഷിച്ച് പഴയ `MIC_*`, `AMP_*`, `BUTTON_PIN` overrides നീക്കുക; S3 adapter defaults നൽകും. Unsafe pins compile സമയത്ത് നിരസിക്കും. Gemini key backend-ൽ മാത്രം.

```powershell
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py --use-config
# COM5 യഥാർഥ port ആയി മാറ്റുക:
.\.venv\Scripts\python.exe scripts\firmware.py --upload --port COM5
& $karenArduinoCli monitor --port COM5 --config baudrate=115200
```

`--upload` ആദ്യം private configuration compile ചെയ്യും; explicit port വേണം. മാറ്റാത്ത example WiFi values അനുവദിക്കില്ല; compile പരാജയപ്പെട്ടാൽ upload നിർത്തും. Port സ്വയം തിരഞ്ഞെടുക്കില്ല. CLI upload സമയത്ത് chip family പരിശോധിക്കുന്നു. ആദ്യ upload-ൽ amplifier ബന്ധിപ്പിക്കരുത്.

Boot log-ൽ `Controller: esp32_s3`, അളന്ന flash/PSRAM bytes, pins, WiFi, Ready എന്നിവ കാണണം. പ്രതീക്ഷിക്കുന്ന flash **16,777,216 bytes**, PSRAM **8,388,608 bytes**; യഥാർഥ board-ൽ ഉറപ്പാക്കണം. നിലവിലെ No OTA layout 2 MB app / ഏകദേശം 2 MB filesystem ഉപയോഗിക്കുന്നു; അധിക flash ഉപയോഗിക്കുന്നില്ല.

### S3-യ്ക്ക് മാത്രം ഉള്ള wiring

Power off ചെയ്ത് GPIO label നോക്കി ബന്ധിപ്പിക്കുക. മുകളിലെ classic table S3-യ്ക്ക് ഉപയോഗിക്കരുത്.

| Signal | ESP32-S3 connection |
|---|---|
| INMP441 VDD / GND | 3V3 / GND |
| INMP441 BCLK/SCK | GPIO4 |
| INMP441 WS | GPIO5 |
| INMP441 SD | GPIO6 |
| INMP441 L/R | GND — ഇടത് channel |
| MAX98357A BCLK | GPIO16 |
| MAX98357A LRC / WS | GPIO17 |
| MAX98357A DIN | GPIO18 |
| MAX98357A VIN / GND | അനുയോജ്യ 5 V / common GND |
| പുറത്തുള്ള momentary question button | GPIO7 മുതൽ GND വരെ; internal pull-up |
| Speaker | SPK+ / SPK− മാത്രം |

Classic 26/25/33/27/14/22/32 wiring ഇവിടെ പകർത്തരുത്. GPIO35–37 octal PSRAM ഉപയോഗിക്കുന്നു. Adapter USB 19/20, flash pins, boot straps, serial-console pins, സാധ്യതയുള്ള RGB pins എന്നിവ ഒഴിവാക്കുന്നു. Reserved/overlapping pins, പിന്തുണയില്ലാത്ത chips എന്നിവ compile-time checks നിരസിക്കുന്നു. Controller ചിത്രങ്ങൾ microphone/amplifier pinout-ഉം speaker marking-ഉം തെളിയിക്കുന്നില്ല; അവ പ്രത്യേകം പരിശോധിക്കുക. മുകളിലെ commissioning, low gain, power/recovery, പത്ത് physical turns എന്നിവ പൂർത്തിയാക്കുക. MAX98357A I2S തന്നെയാണ് amplifier.

### Arduino IDE പകരം ഉപയോഗിക്കുമ്പോൾ

`KAREN_CONTROLLER` വായിക്കുന്നത് Python helper ആണ്. IDE-ൽ Tools → Board തിരഞ്ഞെടുപ്പനുസരിച്ച് adapter മാറും. `firmware/karen_ai/karen_ai.ino` തുറന്ന് private `config.h` തയ്യാറാക്കി യഥാർഥ COM port തിരഞ്ഞെടുക്കുക. Chip target തെറ്റായിരിക്കുമ്പോൾ pins മാത്രം മാറ്റരുത്.

| ക്രമീകരണം | S3 board | Classic board |
|---|---|---|
| Board | ESP32S3 Dev Module | ESP32 Dev Module |
| Flash | ഉറപ്പാക്കിയശേഷം 16 MB | ഉറപ്പാക്കിയശേഷം 4 MB |
| PSRAM | OPI PSRAM | Disabled / യഥാർഥ module അനുസരിച്ച് |
| Flash mode | QIO 80 MHz | Core default |
| Partition | No OTA — 2 MB APP / 2 MB filesystem | അതേ ക്രമീകരണം |
| USB CDC on boot | Disabled; COM/UART ഉപയോഗിക്കുക | ബാധകമല്ല |
| ആദ്യ upload speed | 115200 | 115200 |

റഫറൻസുകൾ: [Arduino installation](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html), [S3 DevKitC interfaces](https://docs.espressif.com/projects/esp-idf/en/v4.4.8/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html), [S3 module memory pin നിയന്ത്രണങ്ങൾ](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf). DevKitC reference HW678 clone-ന്റെ അതേ circuit ആണെന്ന തെളിവല്ല.

## 12. കൂടുതൽ വിവരങ്ങൾ

- [English README](README.md)
- [Hardware wiring, commissioning](docs/HARDWARE.md)
- [പ്രദർശന checklist](docs/EXHIBITION.md)
- [പരിശോധനാഫലങ്ങളും പരിധികളും](docs/VALIDATION.md)
- [Gemini troubleshooting](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [Google model shutdown വിവരം](https://firebase.google.com/docs/ai-logic/faq-and-troubleshooting)
- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition), [gTTS](https://gtts.readthedocs.io/)
- [HTTP status നിർവചനങ്ങൾ](https://www.rfc-editor.org/rfc/rfc9110.html)
- [INMP441 datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [MAX98357A specifications](https://www.analog.com/en/products/max98357a.html)
- [Espressif DevKitC power guidance](https://docs.espressif.com/projects/esp-idf/en/v4.4/esp32/hw-reference/esp32/get-started-devkitc.html) — പൊതുവായ മാർഗനിർദേശം; clone board-ന്റെ circuit ഇതുതന്നെയാണെന്ന തെളിവല്ല
- [ESP-IDF standard I2S](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/i2s.html)
- [ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio)
