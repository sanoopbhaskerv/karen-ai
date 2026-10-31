# Bootstrap kit — Windows and Mac

This is the shortcut for the [English guide](../README.md) and [മലയാളം ഗൈഡ്](../READMEMALAYALAM.md). Malayalam instructions are below the English section.

For the Windows + S3-N16R8 call, use the [staged wiring guide](FIRST_CALL_WINDOWS.md). Board setup now also installs `esptool` 5.x for explicit chip/flash checks. Long setup steps print a heartbeat every 20 seconds; `.tools/bootstrap.log` records timestamps, duration, exit status and sanitized output.

After setup, `doctor-windows.cmd --controller esp32_s3` checks software and reports unfinished hardware/network checks. Add `--port COM5 --probe-chip` only with the actual board port; this read-only probe may reset the board. Add `--server http://YOUR_LAPTOP_IPV4:8080` for a health check without an AI request. Doctor logs go to `.tools/doctor.log`. `scripts/board.py monitor --port COM5 --log` saves redacted timestamped output to `.tools/serial.log`; close it with Ctrl+C before uploading. Read the call guide before wiring.

## English

### What you need first

- Extract the complete project folder. Do not run inside the ZIP.
- Install Python **3.14** once if needed. Existing Python **3.12–3.14** is supported. The launcher finds it; if none is found it shows the official download link. The kit does not install Python, Homebrew or system drivers for you.
- Keep internet available for Python packages. Optional board support needs **at least 8 GB free space** and a large download.
- Use source files on each computer; do not copy another computer's `.venv` or Arduino tool folders.

### Run setup

| Windows | Mac |
|---|---|
| Double-click `bootstrap-windows.cmd` | Double-click `bootstrap-mac.command` |
| Or run ` .\bootstrap-windows.cmd ` in PowerShell | Or run `bash bootstrap-mac.command` in Terminal |

If Finder does not run the Mac file, use the Terminal command. Do not disable the Mac's security settings globally.

The menu has three choices. Type a number and press Enter:

1. **Computer chat only** — recommended first. Creates/reuses `.venv`, installs backend packages and creates missing example settings.
2. **Computer + ESP32-S3 tools** — also prepares Arduino CLI, the pinned ESP32 core and audio library for the photographed board.
3. **Computer + classic ESP32 tools** — same tools, with classic selected for a new settings file.

Pressing Enter without a number chooses 1. Non-interactive runs also default to computer-only setup. Normal setup does not compile or upload firmware. Choose the optional command below to compile an example.

### What happens to your files?

- Existing `.env`, `.env.local`, `firmware/karen_ai/config.h` and `data/memory.txt` are kept. They are never replaced by examples.
- A new `.env` gets a private random `SECRET_KEY`; the Gemini key stays empty for you to enter locally. A fresh file defaults to `esp32_s3`, or the controller you selected.
- Existing controller/model settings are not rewritten. `--controller` chooses a new file's controller and any optional example compile; it does not edit an existing `.env`. For later builds, use `KAREN_CONTROLLER` or the firmware helper's `--controller` option.
- A missing `config.h` is copied from the example, without real WiFi details.
- Saved memory is never edited. A fresh app creates its default memory when first started.
- Packages are installed into `.venv` without a forced upgrade. A broken or foreign `.venv` is kept and reported, not deleted. Ask the owner to move only that folder aside if a replacement is needed.
- Matching installed Arduino packages are reused. Otherwise board packages are installed under ignored `.tools/arduino`, so another project's global packages are not replaced. The firmware helper automatically uses this local toolchain.
- New Arduino CLI downloads come from the official v1.5.1 release and must match a pinned SHA-256 checksum before extraction. Only the executable is extracted.

Windows x64, Intel Mac and Apple Silicon Mac have automatic CLI downloads. Other architectures get manual-install guidance. Existing CLI installations can be reused. The project-local Arduino folder records the OS/CPU; if copied from another platform, setup stops and keeps it instead of pretending it is compatible.

### Finish setup, then start Karen

When **SETUP COMPLETE** appears:

1. Follow README Step 5: put your private Gemini API key in `.env` if blank. Keep an existing key. No key is requested in the setup console.
2. Double-click **`start-windows.cmd`** on Windows or **`start-mac.command`** on Mac. On Mac you can use `bash start-mac.command` instead.
3. Keep that server window open. Open **http://localhost:8080** (default port) and test text, then browser recording.
4. If you selected board tools, skip the manual downloads in README Step 8. Open a second PowerShell in the project folder (Window B), then continue at Step 9 for a compile check and the port/WiFi/upload/wiring steps. The `scripts/board.py` commands locate the correct CLI/local SDK automatically. No board is uploaded by bootstrap.

Use the start launcher for everyday use. You do not need setup every day. If port 8080 is already occupied, use or stop the existing server; the launcher never kills another process automatically. If you changed `PORT`, use that port in the browser.

### Command options

From the project folder, you can skip the menu:

```powershell
.\bootstrap-windows.cmd --firmware --controller esp32_s3 --compile
```

```bash
bash bootstrap-mac.command --firmware --controller esp32_s3 --compile
```

These install/verify board tools and compile **example** firmware. They never upload or compile private WiFi credentials. Use `--controller esp32` for the classic board. Omit `--firmware --compile` for computer-only setup.

Check an installation without running setup steps or making an AI request:

```powershell
.\bootstrap-windows.cmd --check
```

```bash
bash bootstrap-mac.command --check
```

Add `--firmware` to also query the Arduino installation. These checks inspect package imports/versions and local configuration presence. Arduino's own metadata/cache checks may occur. A pass does not validate the Gemini key, internet speech services, actual board memory or wiring. Use the live diagnostic in README Step 6 separately.

`--dev` adds the test dependencies. The shared script can also be run directly with a supported Python: `python scripts/bootstrap.py`. The normal menu is shown only for an interactive no-argument run.

### If setup stops

Read the last message first. The sanitized log is `.tools/bootstrap.log`; do not use a raw `.env` or `config.h` screenshot for support. Rerun the same setup after fixing internet/disk problems. Existing settings and partial downloads are retained where supported by Arduino CLI.

Do not manually delete `.env`, `.env.local` or saved memory to fix installation. If an environment/tool folder belongs to another OS, ask the owner to move only the reported folder aside and rerun. A cancelled/incomplete package download is not successful setup. Do not proceed to hardware until the relevant check passes.

### Verification limits

Fresh and repeated Mac setup, private-file preservation, native Mac startup/Flask health, official CLI checksum/execution and a real S3 example build were tested. The fresh board build reused matching installed Mac core/library packages. Installation into a new isolated SDK folder is covered by regression tests, not a second multi-GB download. Native `.cmd` argument/exit handling, real computer-only bootstrap/check and server health passed on a Windows runner. Physical Windows board-tool setup/upload remains pending on the student's PC. No physical upload or paid/live AI request is made by bootstrap.

## മലയാളം

### ആദ്യം വേണ്ടത്

- മുഴുവൻ project folder extract ചെയ്യുക. ZIP-ന്റെ ഉള്ളിൽനിന്ന് പ്രവർത്തിപ്പിക്കരുത്.
- ആവശ്യമെങ്കിൽ **Python 3.14** ഒരിക്കൽ install ചെയ്യുക. നിലവിലുള്ള **Python 3.12–3.14** ഉപയോഗിക്കാം. Launcher അത് കണ്ടെത്തും. ഇല്ലെങ്കിൽ ഔദ്യോഗിക download link കാണിക്കും. Python, Homebrew, system drivers എന്നിവ ഈ kit സ്വയം install ചെയ്യുന്നില്ല.
- Python packages download ചെയ്യാൻ ഇന്റർനെറ്റ് വേണം. Board tools കൂടി വേണമെങ്കിൽ **കുറഞ്ഞത് 8 GB free space** വേണം; download വലുതാണ്.
- ഓരോ കമ്പ്യൂട്ടറിലും source files ഉപയോഗിച്ച് setup ചെയ്യുക. മറ്റൊരു കമ്പ്യൂട്ടറിന്റെ `.venv`, Arduino tools folders എന്നിവ പകർത്തരുത്.

### Setup തുടങ്ങുക

| Windows | Mac |
|---|---|
| `bootstrap-windows.cmd` double-click ചെയ്യുക | `bootstrap-mac.command` double-click ചെയ്യുക |
| അല്ലെങ്കിൽ PowerShell-ൽ ` .\bootstrap-windows.cmd ` | അല്ലെങ്കിൽ Terminal-ൽ `bash bootstrap-mac.command` |

Mac-ൽ double-click കൊണ്ട് തുറക്കുന്നില്ലെങ്കിൽ Terminal command ഉപയോഗിക്കുക. Mac-ന്റെ security settings മുഴുവനായി off ചെയ്യേണ്ടതില്ല.

Menu-ൽ മൂന്ന് options ഉണ്ട്. നമ്പർ നൽകി Enter അമർത്തുക:

1. **Computer chat only** — ആദ്യം ഇത് തിരഞ്ഞെടുക്കാം. `.venv` തയ്യാറാക്കും, packages install ചെയ്യും, ഇല്ലാത്ത example settings files ഉണ്ടാക്കും.
2. **Computer + ESP32-S3 tools** — ചിത്രത്തിലെ ബോർഡിന് Arduino CLI, തിരഞ്ഞെടുത്ത ESP32 core, audio library എന്നിവയും തയ്യാറാക്കും.
3. **Computer + classic ESP32 tools** — അതേ tools; പുതിയ settings file-ന് classic controller തിരഞ്ഞെടുക്കും.

നമ്പർ നൽകാതെ Enter അമർത്തിയാൽ 1 തിരഞ്ഞെടുക്കും. Terminal interaction ഇല്ലാത്ത run-ലും computer-only setup ആണ് default. സാധാരണ setup compile/upload ചെയ്യുന്നില്ല. Example compile കൂടി വേണമെങ്കിൽ താഴെയുള്ള പ്രത്യേക command ഉപയോഗിക്കാം.

### നിങ്ങളുടെ ഫയലുകൾക്ക് എന്ത് സംഭവിക്കും?

- നിലവിലുള്ള `.env`, `.env.local`, `firmware/karen_ai/config.h`, `data/memory.txt` എന്നിവ സൂക്ഷിക്കും. അവയ്ക്കു മുകളിൽ example files ഇടില്ല.
- പുതിയ `.env`-ൽ private random `SECRET_KEY` ഉണ്ടാക്കും. Gemini key നിങ്ങൾ പിന്നീട് സ്വകാര്യമായി നൽകണം. പുതിയ file-ന് default `esp32_s3` അല്ലെങ്കിൽ നിങ്ങൾ തിരഞ്ഞെടുത്ത controller ആയിരിക്കും.
- പഴയ controller/model settings മാറ്റില്ല. `--controller` പുതിയ file-നും optional example compile-നും ബാധകമാണ്; പഴയ `.env` തിരുത്തില്ല. പിന്നീടുള്ള build-കൾക്ക് `KAREN_CONTROLLER` അല്ലെങ്കിൽ firmware helper-ന്റെ `--controller` option ഉപയോഗിക്കുക.
- `config.h` ഇല്ലെങ്കിൽ യഥാർഥ WiFi വിവരങ്ങളില്ലാത്ത example copy ഉണ്ടാക്കും.
- Saved memory തിരുത്തില്ല. പുതിയ app ആദ്യം തുടങ്ങുമ്പോഴാണ് default memory ഉണ്ടാകുന്നത്.
- `.venv`-ലാണ് packages install ചെയ്യുന്നത്; നിർബന്ധിച്ച് upgrade ചെയ്യില്ല. മറ്റൊരു OS-ലെതോ കേടായതോ ആയ `.venv` delete ചെയ്യില്ല; പ്രശ്നം കാണിക്കും. ആവശ്യമെങ്കിൽ ആ folder മാത്രം മാറ്റിവയ്ക്കാൻ ഉടമയുടെ സഹായം തേടുക.
- ശരിയായ Arduino packages നേരത്തേ ഉണ്ടെങ്കിൽ അവ ഉപയോഗിക്കും. ഇല്ലെങ്കിൽ Git അവഗണിക്കുന്ന `.tools/arduino`-ൽ project-local packages install ചെയ്യും. മറ്റു projects-ന്റെ global packages മാറ്റില്ല. Firmware helper ഈ local tools സ്വയം ഉപയോഗിക്കും.
- പുതിയ Arduino CLI ഔദ്യോഗിക v1.5.1 release-ൽനിന്നാണ് download ചെയ്യുന്നത്. സൂക്ഷിച്ച SHA-256 checksum-നോട് ചേരണം. Executable മാത്രം പുറത്തെടുക്കും.

Windows x64, Intel Mac, Apple Silicon Mac എന്നിവയ്ക്ക് automatic CLI download ഉണ്ട്. മറ്റു architectures-ന് manual installation വിവരം കാണിക്കും. നിലവിലുള്ള CLI ഉപയോഗിക്കാം. Project-local tools OS/CPU രേഖപ്പെടുത്തും; മറ്റൊരു platform-ൽനിന്ന് പകർത്തിയതാണെങ്കിൽ അത് compatible ആണെന്ന് കരുതാതെ നിർത്തും. Folder സൂക്ഷിച്ചുതന്നെ സഹായം ചോദിക്കും.

### Setup കഴിഞ്ഞ് Karen തുടങ്ങുക

**SETUP COMPLETE** കാണുമ്പോൾ:

1. README ഘട്ടം 5 പ്രകാരം `.env`-ൽ Gemini key ഇല്ലെങ്കിൽ സ്വകാര്യമായി നൽകുക. നിലവിലുള്ള key സൂക്ഷിക്കുക. Setup console-ൽ key ചോദിക്കില്ല.
2. Windows-ൽ **`start-windows.cmd`**, Mac-ൽ **`start-mac.command`** double-click ചെയ്യുക. Mac-ൽ പകരം `bash start-mac.command` നൽകാം.
3. ആ server window തുറന്നുവയ്ക്കുക. **http://localhost:8080** തുറന്ന് ആദ്യം text, ശേഷം browser recording പരിശോധിക്കുക. ഇത് default port ആണ്.
4. Board tools തിരഞ്ഞെടുത്തെങ്കിൽ README ഘട്ടം 8-ലെ manual downloads ഒഴിവാക്കാം. Project folder-ൽ രണ്ടാമത്തെ PowerShell തുറക്കുക (Window B). ഘട്ടം 9-ലെ compile check-നും തുടർന്ന് port/WiFi/upload/wiring-നും പോകുക. `scripts/board.py` commands ശരിയായ CLI/local SDK സ്വയം കണ്ടെത്തും. Bootstrap ബോർഡിലേക്ക് upload ചെയ്യുന്നില്ല.

ഓരോ ദിവസവും start launcher മതി. Setup വീണ്ടും വേണ്ട. Port 8080 നേരത്തേ ഉപയോഗത്തിലാണെങ്കിൽ നിലവിലുള്ള server ഉപയോഗിക്കുക അല്ലെങ്കിൽ അത് നിർത്തുക. Launcher മറ്റൊരു process സ്വയം നിർത്തില്ല. `PORT` മാറ്റിയിട്ടുണ്ടെങ്കിൽ browser-ലും ആ port ഉപയോഗിക്കുക.

### നേരിട്ട് commands ഉപയോഗിക്കാം

Menu ഒഴിവാക്കാൻ project folder-ൽനിന്ന്:

```powershell
.\bootstrap-windows.cmd --firmware --controller esp32_s3 --compile
```

```bash
bash bootstrap-mac.command --firmware --controller esp32_s3 --compile
```

Board tools install/verify ചെയ്ത് **example** firmware compile ചെയ്യും. Upload ചെയ്യില്ല; private WiFi credentials ഉപയോഗിച്ച് compile ചെയ്യുകയുമില്ല. Classic board-ന് `--controller esp32` നൽകുക. Computer-only setup-ന് `--firmware --compile` ഒഴിവാക്കുക.

Setup ഘട്ടങ്ങളോ AI request-ഓ നടത്താതെ installation പരിശോധിക്കാൻ:

```powershell
.\bootstrap-windows.cmd --check
```

```bash
bash bootstrap-mac.command --check
```

Arduino കൂടി പരിശോധിക്കാൻ `--firmware` ചേർക്കുക. Package imports/versions-ഉം settings file ഉണ്ടോ എന്നും പരിശോധിക്കും. Arduino-യുടെ സ്വന്തം metadata/cache പരിശോധനകൾ നടക്കാം. ഇത് വിജയിച്ചതുകൊണ്ട് Gemini key, speech services, യഥാർഥ board memory, wiring എന്നിവ ശരിയായെന്ന് തെളിയില്ല. Live diagnostic README ഘട്ടം 6-ൽ വേറെയുണ്ട്.

`--dev` നൽകിയാൽ test dependencies കൂടി install ചെയ്യും. Supported Python ഉപയോഗിച്ച് `python scripts/bootstrap.py` എന്നും നേരിട്ട് തുടങ്ങാം. Arguments ഇല്ലാത്ത interactive run-ൽ മാത്രമാണ് സാധാരണ menu വരുന്നത്.

### Setup നിർത്തിയാൽ

അവസാന message ആദ്യം വായിക്കുക. രഹസ്യവിവരങ്ങൾ നീക്കിയ log `.tools/bootstrap.log`-ൽ ഉണ്ട്. സഹായത്തിന് `.env` / `config.h`-ന്റെ raw screenshot അയയ്ക്കരുത്. Internet/disk പ്രശ്നം ശരിയാക്കിയശേഷം അതേ setup വീണ്ടും നടത്താം. നിലവിലുള്ള settings സൂക്ഷിക്കും; Arduino CLI പിന്തുണയ്ക്കുന്നിടത്ത് ഭാഗിക downloads നിലനിർത്തും.

Installation ശരിയാക്കാൻ `.env`, `.env.local`, saved memory എന്നിവ delete ചെയ്യരുത്. Environment/tool folder മറ്റൊരു OS-ലേതാണെങ്കിൽ പറഞ്ഞ folder മാത്രം മാറ്റിവയ്ക്കാൻ ഉടമയുടെ സഹായം തേടുക. പകുതിയിൽ നിർത്തിയ download വിജയിച്ച setup അല്ല. ബന്ധപ്പെട്ട പരിശോധന വിജയിക്കാതെ hardware ഘട്ടത്തിലേക്ക് പോകരുത്.

### പരിശോധിച്ചതിന്റെ പരിധി

Mac-ൽ fresh setup, വീണ്ടും setup, private files സംരക്ഷിക്കൽ, native start launcher/Flask health, official CLI checksum/execution, യഥാർഥ S3 example build എന്നിവ പരിശോധിച്ചു. Fresh board build നിലവിലുള്ള ശരിയായ Mac core/library packages ഉപയോഗിച്ചു. പുതിയ isolated SDK folder-ലേക്കുള്ള installation regression tests-ൽ പരിശോധിച്ചതാണ്; വീണ്ടും പല GB download നടത്തിയിട്ടില്ല. Windows runner-ൽ native `.cmd` tests, computer-only bootstrap/check, server health എന്നിവ വിജയിച്ചു. വിദ്യാർത്ഥിയുടെ PC-യിൽ board-tool setup/upload ഇനിയും പരിശോധിക്കണം. Bootstrap physical upload-ഓ പണം ചെലവാകുന്ന/live AI request-ഓ നടത്തുന്നില്ല.
