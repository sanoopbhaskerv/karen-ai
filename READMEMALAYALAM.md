# Karen AI — ഓരോ ഘട്ടമായി പഠിക്കാം

**[Read this guide in English → README.md](README.md)**

Windows + S3-N16R8 wiring call-ന് [ആദ്യ കോൾ ഗൈഡ് (English)](docs/FIRST_CALL_WINDOWS.md) ഉപയോഗിക്കുക. ഓരോ ഘട്ടത്തിന്റെയും commands, wiring, പ്രതീക്ഷിക്കേണ്ട logs, stop/go checks അതിലുണ്ട്. ഇപ്പോഴത്തെ kit **main** branch-ൽ നിന്ന് download ചെയ്യുക.

**ശ്രീഹരി V, ക്ലാസ് 9S, PKMMHSS എടരിക്കോട്** എന്ന വിദ്യാർത്ഥിയുടെ ശാസ്ത്രപ്രദർശന പ്രോജക്ടാണ് മലയാളത്തിൽ സംസാരിക്കുന്ന Karen AI. ആദ്യമായി ഇത് ഉപയോഗിക്കുന്ന ഒരാൾക്കുവേണ്ടിയാണ് ഈ ഗൈഡ്. കോഡ് മുഴുവൻ മനസ്സിലാക്കിയ ശേഷമേ തുടങ്ങാവൂ എന്നില്ല. ഒരു ഘട്ടം ശരിയായെന്ന് ഉറപ്പാക്കിയശേഷം അടുത്തതിലേക്ക് പോകുക.

**ആദ്യം കമ്പ്യൂട്ടറിൽ പ്രവർത്തിപ്പിക്കുക. അത് ശരിയായ ശേഷമാണ് മൈക്രോഫോണും സ്പീക്കറും ബന്ധിപ്പിക്കേണ്ടത്.** 2 മുതൽ 9 വരെയുള്ള ഘട്ടങ്ങൾക്ക് ഇലക്ട്രോണിക് ഭാഗങ്ങൾ ബന്ധിപ്പിക്കേണ്ടതില്ല.

## എളുപ്പമുള്ള setup kit — ആദ്യം ഇത് ഉപയോഗിക്കാം

ആദ്യം project extract ചെയ്ത് Python ഒരിക്കൽ install ചെയ്യുക (താഴെയുള്ള ഘട്ടങ്ങൾ 2–3). ശേഷം Windows-ൽ **`bootstrap-windows.cmd`**, Mac-ൽ **`bootstrap-mac.command`** double-click ചെയ്യുക. ആദ്യം computer-only setup തിരഞ്ഞെടുക്കാം. വേണമെങ്കിൽ S3/classic board tools കൂടി ഒരുക്കാം. Private settings-ഉം saved memory-യും സംരക്ഷിക്കും.

PowerShell / Terminal വഴി തുടങ്ങാനും കഴിയും:

```powershell
.\bootstrap-windows.cmd
```

```bash
bash bootstrap-mac.command
```

Setup കഴിഞ്ഞ് `.env`-ൽ Gemini key ഇല്ലെങ്കിൽ സ്വകാര്യമായി നൽകുക (ഘട്ടം 5). ദിവസവും server തുടങ്ങാൻ command ടൈപ്പ് ചെയ്യുന്നതിനുപകരം യോജിച്ച launcher ഉപയോഗിക്കാം:

```powershell
.\start-windows.cmd
```

```bash
bash start-mac.command
```

**http://localhost:8080** തുറന്ന് ഘട്ടങ്ങൾ 6–7 പിന്തുടരുക. Setup board tools install ചെയ്തെങ്കിൽ project folder-ൽ രണ്ടാമത്തെ PowerShell തുറക്കുക (Window B). ഘട്ടം 8-ലെ manual downloads ഒഴിവാക്കി ഘട്ടം 9-ലേക്ക് പോകാം. Port/monitor commands tools സ്വയം കണ്ടെത്തും. ഒരു server പ്രവർത്തിക്കുമ്പോൾ രണ്ടാമത്തേത് തുടങ്ങരുത്. Kit സ്വയം firmware upload ചെയ്യുകയോ Gemini key പരിശോധിക്കുകയോ ചെയ്യുന്നില്ല. [രണ്ട് ഭാഷകളിലുമുള്ള bootstrap options/recovery](docs/BOOTSTRAP.md) നോക്കുക. താഴെ പഴയപോലെ 18 ഘട്ടങ്ങളുള്ള manual വഴിയും ഉണ്ട്.

## 1. ഓരോ ഭാഗവും എന്താണ് ചെയ്യുന്നത്?

| പേര് | ലളിതമായ അർത്ഥം |
|---|---|
| Backend / server | കമ്പ്യൂട്ടറിൽ പ്രവർത്തിക്കുന്ന Python പ്രോഗ്രാം. Karen ഉപയോഗിക്കുമ്പോൾ ഇത് തുറന്നിരിക്കണം. |
| Dashboard | ബ്രൗസറിൽ തുറക്കുന്ന Karen പേജ്. ഇവിടെ ചോദ്യം ടൈപ്പ് ചെയ്യാം, റെക്കോർഡ് ചെയ്യാം, ഓർമ്മയിൽ സൂക്ഷിക്കുന്ന വിവരങ്ങൾ തിരുത്താം. |
| ESP32 controller | ശബ്ദം റെക്കോർഡ് ചെയ്യുകയും മറുപടി പ്ലേ ചെയ്യുകയും ചെയ്യുന്ന ചെറിയ ബോർഡ്. ഇത് WiFi വഴി കമ്പ്യൂട്ടറുമായി ബന്ധപ്പെടും. |
| Firmware | ബോർഡിനുള്ളിൽ ഇടുന്ന പ്രോഗ്രാം. |
| Compile / build | കോഡ് പരിശോധിച്ച് ബോർഡിന് പ്രവർത്തിപ്പിക്കാൻ പറ്റുന്ന ഫയലാക്കുക. ഇതുകൊണ്ടുമാത്രം കോഡ് ബോർഡിൽ എത്തില്ല. |
| Upload / flash | തയ്യാറാക്കിയ പ്രോഗ്രാം USB വഴി ബോർഡിലേക്ക് പകർത്തുക. |
| API key | Backend-ന് Gemini ഉപയോഗിക്കാൻ അനുവദിക്കുന്ന രഹസ്യ പാസ്‌വേഡ് പോലെയുള്ള key. മറ്റുള്ളവർക്ക് കാണിക്കരുത്. |
| COM port | USB-യിൽ ബന്ധിപ്പിച്ച ബോർഡിന് Windows നൽകുന്ന പേര്. ഉദാഹരണം COM5. നിങ്ങളുടെ നമ്പർ വേറെയാകാം. |
| GPIO | ബോർഡിലെ നമ്പറിട്ട signal pin. വരിയിൽ എത്രാമത്തെ pin എന്നല്ല, ബോർഡിൽ എഴുതിയ നമ്പറാണ് ഉപയോഗിക്കേണ്ടത്. |

എല്ലാം ബന്ധിപ്പിച്ചുകഴിഞ്ഞാൽ പ്രവർത്തനം ഇങ്ങനെയാണ്:

```text
നിങ്ങളുടെ ശബ്ദം → മൈക്രോഫോൺ → ബോർഡ് → കമ്പ്യൂട്ടർ + ഇന്റർനെറ്റ്
                → മലയാളം മറുപടി → ബോർഡ് → ആംപ്ലിഫയർ → സ്പീക്കർ
```

Upload ചെയ്തുകഴിഞ്ഞാലും കമ്പ്യൂട്ടർ വേണം. ബോർഡ് ഒറ്റയ്ക്ക് Gemini പ്രവർത്തിപ്പിക്കുന്നില്ല. യഥാർഥ AI മറുപടി, ശബ്ദം തിരിച്ചറിയൽ, മറുപടി ശബ്ദമാക്കൽ എന്നിവയ്ക്ക് ഇന്റർനെറ്റ് വേണം. ഫോൺ hotspot ഉപയോഗിക്കാം; ബോർഡിന് 2.4 GHz WiFi വേണം.

### നിങ്ങളുടെ ബോർഡ് ഏതാണ്?

| ബോർഡിൽ / module-ൽ കാണുന്ന പേര് | ഉപയോഗിക്കേണ്ട setting |
|---|---|
| HW678 ബോർഡ്; Sixspan S3-N16R8 എന്ന് എഴുതിയ module; രണ്ട് USB-C sockets | `KAREN_CONTROLLER=esp32_s3` — നിങ്ങൾ അയച്ച ചിത്രങ്ങളിലെ ബോർഡ് ഇതാണ് |
| ആദ്യം പറഞ്ഞ classic ESP32; 38 pins; Micro-USB | `KAREN_CONTROLLER=esp32` |

താഴെയുള്ള പ്രധാന നിർദേശങ്ങൾ **ചിത്രത്തിലെ S3 ബോർഡിനാണ്**. രണ്ട് ബോർഡുകൾക്കും ഒരേ Python backend മതി. എന്നാൽ മൈക്രോഫോൺ, ആംപ്ലിഫയർ, button എന്നിവയുടെ GPIO നമ്പറുകൾ വ്യത്യസ്തമാണ്.

### ഹാർഡ്‌വെയർ ഘട്ടത്തിന് വേണ്ട സാധനങ്ങൾ

Controller, USB **data** cable, INMP441 മൈക്രോഫോൺ, MAX98357A I2S ആംപ്ലിഫയർ, passive speaker, പുറത്തു ബന്ധിപ്പിക്കുന്ന momentary push button, വയറുകൾ എന്നിവ വേണം. Charging മാത്രം ചെയ്യുന്ന cable ഉപയോഗിച്ച് upload ചെയ്യാൻ കഴിയില്ല. ആംപ്ലിഫയർ ഇനിയും വാങ്ങാനുണ്ടെങ്കിൽ ആദ്യം കമ്പ്യൂട്ടറിലെയും മൈക്രോഫോണിലെയും പരിശോധനകൾ ചെയ്യാം.

Soldering ചെയ്യാനും amplifier power ബന്ധിപ്പിക്കാനും മുതിർന്ന ഒരാളുടെ സഹായം തേടുക. വയറുകൾ മാറ്റുന്നതിനുമുമ്പ് power അഴിക്കുക. മൈക്രോഫോണിന് **3.3 V** മാത്രം നൽകുക; 5 V കൊടുക്കരുത്. സ്പീക്കർ നേരിട്ട് controller pin-ൽ ബന്ധിപ്പിക്കരുത്.

## 2. പ്രോജക്ട് ഫോൾഡറും PowerShell-ഉം തുറക്കുക

1. പ്രോജക്ട് ഉടമയിൽനിന്ന് പുതുക്കിയ project folder വാങ്ങുക. ZIP ആണെങ്കിൽ അതിൽ right-click ചെയ്ത് **Extract All** തിരഞ്ഞെടുക്കുക. ZIP-ന്റെ ഉള്ളിൽനിന്ന് നേരിട്ട് പ്രോഗ്രാം പ്രവർത്തിപ്പിക്കരുത്.
2. Extract ചെയ്ത ഫോൾഡർ തുറക്കുക. അവിടെ `app.py`, `requirements.txt`, `README.md`, `scripts`, `firmware` എന്നിവ കാണണം.
3. Extract ചെയ്ത ഫോൾഡറിനുള്ളിൽ മറ്റൊരു ഫോൾഡർ ഉണ്ടാകാം. `app.py` കാണുന്നതുവരെ ശരിയായത് തുറക്കുക.
4. File Explorer-ന്റെ മുകളിലുള്ള address bar-ൽ ക്ലിക്ക് ചെയ്യുക. അവിടെ `powershell` എന്ന് ടൈപ്പ് ചെയ്ത് Enter അമർത്തുക. ആ ഫോൾഡറിൽ PowerShell തുറക്കും.
5. താഴെയുള്ള command **PowerShell-ൽ** paste ചെയ്ത് Enter അമർത്തുക:

```powershell
Test-Path .\app.py
```

**ശരിയായോ എന്ന് പരിശോധിക്കുക:** `True` എന്ന് വരണം. `False` ആണെങ്കിൽ നിങ്ങൾ ശരിയായ ഫോൾഡറിലല്ല. അത് ശരിയാക്കിയ ശേഷം മാത്രം മുന്നോട്ടുപോകുക.

`powershell` എന്ന് അടയാളപ്പെടുത്തിയ പെട്ടികളിലെ commands PowerShell-ലാണ് നൽകേണ്ടത്. ബ്രൗസറിലോ `>>>` കാണിക്കുന്ന Python window-യിലോ അല്ല. ഓരോ command-ഉം നൽകിയ ശേഷം അത് തീരാൻ കാത്തിരിക്കുക. `{`-ഉം `}`-ഉം ഉള്ള ഒരു block മുഴുവനായും paste ചെയ്യാം.

GitHub repository private ആണ്. Access ഉള്ള account ഉപയോഗിച്ച് ഇപ്പോഴത്തെ **main** branch download ചെയ്യുക, അല്ലെങ്കിൽ അതിന്റെ ZIP ഉടമയോട് വാങ്ങുക. Setup-നും തുടർന്നുള്ള updates-നും main ഉപയോഗിക്കുക.

ഇതിനകം പ്രവർത്തിക്കുന്ന project folder ഉണ്ടെങ്കിൽ അതിലെ `.env`, `.env.local`, `data/memory.txt`, `firmware/karen_ai/config.h` എന്നിവ സൂക്ഷിക്കുക. അവയ്ക്കു മുകളിൽ blank example files പകർത്തരുത്.

## 3. Python ഒരിക്കൽ install ചെയ്യുക

പുതിയ Windows setup-ന് **Python 3.14** ഉപയോഗിക്കുക. പരിശോധിച്ച Mac environment-ലും ഈ Python series ആണ് ഉപയോഗിക്കുന്നത്. ഇതിനകം Python 3.12 virtual environment ശരിയായി പ്രവർത്തിക്കുന്നുണ്ടെങ്കിൽ അത് മാറ്റേണ്ടതില്ല.

**ഈ Windows PC-യിൽ ഇതിനകം പ്രവർത്തിക്കുന്ന `.venv` ഉണ്ടോ?** ഉണ്ടെങ്കിൽ താഴെയുള്ള installer-ഉം `py -3.14` പരിശോധനയും വിട്ട് ഘട്ടം 4-ലേക്ക് പോകാം. അവിടത്തെ creation command നിലവിലുള്ള `.venv` മാറ്റില്ല.

1. [Python-ന്റെ ഔദ്യോഗിക Windows download പേജ്](https://www.python.org/downloads/windows/) തുറക്കുക.
2. നിലവിലുള്ള ഒരു **Python 3.14.x** release തിരഞ്ഞെടുക്കുക. സാധാരണ Intel/AMD Windows PC ആണെങ്കിൽ **Windows installer (64-bit)** എടുക്കുക. സാധാരണ installer ആണ് വേണ്ടത്; embeddable ZIP അല്ല, source code അല്ല. ARM കമ്പ്യൂട്ടറാണെങ്കിൽ ശരിയായ installer തിരഞ്ഞെടുക്കാൻ മുതിർന്ന ഒരാളുടെ സഹായം തേടുക.
3. Installer തുറക്കുക. **Add python.exe to PATH** എന്ന option കാണുന്നുണ്ടെങ്കിൽ tick ചെയ്യുക. **Install Now** അമർത്തുക. Python launcher install ചെയ്യാൻ അനുവദിക്കുക.
4. PowerShell അടയ്ക്കുക. ഘട്ടം 2 പോലെ project folder-ൽ വീണ്ടും PowerShell തുറക്കുക.
5. ഇത് നൽകുക:

```powershell
py -3.14 --version
```

**പരിശോധിക്കുക:** `Python 3.14`-നുശേഷം ഒരു patch number കാണണം. `py` തിരിച്ചറിയുന്നില്ലെങ്കിൽ PowerShell വീണ്ടും തുറന്ന് നോക്കുക. Python-ഉം launcher-ഉം install ആയോ എന്ന് പരിശോധിക്കുക. ഇത് പ്രവർത്തിക്കാതെ അടുത്ത ഘട്ടത്തിലേക്ക് പോകരുത്.

## 4. പ്രോജക്ടിന് വേണ്ട Python packages install ചെയ്യുക

ഈ പ്രോജക്ടിന് മാത്രം packages സൂക്ഷിക്കുന്ന സ്ഥലമാണ് virtual environment. അതിന്റെ ഫോൾഡർ `.venv` ആണ്. Mac-ലെ `.venv` Windows-ലേക്ക് പകർത്തരുത്. ഓരോ കമ്പ്യൂട്ടറിലും അതത് `.venv` ഉണ്ടാക്കണം.

```powershell
if (-not (Test-Path .venv)) { py -3.14 -m venv .venv }
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Download-ന് കുറച്ച് മിനിറ്റ് വേണ്ടിവരാം. ഇന്റർനെറ്റ് ബന്ധം നിലനിർത്തുക. PowerShell-ന്റെ prompt തിരിച്ചുവരുന്നതുവരെ കാത്തിരിക്കുക. അവസാനം installation error കാണുന്നുണ്ടെങ്കിൽ അത് ശരിയാക്കണം.

**പരിശോധിക്കുക:** താഴെയുള്ള command Python version കാണിക്കണം:

```powershell
.\.venv\Scripts\python.exe --version
```

ഇനിയുള്ള Windows commands-ൽ ഈ `.venv` Python path ഉപയോഗിക്കുക. വേറെ activation script പ്രവർത്തിപ്പിക്കുകയോ PowerShell execution policy മാറ്റുകയോ വേണ്ട.

## 5. കമ്പ്യൂട്ടറിന്റെ settings file തയ്യാറാക്കുക

`.env` ഇല്ലെങ്കിൽ മാത്രം അത് ഉണ്ടാക്കുക:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

തുറക്കാൻ:

```powershell
notepad .env
```

ചിത്രത്തിലെ S3 ബോർഡിന് പ്രധാന വരികൾ താഴെപ്പറയുന്നതുപോലെയാകണം. **`PASTE_YOUR_PRIVATE_KEY_HERE` എന്നത് മാറ്റി യഥാർഥ Gemini API key നൽകണം. ആ example വാക്കുകൾ അതേപടി വിടരുത്.** Google account-ന്റെ password അല്ല ഇവിടെ നൽകേണ്ടത്.

```dotenv
GEMINI_API_KEY=PASTE_YOUR_PRIVATE_KEY_HERE
GEMINI_MODEL=gemini-3.5-flash-lite
DEMO_MODE=0
PORT=8080
MEMORY_PATH=data/memory.txt
KAREN_CONTROLLER=esp32_s3
```

മറ്റുള്ള പഴയ വരികൾ മായ്ക്കരുത്. നിലവിലുള്ള `SECRET_KEY` മാറ്റേണ്ടതില്ല. Local testing-ൽ അത് blank ആണെങ്കിൽ app സ്വയം ഒന്ന് ഉണ്ടാക്കും. Server restart ചെയ്തശേഷം browser page refresh ചെയ്യേണ്ടിവരാം.

**Ctrl+S** അമർത്തി save ചെയ്യുക. ശേഷം Notepad അടയ്ക്കുക. Save As ഉപയോഗിച്ച് വേറെ file ഉണ്ടാക്കേണ്ടതില്ല. പേര് `.env` ആയിരിക്കണം; `.env.txt` അല്ല.

Server തുടങ്ങിയശേഷം `.env` മാറ്റിയാൽ Window A-ൽ Ctrl+C അമർത്തി നിർത്തുക. `app.py` വീണ്ടും പ്രവർത്തിപ്പിച്ച് browser refresh ചെയ്യണം. Server തുടങ്ങുമ്പോഴാണ് settings വായിക്കുന്നത്. PowerShell environment values-ന് ആദ്യം മുൻഗണന; ശേഷം `.env.local`; അതിനുശേഷം `.env`. മാറ്റം ബാധിക്കുന്നില്ലെന്ന് തോന്നിയാൽ private settings മായ്ക്കാതെ ഈ overrides പരിശോധിക്കാൻ ഉടമയുടെ സഹായം തേടുക.

**Key കാണിക്കാതെ filename പരിശോധിക്കാൻ:**

```powershell
Test-Path .\.env
```

`True` വരണം. File Explorer-ൽ `.env.txt` എന്നാണ് കാണുന്നതെങ്കിൽ View-ൽ **File name extensions** കാണിക്കാൻ തിരഞ്ഞെടുത്ത് പേര് ശരിയാക്കുക. Key ഉള്ള file-ന്റെ ഉള്ളടക്കമോ screenshot-ഓ അയയ്ക്കരുത്.

പ്രോജക്ട് ഉടമ സുരക്ഷിതമായി നൽകിയ Gemini key ഉപയോഗിക്കാം. അല്ലെങ്കിൽ രക്ഷിതാവിന്റെയോ അധ്യാപകന്റെയോ സഹായത്തോടെ [Google AI Studio](https://aistudio.google.com/apikey)-യിൽ ക്രമീകരിക്കാം. Billing enable ചെയ്യുന്നതിനും quota കൂട്ടുന്നതിനും മുമ്പ് അവരോട് ചോദിക്കുക. API key `config.h`-ൽ ഇടരുത്; മറ്റുള്ളവർക്ക് അയയ്ക്കരുത്.

നിലവിലെ project key ഉപയോഗിച്ച് `gemini-3.5-flash-lite` യഥാർഥ മലയാളം മറുപടി നൽകിയിട്ടുണ്ട്. മറ്റൊരു account-ന്റെ model access വ്യത്യസ്തമാകാം. താഴെയുള്ള പരിശോധന പരാജയപ്പെട്ടാൽ ഊഹിച്ച് model പേര് മാറ്റരുത്; troubleshooting ഭാഗം നോക്കുക. Gemini 1.5 വിരമിച്ചതാണ്. പുതിയ key ഉണ്ടാക്കിയാൽ അത് തിരിച്ചുകിട്ടില്ല.

## 6. ആദ്യം കമ്പ്യൂട്ടറിൽ മലയാളം text chat പരിശോധിക്കുക

അതേ PowerShell window-യിൽ:

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_gemini.py
```

ഇത് ലഭ്യമായ models കാണിച്ചശേഷം യഥാർഥ test request അയയ്ക്കും. Key രഹസ്യമായി ഉപയോഗിക്കും. Karen-ന്റെ saved facts മാറ്റില്ല.

**പരിശോധിക്കുക:** `"inference": "succeeded"` എന്നതും മലയാളം മറുപടിയും കാണണം. Model പേരുകളുടെ പട്ടിക കിട്ടിയതുകൊണ്ടുമാത്രം chat വിജയിച്ചെന്ന് കരുതരുത്. `"inference": "failed"` ആണെങ്കിൽ ഘട്ടം 16 നോക്കുക.

ഇനി server തുടങ്ങുക:

```powershell
.\.venv\Scripts\python.exe app.py
```

1. ഈ window തുറന്നുവയ്ക്കുക. ഇതിനെ **Window A — server** എന്ന് കരുതാം. പ്രോഗ്രാം പ്രവർത്തിക്കുന്നതുകൊണ്ട് prompt ഉടനെ തിരിച്ചുവരാത്തത് സാധാരണമാണ്.
2. Chrome അല്ലെങ്കിൽ Edge തുറക്കുക.
3. Browser address bar-ൽ **http://localhost:8080** നൽകുക.
4. Chat box-ൽ `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` എന്ന് ടൈപ്പ് ചെയ്ത് അയയ്ക്കാനുള്ള arrow അമർത്തുക.
5. മലയാളം മറുപടിക്കായി കാത്തിരിക്കുക. തുടർന്ന് `മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?` ചോദിക്കുക.

**പരിശോധിക്കുക:** ശ്രീഹരിയെക്കുറിച്ചും മഴയെക്കുറിച്ചും യഥാർഥ മറുപടി കിട്ടണം. ക്ഷമാപണം മാത്രം കേട്ടാലോ വായിച്ചാലോ request പരാജയപ്പെട്ടതാണ്. Window A-യിലെ error code നോക്കുക. കാത്തിരിക്കുമ്പോൾ Send വീണ്ടും വീണ്ടും അമർത്തരുത്.

`http://localhost:8080/health` app-ന്റെ നില കാണിക്കും. `configured: true` എന്നത് key നൽകിയിട്ടുണ്ടെന്ന് മാത്രമാണ്. `gemini.status: ready` അവസാനമായി generation വിജയിച്ചതാണ് കാണിക്കുന്നത്. അടുത്ത ചോദ്യം തീർച്ചയായും വിജയിക്കുമെന്ന ഉറപ്പല്ല.

## 7. കമ്പ്യൂട്ടറിലെ recording-ഉം saved memory-യും പരിശോധിക്കുക

ഈ ഘട്ടത്തിലും controller-ഓ amplifier-ഓ വേണ്ട.

### ചോദ്യം റെക്കോർഡ് ചെയ്യുക

1. **കമ്പ്യൂട്ടറിൽ localhost:8080** എന്ന dashboard തുറക്കുക.
2. **Record a question** അമർത്തുക.
3. Browser microphone permission ചോദിച്ചാൽ അനുവദിക്കുക.
   Laptop-ന്റെ microphone അല്ലെങ്കിൽ ബന്ധിപ്പിച്ച headset/USB microphone ഉപയോഗിക്കുക. INMP441 controller-നുള്ളതാണ്; അത് ഒറ്റയ്ക്ക് computer microphone ആയി പ്രവർത്തിക്കില്ല.
4. **Listening for 5 seconds…** കാണുമ്പോൾ ആ അഞ്ചു സെക്കൻഡിനുള്ളിൽ ചെറിയൊരു മലയാളം ചോദ്യം പറയുക.
5. Karen അത് പരിശോധിച്ച് മറുപടി തയ്യാറാക്കുന്നതുവരെ കാത്തിരിക്കുക.
6. മറുപടി കേൾക്കുക. സ്വയം പ്ലേ ആയില്ലെങ്കിൽ audio player-ലെ Play അമർത്തുക. Headphones അല്ലെങ്കിൽ കമ്പ്യൂട്ടറിന്റെ speakers ഉപയോഗിക്കാം.

**പരിശോധിക്കുക:** മനസ്സിലാകുന്ന മലയാളം മറുപടി കിട്ടണം. Page-ൽ **Reply ready** കാണണം. ശബ്ദത്തിൽ പറഞ്ഞ ക്ഷമാപണവും പരാജയമാണ്. Window A-യിലെ error പരിശോധിക്കുക.

### Karen ഓർത്തുവയ്ക്കുന്ന കാര്യങ്ങൾ തിരുത്തുക

**What Karen remembers** എന്ന box-ലുള്ള വിവരങ്ങൾ `data/memory.txt`-ൽ സൂക്ഷിക്കുന്നു.

1. Creator, class, school എന്നിവയുടെ നിലവിലുള്ള വിവരങ്ങൾ നിലനിർത്തുക.
2. പ്രദർശനത്തിനായി ഒരു യഥാർഥ fact ചേർക്കണമെങ്കിൽ ആദ്യം `data/memory.txt`-ന്റെ private backup എടുക്കുക. ഉദാഹരണത്തിന് `data` ഫോൾഡറിനുള്ളിൽ മറ്റൊരു copy സൂക്ഷിക്കാം.
3. Fact ചേർത്തശേഷം **Save memory** അമർത്തുക.
4. അതിനെക്കുറിച്ച് ചോദിച്ച് മറുപടി പരിശോധിക്കുക.

Memory save ചെയ്താൽ പുതിയ സംഭാഷണം തുടങ്ങും. **New chat** സംഭാഷണം മാത്രം മായ്ക്കും; saved facts നിലനിൽക്കും. Server restart ചെയ്താലും സംഭാഷണം മായും, saved facts നിലനിൽക്കും. Dashboard ഉപയോഗിക്കുന്ന എല്ലാവർക്കും ഈ memory പൊതുവാണ്. സ്വകാര്യ വിവരങ്ങൾ ചേർക്കരുത്.

**ഈ കമ്പ്യൂട്ടർ പരിശോധനകൾ പൂർത്തിയാക്കിയ ശേഷമേ മുന്നോട്ടുപോകാവൂ.** Text-ഉം browser voice-ഉം പ്രവർത്തിക്കുന്നില്ലെങ്കിൽ കൂടുതൽ വയറുകൾ ബന്ധിപ്പിച്ചതുകൊണ്ട് AI service ശരിയാവില്ല.

## 8. ബോർഡിന്റെ tools ഒരിക്കൽ install ചെയ്യുക

Window A പ്രവർത്തിച്ചുകൊണ്ടിരിക്കട്ടെ. ഘട്ടം 2 പോലെ project folder-ൽ **രണ്ടാമത്തെ PowerShell** തുറക്കുക. ഇതാണ് **Window B — board tools**. 8 മുതൽ 14 വരെയുള്ള ഘട്ടങ്ങൾക്ക് Window B ഉപയോഗിക്കുക.

Arduino CLI-യ്ക്ക് ഒരു ഫോൾഡർ ഉണ്ടാക്കുക:

```powershell
New-Item -ItemType Directory -Force .tools
```

1. [Arduino CLI-യുടെ ഔദ്യോഗിക installation പേജ്](https://arduino.github.io/arduino-cli/1.5/installation/) തുറക്കുക.
2. Download ഭാഗത്ത് സാധാരണ Intel/AMD PC-യ്ക്കുള്ള Windows 64-bit ZIP എടുക്കുക.
3. ZIP extract ചെയ്യുക.
4. അതിലെ `arduino-cli.exe` project-ന്റെ `.tools` ഫോൾഡറിലേക്ക് പകർത്തുക. ഫയൽ `.tools\arduino-cli.exe` എന്ന സ്ഥാനത്ത് വേണം. അതിനുള്ളിൽ വീണ്ടും മറ്റൊരു ഫോൾഡറിലാകരുത്.

ഫയൽ ശരിയായ സ്ഥാനത്താണോ എന്ന് നോക്കുക:

```powershell
Test-Path .\.tools\arduino-cli.exe
```

`True` വരണം. ഇനി Window B-ൽ:

```powershell
$karenArduinoCli = Join-Path (Get-Location) '.tools\arduino-cli.exe'
& $karenArduinoCli version
```

```powershell
& $karenArduinoCli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
```

```powershell
& $karenArduinoCli core install esp32:esp32@3.3.12 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
```

```powershell
& $karenArduinoCli lib install 'ESP8266Audio@2.4.1'
```

**പരിശോധിക്കുക:** ഓരോ command-ഉം error ഇല്ലാതെ തീരണം. Core വലിയ download ആണ്. മറ്റു ESP32 chip-കൾക്കുള്ള files-ഉം അതിൽ ഉണ്ടാകും. Install നടക്കുമ്പോൾ window അടയ്ക്കരുത്. ഓരോ ദിവസവും ഇവ വീണ്ടും install ചെയ്യേണ്ടതില്ല.

## 9. Controller തിരഞ്ഞെടുത്ത് upload ചെയ്യാതെ compile ചെയ്യുക

ചിത്രത്തിലെ ബോർഡിന്:

```powershell
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py
```

**പരിശോധിക്കുക:** ആദ്യം `Controller: esp32_s3`, `Credentials: example only` എന്നിവ കാണണം. അവസാനം **Sketch uses ...** വരണം. Compile error ഉണ്ടാകരുത്.

ഇത് example settings ഉപയോഗിച്ച് code പരിശോധിക്കുന്നതാണ്. ബോർഡിലേക്ക് ഒന്നും upload ചെയ്യുന്നില്ല. നിങ്ങളുടെ യഥാർഥ WiFi settings-ഉം ഇതിൽ പരീക്ഷിക്കുന്നില്ല. ബോർഡ് ബന്ധിപ്പിക്കാതെയും ചെയ്യാം.

Original classic ESP32 ആണെങ്കിൽ ആദ്യ വരി `$env:KAREN_CONTROLLER = 'esp32'` എന്നാക്കുക. 13–14 ഘട്ടങ്ങളിലെ classic wiring column ഉപയോഗിക്കുക.

ആ PowerShell window-യിലെ setting-ന് `.env`-നെക്കാൾ മുൻഗണനയുണ്ട്. വീണ്ടും `.env` setting ഉപയോഗിക്കാൻ `Remove-Item Env:KAREN_CONTROLLER` നൽകുക. ഈ variable മാറ്റിയതുകൊണ്ട് നേരത്തേ program ചെയ്ത ബോർഡ് മാറില്ല. മറ്റൊരു controller ഉപയോഗിക്കുമ്പോൾ build ചെയ്ത് upload ചെയ്യണം. Python backend രണ്ടിനും ഒരുപോലെ പ്രവർത്തിക്കും.

## 10. ബോർഡ് മാത്രം ബന്ധിപ്പിച്ച് COM port കണ്ടെത്തുക

1. മൈക്രോഫോൺ, external button, amplifier എന്നിവ ഇപ്പോൾ ബന്ധിപ്പിക്കരുത്.
2. S3 ബോർഡിന്റെ പുറകിൽ **COM** എന്ന് എഴുതിയ USB-C connector ഉപയോഗിക്കുക. മറ്റേ connector native USB/USB-OTG ആണ്. ഈ setup-ൽ upload-നും Serial Monitor-നും COM ഉപയോഗിക്കുന്നു. Original classic ബോർഡിൽ അതിന്റെ Micro-USB data connector ഉപയോഗിക്കുക.
3. Data cable ഉപയോഗിച്ച് Windows PC-യുമായി ബന്ധിപ്പിക്കുക.
4. Window B-ൽ:

```powershell
.\.venv\Scripts\python.exe scripts\board.py ports
```

`COM5` പോലെയുള്ള port നോക്കുക. Windows **Device Manager → Ports (COM & LPT)**-ലും കാണാം. Port കാണിച്ചാലും board name അറിയില്ലെന്ന് കാണിക്കുന്നത് സംഭവിക്കാം.

താഴെ port variable നൽകുക. **COM5 മാറ്റി നിങ്ങളുടെ ബോർഡിന് ശരിക്കും കാണിച്ച നമ്പർ നൽകണം.**

```powershell
$karenPort = 'COM5'
```

Chip-ഉം flash size-ഉം പരിശോധിക്കുക:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-board.txt
.\.venv\Scripts\python.exe -m esptool --port $karenPort flash-id
```

**പരിശോധിക്കുക:** ചിത്രത്തിലെ S3 profile-ന് ESP32-S3, 16 MB flash എന്നിവയാണ് പ്രതീക്ഷിക്കുന്നത്. Original classic profile ESP32 / 4 MB-യ്ക്കുള്ളതാണ്. അളന്ന chip/size തിരഞ്ഞെടുത്ത profile-നോട് ചേരുന്നില്ലെങ്കിൽ upload ചെയ്യുന്നതിന് മുമ്പ് project ഉടമയോട് പരിശോധിക്കാൻ പറയുക. Metal shield-ൽ എഴുതിയിരിക്കുന്നത് flash അളന്ന ഫലമല്ല.

COM port കാണുന്നില്ലെങ്കിൽ data cable ആണെന്ന് ഉറപ്പാക്കി മറ്റൊരു USB port പരീക്ഷിക്കുക. USB-UART chip തിരിച്ചറിഞ്ഞശേഷം അതിന്റെ manufacturer's driver install ചെയ്യാൻ മുതിർന്ന ഒരാളുടെ സഹായം തേടുക. ഈ S3-ക്കും classic ബോർഡിന്റെ CP2102 driver തന്നെയാണെന്ന് കരുതരുത്. ആദ്യ പരിഹാരമായി flash erase ചെയ്യരുത്.

## 11. ബോർഡിന് WiFi വിവരങ്ങളും കമ്പ്യൂട്ടറിന്റെ address-ഉം നൽകുക

രണ്ട് വേറിട്ട settings files ഉണ്ട്:

| ഫയൽ | എന്താണ് ഇതിൽ നൽകേണ്ടത്? |
|---|---|
| `.env` | കമ്പ്യൂട്ടറിന്റെ settings, രഹസ്യ Gemini key, controller selection |
| `firmware/karen_ai/config.h` | ബോർഡിന്റെ WiFi name/password, backend കമ്പ്യൂട്ടറിന്റെ address. Gemini key ഇവിടെ വേണ്ട. |

Window B-ൽ:

```powershell
if (-not (Test-Path firmware\karen_ai\config.h)) {
    Copy-Item firmware\karen_ai\config.example.h firmware\karen_ai\config.h
}
notepad firmware\karen_ai\config.h
```

Example WiFi name, password, server address എന്നിവ മാത്രം മാറ്റുക. Quotation marks നിലനിർത്തണം:

```cpp
#define WIFI_SSID "YOUR_2_4_GHZ_HOTSPOT"
#define WIFI_PASSWORD "YOUR_HOTSPOT_PASSWORD"
#define SERVER_ORIGIN "http://192.168.1.50:8080"
```

ഇവ ഉദാഹരണങ്ങളാണ്; യഥാർഥ credentials അല്ല. `YOUR_2_4_GHZ_HOTSPOT`, `YOUR_HOTSPOT_PASSWORD` എന്നിവ മാറ്റി യഥാർഥ WiFi വിവരങ്ങൾ quotes-നുള്ളിൽ നൽകണം. Windows കമ്പ്യൂട്ടറിന്റെ address കണ്ടെത്താൻ:

```powershell
ipconfig
```

നിങ്ങളുടെ WiFi/hotspot-ലേക്ക് ബന്ധിപ്പിച്ച adapter-ന്റെ **IPv4 Address** നോക്കുക. `192.168.1.50`-ന് പകരം ആ address നൽകണം. Default Gateway address ഉപയോഗിക്കരുത്. Backend Mac-ലാണെങ്കിൽ Mac-ന്റെ LAN IP ഉപയോഗിക്കുക.

`http://`-ഉം `:8080`-ഉം നിലനിർത്തുക. അവസാനം `/` ചേർക്കരുത്. ഇവിടെ `localhost` നൽകരുത്; അത് ബോർഡിനെത്തന്നെയാണ് സൂചിപ്പിക്കുക. Board-നും backend കമ്പ്യൂട്ടറിനും പരസ്പരം ബന്ധപ്പെടാൻ കഴിയുന്ന network വേണം. Windows Firewall ചോദിച്ചാൽ വിശ്വസനീയ private network-ൽ Python server അനുവദിക്കുക. Firewall മുഴുവനായി off ചെയ്യരുത്.

ഈ local HTTP test-ന് `STATUS_LED=-1`, `RECORD_SECONDS=5`, `MIC_SHIFT=16`, `ROOT_CA` block എന്നിവ മാറ്റാതെ വിടുക. Onboard RGB LED ഇപ്പോൾ ഉപയോഗിക്കുന്നില്ല. Ctrl+S അമർത്തി save ചെയ്യുക. പേര് `config.h` ആയിരിക്കണം; `config.h.txt` അല്ല.

പഴയ classic setup-ലെ config file ആണെങ്കിൽ S3-യ്ക്ക് മാറ്റുമ്പോൾ പഴയ `MIC_*`, `AMP_*`, `BUTTON_PIN` pin definitions മാത്രം നീക്കാൻ project ഉടമയുടെ സഹായം തേടുക. WiFi വിവരങ്ങളും certificate settings-ഉം സൂക്ഷിക്കുക. ശരിയായ default pins ഇനി adapters നൽകും.

Cloud HTTPS പിന്നീടുള്ള ഘട്ടമാണ്. അതിന് trusted root certificate വേണം. പ്രവർത്തിപ്പിക്കാനായി certificate പരിശോധന off ചെയ്യരുത്.

## 12. ബോർഡിലേക്ക് upload ചെയ്ത് messages പരിശോധിക്കുക

Controller, port variables നൽകിയ Window B ഉപയോഗിക്കുക:

```powershell
.\.venv\Scripts\python.exe scripts\firmware.py --use-config
```

**പരിശോധിക്കുക:** compile വിജയിക്കണം. `Credentials: private config.h` കാണണം. ഇതുവരെ upload ചെയ്തിട്ടില്ല.

ഇനി upload ചെയ്യാം:

```powershell
.\.venv\Scripts\python.exe scripts\firmware.py --upload --port $karenPort
```

Upload error ഇല്ലാതെ തീരാൻ കാത്തിരിക്കുക. ഈ command നിങ്ങളുടെ private settings ഉപയോഗിച്ച് വീണ്ടും build ചെയ്തശേഷമാണ് upload ചെയ്യുന്നത്. മാറ്റാത്ത example WiFi placeholders ഉണ്ടെങ്കിൽ upload അനുവദിക്കില്ല.

Serial Monitor തുറക്കുക:

```powershell
.\.venv\Scripts\python.exe scripts\board.py monitor --port $karenPort
```

Startup messages കാണാൻ ബോർഡിലെ **RST** ഒരിക്കൽ അമർത്തുക. S3-യ്ക്ക് ഇവ നോക്കുക:

```text
Controller: esp32_s3
MIC BCLK/WS/SD: 4/5/6 | AMP BCLK/WS/DIN: 16/17/18 | button: 7
Connected: ...
Ready. Press button, then speak for five seconds.
```

ആദ്യ വരിയിൽ flash, PSRAM bytes-ഉം ഉണ്ടാകും. S3-യുടെ advertised അളവുകൾ **16,777,216 flash bytes**, **8,388,608 PSRAM bytes** ആണ്. വ്യത്യാസമുണ്ടെങ്കിലോ വീണ്ടും വീണ്ടും restart ചെയ്യുകയാണെങ്കിലോ സഹായം തേടുക. LED തെളിയാത്തത് സാധാരണമാണ്.

Board connect ആയോ, Ready ആയോ എന്നറിയാൻ Serial Monitor നോക്കുക. യഥാർഥ ബോർഡ് online ആണോ എന്ന് dashboard പരിശോധിക്കുന്നില്ല.

Classic ബോർഡിൽ `Controller: esp32` എന്നും താഴെയുള്ള tables-ലെ classic pins-ഉം പ്രതീക്ഷിക്കാം. പല classic ബോർഡുകൾക്കും PSRAM ഇല്ല. അത്തരം ബോർഡുകളിൽ PSRAM zero കാണുന്നത് സാധാരണമാണ്.

Upload connect ആകുന്നില്ലെങ്കിൽ ആദ്യം Serial Monitor അടയ്ക്കുക. **BOOT** പിടിച്ചുകൊണ്ട് **RST** ഒന്ന് അമർത്തി upload തുടങ്ങുക. Connect ആകുമ്പോൾ BOOT വിടുക. Onboard BOOT ഈ നടപടിക്കുള്ളതാണ്; അത് ചോദ്യം റെക്കോർഡ് ചെയ്യാനുള്ള button അല്ല.

അടുത്ത upload-ന് മുമ്പ് **Window B-ൽ Ctrl+C** അമർത്തി Serial Monitor നിർത്തുക. അത് Window A-യിലെ server നിർത്തില്ല. `config.h`-ൽ WiFi അല്ലെങ്കിൽ server address മാറ്റിയാൽ വീണ്ടും upload ചെയ്യണം. File save ചെയ്തതുകൊണ്ടുമാത്രം ബോർഡിൽ മാറ്റം വരില്ല.

## 13. മൈക്രോഫോണും പുറത്തുള്ള question button-ഉം ബന്ധിപ്പിക്കുക

**ആദ്യം USB cable അഴിക്കുക.** യഥാർഥ മൈക്രോഫോണിലെ labels വായിക്കുക. Pin order മാറാം. Table-ലെ ഓരോ വരിയായി ബന്ധിപ്പിക്കുക.

| INMP441 / button connection | ചിത്രത്തിലെ S3 `esp32_s3` | Original classic `esp32` |
|---|---|---|
| Microphone VDD | 3V3 | 3V3 |
| Microphone GND | GND | GND |
| Microphone SCK / BCLK | GPIO4 | GPIO26 |
| Microphone WS | GPIO5 | GPIO25 |
| Microphone SD | GPIO6 | GPIO33 |
| Microphone L/R | GND | GND |
| External momentary button-ന്റെ ഒരു വശം | GPIO7 | GPIO32 |
| Button-ന്റെ മറുവശം | GND | GND |

നാല് കാലുള്ള button-ൽ ഒരേ വശത്തെ രണ്ട് കാലുകൾ നേരത്തേ തമ്മിൽ ബന്ധിപ്പിച്ചിട്ടുണ്ടാകാം. അമർത്തുമ്പോൾ മാത്രം തമ്മിൽ ബന്ധപ്പെടുന്ന pair ഏതെന്ന് മുതിർന്ന ഒരാളോട് പരിശോധിപ്പിക്കുക. എല്ലായ്പ്പോഴും ബന്ധമുള്ള കാലുകൾ തിരഞ്ഞെടുക്കരുത്. Button 3V3-ലേക്കോ 5V-ലേക്കോ ബന്ധിപ്പിക്കരുത്. Firmware internal pull-up ഉപയോഗിക്കുന്നു.

USB വീണ്ടും ബന്ധിപ്പിക്കുക. Serial Monitor തുറന്ന് Ready വരാൻ കാത്തിരിക്കുക. External button ഒരിക്കൽ അമർത്തിവിടുക. **Recording. Speak now.** കാണുമ്പോൾ അഞ്ചു സെക്കൻഡിനുള്ളിൽ ചെറിയ ചോദ്യം പറയുക. ശേഷം കാത്തിരിക്കുക.

Amplifier ഇല്ലാതെ ബോർഡിൽനിന്ന് സ്പീക്കർ ശബ്ദം ഇപ്പോൾ പ്രതീക്ഷിക്കേണ്ടതില്ല. Serial Monitor-ൽ server result `ok` വരുന്നതും dashboard refresh ചെയ്യുമ്പോൾ ചോദ്യവും മറുപടിയും കാണുന്നതും microphone path പരിശോധിക്കാൻ സഹായിക്കും. `spoken-error` എന്നത് പരാജയമാണ്; ശരിയായ AI ഉത്തരമല്ല. Karen busy ആയിരിക്കുമ്പോൾ വീണ്ടും വീണ്ടും button അമർത്തരുത്.

## 14. MAX98357A amplifier-ഉം speaker-ഉം ചേർക്കുക

MAX98357A കിട്ടിയിട്ടില്ലെങ്കിൽ കമ്പ്യൂട്ടർ/മൈക്രോഫോൺ പരിശോധനകൾവരെ മാത്രം ചെയ്യുക. **ഈ firmware-ൽ PAM8403 അതിന് പകരമല്ല.**

Power അഴിക്കുക. Amplifier-ന്റെ യഥാർഥ labels, soldering, 5 V supply എങ്ങനെ നൽകണം എന്നിവ മുതിർന്ന ഒരാളെക്കൊണ്ട് പരിശോധിപ്പിക്കുക. ESP32-യിലെ ഏത് supply pin-ൽനിന്നും amplifier-ന് power കൊടുക്കാമെന്ന് ഊഹിക്കരുത്.

| MAX98357A / speaker connection | ചിത്രത്തിലെ S3 `esp32_s3` | Original classic `esp32` |
|---|---|---|
| BCLK | GPIO16 | GPIO27 |
| LRC / WS | GPIO17 | GPIO14 |
| DIN | GPIO18 | GPIO22 |
| VIN | അനുയോജ്യമെന്ന് പരിശോധിച്ച 5 V supply | അനുയോജ്യമെന്ന് പരിശോധിച്ച 5 V supply |
| GND | Controller-നൊപ്പം common GND | Controller-നൊപ്പം common GND |
| SD / EN | യഥാർഥ breakout-ന്റെ enable നിർദേശപ്രകാരം | അതുപോലെ |
| Speaker-ന്റെ രണ്ട് വയറുകൾ | Amplifier SPK+, SPK− മാത്രം | അതുപോലെ |

Speaker-ന്റെ ഒരു വയറും GND-ലേക്കോ controller GPIO-യിലേക്കോ പോകരുത്. യഥാർഥ power circuit പരിശോധിക്കാതെ computer USB power-ഉം പുറത്തുനിന്നുള്ള 5 V-ഉം ബോർഡിൽ തമ്മിൽ കൂട്ടരുത്. വേറെ supply ഉപയോഗിക്കുന്ന amplifier-നും controller-നും common GND വേണം. Microphone VDD-യിലോ GPIO-യിലോ ഒരിക്കലും 5 V കൊടുക്കരുത്.

അവസാനം കാണിച്ച speaker box-ൽ **4 ohms / 10 watts** എന്നാണ്. Speaker-ന്റെ സ്വന്തം marking പരിശോധിക്കുക. ആ rating ഉള്ളതുകൊണ്ട് amplifier 10 watts നൽകുമെന്നല്ല. Firmware കുറഞ്ഞ playback gain-ലാണ് തുടങ്ങുന്നത്. Supply സ്ഥിരമാണെന്നും wiring ശരിയാണെന്നും മുതിർന്ന ഒരാൾ പരിശോധിക്കുന്നതുവരെ gain കൂട്ടരുത്.

Power വീണ്ടും നൽകുക. Ready വരാൻ കാത്തിരിക്കുക. External button ഉപയോഗിച്ച് ഒരു ചെറിയ ചോദ്യം ചോദിക്കുക. മുഴുവൻ മലയാളം മറുപടി കേൾക്കുക. Board restart ചെയ്യുകയോ ചൂടാകുകയോ ശബ്ദം വളരെ മോശമായി മുറിയുകയോ ചെയ്താൽ power അഴിച്ച് supply/wiring പരിശോധിക്കാൻ സഹായം തേടുക. പ്രദർശനത്തിന് മുമ്പ് പത്ത് സാധാരണ ചോദ്യങ്ങൾ തുടർച്ചയായി വിജയിപ്പിക്കുക.

## 15. ഓരോ ദിവസവും ചെയ്യേണ്ടത്

എല്ലാ ദിവസവും packages install ചെയ്യുകയോ വീണ്ടും upload ചെയ്യുകയോ വേണ്ട.

1. കമ്പ്യൂട്ടറിന് ഇന്റർനെറ്റ് നൽകുക. Board-ന് എത്താൻ കഴിയുന്ന 2.4 GHz network ഉണ്ടായിരിക്കണം.
2. Project folder-ൽ PowerShell തുറക്കുക.
3. Server തുടങ്ങുക:

```powershell
.\.venv\Scripts\python.exe app.py
```

4. **http://localhost:8080** തുറന്ന് ഒരു text question പരിശോധിക്കുക.
5. Program ചെയ്ത ബോർഡിന് power നൽകുക. Ready വരാൻ കാത്തിരുന്ന് ഒരു button question പരീക്ഷിക്കുക.
6. കമ്പ്യൂട്ടറിന്റെ IP address-ഓ WiFi വിവരങ്ങളോ മാറിയാൽ `config.h` തിരുത്തി വീണ്ടും upload ചെയ്യുക.
7. പ്രദർശനസമയത്ത് server window തുറന്നുവയ്ക്കുക. കമ്പ്യൂട്ടർ sleep ആകരുത്. Laptop lid അടച്ചാലും access നിൽക്കാം.

നിർത്താൻ: മറുപടി തീരാൻ കാത്തിരിക്കുക. Board-ന്റെ power അഴിക്കുക. തുടർന്ന് **server window-യിൽ Ctrl+C** അമർത്തുക. Saved memory നിലനിൽക്കും. Server വീണ്ടും തുടങ്ങുമ്പോൾ പഴയ സംഭാഷണം മായും.

അതേ network-ലുള്ള ഫോണിൽ `http://<computer-IP>:8080` വഴി text chat-ഉം memory editing-ഉം ഉപയോഗിക്കാം. Phone microphone recording-ന് സാധാരണ trusted HTTPS വേണം. ആദ്യ recording test-ന് **കമ്പ്യൂട്ടറിലെ localhost** ഉപയോഗിക്കുക.

പ്രദർശനത്തിനായി മൂന്ന് ചെറിയ ചോദ്യങ്ങളും ഒരു തുടർചോദ്യവും തയ്യാറാക്കുക. Power bank charge ചെയ്യുക. Hardware പ്രശ്നമായാൽ ഉപയോഗിക്കാൻ computer dashboard തയ്യാറായിരിക്കണം. ഇന്റർനെറ്റ് പോയാൽ പുതിയ cloud answers കിട്ടില്ല. `DEMO_MODE=1` എന്നത് മുൻകൂട്ടി തയ്യാറാക്കിയ text demo മാത്രമാണ്; അങ്ങനെത്തന്നെ അടയാളപ്പെടുത്തും, voice പ്രവർത്തിക്കില്ല. Live ഉപയോഗത്തിന് അത് `0` ആക്കി server restart ചെയ്യുക. [പ്രദർശന checklist](docs/EXHIBITION.md) കൂടി നോക്കുക.

Dashboard-ൽ login ഇല്ല. അതിൽ എത്താൻ കഴിയുന്നവർക്ക് shared memory കാണാനും മാറ്റാനും API quota ഉപയോഗിക്കാനും കഴിയും. വിശ്വസനീയ exhibition network ഉപയോഗിക്കുക. പ്രദർശനം കഴിഞ്ഞാൽ server നിർത്തുക.

## 16. എന്തെങ്കിലും പ്രവർത്തിക്കുന്നില്ലെങ്കിൽ

Browser, server Window A, Serial Monitor എന്നിവയിൽ കാണുന്ന **കൃത്യമായ message** ആദ്യം നോക്കുക. എല്ലാ packages-ഉം വീണ്ടും install ചെയ്തുകൊണ്ടിരിക്കേണ്ടതില്ല.

| കാണുന്ന പ്രശ്നം | ആദ്യം ചെയ്യേണ്ടത് |
|---|---|
| `Test-Path .\app.py` → `False` | `app.py` യഥാർഥത്തിൽ ഉള്ള extracted folder തുറക്കുക. |
| `py` തിരിച്ചറിയുന്നില്ല | Python-ഉം launcher-ഉം install ചെയ്തശേഷം PowerShell വീണ്ടും തുറക്കുക. |
| `.venv\Scripts\python.exe` ഇല്ല | ഈ Windows PC-യിൽ ഘട്ടം 4 പൂർത്തിയാക്കുക. Mac `.venv` പകർത്തരുത്. |
| `ModuleNotFoundError` | `.venv` Python command ഉപയോഗിക്കുക. Project folder-ൽനിന്ന് `requirements.txt` install ചെയ്യുക. |
| Browser connect ആകുന്നില്ല | Window A പ്രവർത്തിക്കുന്നുണ്ടോ, അതിൽ error ഉണ്ടോ, URL/8080 ശരിയാണോ എന്ന് നോക്കുക. |
| Port 8080 already in use | മറ്റൊരു server നേരത്തേ പ്രവർത്തിക്കുന്നുണ്ടാകാം. അത് ഉപയോഗിക്കുക; അല്ലെങ്കിൽ അത് നിർത്തിയശേഷം പുതിയത് തുടങ്ങുക. |
| `Page expired` | Server restart ചെയ്തശേഷം dashboard refresh ചെയ്യുക. |
| `model_auth` / 401, 403 | Gemini key-ഉം account/project restrictions-ഉം ഉടമയോടൊപ്പം പരിശോധിക്കുക. |
| `model_not_found` / 404 | Diagnostic നടത്തി ലഭ്യമായ കൃത്യമായ model ID തിരഞ്ഞെടുക്കാൻ ഉടമയുടെ സഹായം തേടുക. വിരമിച്ച 1.5-ലേക്ക് മാറരുത്. |
| `model_quota` / 429 | കാത്തിരിക്കുക. Quota പരിശോധിക്കാൻ ഉടമയോട് പറയുക. സ്വയം billing enable ചെയ്യരുത്. |
| `model_unavailable` / 503 | Provider busy ആയിരിക്കാം. പരിമിത retries ഇതിനകം നടക്കും. കുറച്ച് കാത്തശേഷം പുതിയ ചോദ്യം ചോദിക്കുക. |
| `model_timeout` / 504 | സമയപരിധിക്കുള്ളിൽ AI തീർന്നില്ല. Diagnostic നോക്കുക. സമയം കൂട്ടിയതുകൊണ്ടുമാത്രം പരിഹാരമായെന്ന് കരുതരുത്. |
| HTTP 505 | HTTP version പിന്തുണയില്ല. ഇത് 504-ൽനിന്ന് വ്യത്യസ്തമാണ്. Key മറച്ചുവച്ച് error code ഉടമയെ കാണിക്കുക. |
| `busy` അല്ലെങ്കിൽ നീണ്ട കാത്തിരിപ്പിന് ശേഷം request ID | നിലവിലെ ജോലി തീരട്ടെ. അതേ ചോദ്യം വീണ്ടും അയയ്ക്കുന്നതിന് മുമ്പ് `http://localhost:8080/requests/`-നുശേഷം ആ ID ചേർത്ത് പരിശോധിക്കുക. അതേ server-ൽ ഫലം പത്ത് മിനിറ്റ് വരെ ലഭിക്കും. |
| Recording ലഭ്യമല്ല | കമ്പ്യൂട്ടറിലെ localhost ഉപയോഗിക്കുക. Browser-ൽ ശരിയായ microphone അനുവദിക്കുക. |
| `stt_unavailable`, `tts_unavailable` | ഇന്റർനെറ്റും server log-ഉം നോക്കുക. Cloud speech service ലഭ്യമല്ലാതിരിക്കാം. |
| COM port ഇല്ല | COM connector, data cable, തിരിച്ചറിഞ്ഞ ശരിയായ USB-UART driver എന്നിവ പരിശോധിക്കുക. |
| COM port open ആകുന്നില്ല / access denied | Serial Monitor-ഉം ആ port ഉപയോഗിക്കുന്ന മറ്റു programs-ഉം അടയ്ക്കുക. Port നമ്പർ വീണ്ടും നോക്കുക. |
| Upload connect ആകുന്നില്ല | S3 selection, യഥാർഥ port, COM connector എന്നിവ നോക്കുക. ഘട്ടം 12-ലെ BOOT/RST രീതി പരീക്ഷിക്കുക. |
| `Unknown KAREN_CONTROLLER` | കൃത്യമായി `esp32_s3` അല്ലെങ്കിൽ `esp32` മാത്രം ഉപയോഗിക്കുക. |
| Invalid/reserved/overlapping pins | Board selection പരിശോധിക്കുക. S3-ൽ പഴയ classic pin overrides നീക്കുക. |
| WiFi connect ആകുന്നില്ല | WiFi name/password, 2.4 GHz support എന്നിവ നോക്കുക. Settings തിരുത്തിയാൽ upload വീണ്ടും ചെയ്യണം. |
| Board-ന് server കിട്ടുന്നില്ല | Window A തുറന്നുവയ്ക്കുക. നിലവിലെ computer LAN IP, firewall, shared network എന്നിവ നോക്കുക. |
| Microphone ശബ്ദം കിട്ടുന്നില്ല / വ്യക്തമല്ല | VDD=3V3, L/R=GND, ശരിയായ wiring column, soldered connections എന്നിവ നോക്കുക. |
| Speaker ശബ്ദമില്ല | MAX98357A തന്നെയാണോ, power/enable, common GND, SPK+/SPK− എന്നിവ ശരിയാണോ നോക്കുക. |
| Board വീണ്ടും വീണ്ടും restart ചെയ്യുന്നു | Power അഴിക്കുക. വീണ്ടും ശ്രമിക്കുന്നതിന് മുമ്പ് supply/wiring പരിശോധിക്കാൻ സഹായം തേടുക. |

ഒരു request-ന് സമയം വേണ്ടിവരാം. Browser/device-ന്റെ സാധാരണ wait budget ഏകദേശം **2 മിനിറ്റ് 40 സെക്കൻഡ്** ആണ്. ഒരിക്കൽ അമർത്തിയശേഷം മറുപടിയോ error-ഓ വരാൻ കാത്തിരിക്കുക. ഒരു ചോദ്യത്തെ തിരിച്ചറിയുന്ന നീളമുള്ള code ആണ് request ID. ഫലം പരിശോധിക്കുമ്പോൾ അത് കൃത്യമായി പകർത്തുക. Connection നഷ്ടപ്പെട്ടാൽ അതേ ID ഉപയോഗിച്ച് ഫലം വീണ്ടെടുക്കാം; മറ്റൊരു conversation turn ഉണ്ടാക്കേണ്ടതില്ല. Server restart ചെയ്താലോ ഫലത്തിന്റെ കാലാവധി കഴിഞ്ഞാലോ ഈ recovery സാധ്യമാകില്ല.

സഹായം ചോദിക്കുമ്പോൾ controller name, ഏത് ഘട്ടം, COM number, error code എന്നിവ പറയുക. Screenshot-ൽ API key, WiFi password, private saved facts എന്നിവ മറയ്ക്കുക. `.env`, `.env.local`, `config.h`, saved memory എന്നിവ source repository-യിൽ ഇടരുത്.

## 17. Mac ആണ് ഉപയോഗിക്കുന്നതെങ്കിൽ

മുകളിലെ Windows commands Windows PC-യ്ക്കുള്ളതാണ്. നിലവിലുള്ള project Mac-ൽ:

```bash
cd /Users/sanoopbhaskerv/workspace/karen-ai
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

പുതിയ Mac checkout-ൽ മാത്രം ആദ്യം `python3 -m venv .venv` ഉപയോഗിച്ച് `.venv` ഉണ്ടാക്കുക. `.env` ഇല്ലെങ്കിൽ മാത്രം ഉണ്ടാക്കുക. പ്രവർത്തിക്കുന്ന private settings മാറ്റി blank files ഇടരുത്. Board build ഉദാഹരണം:

```bash
KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py
```

Mac serial port `/dev/cu...` എന്നപോലെയാകും; COM5 അല്ല. Mac upload നിർദേശങ്ങൾക്ക് [hardware commissioning](docs/HARDWARE.md) നോക്കുക.

## 18. ഇതുവരെ പരിശോധിച്ചതും കൂടുതൽ വിവരങ്ങളും

**രേഖപ്പെടുത്തിയ software പരിശോധനകൾ:** Mac-ൽ 109 tests വിജയിച്ചു. Windows runner-ൽ native launcher tests, computer-only setup, server health checks എന്നിവ വിജയിച്ചു. Classic ESP32, S3 firmware രണ്ടും Mac-ൽ compile ചെയ്തു. യഥാർഥ മലയാളം chat-ഉം കൃത്രിമ മലയാളം ശബ്ദം ഉപയോഗിച്ച WAV→MP3/browser test-ഉം വിജയിച്ചു. **ഇനിയും പരിശോധിക്കാനുള്ളത്:** നിങ്ങളുടെ Windows PC-യിലെ USB/driver, board-tool setup/build, S3 flash/PSRAM, upload, microphone/speaker quality, power stability. അവ വിജയിക്കുന്നതുവരെ hardware തയ്യാറായെന്ന് കരുതരുത്. മുഴുവൻ തെളിവുകളും പരിധികളും [VALIDATION.md](docs/VALIDATION.md)-ൽ ഉണ്ട്.

- [English: complete beginner guide](README.md)
- [Windows technical setup, Arduino IDE പകരം ഉപയോഗിക്കൽ](docs/WINDOWS.md)
- [രണ്ട് wiring maps-ഉം hardware commissioning-ഉം](docs/HARDWARE.md)
- [പ്രദർശന checklist](docs/EXHIBITION.md)
- [English സാങ്കേതിക വിവരങ്ങൾ: routes, timeouts, tests, cloud hosting](docs/TECHNICAL.md)
- [മലയാളം സാങ്കേതിക വിവരങ്ങൾ](docs/TECHNICAL_ML.md)

പഴയ വിശദമായ engineering notes ഈ technical reference files-ൽ സൂക്ഷിച്ചിട്ടുണ്ട്. Cloud hosting പിന്നീടുള്ള ജോലിയാണ്. മുകളിലെ ഘട്ടങ്ങൾ നിങ്ങളുടെ local network-ലുള്ള കമ്പ്യൂട്ടറാണ് ഉപയോഗിക്കുന്നത്.
