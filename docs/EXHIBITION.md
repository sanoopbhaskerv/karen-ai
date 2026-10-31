# Exhibition runbook

## Before leaving

- Compile and flash on the actual board; complete every acceptance step below.
- Keep a copy of the source ZIP, latest memory text, hotspot credentials, and deployment URL.
- Charge the phone and power bank. Verify 2.4 GHz hotspot connectivity and mobile data at the venue.
- Verify Gemini key/model/quota. Keep the key on the server only.
- Confirm the hosted process stays awake, the URL is reachable, TLS works from ESP32 and saved memory survives the restart procedure you will use.
- After installing the anonymous-identity update, stop and restart every running server, then refresh the dashboard. This clears old RAM conversation and cached text/audio results as well as loading the new privacy behaviour.

## Live acceptance checklist

Mac text and synthesized-speech software checks are recorded in `VALIDATION.md`. Physical device, human microphone, venue network and hosted deployment checks remain pending. Do not edit the real saved memory merely to repeat automated tests; use a temporary copy for destructive checks.

1. Start the server with `DEMO_MODE=0` and open the dashboard. Check `/health` reports live/configured and the expected model. `gemini.status` is `untested` before the first inference. Run `python scripts/diagnose_gemini.py` for a separate live test; a model-list success alone does not validate inference.
2. Text: ask `നിന്റെ പേര് എന്താണ്?` Expect Malayalam identifying Karen.
3. Ask `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` Expect a neutral Malayalam reply without a creator name, school, class section or home details. Also ask `നീ എങ്ങനെയാണ് പ്രവർത്തിക്കുന്നത്?` and check the explanation against the actual hardware/server flow.
4. Back up permanent memory before a planned demonstration edit. Add a real approved fact, save, and ask about it. Confirm the new fact and fresh conversation. Never replace actual saved facts with test data.
5. Ask a follow-up referring to the previous response. Confirm context is retained. Use New chat and confirm history is cleared.
6. Restart the server. Confirm the new permanent fact remains and session history is empty.
7. Browser microphone: on Mac localhost, speak a Malayalam question for five seconds. Hear a complete MP3 reply. Check microphone permission and trusted HTTPS if unavailable. A phone LAN HTTP URL supports text but cannot normally record.
8. ESP32: confirm boot WiFi logs, then record the same question with the button. Hear a clear complete reply without clipping.
9. Disconnect mobile data. Confirm the system fails visibly and recovers when connectivity returns. Do not expect newly synthesized speech during an outage.
10. Run ten consecutive hardware turns to check memory pressure, timeout handling, I2S reinitialization and flash cleanup.

## Suggested demonstration

Introduce Karen and the problem it addresses → ask how it works → ask a science question → ask a follow-up → edit an approved science fact on the phone → ask about that fact → explain that the ESP32 handles audio while the server and online services perform speech processing and reasoning.

Keep the demonstration anonymous as requested. New installations use a neutral identity; startup removes the known older creator biography while preserving unrelated saved science facts. Editable memory does not override the fixed identity-privacy instructions. Registration records and the pupils' genuine construction-participation evidence remain separate from Karen's spoken/public identity; follow the applicable organiser instructions for those records.

Use the dashboard text chat if the physical microphone/speaker fails. If all internet access fails, use explicitly labelled demo mode only to show the interface; explain that its replies are scripted.

## Troubleshooting

| Symptom | Check |
|---|---|
| Setup needed | Server key environment variable and restart |
| AI unavailable | Python console stage/code/provider-code, `/health` last inference, live diagnostic |
| 504 / `model_timeout` | Deadline exceeded; test the currently selected model, not just key presence |
| 503 / `model_unavailable` | Temporary demand/provider failure; two bounded attempts already run |
| 505 | HTTP version not supported; this is different from the reproduced 504 |
| Lost browser/device response | Inspect `/requests/<id>` before another question; same ID avoids duplicate turns |
| Malayalam not recognized | Mic channel wiring, quiet environment, gain, 16-bit mono WAV |
| Empty/garbled mic | INMP441 L/R to GND, clock pins, microphone supply |
| No speaker output | Amplifier enable/VIN/GND, speaker terminals, pin mapping |
| TLS failure | Exact hostname, valid root CA, NTP connectivity/time |
| ESP32 brownout/reboot | Power source/current, amplifier wiring, decoupling |
| HTTP 400 | WAV format, duration and multipart field name `audio` |
| HTTP 413 | Upload larger than 2 MiB |
| JSON instead of MP3 | Provider failure; inspect status/dashboard rather than playing it |
| Page expired | Refresh browser for a new CSRF token after server restart |
| Memory disappears after publishing | Runtime disk was ephemeral; restore backup or use persistent hosting |

## Data and operational limits

The server sends recorded speech to Google recognition, text/history/personality to Gemini, and the reply to gTTS. Avoid private personal information during the exhibit. The server does not intentionally save audio; firmware removes its transient files. Text history is in RAM; editable personality facts are on disk. Anyone who reaches the no-login dashboard can see that shared conversation and edit memory. Stop the app or restrict ingress after the event.
