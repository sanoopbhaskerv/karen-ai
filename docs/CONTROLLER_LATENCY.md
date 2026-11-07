# Controller response time / കൺട്രോളറിന്റെ മറുപടി സമയം

Browser recording and the controller use the same `/chat` speech-recognition → Gemini → speech-generation pipeline. If recorded browser voice replies quickly but the board takes 30–35 seconds **before speech starts**, compare the board stages below. Typed chat uses `/test_chat` and skips both speech services.

The board always records for five seconds with the example settings. Compare browser and board from the **start of recording to the first audible reply**, using the same short question, server and WiFi. Also note whether only the first board question is slow. `[TURN] Finished` includes the entire spoken reply and is a different measurement.

## Firmware changes

- Send `question.wav` directly as `audio/wav`; avoid a second flash copy just to add multipart wrapping. The existing server already accepts this format.
- Use HTTP/1.1 connection reuse for status polling, consuming each pending response before the next request. A server may still close a connection; existing same-request-ID recovery handles transport failures.
- Disable WiFi power saving while the voice assistant is running. This trades some power consumption for network responsiveness.
- Start HTTPS clock synchronization after WiFi connects, before recording. If time is still unavailable, explicitly try Google, Cloudflare and pool.ntp.org as primary servers for up to 15 seconds each. Reuse a synchronized clock; certificate verification stays enabled. If all attempts fail, try a network that allows NTP (UDP 123), such as another 2.4 GHz hotspot. An NTP timeout occurs before certificate validation and does not mean the root CA is wrong.
- Print recording, upload/response, download and button-to-playback timings. An updated backend also returns `Server-Timing` for recognition (`stt`), answer generation (`gemini`) and speech generation (`tts`).

These changes remove known overhead. A particular response-time improvement still needs measurement on the physical board.

## Apply and measure on Windows

Use the project revision containing this change. Keep your existing `.env`, saved memory and private `firmware/karen_ai/config.h`, including its WiFi, HTTPS address, device token and root CA. For the photographed ESP32-S3 board, close Serial Monitor and run from the project folder:

```powershell
.\.venv\Scripts\python.exe scripts\board.py ports
$karenPort = Read-Host "Type the actual COM port shown above"
.\.venv\Scripts\python.exe scripts\firmware.py --controller esp32_s3 --upload --port $karenPort --verbose
.\.venv\Scripts\python.exe scripts\board.py monitor --port $karenPort --log
```

For the classic board, select `--controller esp32` instead. After upload succeeds, ask one short question and repeat it twice, waiting for each reply to finish. The serial log is saved to `.tools/serial.log`.

| Serial timing | What it helps identify |
|---|---|
| `[MIC] Complete elapsed=…` | Capture and flash writes; normally near the configured five seconds |
| `[TLS]` clock timing | First-use clock synchronization or unavailable NTP |
| `[HTTP]` POST/header and poll timings | Upload, connection setup, backend processing and status-check overhead |
| Backend `stt`, `gemini`, `tts` timing | Time spent inside each backend stage, excluding board upload/download |
| MP3 download timing | Network transfer and writing the reply to flash |
| Button-to-playback timing | Delay until the decoder starts output; confirm the first sound by listening |
| `[TURN] Finished` | Whole interaction, including the spoken answer |

Firmware improvements work with the existing hosted server. Backend stage timing appears only after the server runs the updated backend; missing timing headers do not prevent playback. Updating the files locally does not update the AWS server or the board automatically.

Share these timing lines and the request ID for a slow turn. They can be matched to backend `request=… stage=… elapsed_ms=…` logs. Never share `config.h`, device tokens, WiFi passwords or API keys.

## മലയാളത്തിൽ

Website-ൽ **record ചെയ്ത ശബ്ദചോദ്യം** വേഗത്തിൽ മറുപടി തരുമ്പോൾ board-ൽ ശബ്ദം തുടങ്ങാൻ 30–35 സെക്കൻഡ് എടുക്കുന്നുവെങ്കിൽ, രണ്ടിലും ഒരേ `/chat` backend ആണ്. Board-ന്റെ recording, upload, HTTPS polling, MP3 download ഘട്ടങ്ങൾ വേർതിരിച്ച് സമയം നോക്കണം. Text ചോദ്യം ഇതേ താരതമ്യത്തിന് ഉപയോഗിക്കരുത്.

Board അഞ്ച് സെക്കൻഡ് record ചെയ്യും. `[TURN] Finished` കാണിക്കുന്ന സമയത്തിൽ മുഴുവൻ മറുപടി പറഞ്ഞുതീരുന്ന സമയവും ഉൾപ്പെടും. **Button അമർത്തിയത് മുതൽ ആദ്യ ശബ്ദം കേൾക്കുന്നതുവരെ** ഉള്ള സമയം പ്രത്യേകം നോക്കുക. ആദ്യ ചോദ്യം മാത്രം വൈകുന്നുണ്ടോ എന്നും ശ്രദ്ധിക്കുക.

ഈ മാറ്റത്തിൽ recording രണ്ടാമതൊരു file-ലേക്ക് copy ചെയ്യുന്നത് ഒഴിവാക്കി, status പരിശോധിക്കാൻ HTTPS connection വീണ്ടും ഉപയോഗിക്കുന്നു. WiFi power saving ഒഴിവാക്കുകയും clock sync ആവശ്യമുള്ളപ്പോൾ മാത്രം നടത്തുകയും ചെയ്യുന്നു. ഓരോ ഘട്ടത്തിന്റെയും സമയം Serial Monitor-ൽ കാണാം. Board-ൽ പരീക്ഷിച്ചശേഷമേ എത്ര സമയം കുറഞ്ഞു എന്ന് പറയാൻ കഴിയൂ.

മുകളിലെ PowerShell commands ഉപയോഗിച്ച് പുതിയ firmware upload ചെയ്ത് Serial Monitor തുറക്കുക. യഥാർഥ COM port നൽകണം. നിലവിലെ private settings മാറ്റേണ്ടതില്ല. ഒരേ ചെറിയ ചോദ്യം മൂന്ന് പ്രാവശ്യം ചോദിച്ച് ഓരോ മറുപടിയും പൂർത്തിയാകാൻ കാത്തിരിക്കുക. `.tools/serial.log`-ൽ timing lines സൂക്ഷിക്കും. പുതിയ backend server-ൽ പ്രവർത്തിക്കുന്നുണ്ടെങ്കിൽ `stt`, `gemini`, `tts` സമയവും ലഭിക്കും; പഴയ server-ലും firmware പ്രവർത്തിക്കും.

വൈകിയ ചോദ്യത്തിന്റെ timing lines-ഉം request ID-യും നൽകിയാൽ ഏതു ഘട്ടത്തിലാണ് സമയം പോകുന്നത് എന്ന് കണ്ടെത്താം. `config.h`, password, token, API key എന്നിവ അയക്കരുത്. File download ചെയ്തതുകൊണ്ട് മാത്രം board/server update ആകില്ല; board-ൽ firmware upload വേണം, server update വേറെ നടപടിയാണ്.
