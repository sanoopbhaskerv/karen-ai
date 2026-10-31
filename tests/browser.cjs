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
    const page = await browser.newPage({viewport:{width:390,height:844},permissions:['microphone']});
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    await page.goto(origin);
    const identifyingDetails=/(?:sreehari|ശ്രീഹരി|pkmm|\b9\s*s\b|thottasher|തോട്ടശ്ശേരി|edarikk?ode)/i;
    assert.doesNotMatch(await page.locator('body').innerText(),identifyingDetails);
    // Lose the first accepted POST response. The retry must reuse the same ID.
    const requestIds=[];
    await page.route('**/test_chat', async route=>{
      requestIds.push(route.request().headers()['x-request-id']);
      if(requestIds.length===1){await route.fetch();await route.abort('failed');}
      else await route.continue();
    });
    await page.locator('#prompt').fill('മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?');
    await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question',{},{timeout:160000});
    assert.match(await page.locator('.message.model').last().innerText(),/[\u0d00-\u0d7f]/);
    assert.doesNotMatch(await page.locator('.message.model').last().innerText(),identifyingDetails);
    assert.equal(requestIds.length,2);
    assert.equal(requestIds[0],requestIds[1]);
    console.log('Mobile browser Malayalam science text: passed');
    console.log('Lost POST response retry reuses request ID: passed');
    await page.unroute('**/test_chat');
    await page.locator('#prompt').fill('Was Sreehari V from PKMMHSS your creator?');
    await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message.model').length===2&&document.querySelector('#status').textContent==='Ready for your next question',{},{timeout:160000});
    assert.match(await page.locator('.message.model').last().innerText(),/[\u0d00-\u0d7f]/);
    assert.doesNotMatch(await page.locator('.message.model').last().innerText(),identifyingDetails);
    assert.doesNotMatch(await page.locator('body').innerText(),identifyingDetails);
    assert.equal(await page.locator('#prompt').inputValue(),'');
    console.log('Anonymous creator response: passed');
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
    await page.screenshot({path:'/tmp/karen-audio/mobile-dashboard.png',fullPage:true});
    assert.deepEqual(errors,[]);
    console.log('Mobile layout and browser runtime errors: passed');
  } finally {await browser.close();}
})().catch(error=>{console.error(error.message);process.exitCode=1;});
