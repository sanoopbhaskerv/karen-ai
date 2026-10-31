const form = document.querySelector('#chat-form');
const promptBox = document.querySelector('#prompt');
const messages = document.querySelector('#messages');
const statusText = document.querySelector('#status');
const send = document.querySelector('#send');
const record = document.querySelector('#record');
let csrf = document.querySelector('meta[name="csrf-token"]').content;
let busy = false, audioURL, recording;
function within(promise, milliseconds, message, signal) {
  return new Promise((resolve,reject) => {
    const finish = (callback,value) => {clearTimeout(timer);signal?.removeEventListener('abort',abort);callback(value);};
    const abort = () => finish(reject,new DOMException('Recording cancelled.','AbortError'));
    const timer = setTimeout(() => finish(reject,new Error(message)),milliseconds);
    if(signal?.aborted){abort();return;}
    signal?.addEventListener('abort',abort,{once:true});
    Promise.resolve(promise).then(value=>finish(resolve,value),error=>finish(reject,error));
  });
}
async function fetchTimed(path,options,milliseconds) {
  const controller = new AbortController();
  const timer = setTimeout(()=>controller.abort(),milliseconds);
  try{
    const response=await fetch(path,{...options,signal:controller.signal});
    // Keep the deadline active through the response body, including MP3 data.
    await response.clone().arrayBuffer();
    return response;
  }finally{clearTimeout(timer);}
}
// One logical request ID survives transport retries. Never retry a POST with a new ID.
async function ask(path, options) {
  const id = crypto.randomUUID ? crypto.randomUUID() : Array.from(crypto.getRandomValues(new Uint8Array(16)),x=>x.toString(16).padStart(2,'0')).join('');
  const deadline = Date.now() + 160000;
  options.headers = {...options.headers, 'X-Request-ID':id, 'Prefer':'respond-async'};
  let response;
  for(let attempt=0; attempt<2; attempt++) {
    try {
      response = await fetchTimed(path,options,15000);
      if(response.status===403 && (await response.clone().json().catch(()=>({}))).code==='csrf_expired'){
        const refreshed=await fetchTimed('/csrf-token',{},10000);
        if(!refreshed.ok)throw new Error('Refresh the page and try again.');
        csrf=(await refreshed.json()).csrf;
        options.headers['X-CSRF-Token']=csrf;
        response=await fetchTimed(path,options,15000);
      }
      break;
    }
    catch {if(attempt===1) statusText.textContent=`Checking request ${id}…`;}
  }
  while(!response || response.status===202) {
    if(Date.now()>=deadline) throw new Error(`Request ${id} is taking too long. Check /requests/${id} before sending again.`);
    await new Promise(resolve=>setTimeout(resolve,1000));
    try {response=await fetchTimed(`/requests/${id}`,{},Math.min(15000,Math.max(1,deadline-Date.now())));}
    catch {response=null;}
  }
  if(!response.ok) {
    const result=await response.json().catch(()=>({error:'The server could not complete the request. Please try again.'}));
    throw new Error(`${result.error || 'Request failed'} [${result.code || response.status}; request ${id}]`);
  }
  return response;
}
function append(role, text) {
  document.querySelector('#welcome')?.remove();
  const item = document.createElement('article'); item.className = 'message ' + role;
  const label = document.createElement('small'); label.textContent = role === 'user' ? 'YOU' : 'KAREN';
  const paragraph = document.createElement('p'); paragraph.textContent = text;
  item.append(label, paragraph); messages.append(item); messages.scrollTop = messages.scrollHeight;
}
function setBusy(value) {
  busy = value; send.disabled = value;
  record.disabled = value || document.querySelector('.pill').textContent.includes('DEMO');
  record.textContent = recording ? 'Cancel recording' : '● Record a question';
  document.querySelectorAll('button[type="submit"]').forEach(button=>button.disabled=value);
}
function releaseMicrophone(task) {
  task.stream?.getTracks().forEach(track=>track.stop());
  for(const node of [task.processor,task.source,task.silent]){try{node?.disconnect();}catch{}}
  if(task.context && task.context.state!=='closed'){
    try{task.context.close().catch(()=>{});}catch{}
  }
}
function cancelRecording(message) {
  if(!recording)return;
  const task=recording; recording=null;task.controller.abort();releaseMicrophone(task);setBusy(busy);
  if(message)statusText.textContent=message;
}
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {promptBox.value = button.dataset.prompt; promptBox.focus();}));
form.addEventListener('submit', async event => {
  event.preventDefault(); if (busy || !promptBox.value.trim()) return;
  cancelRecording();
  const text = promptBox.value.trim(); setBusy(true); statusText.textContent = 'Karen is thinking…';
  try {
    const response = await ask('/test_chat', {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json','X-CSRF-Token':csrf}, body:JSON.stringify({user_message:text})});
    const result = await response.json(); if (!response.ok) throw new Error(result.error || 'Request failed');
    append('user', text); append('model', result.reply); promptBox.value = ''; statusText.textContent = 'Ready for your next question';
  } catch (error) { statusText.textContent = error.message; } finally {setBusy(false);}
});
// Encode mono PCM instead of uploading browser-specific WebM/Opus.
function wavBlob(samples, rate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2); const view = new DataView(buffer);
  const str = (offset, text) => [...text].forEach((c,i) => view.setUint8(offset+i,c.charCodeAt(0)));
  str(0,'RIFF'); view.setUint32(4,36+samples.length*2,true); str(8,'WAVE'); str(12,'fmt ');
  view.setUint32(16,16,true); view.setUint16(20,1,true); view.setUint16(22,1,true); view.setUint32(24,rate,true);
  view.setUint32(28,rate*2,true); view.setUint16(32,2,true); view.setUint16(34,16,true); str(36,'data'); view.setUint32(40,samples.length*2,true);
  samples.forEach((x,i) => view.setInt16(44+i*2,Math.max(-1,Math.min(1,x))*32767,true));
  return new Blob([buffer],{type:'audio/wav'});
}
function microphoneMessage(error) {
  if(error.name==='NotAllowedError'||error.name==='SecurityError')return 'Microphone access is blocked. Allow microphone access for this site in browser settings, then try again. You can still type a question.';
  if(error.name==='NotReadableError'||error.name==='AbortError')return 'The microphone is unavailable. End any phone/WhatsApp call or other recording, reopen this page and try again. You can still type a question.';
  if(error.name==='NotFoundError')return 'No microphone was found. Connect one or type a question.';
  return error.message || 'Recording failed. You can still type a question.';
}
record.addEventListener('click', async () => {
  if(recording){cancelRecording('Recording cancelled. You can type a question or try recording again.');return;}
  if(busy)return;
  const task={controller:new AbortController()};recording=task;setBusy(false);
  try {
    if(!navigator.mediaDevices?.getUserMedia)throw new Error('Recording needs HTTPS or localhost. You can still type a question.');
    const AudioContextClass=window.AudioContext||window.webkitAudioContext;
    if(!AudioContextClass)throw new Error('This browser cannot record audio. Try Safari/Chrome or type a question.');
    // Start/resume Web Audio during the tap, before awaiting the permission prompt.
    task.context=new AudioContextClass();
    statusText.textContent='Allow microphone access when asked. You can cancel or type instead.';
    const ready=within(task.context.resume(),15000,'Audio is unavailable. End any active call, reopen this page and try again. You can still type a question.',task.controller.signal);
    const pending=navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true},video:false});
    // getUserMedia cannot be aborted. Stop a late stream after cancel/timeout.
    pending.then(stream=>{task.stream=stream;if(task.controller.signal.aborted)stream.getTracks().forEach(track=>track.stop());}).catch(()=>{});
    const [stream]=await Promise.all([within(pending,15000,'Microphone permission is still pending. Allow it in browser settings or type a question.',task.controller.signal),ready]);
    task.stream=stream;
    if(task.controller.signal.aborted){releaseMicrophone(task);return;}
    if(task.context.state!=='running')throw new Error('Audio was interrupted. End any active call and try recording again. You can still type a question.');
    const chunks=[];
    task.source=task.context.createMediaStreamSource(stream);
    task.processor=task.context.createScriptProcessor(4096,1,1);
    task.silent=task.context.createGain();task.silent.gain.value=0;
    task.processor.onaudioprocess=event=>chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
    task.source.connect(task.processor);task.processor.connect(task.silent);task.silent.connect(task.context.destination);
    statusText.textContent='Listening for 5 seconds…';
    await within(new Promise(resolve=>setTimeout(resolve,5000)),6000,'Recording was interrupted. Try again or type a question.',task.controller.signal);
    if(task.context.state!=='running')throw new Error('Audio was interrupted. End any active call and try again. You can still type a question.');
    const sampleRate=task.context.sampleRate;releaseMicrophone(task);
    const joined=new Float32Array(chunks.reduce((sum,chunk)=>sum+chunk.length,0));let position=0;
    for(const chunk of chunks){joined.set(chunk,position);position+=chunk.length;}
    const ratio=sampleRate/16000;const pcm=new Float32Array(Math.floor(joined.length/ratio));let peak=0;
    for(let i=0;i<pcm.length;i++){const start=Math.floor(i*ratio),end=Math.max(start+1,Math.floor((i+1)*ratio));let sum=0;for(let j=start;j<end;j++)sum+=joined[j]||0;pcm[i]=sum/(end-start);peak=Math.max(peak,Math.abs(pcm[i]));}
    if(pcm.length<1600||peak<0.00001)throw new Error('No microphone audio was captured. End any active call, check the microphone and try again. You can still type a question.');
    const body=new FormData();body.append('audio',wavBlob(pcm,16000),'question.wav');
    recording=null;setBusy(true);task.submitted=true;statusText.textContent='Listening → thinking → speaking…';
    const response=await ask('/chat',{method:'POST',headers:{'X-CSRF-Token':csrf},body});
    if(!response.headers.get('Content-Type')?.startsWith('audio/mpeg'))throw new Error('Server returned an unexpected audio format.');
    if(audioURL)URL.revokeObjectURL(audioURL);audioURL=URL.createObjectURL(await response.blob());
    const player=document.querySelector('#reply-audio');player.src=audioURL;player.hidden=false;
    statusText.textContent=response.headers.get('X-Karen-Result')==='spoken-error'?`Karen could not answer [${response.headers.get('X-Karen-Error')}]. Try again or type a question.`:'Reply ready. Refresh the page to see the voice conversation.';
    try{await within(player.play(),3000,'Tap Play to listen.',task.controller.signal);}catch{statusText.textContent+=' Tap Play to listen.';}
  }catch(error){
    if(!task.controller.signal.aborted)statusText.textContent=microphoneMessage(error);
  }finally{
    task.controller.abort();releaseMicrophone(task);
    if(recording===task)recording=null;
    if(task.submitted)setBusy(false);else setBusy(busy);
  }
});
window.addEventListener('pagehide',()=>cancelRecording());
document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelRecording('Recording stopped when this page moved to the background. Try recording again or type a question.');});
messages.scrollTop=messages.scrollHeight;
