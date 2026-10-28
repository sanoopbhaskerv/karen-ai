const form = document.querySelector('#chat-form');
const promptBox = document.querySelector('#prompt');
const messages = document.querySelector('#messages');
const statusText = document.querySelector('#status');
const send = document.querySelector('#send');
const record = document.querySelector('#record');
const csrf = document.querySelector('meta[name="csrf-token"]').content;
let busy = false, audioURL;
function append(role, text) {
  document.querySelector('#welcome')?.remove();
  const item = document.createElement('article'); item.className = 'message ' + role;
  const label = document.createElement('small'); label.textContent = role === 'user' ? 'YOU' : 'KAREN';
  const paragraph = document.createElement('p'); paragraph.textContent = text;
  item.append(label, paragraph); messages.append(item); messages.scrollTop = messages.scrollHeight;
}
function setBusy(value) { busy = value; send.disabled = value; record.disabled = value || document.querySelector('.pill').textContent.includes('DEMO'); }
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {promptBox.value = button.dataset.prompt; promptBox.focus();}));
form.addEventListener('submit', async event => {
  event.preventDefault(); if (busy || !promptBox.value.trim()) return;
  const text = promptBox.value.trim(); setBusy(true); statusText.textContent = 'Karen is thinking…';
  try {
    const response = await fetch('/test_chat', {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json','X-CSRF-Token':csrf}, body:JSON.stringify({user_message:text}), signal:AbortSignal.timeout(60000)});
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
record.addEventListener('click', async () => {
  if(busy) return; setBusy(true); let stream, context, source, processor, silent;
  try {
    if(!navigator.mediaDevices?.getUserMedia) throw new Error('Recording needs HTTPS or localhost. Text chat remains available.');
    stream = await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true},video:false});
    context = new AudioContext(); await context.resume(); const chunks = [];
    source = context.createMediaStreamSource(stream);
    // ScriptProcessor is widely supported on exhibition phones; a future version can use AudioWorklet.
    processor = context.createScriptProcessor(4096,1,1); silent = context.createGain(); silent.gain.value=0;
    processor.onaudioprocess = e => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    source.connect(processor); processor.connect(silent); silent.connect(context.destination);
    statusText.textContent='Listening for 8 seconds…'; await new Promise(resolve=>setTimeout(resolve,8000));
    processor.disconnect(); source.disconnect(); silent.disconnect(); stream.getTracks().forEach(t=>t.stop());
    const sampleRate=context.sampleRate; await context.close(); context=null;
    const joined=new Float32Array(chunks.reduce((sum,x)=>sum+x.length,0)); let pos=0; for(const c of chunks){joined.set(c,pos);pos+=c.length;}
    // Average input windows when downsampling to 16 kHz.
    const ratio=sampleRate/16000; const pcm=new Float32Array(Math.floor(joined.length/ratio));
    for(let i=0;i<pcm.length;i++){const start=Math.floor(i*ratio),end=Math.max(start+1,Math.floor((i+1)*ratio));let sum=0;for(let j=start;j<end;j++)sum+=joined[j]||0;pcm[i]=sum/(end-start);}
    const body=new FormData(); body.append('audio',wavBlob(pcm,16000),'question.wav'); statusText.textContent='Listening → thinking → speaking…';
    const response=await fetch('/chat',{method:'POST',body,signal:AbortSignal.timeout(120000)});
    if(!response.ok){const result=await response.json();throw new Error(result.error||'Voice request failed');}
    if(audioURL)URL.revokeObjectURL(audioURL); audioURL=URL.createObjectURL(await response.blob());
    const player=document.querySelector('#reply-audio'); player.src=audioURL; player.hidden=false;
    statusText.textContent=response.headers.get('X-Karen-Result')==='spoken-error'?'Karen could not answer. Listen, then retry.':'Reply ready. Refresh the page to see the voice conversation.';
    try{await player.play();}catch{statusText.textContent+=' Tap Play to listen.';}
  }catch(error){statusText.textContent=error.message;}finally{stream?.getTracks().forEach(t=>t.stop());if(context&&context.state!=='closed')await context.close();setBusy(false);}
});
messages.scrollTop=messages.scrollHeight;
