// Offline UI regression: real template/JS/CSS, mocked chat transport and microphone.
// Run with Playwright and Chrome installed: node tests/browser_failures.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const python = process.env.KAREN_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const rendered = spawnSync(python, ['-c', [
  'from tempfile import TemporaryDirectory',
  'from app import create_app',
  'with TemporaryDirectory() as temporary:',
  ' app = create_app({"TESTING": True, "DEMO_MODE": False, "GEMINI_API_KEY": "", "MEMORY_PATH": temporary + "/memory.txt"})',
  ' print(app.test_client().get("/").get_data(as_text=True))',
].join('\n')], {cwd: root, encoding: 'utf8'});
assert.equal(rendered.status, 0, rendered.stderr);

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true, args: [
    '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
  ]});
  try {
    const page = await browser.newPage({viewport: {width: 390, height: 844}, permissions: ['microphone']});
    const errors = [], posts = [], polls = [];
    let voiceUploads = 0;
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => {
      const getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      window.recordedTracks = [];
      navigator.mediaDevices.getUserMedia = async options => {
        const stream = await getUserMedia(options);
        window.recordedTracks.push(...stream.getTracks());
        return stream;
      };
    });
    await page.route('http://localhost:8080/**', async route => {
      const request = route.request(), url = new URL(request.url());
      if (url.pathname === '/' || url.pathname === '/reset') {
        return route.fulfill({contentType: 'text/html', body: rendered.stdout});
      }
      if (['/static/app.js', '/static/style.css'].includes(url.pathname)) {
        return route.fulfill({contentType: url.pathname.endsWith('.js') ? 'text/javascript' : 'text/css', body: fs.readFileSync(path.join(root, url.pathname.slice(1)))});
      }
      if (url.pathname === '/test_chat') {
        posts.push(request.headers()['x-request-id']);
        // A transport retry and an async poll must still count as one question.
        if (posts.length === 1) return route.abort('failed');
        if (posts.length === 2) return route.fulfill({status: 202, json: {}});
        return route.fulfill({json: {user_message: 'A science question', reply: 'A science answer'}});
      }
      if (url.pathname.startsWith('/requests/')) {
        polls.push(url.pathname.split('/').pop());
        return route.fulfill({json: {user_message: 'A science question', reply: 'A science answer'}});
      }
      if (url.pathname === '/chat') voiceUploads += 1;
      return route.fulfill({status: 500, json: {error: 'Unexpected request'}});
    });
    await page.goto('http://localhost:8080');
    const submit = async text => {
      await page.locator('#prompt').fill(text);
      await page.locator('#send').click();
      await page.waitForFunction(() => !document.querySelector('#send').disabled);
    };
    const ready = async () => assert.equal(await page.locator('#status').innerText(), 'Ready for your next question');
    const outage = '502 Bad Gateway — Server unavailable. Please try again.';

    await submit('   '); // Blank submissions do not advance the counter.
    assert.equal(posts.length, 0);
    await submit('Question one');
    await ready();
    assert.equal(posts.length, 2);
    assert.equal(posts[0], posts[1]);
    assert.deepEqual(polls, [posts[0]]);
    await submit('Question two');
    assert.equal(await page.locator('.message.error[role="alert"] p').innerText(), outage);
    assert.equal(await page.locator('#prompt').inputValue(), 'Question two');
    assert.equal(await page.locator('#status').innerText(), outage);
    assert.equal(posts.length, 2);
    await page.locator('#send').click(); // Retry preserved text: question three succeeds.
    await page.waitForFunction(() => !document.querySelector('#send').disabled);
    await ready();
    assert.equal(posts.length, 3);
    assert.equal(await page.locator('#prompt').inputValue(), '');

    await page.locator('#record').click(); // Fourth question: voice shares the same counter.
    await page.waitForFunction(() => document.querySelectorAll('.message.error').length === 2);
    assert.equal(voiceUploads, 0);
    assert.equal(await page.locator('#record').isEnabled(), true);
    assert.equal(await page.evaluate(() => window.recordedTracks.length > 0 && window.recordedTracks.every(track => track.readyState === 'ended')), true);
    await submit('Question five');
    await ready();
    await submit('Question six');
    assert.equal(await page.locator('.message.error').count(), 3);
    assert.equal(posts.length, 4);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    const screenshot = process.env.KAREN_SCREENSHOT;
    if (screenshot) await page.screenshot({path: screenshot, fullPage: true});
    await page.getByRole('button', {name: 'New chat'}).click();
    await page.locator('#welcome').waitFor();
    await submit('Fresh chat question one');
    await ready();
    assert.equal(posts.length, 5);
    await page.reload();
    await submit('Reloaded question one');
    await ready();
    assert.equal(posts.length, 6);
    assert.deepEqual(errors, []);
    console.log('Alternating text/voice outages, retry/poll counting, input retention, recovery, reset, mobile layout: passed');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
