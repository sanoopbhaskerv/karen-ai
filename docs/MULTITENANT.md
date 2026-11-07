# Client-specific Karen installations

This branch starts from `codex/aws-cloud-server` and adds `multitenant:create_service()` as the server entry point. Existing root URLs, the existing device token, saved memory, creator identity, Malayalam voice and science-fair research remain the default installation. New clients get independent memory, conversation history, CSRF sessions, provider instances and asynchronous request/replay caches.

## Identify a client

Each registered ESP32 receives its own random bearer token. The server resolves that credential to a client profile on every POST and poll; language, names, transcripts and user-supplied IDs never select an identity. An optional `X-Client-ID` must match the authenticated client. Unknown tokens fail authentication; another client's token cannot access a mounted client URL or its results.

The existing firmware works without protocol changes: keep `SERVER_ORIGIN` as the HTTPS origin, set the client's private `KAREN_DEVICE_TOKEN` and trusted `ROOT_CA`, select `--controller esp32` for a classic board, then upload. Its requests remain `POST /chat` and `GET /requests/<id>`. Do not flash a newly registered token until this branch and its registry are deployed together.

Browser access is `/clients/<id>/`, using that client's generated admin username/password. Client administrators can edit only their own memory. Browser requests, forms, assets and CSRF refreshes stay within that URL prefix. Device credentials grant voice submission/polling only. The installation owner's existing credentials control registration, not client browser login.

## Register a client

Use a private JSON profile, for example:

```json
{
  "id": "example-learner",
  "name": "Example Learner",
  "grade": 7,
  "location": "Example town",
  "controller": "esp32",
  "language": "en",
  "science_context": false
}
```

`language` is the reply and voice language (`en` or `ml`), independent of whether the question is Malayalam or English. Registered OpenAI clients use bilingual `gpt-transcribe` language hints; other transcription models use automatic language detection. Gemini registered clients use native audio transcription with a Malayalam/English instruction. Speech synthesis uses the configured language. Science-fair lookup and its implicit exhibition/creator identity are absent for general-learning clients. Grade informs the teaching level; full name/location stay in the private administrative registry and are not inserted into prompts or public health responses.

Registration options:

- `POST /api/clients` with installation-owner HTTP Basic credentials over HTTPS and a JSON profile. The 201 response returns a device token and client admin password once; store it privately. `GET /api/clients` lists profiles without credentials, for the owner only. Duplicate/invalid IDs fail; IDs cannot be used as file paths.
- Local CLI, using the same registry as the server:

```bash
.venv/bin/python scripts/register_client.py \
  --registry data/clients.sqlite3 \
  --profile .tools/clients/example-profile.json \
  --credentials .tools/clients/example-access.json
```

The CLI refuses to overwrite an existing credentials file and prints only its path. SQLite stores credential hashes, not raw tokens/passwords. Registry files contain personal information: keep them private and back them up securely with the client memories. Never commit profiles or credentials. The live registry defaults to `clients.sqlite3` beside `MEMORY_PATH`; `CLIENT_REGISTRY_PATH` overrides it. Child memory files are stored in `clients/<id>/memory.txt` beside the registry.

## Run and deploy

Local: run `python app.py` (now starts the tenant-aware service), or `gunicorn --workers 1 --threads 4 'multitenant:create_service()'`. Docker uses the same entry point. The existing `/app/data` volume retains both registry and client memory files. Transfer the prepared registry and matching client memories privately into that volume before provisioning devices. Preserve existing memory, credentials and certificates. This branch does not deploy automatically.

Provider API credentials and billing remain installation-wide; this version does not add per-client quotas or billing.

Use one application worker: conversations and pending jobs remain process-local. The first version supports at most 32 registered clients, with 16 retained jobs per registered client in the ten-minute replay window (root legacy cache remains unchanged). A full client cache returns busy until retained jobs expire. Restarting loses in-flight jobs/history but preserves registration/memory. Registration/settings management is currently API/CLI; there is no registration dashboard, credential rotation or profile update endpoint yet. Horizontal scaling needs a shared job/session store before adding workers.

Run `python -m pytest -q` and, with Playwright installed, `node tests/browser_multitenant.cjs` plus `node tests/browser_recording.cjs`. Set `KAREN_PYTHON` for the new browser check if the environment is outside `.venv`.

Tests use fake providers for authentication, concurrent tenant separation, cross-client replay denial, per-client memory/CSRF, registered-language prompts/transcription/TTS, and legacy regressions. These checks do not replace real microphone/language listening tests on a newly provisioned ESP32.

OpenAI transcription parameter reference: [Create transcription](https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create).

## Watch ESP32 logs on a Mac

Double-click `monitor-mac.command` in the project root, then paste the controller's actual USB serial port from the displayed list. From Terminal you can pass the port directly:

```bash
./monitor-mac.command /dev/cu.usbserial-0001
```

The launcher uses this checkout's firmware configuration for credential redaction, opens 115200 baud and appends timestamped logs to `.tools/serial.log`. Keep the Terminal window open while pressing the external question button. Ctrl+C closes the monitor; close it before another upload. A missing USB serial port requires reconnecting the board with a USB data cable. The Serial Monitor does not start a local backend; cloud-configured boards continue to use AWS.
