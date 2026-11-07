import base64
import json
import threading

import pytest
from app import create_app
from multitenant import create_service, ClientRegistry
from test_app import Fake, pcm


def basic(user, password):
    return {'Authorization': 'Basic ' + base64.b64encode((user + ':' + password).encode()).decode()}


def bearer(registration):
    return {'Authorization': 'Bearer ' + registration['device_token']}


def profile(identifier='english-one', language='en', science=False):
    return dict(id=identifier, name='Test learner', grade=7, location='Test town',
                controller='esp32', language=language, science_context=science)


@pytest.fixture
def service(tmp_path):
    providers = {}
    def factory(p):
        provider = Fake()
        provider.transcribe = lambda _: 'How does rain form?'
        provider.answer = lambda memory, history, message: provider.seen.append((memory, history, message)) or 'Rain falls from clouds.'
        providers[p['id']] = provider
        return provider
    app = create_service(dict(TESTING=True, SECRET_KEY='test', MEMORY_PATH=str(tmp_path/'memory.txt'),
        CLIENT_REGISTRY_PATH=str(tmp_path/'clients.sqlite3'), DEMO_MODE=False,
        KAREN_ADMIN_USERNAME='owner', KAREN_ADMIN_PASSWORD='owner-password',
        KAREN_DEVICE_TOKEN='legacy-token', KAREN_PUBLIC_UI=False), factory)
    registry = app.extensions['clients']['registry']
    english = registry.register(profile())
    malayalam = registry.register(profile('malayalam-one', 'ml', True))
    return app, registry, english, malayalam, providers


def test_credential_routing_isolates_history_jobs_and_replay(service):
    app, registry, en, ml, providers = service
    c = app.test_client()
    for registration in (en, ml):
        h = {**bearer(registration), 'X-Request-ID': 'same-request-123', 'Prefer': 'respond-async'}
        assert c.post('/chat', data=pcm(), content_type='audio/wav', headers=h).status_code in (200, 202)
        child = app.extensions['clients']['apps'][registration['client']['id']]
        child.extensions['karen']['jobs'].get('same-request-123').thread.join(2)
        assert c.get('/requests/same-request-123', headers=bearer(registration)).headers['X-Karen-Result'] == 'ok'
    assert providers[en['client']['id']].seen[0][1] == []
    assert providers[ml['client']['id']].seen[0][1] == []
    assert c.get('/requests/same-request-123', headers={'Authorization':'Bearer legacy-token'}).status_code == 404
    for reg in (en, ml):
        assert c.get('/requests/not-my-request', headers=bearer(reg)).status_code == 404
    assert len(app.extensions['clients']['apps']['english-one'].extensions['karen']['history']) == 2


def test_unknown_credentials_and_spoofed_id_fail_closed(service):
    app, _, en, ml, _ = service
    c = app.test_client()
    assert c.post('/chat', data=pcm(), content_type='audio/wav', headers={'Authorization':'Bearer wrong'}).status_code == 401
    assert c.post('/chat', data=pcm(), content_type='audio/wav', headers={**bearer(en), 'X-Client-ID':'malayalam-one'}).status_code == 403
    assert c.get('/clients/malayalam-one/requests/unknown-key', headers=bearer(en)).status_code == 403
    assert c.get('/clients/unknown-client/health').status_code == 404
    assert c.get('/api/clients', headers=bearer(en)).status_code == 403
    assert c.get('/clients/english-one/').status_code == 401
    assert c.get('/clients/english-one/', headers=basic(ml['admin_username'],ml['admin_password'])).status_code == 401


def test_profile_language_context_and_private_biography(service, monkeypatch):
    app, _, en, _, _ = service
    c = app.test_client(); headers=basic(en['admin_username'],en['admin_password'])
    page=c.get('/clients/english-one/',headers=headers)
    assert page.status_code == 200 and b'English learning companion' in page.data
    assert b'SREEHARI V' not in page.data
    assert b'/clients/english-one/test_chat' in page.data
    assert b'/clients/english-one/static/app.js' in page.data
    child=app.extensions['clients']['apps']['english-one']
    assert child.config['REPLY_LANGUAGE']=='en' and not child.config['SCIENCE_CONTEXT']
    assert 'Test learner' not in child.config['REPLY_RULES'] and 'Test town' not in child.config['REPLY_RULES']
    assert 'Sreehari' not in child.config['REPLY_RULES']
    monkeypatch.setattr('app.research_lookup',lambda *_:pytest.fail('Research lookup must be disabled'))
    c.get('/clients/english-one/csrf-token',headers=headers)
    token=c.get('/clients/english-one/csrf-token',headers=headers).json['csrf']
    for question in ('How does rain form?', 'മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?'):
        r=c.post('/clients/english-one/test_chat',json={'user_message':question},headers={**headers,'X-CSRF-Token':token})
        assert r.status_code==200 and r.json['reply']=='Rain falls from clouds.'


def test_memory_update_and_csrf_are_tenant_scoped(service):
    app, _, en, ml, _ = service
    c=app.test_client(); eh=basic(en['admin_username'],en['admin_password']); mh=basic(ml['admin_username'],ml['admin_password'])
    et=c.get('/clients/english-one/csrf-token',headers=eh).json['csrf']
    mt=c.get('/clients/malayalam-one/csrf-token',headers=mh).json['csrf']
    assert c.post('/clients/malayalam-one/update',data={'csrf_token':et,'memory_text':'bad'},headers=mh).status_code==403
    assert c.post('/clients/english-one/update',data={'csrf_token':et,'memory_text':'Favorite color is blue.'},headers=eh).status_code==200
    children=app.extensions['clients']['apps']
    assert 'blue' in open(children['english-one'].config['MEMORY_PATH']).read()
    assert 'blue' not in open(children['malayalam-one'].config['MEMORY_PATH']).read()


def test_registration_auth_validation_and_hash_only_storage(service):
    app, registry, _, _, _=service;c=app.test_client();owner=basic('owner','owner-password')
    assert c.post('/api/clients',json=profile('new-client')).status_code==401
    r=c.post('/api/clients',json=profile('new-client'),headers=owner)
    assert r.status_code==201 and r.json['device_token'] and r.json['admin_password']
    assert 'no-store' in r.headers['Cache-Control']
    assert c.post('/api/clients',json=profile('new-client'),headers=owner).status_code==400
    assert c.post('/api/clients',json=profile('../escape'),headers=owner).status_code==400
    stored=registry.path.read_bytes()
    assert r.json['device_token'].encode() not in stored and r.json['admin_password'].encode() not in stored
    assert 'device_token' not in c.get('/api/clients',headers=owner).text
    restarted=ClientRegistry(registry.path)
    assert restarted.get(token=r.json['device_token'])['id']=='new-client'


def test_english_provider_language_and_speech(monkeypatch,tmp_path):
    from openai_provider import OpenAIProvider
    import gtts
    app=create_app(dict(TESTING=True,MEMORY_PATH=str(tmp_path/'m'),CLIENT_PROFILE=profile(),
                        REPLY_LANGUAGE='en',SCIENCE_CONTEXT=False,DEMO_MODE=False),Fake())
    provider=OpenAIProvider(app,app.config['REPLY_RULES']); calls=[]
    def response(stage,path,**kw):
        calls.append((stage,kw))
        return {'text':'മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?'} if stage=='stt' else {'output':[{'type':'message','content':[{'type':'output_text','text':'Rain comes from clouds.'}]}]}
    monkeypatch.setattr(provider,'_request',response)
    assert provider.answer('Helpful tutor',[], 'മഴ എങ്ങനെ?')=='Rain comes from clouds.'
    assert 'in English' in calls[0][1]['json']['instructions']
    assert 'Always respond only in natural conversational Malayalam' not in calls[0][1]['json']['instructions']
    assert provider.transcribe(pcm()).startswith('മഴ')
    assert calls[-1][1]['data']['languages[]'] == ['ml', 'en']
    seen={}
    class Voice:
        def __init__(self,**kw): seen.update(kw)
        def write_to_fp(self,out): out.write(b'ID3english')
    monkeypatch.setattr(gtts,'gTTS',Voice)
    assert provider.speak('Hello')==b'ID3english' and seen['lang']=='en'


def test_unique_result_cannot_be_polled_by_another_client(service):
    app, _, en, ml, _ = service;c=app.test_client()
    headers={**bearer(en),'X-Request-ID':'english-only-123','Prefer':'respond-async'}
    assert c.post('/chat',data=pcm(),content_type='audio/wav',headers=headers).status_code in (200,202)
    child=app.extensions['clients']['apps']['english-one']
    child.extensions['karen']['jobs'].get('english-only-123').thread.join(2)
    assert c.get('/requests/english-only-123',headers=bearer(ml)).status_code==404
    assert c.get('/requests/english-only-123',headers=bearer(en)).status_code==200


def test_concurrent_tenants_receive_their_own_memory_and_language(service):
    app, _, en, ml, providers=service
    # Initialize independent apps then overlap their provider execution.
    for reg in (en,ml):
        app.test_client().get('/clients/'+reg['client']['id']+'/health')
    barrier=threading.Barrier(2)
    def answer_for(identifier):
        def answer(memory,history,message):
            barrier.wait(timeout=3)
            providers[identifier].seen.append((memory,history,message))
            return identifier
        return answer
    for identifier,p in providers.items(): p.answer=answer_for(identifier)
    results={}
    def submit(reg):
        c=app.test_client();identifier=reg['client']['id']
        results[identifier]=c.post('/chat',data=pcm(),content_type='audio/wav',headers=bearer(reg)).status_code
    threads=[threading.Thread(target=submit,args=(reg,)) for reg in (en,ml)]
    for thread in threads: thread.start()
    for thread in threads: thread.join(5)
    assert results=={'english-one':200,'malayalam-one':200}
    for identifier in results:
        child=app.extensions['clients']['apps'][identifier]
        assert child.extensions['karen']['history'][-1][1]==identifier
        assert providers[identifier].seen[0][1]==[]


def test_english_errors_and_privacy_fallback_stay_english(service):
    app, _, en, _, providers=service;c=app.test_client()
    c.get('/clients/english-one/health')
    p=providers['english-one']
    from jobs import ServiceError
    def fail(_): raise ServiceError('Provider failure', 'stt_unavailable')
    p.transcribe=fail
    spoken=[]
    p.speak=lambda text: spoken.append(text) or b'ID3error'
    response=c.post('/chat',data=pcm(),content_type='audio/wav',headers=bearer(en))
    assert response.status_code==200 and response.headers['X-Karen-Result']=='spoken-error'
    assert spoken and not any('\u0d00'<=ch<='\u0d7f' for ch in spoken[0])
    from openai_provider import OpenAIProvider
    child=app.extensions['clients']['apps']['english-one']
    adapter=OpenAIProvider(child,child.config['REPLY_RULES'])
    assert not any('\u0d00'<=ch<='\u0d7f' for ch in adapter._safe_reply('Sreehari lives in Edapally.'))


def test_english_science_context_translates_reference_without_malayalam_override(tmp_path,monkeypatch):
    from app import create_app
    provider=Fake();seen=[]
    provider.transcribe=lambda _: 'science question'
    provider.answer=lambda memory,history,message: seen.append(memory) or 'An English explanation.'
    spoken=[];provider.speak=lambda text: spoken.append(text) or b'ID3english'
    app=create_app(dict(TESTING=True,MEMORY_PATH=str(tmp_path/'memory'),CLIENT_PROFILE=profile(science=True),
                        REPLY_LANGUAGE='en',SCIENCE_CONTEXT=True,DEMO_MODE=False),provider)
    monkeypatch.setattr('app.research_lookup',lambda *_:dict(reply='മലയാളത്തിലുള്ള വസ്തുത',spoken_reply='മലയാളത്തിലുള്ള ശബ്ദം',sources=[],topic_id='science',fact_ids=[]))
    response=app.test_client().post('/chat',data=pcm(),content_type='audio/wav')
    assert response.status_code==200 and spoken==['An English explanation.']
    assert 'മലയാളത്തിലുള്ള വസ്തുത' in seen[0]


def test_registered_gemini_transcribes_both_input_languages(tmp_path,monkeypatch):
    from app import Providers
    from google import genai
    app=create_app(dict(TESTING=True,MEMORY_PATH=str(tmp_path/'m'),CLIENT_PROFILE=profile(),
                        REPLY_LANGUAGE='en',SCIENCE_CONTEXT=False,DEMO_MODE=False),Fake())
    seen={}
    class Models:
        def generate_content(self,**kw):
            seen.update(kw)
            return type('Result',(),{'text':'മഴ എങ്ങനെ?'})()
    class Client:
        models=Models()
        def __init__(self,**kw): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
    monkeypatch.setattr(genai,'Client',Client)
    assert Providers(app).transcribe(pcm())=='മഴ എങ്ങനെ?'
    assert 'Malayalam or English' in seen['contents'][1]


def test_unknown_bearer_is_rejected_even_with_open_legacy_local_mode(tmp_path):
    app=create_service(dict(TESTING=True,MEMORY_PATH=str(tmp_path/'memory'),
                            KAREN_ADMIN_PASSWORD='',KAREN_DEVICE_TOKEN=''))
    r=app.test_client().post('/chat',data=pcm(),content_type='audio/wav',headers={'Authorization':'Bearer unknown'})
    assert r.status_code==401
