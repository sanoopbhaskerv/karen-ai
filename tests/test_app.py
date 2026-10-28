import io
import wave
import pytest
from app import create_app, ServiceError

class Fake:
    def __init__(self): self.seen=[]; self.fail=False; self.stt_fail=False; self.tts_fail=False
    def answer(self,memory,history,message):
        if self.fail: raise ServiceError('Provider down')
        self.seen.append((memory,history,message))
        return 'നമസ്കാരം! ഞാൻ കാരെൻ.'
    def transcribe(self,data):
        if self.stt_fail: raise ServiceError('വീണ്ടും പറയൂ.')
        return 'നിന്റെ പേര് എന്താണ്?'
    def speak(self,text):
        if self.tts_fail: raise ServiceError('Speech unavailable')
        return b'ID3fake-test-audio'

@pytest.fixture
def setup(tmp_path):
    provider=Fake()
    app=create_app({'TESTING':True,'SECRET_KEY':'test','MEMORY_PATH':str(tmp_path/'memory.txt'),'DEMO_MODE':False},provider)
    client=app.test_client();client.get('/')
    with client.session_transaction() as s: token=s['csrf']
    return app,client,provider,token

def pcm(seconds=1):
    data=io.BytesIO()
    with wave.open(data,'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000);f.writeframes(b'\0\0'*int(seconds*16000))
    return data.getvalue()

def post(client,token,text='hello'):
    return client.post('/test_chat',json={'user_message':text},headers={'X-CSRF-Token':token,'Accept':'application/json'})

def test_dashboard_and_health(setup):
    app,c,p,t=setup
    assert c.get('/').status_code==200
    assert 'കാരെൻ' in c.get('/').get_data(as_text=True)
    assert c.get('/health').json['status']=='ok'

def test_history_and_memory_reset(setup):
    app,c,p,t=setup
    assert post(c,t).status_code==200
    post(c,t,'follow up')
    assert len(p.seen[-1][1])==2
    r=c.post('/update',data={'csrf_token':t,'memory_text':'Favorite food is biryani.'})
    assert r.status_code==200
    assert not app.extensions['karen']['history']
    post(c,t)
    assert p.seen[-1][0]=='Favorite food is biryani.'
    restarted=create_app({'TESTING':True,'MEMORY_PATH':app.config['MEMORY_PATH']},p)
    assert not restarted.extensions['karen']['history']
    assert 'biryani' in restarted.test_client().get('/').get_data(as_text=True)

def test_failed_turn_is_not_saved(setup):
    app,c,p,t=setup;p.fail=True
    assert post(c,t).status_code==503
    assert app.extensions['karen']['history']==[]

def test_csrf_and_escaped_html(setup):
    app,c,p,t=setup
    assert c.post('/update',data={'memory_text':'bad'}).status_code==403
    assert c.post('/test_chat',json={'user_message':'hi'}).status_code==403
    post(c,t,'<script>alert(1)</script>')
    html=c.get('/').get_data(as_text=True)
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html

@pytest.mark.parametrize('text',['',' '*5,'x'*2001,None,12])
def test_bad_text(setup,text):
    app,c,p,t=setup
    assert post(c,t,text).status_code==503
    assert not p.seen

def test_bounded_history(setup):
    app,c,p,t=setup
    for i in range(14): assert post(c,t,str(i)).status_code==200
    assert len(app.extensions['karen']['history'])==20

def test_voice_multipart_and_raw(setup):
    app,c,p,t=setup
    for kwargs in ({'data':{'audio':(io.BytesIO(pcm()),'question.wav')}},{'data':pcm(),'content_type':'audio/wav'}):
        r=c.post('/chat',**kwargs)
        assert r.status_code==200 and r.mimetype=='audio/mpeg'
        assert r.data==b'ID3fake-test-audio' and r.headers['X-Karen-Result']=='ok'

def test_voice_errors(setup):
    app,c,p,t=setup
    assert c.post('/chat').status_code==400
    assert c.post('/chat',data=b'not audio',content_type='audio/wav').status_code==400
    assert c.post('/chat',data=pcm(16),content_type='audio/wav').status_code==400
    assert c.post('/chat',data=pcm()[:-20],content_type='audio/wav').status_code==400
    p.stt_fail=True
    r=c.post('/chat',data=pcm(),content_type='audio/wav')
    assert r.status_code==200 and r.headers['X-Karen-Result']=='spoken-error'
    assert not app.extensions['karen']['history']
    p.tts_fail=True
    assert c.post('/chat',data=pcm(),content_type='audio/wav').status_code==503

def test_size_limit(setup):
    app,c,p,t=setup
    assert c.post('/chat',data=b'x'*(2*1024*1024+1),content_type='audio/wav').status_code==413

def test_demo_mode(tmp_path):
    app=create_app({'TESTING':True,'DEMO_MODE':True,'MEMORY_PATH':str(tmp_path/'memory.txt')})
    c=app.test_client();c.get('/')
    with c.session_transaction() as s:t=s['csrf']
    assert post(c,t).json['mode']=='demo'
    assert c.post('/chat',data=pcm(),content_type='audio/wav').status_code==503

def test_form_fallback_and_reset(setup):
    app,c,p,t=setup
    r=c.post('/test_chat',data={'csrf_token':t,'user_message':'hello'})
    assert r.status_code==200 and r.mimetype=='text/html'
    assert c.post('/reset',data={'csrf_token':t}).status_code==302
    assert not app.extensions['karen']['history']

def test_empty_memory_rejected(setup):
    app,c,p,t=setup
    assert c.post('/update',data={'csrf_token':t,'memory_text':' '}).status_code==400

def test_provider_language_contract(setup,monkeypatch):
    import speech_recognition as sr
    import gtts
    from app import Providers
    app,c,p,t=setup
    seen={}
    def recognize(self,audio,**kwargs):
        seen['stt']=kwargs['language'];return 'നമസ്കാരം'
    class TTS:
        def __init__(self,**kwargs):seen['tts']=kwargs['lang']
        def write_to_fp(self,fp):fp.write(b'ID3')
    monkeypatch.setattr(sr.Recognizer,'recognize_google',recognize)
    monkeypatch.setattr(gtts,'gTTS',TTS)
    live=Providers(app)
    assert live.transcribe(pcm())=='നമസ്കാരം'
    assert live.speak('നമസ്കാരം')==b'ID3'
    assert seen=={'stt':'ml-IN','tts':'ml'}

def test_gemini_adapter(setup,monkeypatch):
    from google import genai
    from app import Providers
    from types import SimpleNamespace
    app,c,p,t=setup;app.config['GEMINI_API_KEY']='test-not-real'
    seen={}
    class Client:
        def __init__(self,**kwargs):self.models=self
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def generate_content(self,**kwargs):seen.update(kwargs);return SimpleNamespace(text='മലയാളം')
    monkeypatch.setattr(genai,'Client',Client)
    reply=Providers(app).answer('Identity facts',[('user','hi'),('model','hello')],'next')
    assert reply=='മലയാളം'
    assert [c.role for c in seen['contents']]==['user','model','user']
    assert 'Malayalam' in seen['config'].system_instruction
    assert 'Identity facts' in seen['config'].system_instruction
