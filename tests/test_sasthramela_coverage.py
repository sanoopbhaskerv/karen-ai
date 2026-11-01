"""User acceptance plus independent paraphrases; never loaded by runtime retrieval."""
from pathlib import Path
import json
import pytest
from sasthramela import lookup, history_sources
from sasthramela_topics import config
from test_app import setup, pcm

CASES=json.loads(Path(__file__).with_name('sasthramela_acceptance.json').read_text())
@pytest.mark.parametrize('case,q',[(c,q) for c in CASES for q in c['questions']],ids=[f"q{c['number']}-{i}" for c in CASES for i in range(3)])
def test_requested_coverage_and_paraphrases(case,q):
    answer=lookup(q)
    assert answer is not None,(case['number'],q)
    assert answer.get('topic_id')==case['topic'],(q,answer)
    assert answer['sources'],(q,answer)
    for term in case['required_terms']:assert term in answer['reply'],(q,term,answer['reply'])
    assert all(s['url'].startswith(('https://','http://')) for s in answer['sources'])

@pytest.mark.parametrize('case',CASES,ids=lambda c:f"q{c['number']}")
def test_full_text_and_voice_route_without_generation(setup,case):
    app,client,provider,token=setup
    question=case['questions'][0];expected=lookup(question)
    r=client.post('/test_chat',json={'user_message':question},headers={'X-CSRF-Token':token})
    assert r.status_code==200 and r.json['research_topic']==case['topic']
    assert r.json['sources']==expected['sources']
    provider.transcribe=lambda data:question
    spoken=[];provider.speak=lambda text:spoken.append(text) or b'ID3test'
    r=client.post('/chat',data=pcm(),content_type='audio/wav')
    assert r.status_code==200 and r.headers['X-Karen-Research-Topic']==case['topic']
    assert spoken==[expected.get('spoken_reply',expected['reply'])]
    assert not provider.seen
    assert history_sources(app.extensions['karen']['history'])

@pytest.mark.parametrize('question,topic,terms',[
 ('Which category is class 9 eligible for in the 2026 science fair?','registration-categories',['8–10','HS']),
 ('What are the 2026 Working Model item codes?','working-item-codes',['106','115','126']),
 ('How does the school register entries through the 2026 portal?','school-login',['Sampoorna','2022–23']),
 ('How do we qualify for the next level in 2026?','progression',['A ഗ്രേഡും','ഒന്നോ രണ്ടോ']),
 ('What is the 2026 subdistrict registration fee?','registration-contribution',['ഇരുപത്','പന്ത്രണ്ട്']),
 ('What is the subdistrict appeal fee and time limit?','appeals',['1000','മണിക്കൂ']),
 ('What documents must we submit at registration?','registration-documents',['ജില്ലാ','ഉപജില്ല']),
 ('What is the 2026 science fair theme?','2026-theme',['Viksit Bharat','Artificial Intelligence']),
 ('Where is the 2026 state event venue?','2026-state-venues',['മണ്ണാർക്കാട്','Kalladi']),
 ('What is the 2026 subdistrict registration deadline?','2026-planned-deadlines',['ആസൂത്രിത','ഊഹിക്കരുത്']),
 ('Which manual applies to the 2026 fair?','current-manual',['2025']),
 ('Are grace marks guaranteed for the coming examination?','grace-marks',['2025–26'])])
def test_existing_2026_registration_material(question,topic,terms):
    a=lookup(question);assert a and a['topic_id']==topic
    for t in terms:assert t in a['reply']
    assert a['sources']

def test_unrelated_and_unsupported_boundaries():
    for q in ['How does rain form?','Tell me about Roman history','How does Arduino PWM work?','How long can a YouTube video be?']:
        assert lookup(q) is None
    for q in ['What are the 2039 working model rules?','Who won 2024 state HS Robotics in sastra mela?','Who won 2025 district HS Robotics in sastra mela?']:
        assert not lookup(q)['sources']
    assert lookup('How does rain form?', [('user','What is TinyML?'),('model','RP2040')]) is None


def test_combined_preparation_and_registration_overview():
    a=lookup('What team size, charts and participation video are needed for HS Working Model?')
    assert a['topic_id']=='working-preparation'
    for term in ['രണ്ട്','ചാർട്ട','വീഡിയോ']:assert term in a['reply']
    a=lookup('Give all 2026 Sasthramela registration category details and rules')
    assert a['topic_id']=='registration-overview'
    for term in ['LP','UP','HS','115','Sampoorna','122']:assert term in a['reply']
    assert len(a['spoken_reply'])<len(a['reply'])

def test_plain_it_pronoun_is_not_it_fair():
    a=lookup('For the working model, must it be offline or is cloud internet allowed?')
    assert a['topic_id']=='network-rules'
    assert 'offline-only' in a['reply']

def test_followup_uses_recent_project_without_rewriting_its_award():
    prior='What is Arif’s Simulation Driving Instrument prize?'
    a=lookup('Did it win overall?', [('user',prior),('model',lookup(prior)['reply'])])
    assert a['topic_id']=='arif-award'
    assert 'ഒന്നാം സമ്മാനമല്ല' in a['reply']


def test_short_followups_inherit_fair_or_working_model_context():
    a=lookup('When did it start?', [('user','Tell me about Kerala Sasthramela'),('model','x')])
    assert a['topic_id']=='state-origin' and 'ഉറപ്പായിട്ടില്ല' in a['reply']
    a=lookup('Can I go alone?', [('user','What are the HS Working Model rules?'),('model','x')])
    assert 'രണ്ട്' in a['reply']


def test_it_pronoun_does_not_hide_overall_standings_or_admit_foreign_fees():
    a=lookup('Which school topped the 2025 overall table and can it be verified?')
    assert 'Sacred Heart' in a['reply'] and a['sources']
    assert lookup('What is the 2026 university registration fee?') is None
    assert lookup('What is the fee for a court appeal?') is None


@pytest.mark.parametrize('q,topic',[
 ('2026ലെ രജിസ്ട്രേഷൻ വിഭാഗങ്ങളും ക്ലാസുകളും പറയാമോ?','registration-categories'),
 ('2026 പ്രവർത്തനമാതൃകയുടെ ഇന കോഡുകൾ എന്താണ്?','working-item-codes'),
 ('2026ൽ സ്കൂളുകൾ പോർട്ടലിൽ രജിസ്ട്രേഷൻ ചെയ്യുന്നത് എങ്ങനെ?','school-login'),
 ('അടുത്ത തലത്തിലേക്ക് യോഗ്യത എങ്ങനെയാണ്?','progression'),
 ('ഉപജില്ലയിലെ അപ്പീലിന്റെ ഫീസ് എത്രയാണ്?','appeals'),
 ('2026 ഉപജില്ലാ രജിസ്ട്രേഷൻ ഫീസ് എത്രയാണ്?','registration-contribution'),
 ('രജിസ്ട്രേഷനിൽ സമർപ്പിക്കേണ്ട രേഖകൾ എന്തൊക്കെ?','registration-documents'),
 ('2026 ശാസ്ത്രമേളയുടെ പ്രമേയം എന്താണ്?','2026-theme'),
 ('2026 സംസ്ഥാന മേളയുടെ വേദികൾ എവിടെയാണ്?','2026-state-venues'),
 ('2026 ഉപജില്ലാ രജിസ്ട്രേഷന്റെ അവസാന തീയതി ഏതാണ്?','2026-planned-deadlines'),
 ('2026ൽ നിലവിലെ മാന്വൽ ഏതാണ്?','current-manual'),
 ('വർക്കിങ് മോഡലിന്റെ മാർക്കുകൾ എങ്ങനെയാണ്?','working-rubric')])
def test_registration_and_rule_malayalam_inflections(q,topic):
    a=lookup(q);assert a and a.get('topic_id')==topic
    assert a['sources']


def test_fast_research_burst_retains_earlier_results(setup):
    app,client,provider,token=setup
    first=None
    for n in range(80):
        r=client.post('/test_chat',json={'user_message':'How many pupils must participate in HS Science Working Model?'},
                      headers={'X-CSRF-Token':token,'X-Request-ID':f'coverage-burst-{n:03d}'})
        assert r.status_code==200
        if first is None:first=r.json
    assert not provider.seen
    assert client.get('/requests/coverage-burst-000').json==first
    assert app.extensions['karen']['jobs'].capacity==256
