// Live memory-editor test in a temporary copy. Never runs against saved user memory.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const root=path.resolve(__dirname,'..');
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'karen-memory-test-'));
const memory=path.join(temporary,'memory.txt');
fs.copyFileSync(path.join(root,'data','memory.txt'),memory);
let server,browser;
async function startServer(){
  server=spawn(path.join(root,'.venv','bin','python'),['-u','-c',
    'import os; from app import create_app; from werkzeug.serving import make_server; s=make_server("127.0.0.1",0,create_app({"MEMORY_PATH":os.environ["KAREN_TEST_MEMORY"],"DEMO_MODE":False}),threaded=True); print(s.server_port,flush=True); s.serve_forever()'
  ],{cwd:root,env:{...process.env,KAREN_TEST_MEMORY:memory},stdio:['ignore','pipe','ignore']});
  const port=await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Isolated server failed to start')),10000);
    server.stdout.once('data',data=>{clearTimeout(timer);resolve(Number(data.toString().trim()));});
    server.once('error',reject);
  });
  assert.ok(port>0);return `http://localhost:${port}`;
}
async function stopServer(){
  if(server&&server.exitCode===null){server.kill();await once(server,'exit');}
}
(async()=>{
  try {
    let origin=await startServer();
    browser=await chromium.launch({channel:'chrome',headless:true});
    const page=await browser.newPage({viewport:{width:390,height:844}});
    await page.goto(origin);
    const original=await page.locator('#memory').inputValue();
    const edited=original+'\nFor isolated software testing: the favorite planet is Saturn.';
    await page.locator('#memory').fill(edited);
    await page.getByRole('button',{name:'Save memory'}).click();
    await page.getByRole('status').filter({hasText:'Memory saved'}).waitFor();
    // HTML form submission uses CRLF; textarea values normalize it back to LF.
    assert.equal(fs.readFileSync(memory,'utf8').replace(/\r\n/g,'\n'),edited);
    await page.locator('#prompt').fill('പരീക്ഷണത്തിനായി പറഞ്ഞ ഇഷ്ടഗ്രഹത്തിന്റെ പേര് എന്താണ്?');
    await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question',{},{timeout:160000});
    assert.match(await page.locator('.message.model').last().innerText(),/ശനി|Saturn/i);
    await page.getByRole('button',{name:'New chat'}).click();
    await page.locator('#welcome').waitFor();
    assert.equal(await page.locator('.message').count(),0);
    await stopServer();origin=await startServer();await page.goto(origin);
    assert.equal(await page.locator('#memory').inputValue(),edited);
    assert.equal(await page.locator('.message').count(),0);
    console.log('Isolated browser memory save → real Malayalam fact retrieval → reset → restart persistence: passed');
    console.log('Original saved memory was never edited.');
  }finally{
    if(browser)await browser.close();await stopServer();fs.rmSync(temporary,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error.message);process.exitCode=1;});
