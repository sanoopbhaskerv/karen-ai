import pytest
from sasthramela import lookup, corpus, history_sources
from test_app import pcm, setup

@pytest.mark.parametrize('question,fact', [
 ('Science working model rules', 'working-rubric'),
 ('How many pupils in HS science working model?', 'working-two-pupils'),
 ('ശാസ്ത്രമേള വർക്കിങ് മോഡൽ വീഡിയോ എത്ര മിനിറ്റാണ്?', 'working-video'),
 ('Science working model judging marks rubric?', 'working-rubric'),
 ('What is the history of Kerala science exhibitions?', 'history-1962-63-regional-fairs'),
 ('When is the 2026 state science fair?', 'state-2026-scheduled'),
])
def test_grounded_bilingual_selection(question,fact):
    answer=lookup(question)
    assert fact in answer['fact_ids']
    assert answer['sources'] and all(s['url'].startswith(('https://','http://')) for s in answer['sources'])
    assert all(f['claim_ml'] in answer['reply'] for f in corpus()[0] if f['id'] in answer['fact_ids'])

def test_unknown_uniform_future_and_science_boundaries():
    assert not lookup('Is there a science fair uniform ban?')['sources']
    assert not lookup('What are the 2039 science working model rules?')['sources']
    assert lookup('How does rain form?') is None
    assert 'working-two-pupils' not in lookup('2025 science fair participants count')['fact_ids']
    assert 'working-video' not in lookup('IT science fair working model video')['fact_ids']

def test_followup_and_sources_survive_history():
    q='HS science working model team size'
    a=lookup(q)
    assert lookup('How long can the video be?', [('user',q),('model',a['reply'])])['fact_ids']==['working-video']
    assert history_sources([('user',q),('model',a['reply'])])[1]==a['sources']

def test_text_voice_privacy_and_no_provider_call(setup):
    app,client,provider,token=setup
    q='How many pupils in HS science working model?'
    r=client.post('/test_chat',json={'user_message':q},headers={'X-CSRF-Token':token})
    assert r.status_code==200 and r.json['sources']
    assert not provider.seen
    assert client.get('/health').json['research']['fact_count'] > 230
    assert r.json['sources'][0]['url'] in client.get('/').text
    provider.transcribe=lambda data:q
    spoken=[]
    provider.speak=lambda text:spoken.append(text) or b'ID3test'
    r=client.post('/chat',data=pcm(),content_type='audio/wav')
    assert r.status_code==200 and spoken[0]==lookup(q)['reply']
    assert not provider.seen


def test_general_science_after_fair_still_uses_provider():
    assert lookup('How does rain form?', [('user','Kerala science fair history'),('model','1962')]) is None
