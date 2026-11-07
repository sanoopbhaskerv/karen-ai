// Real browser checks with isolated fake providers; no API requests or private profiles.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawn}=require('node:child_process');
const {once}=require('node:events');
const root=path.resolve(__dirname,'..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'karen-tenants-'));
let server,browser;
(async()=>{try{
 const python=process.env.KAREN_PYTHON || path.join(root,'.venv/bin/python');
 const code=`import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tests'))
from test_app import Fake
from multitenant import create_service
from werkzeug.serving import make_server
def provider(profile):
 p=Fake()
 p.answer=lambda *args: 'English answer about rain.' if profile['language']=='en' else 'മഴ മേഘങ്ങളിൽ നിന്ന് പെയ്യുന്നു.'
 return p
app=create_service({'MEMORY_PATH':str(Path(sys.argv[1])/'memory.txt'),'CLIENT_REGISTRY_PATH':str(Path(sys.argv[1])/'clients.sqlite3'),'SECRET_KEY':'test','KAREN_ADMIN_PASSWORD':'test-owner','KAREN_DEVICE_TOKEN':'test-default','DEMO_MODE':False,'SESSION_COOKIE_SECURE':False},provider)
registry=app.extensions['clients']['registry']
registered=[]
for lang in ('en','ml'):
 registered.append(registry.register({'id':'browser-'+lang,'name':'Test learner','location':'Test town','grade':7,'controller':'esp32','language':lang,'science_context':False}))
s=make_server('127.0.0.1',0,app,threaded=True)
print(json.dumps({'port':s.server_port,'clients':registered}),flush=True)
s.serve_forever()`;
 server=spawn(python,['-u','-c',code,temp],{cwd:root,stdio:['ignore','pipe','ignore']});
 const setup=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server did not start')),10000);server.stdout.once('data',d=>{clearTimeout(timer);resolve(JSON.parse(d.toString()))});server.once('error',reject)});
 browser=await chromium.launch({headless:true});
 const origin='http://127.0.0.1:'+setup.port;
 for(const registration of setup.clients){
  const id=registration.client.id,base='/clients/'+id;
  const context=await browser.newContext({httpCredentials:{username:registration.admin_username,password:registration.admin_password}});
  const page=await context.newPage();const requests=[];
  page.on('request',r=>requests.push(new URL(r.url()).pathname));
  await page.goto(origin+base+'/');
  assert.equal(await page.locator('#send').isEnabled(),true);
  if(registration.client.language==='en')assert.match(await page.locator('.intro').innerText(),/English learning companion/);
  assert.equal(await page.locator('footer').innerText().then(t=>t.includes('SREEHARI')),false);
  await page.locator('#prompt').fill('മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?');await page.locator('#send').click();
  await page.waitForFunction(()=>document.querySelector('#status').textContent==='Ready for your next question');
  assert.equal(await page.locator('.message.model').last().innerText().then(t=>t.includes(registration.client.language==='en'?'English answer':'മഴ')),true);
  await page.locator('#memory').fill('Only '+id+' likes blue.');await page.getByRole('button',{name:'Save memory'}).click();
  await page.waitForURL(origin+base+'/update');
  assert.equal(await page.locator('#memory').inputValue(),'Only '+id+' likes blue.');
  assert(requests.some(p=>p===base+'/test_chat'));
  assert(requests.every(p=>p.startsWith(base+'/')),'Browser request escaped client mount');
  await page.goto(origin+base+'/');assert.equal(await page.locator('#memory').inputValue(),'Only '+id+' likes blue.');
  await context.close();
 }
 console.log('Tenant browser auth, Malayalam input, configured reply languages, mounted assets/chat/forms and isolated memory: passed');
}finally{if(browser)await browser.close();if(server&&server.exitCode===null){server.kill();await once(server,'exit')}fs.rmSync(temp,{recursive:true,force:true})}})().catch(e=>{console.error(e);process.exitCode=1});
