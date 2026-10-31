// Live smoke test. Requires a running server, Playwright and Chrome on this Mac.
// Browser voice uses a generated speech fixture, never a claim of a human mic test.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const origin = process.env.KAREN_URL || 'http://localhost:8080';
(async()=>{
  const browser = await chromium.launch({channel:'chrome',headless:true,args:[
    '--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',
    `--use-file-for-fake-audio-capture=${process.env.KAREN_WAV || '/tmp/karen-audio/question.wav'}`
  ]});
  try {
    const options={viewport:{width:390,height:844},permissions:['microphone','clipboard-read','clipboard-write']};
    if(process.env.KAREN_TEST_USERNAME&&process.env.KAREN_TEST_PASSWORD){
      options.httpCredentials={username:process.env.KAREN_TEST_USERNAME,password:process.env.KAREN_TEST_PASSWORD};
    }
    const context = await browser.newContext(options);
    const page = await context.newPage();
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    await page.goto(origin);
    const links=await page.locator('.guide-links a').evaluateAll(nodes=>nodes.map(node=>node.getAttribute('href')));
    assert.equal(links.length,3);
    for(const link of links){
      const guide=await page.context().newPage();
      await guide.goto(new URL(link,origin).href);
      assert.equal(await guide.locator('html').getAttribute('lang'),'ml');
      const box=guide.locator('.done input').first();
      await box.check();
      assert.match(await guide.locator('#progress').textContent(),/^1 \/ /);
      const copy=guide.locator('[data-copy]').first();
      const target=await copy.getAttribute('data-copy');
      const expected=await guide.locator('#'+target).textContent();
      await copy.click();
      await guide.waitForFunction(id=>document.querySelector(`[data-copy="${id}"]`).textContent==='കോപ്പി ചെയ്തു',target,{timeout:3000});
      assert.equal(await copy.textContent(),'കോപ്പി ചെയ്തു');
      assert.equal(await guide.evaluate(()=>navigator.clipboard.readText()),expected);
      assert.equal(await guide.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      assert.equal(await guide.locator('.step').first().evaluate(node=>getComputedStyle(node).borderRadius),'14px');
      await guide.close();
    }
    console.log('All three hosted Malayalam guides: linked, styled, responsive, copy and checklist passed');
    // Lose the first accepted POST response. The retry must reuse the same ID.
    const requestIds=[];
    await page.route('**/test_chat', async route=>{
      requestIds.push(route.request().headers()['x-request-id']);
      if(requestIds.length===1){await route.fetch();await route.abort('failed');}
      else await route.continue();
    });
    await page.locator('#prompt').fill('നിന്നെ ആരാണ് നിർമ്മിച്ചത്?');
    await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question',{},{timeout:160000});
    assert.match(await page.locator('.message.model').last().innerText(),/[\u0d00-\u0d7f]/);
    assert.match(await page.locator('.message.model').last().innerText(),/ശ്രീഹരി/);
    assert.equal(requestIds.length,2);
    assert.equal(requestIds[0],requestIds[1]);
    console.log('Mobile browser Malayalam text: passed');
    console.log('Lost POST response retry reuses request ID: passed');
    const voiceUpload = page.waitForRequest(request=>request.url().endsWith('/chat')&&request.method()==='POST');
    await page.locator('#record').click();
    const upload = await voiceUpload;
    assert.equal(upload.headers()['prefer'],'respond-async');
    await page.waitForFunction(()=>!document.querySelector('#reply-audio').hidden,{},{timeout:160000});
    assert.match(await page.locator('#status').innerText(),/^Reply ready/);
    await page.waitForFunction(()=>document.querySelector('#reply-audio').duration>0,{},{timeout:10000});
    const duration=await page.locator('#reply-audio').evaluate(audio=>audio.duration);
    assert.ok(duration>0);
    console.log('Browser recorder → PCM WAV → live STT/Gemini/gTTS → decoded MP3: passed; duration',duration);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false);
    await page.screenshot({path:process.env.KAREN_SCREENSHOT||'/tmp/karen-audio/mobile-dashboard.png',fullPage:true});
    assert.deepEqual(errors,[]);
    console.log('Mobile layout and browser runtime errors: passed');
  } finally {await browser.close();}
})().catch(error=>{console.error(error.message);process.exitCode=1;});
