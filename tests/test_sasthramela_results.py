import pytest
from sasthramela import lookup, history_sources
from sasthramela_results import tables
from test_app import setup, pcm

@pytest.mark.parametrize('year,name,points',[(2019,'GURUKULAM',146),(2022,'Durga',112),(2023,'Durga',142),(2024,'Durga',135),(2025,'Dwaraka',164)])
def test_school_leaders_come_from_each_published_table(year,name,points):
    a=lookup(f'Which school topped the published {year} overall school table?')
    assert name in a['reply'] and str(points) in a['reply']
    assert a['sources'][0]['id']==f'core-result-{year}-school'
    assert ('വ്യത്യാസങ്ങളുണ്ട്' in a['reply']) is (year!=2025)

@pytest.mark.parametrize('year,name,points',[(2019,'Palakkad',1366),(2022,'Palakkad',1383),(2023,'Malappuram',1407),(2024,'Malappuram',1429),(2025,'Malappuram',1548)])
def test_district_scope_stays_separate(year,name,points):
    a=lookup(f'Which district topped the {year} overall district table?')
    assert name in a['reply'] and str(points) in a['reply']
    assert a['sources'][0]['id']==f'core-result-{year}-district'

def test_top_rows_counts_followup_and_missing_year():
    a=lookup('Show top 3 schools in the 2025 overall school table')
    for value in ['Dwaraka','Durga','Fathima','164','140','135']:assert value in a['reply']
    a=lookup('How many schools are listed in the 2025 overall school table?')
    assert '1288' in a['reply']
    q='Which school topped the 2025 overall school table?'
    a=lookup('Who came second?', [('user',q),('model',lookup(q)['reply'])])
    assert 'Durga' in a['reply'] and '140' in a['reply'] and 'Dwaraka' not in a['reply']
    assert not lookup('Who topped the 2026 overall school table?')['sources']
    assert not lookup('Which school topped the overall school table?')['sources']
    assert lookup('How does rain form?') is None

def test_malayalam_and_range_sources():
    a=lookup('2025ലെ മൊത്തം സ്കൂൾ പട്ടികയിൽ ഒന്നാമത് ഏത് സ്കൂളാണ്?')
    assert 'Sacred Heart' in a['reply'] and '164' in a['reply']
    a=lookup('Which schools topped the overall school tables from 2019 to 2025?')
    assert len(a['sources'])==5
    assert len(tables()[0])==10

def test_exact_reported_question_text_voice_sources_and_no_model(setup):
    app,client,provider,token=setup
    q='Which school topped the published 2025 overall school table?'
    a=lookup(q)
    r=client.post('/test_chat',json={'user_message':q},headers={'X-CSRF-Token':token})
    assert r.status_code==200 and r.json['reply']==a['reply']
    assert r.json['sources'][0]['id']=='core-result-2025-school'
    assert not provider.seen
    assert a['sources'][0]['url'] in client.get('/').text
    assert history_sources([('user',q),('model',a['reply'])])[1]==a['sources']
    provider.transcribe=lambda data:q
    spoken=[];provider.speak=lambda text:spoken.append(text) or b'ID3test'
    r=client.post('/chat',data=pcm(),content_type='audio/wav')
    assert r.status_code==200 and spoken==[a['reply']] and not provider.seen


def test_other_competitions_and_named_rank_do_not_receive_school_leader():
    from sasthramela_results import lookup as result_lookup
    assert result_lookup('Which school topped the 2025 SISF overall school table?') is None
    assert result_lookup('Which school topped the 2025 subdistrict overall school table?') is None
    assert not lookup('What rank was Durga in the 2025 overall school table?')['sources']
