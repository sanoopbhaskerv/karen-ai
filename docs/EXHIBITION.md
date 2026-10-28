# Exhibition runbook

## Before leaving

- Compile and flash on the actual board; complete every acceptance step below.
- Keep a copy of the source ZIP, latest memory text, hotspot credentials, and deployment URL.
- Charge the phone and power bank. Verify 2.4 GHz hotspot connectivity and mobile data at the venue.
- Verify Gemini key/model/quota. Keep the key on the server only.
- Confirm the hosted process stays awake, the URL is reachable, TLS works from ESP32 and saved memory survives the restart procedure you will use.

## Live acceptance test (not yet performed)

1. Start the server with `DEMO_MODE=0` and open the dashboard. Check `/health` reports live and configured; this is a configuration check, not a provider connectivity test.
2. Text: ask `നിന്റെ പേര് എന്താണ്?` Expect Malayalam identifying Karen.
3. Ask `നിന്നെ ആരാണ് നിർമ്മിച്ചത്?` Expect Sreehari V / the supplied school details.
4. Edit memory to add `Sreehari's favorite food is biryani.` Save. Ask `ശ്രീഹരിയുടെ ഇഷ്ടഭക്ഷണം എന്താണ്?` Verify the new fact.
5. Ask a follow-up referring to the previous response. Confirm context is retained. Use New chat and confirm history is cleared.
6. Restart the server. Confirm the new permanent fact remains and session history is empty.
7. Browser microphone: speak a Malayalam question. Hear a complete MP3 reply. Check microphone permission and HTTPS if unavailable.
8. ESP32: confirm boot WiFi logs, then record the same question with the button. Hear a clear complete reply without clipping.
9. Disconnect mobile data. Confirm the system fails visibly and recovers when connectivity returns. Do not expect newly synthesized speech during an outage.
10. Run ten consecutive hardware turns to check memory pressure, timeout handling, I2S reinitialization and flash cleanup.

## Suggested demonstration

Introduce the creator → ask Karen who made it → ask a science question → ask a follow-up → edit a personality fact on the phone → ask about that fact → explain that a small device handles audio while the cloud performs speech and reasoning.

Use the dashboard text chat if the physical microphone/speaker fails. If all internet access fails, use explicitly labelled demo mode only to show the interface; explain that its replies are scripted.

## Troubleshooting

| Symptom | Check |
|---|---|
| Setup needed | Server key environment variable and restart |
| AI unavailable | Key, model access, quota, outbound network |
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
