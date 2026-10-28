# Karen AI — English guide, step by step

**[മലയാളത്തിൽ വായിക്കാൻ ഇവിടെ അമർത്തുക → READMEMALAYALAM.md](READMEMALAYALAM.md)**

Karen is a Malayalam-speaking science exhibition project by **Sreehari V, Class 9S, PKMMHSS Edarikode**. This guide assumes you are setting it up for the first time. You do not need to understand all the code before you begin.

**Start with the computer. Connect the microphone and speaker only after the computer tests work.** You can finish Steps 2–9 without connecting any electronics.

## 1. Know what each part does

| Word or part | Simple meaning |
|---|---|
| Backend / server | The Python program running on your computer. Keep this program open while using Karen. |
| Dashboard | The Karen page you open in a web browser. You can type, record a question and edit Karen's saved facts here. |
| ESP32 controller | The small board that records sound and plays the reply. It connects to the computer over WiFi. |
| Firmware | The program placed inside the controller. |
| Compile / build | Check the firmware and turn it into a file the board can run. This does not put it on the board. |
| Upload / flash | Copy the compiled firmware onto the board through USB. |
| API key | A private password that lets the backend use Gemini. Keep it private. |
| COM port | The name Windows gives the board's USB connection, such as COM5. Your number may be different. |
| GPIO | A numbered signal pin on the controller. Use the printed number, not the pin's position in the row. |

When everything is connected:

```text
You speak → microphone → controller → computer + internet
          → Malayalam reply → controller → amplifier → speaker
```

The computer is still needed after uploading. The board does not run Gemini by itself. Live chat, speech recognition and speech output need internet. You can use a phone hotspot; the board needs a 2.4 GHz WiFi connection.

### Which controller is yours?

| What is written on the board/module? | Setting to use |
|---|---|
| HW678 board, module marked Sixspan S3-N16R8, two USB-C sockets | `KAREN_CONTROLLER=esp32_s3` — this is the board in your photos |
| Original classic ESP32, 38 pins, Micro-USB | `KAREN_CONTROLLER=esp32` |

The instructions below use the **photographed S3 board**. Both boards use the same Python backend. Their microphone, amplifier and button pins are different.

### Before the hardware stage

You will need the controller, a USB **data** cable, INMP441 microphone, MAX98357A I2S amplifier, passive speaker, external momentary push button and wires. A charge-only cable will not upload code. The amplifier is still being sourced; you can test the computer and microphone path before it arrives.

Ask an adult to help with soldering and amplifier power connections. Unplug power before moving wires. Give the microphone **3.3 V**, never 5 V. Do not connect a speaker directly to the controller.

## 2. Open the project and PowerShell

1. Get the updated project folder from the project owner. If you received a ZIP, right-click it and choose **Extract All**. Do not run the project inside the ZIP.
2. Open the extracted folder. You must be able to see `app.py`, `requirements.txt`, this `README.md`, `scripts` and `firmware`.
3. There may be a second folder inside the extracted folder. Open it if needed to find `app.py`.
4. In File Explorer, click the address bar at the top, type `powershell`, then press Enter. This opens PowerShell in that folder.
5. Paste this command into PowerShell and press Enter:

```powershell
Test-Path .\app.py
```

**Check:** it must print `True`. If it prints `False`, open the correct folder before continuing.

Commands in boxes marked `powershell` go into PowerShell. Do not paste them into the browser or into a Python window showing `>>>`. Copy one command at a time. A block containing `{` and `}` can be pasted as a whole. Wait for it to finish before the next block.

The repository is private. If downloading from GitHub, ask the owner for access to the updated files. While PR #1 is open, the updated code is on branch `fix/gemini-diagnostics-and-commissioning`, not the original `main` import.

If a project folder already works, keep its `.env`, `.env.local`, `data/memory.txt` and `firmware/karen_ai/config.h`. Do not replace these with blank example files.

## 3. Install Python once

For a new Windows setup, use **Python 3.14**, which is also the Python series used by the tested Mac environment. A working existing Python 3.12 virtual environment can stay as it is.

**Already have a working `.venv` on this Windows PC?** Skip the installer and the `py -3.14` check below; continue at Step 4. Its creation command leaves an existing `.venv` alone.

1. Open the [official Python Windows downloads page](https://www.python.org/downloads/windows/).
2. Find a current **Python 3.14.x** release. For a usual Intel/AMD Windows PC, choose **Windows installer (64-bit)**. Use the normal installer, not the embeddable ZIP or source code. If the computer is an ARM model, ask an adult to help select the matching installer.
3. Run the installer. Tick **Add python.exe to PATH** if that option is shown, then choose **Install Now**. Allow the Python launcher to be installed.
4. Close PowerShell. Open a fresh PowerShell in the project folder as in Step 2.
5. Check the installation:

```powershell
py -3.14 --version
```

**Check:** it should print `Python 3.14` followed by a patch number. If `py` is not recognised, reopen PowerShell and check that Python and its launcher were installed. Do not continue until this works.

## 4. Install the project's Python packages once

A virtual environment is a separate place for this project's Python packages. It is stored in `.venv`. Do not copy a Mac `.venv` onto Windows; each computer needs its own.

```powershell
if (-not (Test-Path .venv)) { py -3.14 -m venv .venv }
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This download may take a few minutes. Leave internet connected and wait for PowerShell's prompt to return. If the final lines contain an installation error, fix that before continuing.

**Check:** this should print a Python version:

```powershell
.\.venv\Scripts\python.exe --version
```

Use this `.venv` Python path for the remaining Windows commands. You do not need to run an activation script or change PowerShell's execution policy.

## 5. Create the computer's settings file

Create `.env` only if it is missing:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Open it:

```powershell
notepad .env
```

For the photographed S3 board, the important lines should look like this. **Replace `PASTE_YOUR_PRIVATE_KEY_HERE` with the real Gemini key. Do not leave that example text.**

```dotenv
GEMINI_API_KEY=PASTE_YOUR_PRIVATE_KEY_HERE
GEMINI_MODEL=gemini-3.5-flash-lite
DEMO_MODE=0
PORT=8080
MEMORY_PATH=data/memory.txt
KAREN_CONTROLLER=esp32_s3
```

Do not erase other existing lines. Leave an existing `SECRET_KEY` unchanged. For local testing, an empty `SECRET_KEY` lets the app create one automatically; a browser page may need refreshing after a restart.

Press **Ctrl+S**, then close Notepad. Use Save, not Save As: the file must be named `.env`, not `.env.txt`.

If you change `.env` after starting the server, stop Window A with Ctrl+C, run `app.py` again and refresh the browser. Settings are read when the server starts. PowerShell environment values override `.env.local`, which overrides `.env`. If an edit seems ignored, ask the owner to check those overrides without deleting private settings.

**Check the filename without showing your key:**

```powershell
Test-Path .\.env
```

It must print `True`. If File Explorer shows `.env.txt`, enable **File name extensions** under View and correct the name. Do not post the file's contents or a screenshot of the key.

Use a Gemini key supplied securely by the project owner or configured in [Google AI Studio](https://aistudio.google.com/apikey) with help from a parent/teacher. Ask them before enabling billing or increasing quota. Do not put this key in `config.h` or send it to other people.

`gemini-3.5-flash-lite` passed real Malayalam tests with the existing project key. Another account can have different model access. If the diagnostic below fails, use the troubleshooting section rather than guessing another model name. Gemini 1.5 is retired; a new key will not bring it back.

## 6. Test Malayalam text on the computer

In the same PowerShell window, run:

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_gemini.py
```

This lists available models and then makes a real test request. It uses the key privately. It does not change Karen's saved facts.

**Check:** look for `"inference": "succeeded"` and a Malayalam reply. A list of model names alone is not a successful chat test. If you see `"inference": "failed"`, use Step 16.

Now start the server:

```powershell
.\.venv\Scripts\python.exe app.py
```

1. Keep this window open. Call it **Window A — server**. It will be busy running the app; that is normal.
2. Open Chrome or Edge.
3. Type **http://localhost:8080** into the browser's address bar.
4. In the chat box, type `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` and click the arrow to send.
5. Wait for the Malayalam reply. Try `മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?` next.

**Check:** you should get real answers about Sreehari and rain. If you only hear/read an apology, the request has failed; look at Window A for the error code. Do not press Send repeatedly while waiting.

`http://localhost:8080/health` shows the app's status. `configured: true` only means a key is present. `gemini.status: ready` describes the last successful generation. It does not guarantee that the next request will succeed.

## 7. Test computer recording and saved memory

You still do not need the controller or amplifier for this step.

### Record a question

1. Use the dashboard at **localhost:8080 on the computer**.
2. Click **Record a question**.
3. Allow microphone access if the browser asks.
   Use the laptop's microphone or a connected headset/USB microphone. The INMP441 is for the controller; it is not a computer microphone by itself.
4. Watch for **Listening for 5 seconds…**. Ask a short Malayalam question during those five seconds.
5. Wait while the page shows that Karen is processing it.
6. Listen to the reply. If it does not play automatically, click Play on the audio player. Use headphones or the computer's speakers.

**Check:** the answer should be understandable Malayalam and the page should say **Reply ready**. A spoken apology still means a failure. Check the error in Window A.

### Edit what Karen remembers

The **What Karen remembers** box contains facts saved in `data/memory.txt`.

1. Keep the existing creator, class and school information.
2. If you want to add a real fact for the exhibition, first make a private backup of `data/memory.txt`, for example another copy inside the `data` folder.
3. Add the fact, then click **Save memory**.
4. Ask a question about it to check the answer.

Saving memory starts a new conversation. **New chat** clears the conversation but keeps saved facts. Restarting the server also clears the conversation and keeps saved facts. These facts are shared by everyone using this dashboard; do not add private information.

**Finish this computer stage before moving on.** If text and browser voice do not work, connecting more wires will not fix the AI service.

## 8. Install the board tools once

Leave Window A running. Open a **second PowerShell in the project folder** using Step 2. Call it **Window B — board tools**. Use Window B for Steps 8–14.

Create a folder for Arduino CLI:

```powershell
New-Item -ItemType Directory -Force .tools
```

1. Open the [official Arduino CLI installation page](https://arduino.github.io/arduino-cli/1.5/installation/).
2. Under Download, get the Windows 64-bit ZIP for a usual Intel/AMD PC.
3. Extract the ZIP.
4. Copy `arduino-cli.exe` into the project's `.tools` folder. The result must be `.tools\arduino-cli.exe`, not another nested folder.

Check the file:

```powershell
Test-Path .\.tools\arduino-cli.exe
```

It must print `True`. Then run these commands in Window B:

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

**Check:** each command must finish without an error. The core is a large download and includes other ESP32 chip types too. Do not close the window during installation. You do not need to reinstall these for every exhibition session.

## 9. Select the controller and compile without uploading

For the photographed board:

```powershell
$env:KAREN_CONTROLLER = 'esp32_s3'
.\.venv\Scripts\python.exe scripts\firmware.py
```

**Check:** the first lines should include `Controller: esp32_s3` and `Credentials: example only`. At the end, look for **Sketch uses ...** and no compile error.

This checks the code with example settings. It does **not** upload anything and does not test your actual WiFi settings. It is safe to run without a board connected.

If using the original classic ESP32 instead, change the first line to `$env:KAREN_CONTROLLER = 'esp32'`. Use its different wiring column in Steps 13–14.

The PowerShell value overrides `.env` in that window. To return to the `.env` setting, run `Remove-Item Env:KAREN_CONTROLLER`. Changing this setting does not change a board already programmed: build and upload again for a different controller. The Python backend itself serves both boards.

## 10. Connect only the board and find its port

1. Leave microphone, button and amplifier disconnected for now.
2. On the S3 board, use the USB-C connector labelled **COM** on the back. The other one is native USB/USB-OTG. This setup uses COM for uploading and Serial Monitor. On the original classic board, use its Micro-USB data connector.
3. Connect it to the Windows PC with a data cable.
4. In Window B, run:

```powershell
& $karenArduinoCli board list
```

Look for a port such as `COM5`. You can also check Windows **Device Manager → Ports (COM & LPT)**. The name of the board may be unknown even when its port is listed.

Set the port variable below. **Replace COM5 with the number actually shown for your board.**

```powershell
$karenPort = 'COM5'
```

Check the chip and flash size:

```powershell
.\.venv\Scripts\python.exe -m pip install esptool
.\.venv\Scripts\python.exe -m esptool --port $karenPort flash-id
```

**Check:** for the photographed S3 profile, expect an ESP32-S3 and 16 MB flash. The original classic profile targets ESP32 / 4 MB. If the measured chip or size does not match the selected profile, ask the project owner to check it before uploading. The marking on the metal shield is not the same as measuring the flash.

If no COM port appears, try a known data cable and another USB port. Ask an adult to help identify the USB-UART chip before installing its manufacturer's driver. Do not assume this S3 board uses the classic board's CP2102 driver. Do not erase the flash as a first troubleshooting step.

## 11. Give the board its WiFi settings and the computer's address

There are two different settings files:

| File | What goes here? |
|---|---|
| `.env` | Computer settings, including the private Gemini key and controller selection |
| `firmware/karen_ai/config.h` | Board's WiFi name/password and the backend computer's address. No Gemini key. |

In Window B:

```powershell
if (-not (Test-Path firmware\karen_ai\config.h)) {
    Copy-Item firmware\karen_ai\config.example.h firmware\karen_ai\config.h
}
notepad firmware\karen_ai\config.h
```

Replace only the example WiFi name, password and server address. Keep the quotation marks:

```cpp
#define WIFI_SSID "YOUR_2_4_GHZ_HOTSPOT"
#define WIFI_PASSWORD "YOUR_HOTSPOT_PASSWORD"
#define SERVER_ORIGIN "http://192.168.1.50:8080"
```

Those are examples, not real credentials. Replace both `YOUR_2_4_GHZ_HOTSPOT` and `YOUR_HOTSPOT_PASSWORD` with your actual WiFi details, inside the quotes. To find your Windows computer's address, run:

```powershell
ipconfig
```

Find **IPv4 Address** under the adapter connected to your WiFi/hotspot. Use that address in place of `192.168.1.50`. Do not use the Default Gateway address. If the backend runs on the Mac instead, use the Mac's LAN IP.

Keep `http://` and `:8080`. Do not add `/` at the end. Do not use `localhost` here: on the board, that would refer to the board itself. Connect the board and backend computer to a network where they can reach each other. If Windows Firewall asks, allow the Python server on your trusted private network; do not turn the firewall off globally.

Leave `STATUS_LED=-1`, `RECORD_SECONDS=5`, `MIC_SHIFT=16` and the `ROOT_CA` block unchanged for this local HTTP test. The onboard RGB LED stays unused. Save with Ctrl+S. The file must be `config.h`, not `config.h.txt`.

If this file came from the old classic setup, ask the project owner to remove only old `MIC_*`, `AMP_*` and `BUTTON_PIN` pin definitions when moving to S3. Preserve WiFi and certificate settings. The adapters now supply the correct defaults.

Cloud HTTPS is a later step. It needs a trusted root certificate; do not disable certificate checks to make it work.

## 12. Upload to the board, then check its messages

Use Window B with the controller and port variables already set:

```powershell
.\.venv\Scripts\python.exe scripts\firmware.py --use-config
```

**Check:** it must compile successfully and show `Credentials: private config.h`. This still does not upload.

Now upload:

```powershell
.\.venv\Scripts\python.exe scripts\firmware.py --upload --port $karenPort
```

Wait for upload to finish without an error. This command builds again using your private settings and then uploads. Untouched example WiFi placeholders are refused.

Open Serial Monitor:

```powershell
& $karenArduinoCli monitor --port $karenPort --config baudrate=115200
```

Press the board's **RST** button once to see startup messages. For S3, look for:

```text
Controller: esp32_s3
MIC BCLK/WS/SD: 4/5/6 | AMP BCLK/WS/DIN: 16/17/18 | button: 7
Connected: ...
Ready. Press button, then speak for five seconds.
```

The first line also reports flash and PSRAM bytes. Expected advertised S3 capacities are **16,777,216 flash bytes** and **8,388,608 PSRAM bytes**. Ask for help if they differ or it keeps restarting. The LED staying off is normal.

Use Serial Monitor for the board's connection/Ready messages. The dashboard does not track whether a physical board is online.

For the classic board, expect `Controller: esp32` and the classic pins from the tables below. Many classic boards have no PSRAM; zero PSRAM is normal on those boards.

If upload cannot connect, close Serial Monitor first. Try holding **BOOT**, briefly pressing **RST**, then starting the upload and releasing BOOT when it connects. Use the onboard BOOT button only for this procedure; it is not the question button.

Press Ctrl+C in **Window B** to close Serial Monitor before the next upload. This does not stop the server in Window A. If you edit WiFi or server settings in `config.h`, upload again; saving the file alone cannot update the board.

## 13. Connect the microphone and external question button

**Unplug the USB cable first.** Check the labels on the actual microphone; its pin order can vary. Use one row at a time.

| INMP441 / button connection | Photographed S3 `esp32_s3` | Original classic `esp32` |
|---|---|---|
| Microphone VDD | 3V3 | 3V3 |
| Microphone GND | GND | GND |
| Microphone SCK / BCLK | GPIO4 | GPIO26 |
| Microphone WS | GPIO5 | GPIO25 |
| Microphone SD | GPIO6 | GPIO33 |
| Microphone L/R | GND | GND |
| One side of external momentary button | GPIO7 | GPIO32 |
| Other side of external button | GND | GND |

A four-leg button often has two legs already joined on each side. Ask an adult to check which pair connects only when pressed. Do not choose legs that are always connected. Do not wire the external button to 3V3 or 5V; the firmware supplies an internal pull-up.

Reconnect USB, reopen Serial Monitor, and wait for Ready. Press and release the external button once. When you see **Recording. Speak now.**, speak a short question for five seconds. Then wait.

Without the amplifier, no board speaker sound is expected yet. A server result of `ok` in Serial Monitor and a question/reply visible after refreshing the dashboard help check the microphone path. `spoken-error` is a failed request, not a successful answer. Do not press repeatedly while Karen is busy.

## 14. Add the MAX98357A amplifier and speaker

If you do not have the MAX98357A yet, stop at the computer/microphone tests. **A PAM8403 does not replace it in this firmware.**

Unplug power. Have an adult check the amplifier's actual labels, soldering and 5 V power arrangement before connecting it. Do not guess which ESP32 supply pin can power the amplifier.

| MAX98357A / speaker connection | Photographed S3 `esp32_s3` | Original classic `esp32` |
|---|---|---|
| BCLK | GPIO16 | GPIO27 |
| LRC / WS | GPIO17 | GPIO14 |
| DIN | GPIO18 | GPIO22 |
| VIN | Suitable verified 5 V supply | Suitable verified 5 V supply |
| GND | Common GND with controller | Common GND with controller |
| SD / EN | Follow the actual breakout's enable instructions | Same |
| Speaker's two wires | Amplifier SPK+ and SPK− only | Same |

Neither speaker wire goes to GND or to a controller GPIO. Keep the computer's USB power separate from any external 5 V connection to the board unless the actual power circuit has been checked. A separately powered amplifier still needs common GND with the controller. Never put 5 V on microphone VDD or a GPIO.

The speaker's latest box says **4 ohms / 10 watts**. Check the marking on the speaker itself. That rating does not make the amplifier produce 10 watts. Firmware starts at low playback gain; do not increase it until the supply is stable and an adult has checked the wiring.

Reconnect power. Wait for Ready. Ask one short question using the external button. Listen for a complete Malayalam reply. If it restarts, becomes hot or the sound clips badly, disconnect power and check the supply/wiring with help. Run ten normal questions successfully before using it at the exhibition.

## 15. What to do each day

You do not need to install packages or upload again every day.

1. Connect the computer to internet. Keep the board on the reachable 2.4 GHz network.
2. Open PowerShell in the project folder.
3. Start the server:

```powershell
.\.venv\Scripts\python.exe app.py
```

4. Open **http://localhost:8080**. Test one text question.
5. Power the already-programmed board. Wait for Ready, then test one button question.
6. If the computer's IP address or WiFi details changed, update `config.h` and upload again.
7. Keep the server window open and the computer awake during the demonstration. Closing the lid or letting it sleep can stop access.

To stop: wait for the reply to finish, switch off/unplug the board, then press **Ctrl+C in the server window**. Saved memory remains; conversation history clears when the server restarts.

On a phone on the same network, `http://<computer-IP>:8080` supports text and memory editing. Phone microphone recording usually needs trusted HTTPS; use **localhost on the computer** for the first recording test.

For the exhibition, prepare three short questions, a follow-up, a charged power bank and the computer dashboard as a fallback. If internet fails, new cloud answers will not work. `DEMO_MODE=1` is only a clearly labelled scripted text demo; voice is disabled. Return it to `0` and restart for live use. See the [exhibition checklist](docs/EXHIBITION.md).

The dashboard has no login by design. Anyone who can reach it can view/change the shared memory and use the API quota. Use the trusted exhibition network and stop the server afterward.

## 16. If something goes wrong

Start with the exact message in the browser, server Window A or Serial Monitor. Do not keep reinstalling everything.

| What you see | Try this first |
|---|---|
| `Test-Path .\app.py` says `False` | Open the extracted folder that actually contains `app.py`. |
| `py` is not recognised | Reopen PowerShell after installing Python and its launcher. |
| `.venv\Scripts\python.exe` is missing | Finish Step 4 on this Windows PC; do not copy a Mac `.venv`. |
| `ModuleNotFoundError` | Use the `.venv` Python command and reinstall `requirements.txt` from the project folder. |
| Browser says it cannot connect | Keep Window A running; read its error. Check the URL and port 8080. |
| Port 8080 is already in use | A server may already be running. Use that one or stop the old one before starting another. |
| `Page expired` | Refresh the dashboard after restarting the server. |
| `model_auth` / 401 or 403 | Check the private Gemini key and account/project restrictions with the owner. |
| `model_not_found` / 404 | Run the diagnostic; ask the owner to choose an available exact model ID. Do not switch to retired 1.5. |
| `model_quota` / 429 | Wait and ask the owner to check quota. Do not enable billing yourself. |
| `model_unavailable` / 503 | Provider may be busy; limited retries already happen. Wait, then try a new question. |
| `model_timeout` / 504 | The AI did not finish before the deadline. Read the diagnostic; a longer wait alone is not a verified fix. |
| HTTP 505 | HTTP version not supported. This differs from 504; show the owner the error code without keys. |
| `busy` or a request ID after a long wait | Let the current job finish. Check `http://localhost:8080/requests/` followed by that ID before sending the same question again. Results last ten minutes in the same running server. |
| Recording unavailable | Use localhost on the computer and allow the correct microphone in the browser. |
| `stt_unavailable` or `tts_unavailable` | Check internet and the server log; cloud speech may be unavailable. |
| No COM port | Use the COM connector, a data cable and the correct identified USB-UART driver. |
| Cannot open COM port / access denied | Close Serial Monitor or any other program using that port. Recheck its number. |
| Upload cannot connect | Confirm S3 selection, actual port and COM connector; try the BOOT/RST procedure in Step 12. |
| `Unknown KAREN_CONTROLLER` | Use exactly `esp32_s3` or `esp32`, with no extra characters. |
| Invalid/reserved/overlapping pins | Check the board selection and remove old classic pin overrides when using S3. |
| WiFi never connects | Check exact WiFi name/password and 2.4 GHz support, then upload edited settings again. |
| Board cannot reach server | Keep Window A open; check the computer's current LAN IP, firewall and shared network. |
| Empty/unclear microphone | Check VDD=3V3, L/R=GND, the correct pin column and soldered connections. |
| No speaker sound | Confirm MAX98357A, amplifier power/enable, common GND and SPK+/SPK− wiring. |
| Board keeps restarting | Disconnect power and have the power/wiring checked before trying again. |

A request can take time. The normal browser/device wait budget is about **2 minutes 40 seconds**. Press once and wait for a reply or error. A request ID is a long code identifying one question; copy it exactly when checking its result. If the connection is lost, the same ID helps recover the result without adding another conversation turn. A server restart or result expiry ends that recovery window.

When asking for help, share the controller name, step number, COM number and error code. Hide API keys, WiFi passwords and private saved facts in screenshots. Your source repository should not include `.env`, `.env.local`, `config.h` or saved memory.

## 17. If you are using the Mac instead

The Windows commands above are for a Windows PC. On the existing project Mac:

```bash
cd /Users/sanoopbhaskerv/workspace/karen-ai
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

For a new Mac checkout only, create `.venv` first with `python3 -m venv .venv` and create `.env` only if absent. Do not replace working private settings. Board build example:

```bash
KAREN_CONTROLLER=esp32_s3 .venv/bin/python scripts/firmware.py
```

A Mac serial port looks like `/dev/cu...`, not COM5. See [hardware commissioning](docs/HARDWARE.md) for the Mac upload path.

## 18. What has been checked, and where to read more

**Recorded software checks:** 53 tests passed; classic ESP32 and S3 firmware compiled on the Mac; real Malayalam chat and a synthesized-speech WAV→MP3/browser test passed. **Not yet verified:** running these Windows steps on your PC, actual board flash/PSRAM, upload, physical microphone/speaker quality and power stability. Do not call the hardware ready until those checks pass. Full evidence is in [VALIDATION.md](docs/VALIDATION.md).

- [മലയാളം: complete beginner guide](READMEMALAYALAM.md)
- [Windows technical setup and Arduino IDE alternative](docs/WINDOWS.md)
- [Both wiring maps and hardware commissioning](docs/HARDWARE.md)
- [Exhibition checklist](docs/EXHIBITION.md)
- [Technical reference: routes, timeouts, tests and cloud hosting](docs/TECHNICAL.md)
- [മലയാളം സാങ്കേതിക വിവരങ്ങൾ](docs/TECHNICAL_ML.md)

The old detailed engineering notes are kept in those technical references. Cloud hosting is a later task; the steps above use a computer on your local network.
