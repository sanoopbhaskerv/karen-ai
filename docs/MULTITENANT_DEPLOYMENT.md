# Multi-tenant deployment record

The multi-tenant service was deployed to the existing AWS Lightsail host at `https://sreehariv.makemykindred.com` from `codex/multitenant-languages`, application commit `abea142`.

Deployment retained a private rollback image/source/settings/data backup, verified deployed source hashes and container health, preserved the existing root memory/settings, and restored the exact pre-deployment firewall rules after temporary operator-only SSH access. The private `neeerav` registration was imported into the persistent registry without changing any existing client records. Raw tokens and personal profile details are not part of this record or Git.

Live HTTPS verification passed for:

- Original root dashboard and default Malayalam profile.
- Neeerav's English/general-learning profile and client browser login.
- English and Malayalam text input, returning English answers.
- Authenticated English and Malayalam WAV uploads, asynchronous polling and complete MP3 replies.
- Invalid device credentials and spoofed client IDs rejected; legacy credentials could not poll Neeerav's results.

The classic ESP32 configuration uses Neeerav's token, the existing private WiFi settings, and the verified cloud CA bundle. Its compiled firmware uses the classic GPIO defaults. Private configuration, credentials, test recordings and rollout details remain under ignored local files; use the existing registration/provisioning guide for future devices.

At the owner's explicit request, all three AWS cleanup schedules were extended seven days. Instance deletion is now **14 November 2026, 19:40:54 IST**, DNS deletion follows one minute later, and static-IP release follows five minutes after instance deletion. Targets, permissions and retry settings were preserved and schedule updates were read back for verification. The existing instance continues accruing AWS charges until deletion. The recorded deadlines are in `deploy/aws-test-state.json`.

The physical classic ESP32 upload was hash-verified and WiFi startup passed. A first recording returned `stt_unrecognized`; a clear retry successfully reached Neeerav's isolated AWS context, returned an English answer and a complete 38,784-byte MP3, and finished decoding. Button-to-decoder time was 13,146 ms, with all 80,000 microphone samples captured and no clipping. Legacy credentials could not read that request's result. The owner reported no audible sound, so amplifier/speaker electrical and connection checks remain pending; decoder completion is not proof of speaker output.
