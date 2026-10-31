// Deterministic browser regressions. Uses isolated memory and fake providers;
// permission/audio failures are injected, so these checks never call AI services.
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
const {spawn}=require('node:child_process');const {once}=require('node:events');
const root=path.resolve(__dirname,'..');
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'karen-recording-test-'));
let server,browser;
(async()=>{try{
 server=spawn(path.join(root,'.venv','bin','python'),['-u','-c',
  'import sys; from pathlib import Path; sys.path.insert(0,str(Path.cwd()/"tests")); from test_app import Fake; from app import create_app; from werkzeug.serving import make_server; app=create_app({"MEMORY_PATH":sys.argv[1],"KAREN_ADMIN_PASSWORD":"test-owner","KAREN_PUBLIC_UI":True,"SESSION_COOKIE_SECURE":False,"DEMO_MODE":False},Fake()); s=make_server("127.0.0.1",0,app,threaded=True); print(s.server_port,flush=True); s.serve_forever()',path.join(temporary,'memory.txt')],{cwd:root,stdio:['ignore','pipe','ignore']});
 const port=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Isolated server did not start')),10000);server.stdout.once('data',data=>{clearTimeout(timer);resolve(Number(data.toString().trim()));});server.once('error',reject);});
 const origin=`http://localhost:${port}`;
 browser=process.env.KAREN_TEST_BROWSER==='webkit'?await webkit.launch({headless:true}):await chromium.launch({channel:'chrome',headless:true});
 async function pageFor(mode){
  const page=await browser.newPage();page.on('pageerror',error=>console.error('Browser script error:',error.message));await page.clock.install();
  await page.addInitScript(mode=>{
   window.stoppedTracks=0;window.voiceUploads=0;
   const stream={getTracks:()=>[{stop:()=>{window.stoppedTracks++;}}]};
   class Audio{
    constructor(){this.state='running';this.sampleRate=48000;this.destination={};}
    resume(){if(mode==='resume-hang'){this.state='suspended';return new Promise(()=>{});}return Promise.resolve();}
    close(){this.state='closed';return Promise.resolve();}
    createMediaStreamSource(){return {connect(){},disconnect(){}};}
    createScriptProcessor(){const node={connect(){if(mode==='playback-hang')queueMicrotask(()=>node.onaudioprocess({inputBuffer:{getChannelData:()=>new Float32Array(240000).fill(0.05)}}));},disconnect(){}};return node;}
    createGain(){return {gain:{value:0},connect(){},disconnect(){}};}
   }
   window.AudioContext=Audio;
   if(mode==='playback-hang')HTMLMediaElement.prototype.play=()=>new Promise(()=>{});
   Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:()=>{
    if(mode==='permission-hang')return new Promise(resolve=>{window.grantLate=()=>resolve(stream);});
    if(mode==='denied')return Promise.reject(new DOMException('Denied','NotAllowedError'));
    if(mode==='in-use')return Promise.reject(new DOMException('In use','NotReadableError'));
    return Promise.resolve(stream);
   }}});
  },mode);
  await page.route('**/chat',async route=>{await page.evaluate(()=>window.voiceUploads++);await route.continue();});
  await page.goto(origin);return page;
 }
 async function sendText(page){await page.locator('#prompt').fill('hello');await page.locator('#send').click();await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question');}
 let page=await pageFor('permission-hang');
 await page.getByRole('link',{name:'Local setup'}).waitFor();await page.getByRole('link',{name:'Cloud setup'}).waitFor();
 await page.locator('#record').click();assert.equal(await page.locator('#send').isEnabled(),true);
 await sendText(page);await page.evaluate(()=>window.grantLate());await page.waitForFunction(()=>window.stoppedTracks>0);
 assert.equal(await page.locator('#record').isEnabled(),true);assert.equal(await page.evaluate(()=>window.voiceUploads),0);await page.close();
 console.log('Pending microphone permission does not block text; text cancels recording and late streams stop: passed');
 for(const [mode,message] of [['permission-hang','permission is still pending'],['resume-hang','Audio is unavailable'],['denied','Microphone access is blocked'],['in-use','End any phone/WhatsApp call'],['silence','No microphone audio was captured']]){
  page=await pageFor(mode);await page.locator('#record').click();
  if(mode.endsWith('hang'))await page.clock.fastForward(16000);
  if(mode==='silence')await page.clock.fastForward(5500);
  await page.waitForFunction(message=>document.querySelector('#status').textContent.includes(message),message);
  assert.equal(await page.locator('#send').isEnabled(),true);assert.equal(await page.locator('#record').isEnabled(),true);
  assert.equal(await page.evaluate(()=>window.voiceUploads),0);
  if(mode==='resume-hang')assert.ok(await page.evaluate(()=>window.stoppedTracks)>0);
  await sendText(page);await page.close();
 }
 console.log('Permission timeout, interrupted audio startup, denial, microphone in use and silent capture recover to text: passed');
 page=await pageFor('permission-hang');await page.locator('#record').click();await page.getByRole('button',{name:'Cancel recording'}).click();assert.match(await page.locator('#status').innerText(),/Recording cancelled/);await page.close();
 page=await pageFor('denied');await page.evaluate(()=>{crypto.randomUUID=undefined;AbortSignal.timeout=undefined;});
 const ids=[];await page.route('**/test_chat',async route=>{
  ids.push(route.request().headers()['x-request-id']);
  if(ids.length===1){const response=await route.fetch({headers:{...route.request().headers(),'x-csrf-token':'expired'}});await route.fulfill({response});}
  else await route.continue();
 });
 await sendText(page);assert.equal(ids.length,2);assert.equal(ids[0],ids[1]);assert.match(ids[0],/^[a-f0-9]{32}$/);await page.close();
 console.log('Cancel button, expired-CSRF recovery and older-browser request APIs: passed');
 page=await pageFor('playback-hang');await page.locator('#record').click();await page.clock.fastForward(5500);
 await page.waitForFunction(()=>!document.querySelector('#reply-audio').hidden);
 await page.clock.fastForward(3500);await page.waitForFunction(()=>!document.querySelector('#send').disabled);
 assert.match(await page.locator('#status').innerText(),/Tap Play/);await page.close();
 page=await pageFor('denied');await page.evaluate(()=>{
  const original=window.fetch;let first=true;window.transportIds=[];
  window.fetch=(url,options)=>{
   if(url==='/test_chat'){
    window.transportIds.push(options.headers['X-Request-ID']);
    if(first){first=false;return Promise.resolve(new Response(new ReadableStream({start(controller){options.signal.addEventListener('abort',()=>controller.error(new DOMException('Timed out','AbortError')));}}),{status:202,headers:{'Content-Type':'application/json'}}));}
   }
   return original(url,options);
  };
 });
 await page.locator('#prompt').fill('hello');await page.locator('#send').click();await page.clock.fastForward(16000);
 await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question');
 const transportIds=await page.evaluate(()=>window.transportIds);assert.equal(transportIds.length,2);assert.equal(transportIds[0],transportIds[1]);await page.close();
 console.log('Interrupted playback releases text controls; stalled response bodies time out and retry with the same request ID: passed');
}finally{if(browser)await browser.close();if(server&&server.exitCode===null){server.kill();await once(server,'exit');}fs.rmSync(temporary,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
