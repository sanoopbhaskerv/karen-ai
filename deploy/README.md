# Temporary AWS test

The test deployment uses `https://sreehariv.makemykindred.com` on a single Ubuntu 24.04 Lightsail instance in Mumbai, from branch `codex/aws-cloud-server`. The UI links to all three Malayalam HTML guides. Local installations retain their original behavior when cloud credentials are unset.

## Cost and lifetime

The selected `micro_3_1` IPv4 bundle is $7/month: 1 GB RAM, 40 GB disk and 1 TB monthly transfer in Mumbai. Seven days is approximately $1.60 before tax, DNS queries and Gemini usage. No free-tier allowance was confirmed for this account; do not assume zero cost. The existing Route 53 hosted zone is reused. No load balancer, database, NAT gateway or additional hosted zone is needed.

AWS EventBridge Scheduler deletes the instance on **7 November 2026, 19:40:54 IST**, deletes only this test's DNS A record one minute later, and releases the static IP five minutes after instance deletion. These one-time schedules delete themselves after execution. The cleanup IAM role and SSH key have no running-server charge; the manual cleanup command below removes them too. The schedules retry transient failures, so check deletion in AWS afterward. Stopping a Lightsail instance alone does not stop its charges.

The recorded nonsecret identities and deadlines are in `aws-test-state.json`. Do not reuse these resource names for another application before cleanup. Server deletion also deletes its Docker volumes: back up permanent memory before the deadline.

Sources: [Lightsail pricing](https://aws.amazon.com/lightsail/pricing/), [billing and Free Tier](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html), [Route 53 pricing](https://aws.amazon.com/route53/pricing/).

## Access and secrets

For the deployment operator, generated credentials are saved locally at `.tools/aws/access.txt` and `.tools/aws/cloud.env` with mode 0600. Neither file is in Git, the source archive, the Docker build context or the hosted guides. Keep the owner password private; transfer the board token privately to the student; never put them in a URL or screenshot.

The UI, text/voice chat and guides are public when `KAREN_PUBLIC_UI=1`, as requested for the exhibition. Only `/admin` and saved-memory updates require owner HTTP Basic authentication over HTTPS. Public browser voice submissions require the page CSRF token; board bearer-token submissions do not need browser cookies. `KAREN_DEVICE_TOKEN` authenticates only `POST /chat` and voice-result polling. It cannot open the dashboard, edit memory, reset chat or read browser text results. `/health` remains public and does not make an AI request. Browser mutations still require CSRF tokens. Hosted session cookies are secure-only.

The AWS profile recorded for this test is `fantasy-staging`; identity and DNS checks established that it owns the `makemykindred.com` zone. The default profile points to a different account. Always verify the account before AWS changes. SSH is restricted to the operator's source IPv4 at deployment time; 8080 is internal to Docker. Only 80 (HTTPS certificate/redirect) and 443 are public.

## Deploy or update the application

Prepare an Ubuntu 24.04 host with `server-bootstrap.sh` using `sudo sh server-bootstrap.sh`. Lightsail wraps user data in `/bin/sh`, so the script intentionally uses POSIX shell. Docker starts automatically after a host reboot, and the containers use `unless-stopped` restart policies.

Copy the repository source to `/opt/karen-ai` over SSH, excluding Git, `.tools`, `.venv`, `.env*`, private firmware configuration and saved data. Place a private `deploy/.env` on the server with:

```dotenv
KAREN_DOMAIN=sreehariv.makemykindred.com
GEMINI_API_KEY=SET_PRIVATELY
GEMINI_MODEL=gemini-3.5-flash-lite
SECRET_KEY=GENERATE_A_LONG_RANDOM_VALUE
KAREN_ADMIN_USERNAME=karen
KAREN_ADMIN_PASSWORD=GENERATE_A_LONG_RANDOM_VALUE
KAREN_DEVICE_TOKEN=GENERATE_A_DIFFERENT_RANDOM_VALUE
KAREN_PUBLIC_UI=1
```

Restrict this file to mode 0600. From `/opt/karen-ai/deploy`:

```bash
sudo docker compose config --quiet
sudo docker compose up --build --detach
sudo docker compose ps
```

Caddy obtains a Let's Encrypt certificate and proxies HTTPS to Gunicorn on the internal Docker network. Its upstream response timeout is 155 seconds. Keep **one app instance, one Gunicorn worker and four threads**: the application's conversation and pending requests are process-local. The `memory` volume persists permanent memory across container restarts/rebuilds; conversation history clears on restart. Certificate state persists in separate Caddy volumes.

Do not run `docker compose down --volumes` when updating. Inspect logs with `sudo docker compose logs --tail 100 app proxy`; do not print the resolved Compose configuration or environment because those include secrets.

## Board and browser tests

Open the UI over HTTPS and use the cloud Malayalam guide linked on the page. Set `SERVER_ORIGIN` to the hosted origin, set the private `KAREN_DEVICE_TOKEN`, and paste `docs/cloud-root-ca.pem` inside the existing `ROOT_CA` block. The bundle contains the public ISRG Root X1/X2 trust anchors downloaded from Let's Encrypt. Keep certificate verification and NTP enabled. Recompile/upload the S3 firmware after changing settings; do not overwrite Wi-Fi or GPIO settings.

Automated coverage includes cloud authentication, device permissions, CSRF, hosted guides and CSP hashes, request replay/polling and existing local behavior. Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/firmware.py --controller esp32_s3
```

The live browser check in `tests/browser.cjs` accepts `KAREN_URL`, `KAREN_TEST_USERNAME`, `KAREN_TEST_PASSWORD`, `KAREN_WAV` and `KAREN_SCREENSHOT` via the process environment. It tests all three guide links/copy/checklist controls, a real Malayalam text reply, a lost-response retry, browser recording with a generated audio fixture and MP3 decoding. Do not put credentials directly in shell commands/history. These software checks cannot prove physical microphone, ESP32 TLS/NTP or speaker sound; finish with a real board question.

With Playwright and Chrome/WebKit installed, `node tests/browser_recording.cjs` runs isolated browser regressions without contacting AI services or touching saved user memory. Set `KAREN_TEST_BROWSER=webkit` to test the WebKit engine. These cover unanswered microphone prompts, cancellation/late streams, denied or occupied microphones, interrupted audio startup, silence, blocked playback, stalled response bodies, expired page tokens and older browser request APIs. Text remains available during microphone setup; recording can be cancelled. An active phone/WhatsApp call can still prevent the operating system from providing microphone audio.

## Back up or delete early

Before deletion, copy `/app/data/memory.txt` out of the app container to a private backup. Do not commit that file. Keep the backup outside the server being deleted.

Inspect the recorded cleanup plan without changing AWS:

```bash
.venv/bin/python scripts/cleanup_aws_test.py
```

Delete early, after backing up anything needed:

```bash
.venv/bin/python scripts/cleanup_aws_test.py --execute
```

The command checks the AWS account, instance ARN, static-IP ARN and exact DNS record before deletion. It removes this test's schedules only after the billable resources are removed. It preserves other hosted-zone records and local credentials/backups. To extend the test, update all three AWS schedules together before the deadline; changing a local date alone does not reschedule AWS.
