"""Request-scoped web citations across text, voice, history and replay."""
from collections import deque
import re
import threading
import time
from urllib.parse import quote

import pytest

from app import create_app
from exhibition_identity import CREATOR_REPLY, PRIVATE_REPLY
from jobs import ServiceError
from test_app import Fake, pcm, post
from test_exhibition_identity import LEGACY_MEMORY


QUESTION = 'Who won 2026 t20 world cup men?'
REPLY = 'പരിശോധിച്ച മത്സരഫലം ലഭിച്ചു.'
SOURCES = [{'url': 'https://www.icc-cricket.com/news/checked-result', 'title': 'Official result'}]
OTHER = [{'url': 'https://www.nobelprize.org/prizes/checked-result/', 'title': 'Official prizes'}]


class WebFake(Fake):
    def __init__(self):
        super().__init__()
        self.answers = deque()
        self.spoken = []

    def answer(self, *args):
        raise AssertionError('A provider with request-scoped sources must use its rich answer method')

    def answer_with_sources(self, memory, history, message):
        self.seen.append((memory, history, message))
        if self.fail:
            raise ServiceError('Answer temporarily unavailable.', 'model_unavailable')
        return self.answers.popleft() if self.answers else (REPLY, SOURCES)

    def transcribe(self, data):
        return QUESTION

    def speak(self, text):
        self.spoken.append(text)
        return super().speak(text)


@pytest.fixture
def web_app(tmp_path):
    provider = WebFake()
    app = create_app({'TESTING': True, 'SECRET_KEY': 'sources-test',
                      'MEMORY_PATH': str(tmp_path / 'memory.txt'), 'DEMO_MODE': False,
                      'AI_PROVIDER': 'gemini', 'KAREN_ADMIN_PASSWORD': '',
                      'KAREN_DEVICE_TOKEN': '', 'SESSION_COOKIE_SECURE': False}, provider)
    client = app.test_client()
    client.get('/')
    with client.session_transaction() as session:
        csrf = session['csrf']
    return app, client, provider, csrf


def finish(app, client, key):
    job = app.extensions['karen']['jobs'].get(key)
    job.thread.join(2)
    assert not job.thread.is_alive()
    return client.get('/requests/' + key)


def test_web_text_sources_survive_dashboard_polling_and_duplicate_request(web_app):
    app, client, provider, csrf = web_app
    headers = {'X-CSRF-Token': csrf, 'X-Request-ID': 'web-text-source-001'}
    first = client.post('/test_chat', json={'user_message': QUESTION}, headers=headers)
    assert first.status_code == 200
    assert first.json['reply'] == REPLY
    assert first.json['sources'] == SOURCES
    assert first.json['research_topic'] == 'web'
    assert client.get('/requests/web-text-source-001').json == first.json
    assert client.post('/test_chat', json={'user_message': QUESTION}, headers=headers).json == first.json
    assert len(provider.seen) == 1 and len(app.extensions['karen']['history']) == 2
    page = client.get('/').text
    assert SOURCES[0]['url'] in page and SOURCES[0]['title'] in page


def test_identical_reply_text_keeps_each_requests_own_sources(web_app):
    _, client, provider, csrf = web_app
    provider.answers.extend([(REPLY, SOURCES), (REPLY, OTHER)])
    assert post(client, csrf, QUESTION).json['sources'] == SOURCES
    assert post(client, csrf, 'Who won Nobel prize last year?').json['sources'] == OTHER
    answers = re.findall(r'<article class="message model">(.*?)</article>', client.get('/').text, re.S)
    assert len(answers) == 2
    assert SOURCES[0]['url'] in answers[0] and OTHER[0]['url'] not in answers[0]
    assert OTHER[0]['url'] in answers[1] and SOURCES[0]['url'] not in answers[1]


def test_web_voice_speaks_only_reply_and_retains_sources_after_refresh_and_replay(web_app):
    app, client, provider, _ = web_app
    headers = {'X-Request-ID': 'web-voice-source-001'}
    first = client.post('/chat', data=pcm(), content_type='audio/wav', headers=headers)
    assert first.status_code == 200 and first.mimetype == 'audio/mpeg'
    assert first.headers['X-Karen-Result'] == 'ok'
    assert first.headers['X-Karen-Research-Topic'] == 'web'
    assert provider.spoken == [REPLY]
    assert client.get('/requests/web-voice-source-001').data == first.data
    assert client.post('/chat', data=pcm(), content_type='audio/wav', headers=headers).data == first.data
    assert provider.spoken == [REPLY] and len(provider.seen) == 1
    assert SOURCES[0]['url'] in client.get('/').text
    assert app.extensions['karen']['history'][-1] == ('model', REPLY)


def test_external_history_replacement_cannot_attach_old_sources_to_equal_text(web_app):
    app, client, _, csrf = web_app
    assert post(client, csrf, QUESTION).json['sources'] == SOURCES
    history = app.extensions['karen']['history']
    history[:] = [('user', 'A different question'), ('model', REPLY)]
    assert SOURCES[0]['url'] not in client.get('/').text
    assert not app.extensions['karen']['turn_sources']


def test_source_storage_trims_with_the_twenty_turn_history(web_app):
    app, client, provider, csrf = web_app
    for index in range(12):
        source = {'url': f'https://results.example/final/{index}', 'title': f'Result {index}'}
        provider.answers.append((f'പരിശോധിച്ച ഫലം {index}.', [source]))
        assert post(client, csrf, f'Who won match number {index} in 2026?').status_code == 200
    assert len(app.extensions['karen']['history']) == 20
    assert len(app.extensions['karen']['turn_sources']) == 10
    page = client.get('/').text
    assert 'href="https://results.example/final/0"' not in page
    assert 'href="https://results.example/final/1"' not in page
    assert 'href="https://results.example/final/11"' in page


@pytest.mark.parametrize('mutation', ['reset', 'memory'])
def test_reset_and_memory_save_clear_stored_sources(web_app, mutation):
    app, client, _, csrf = web_app
    assert post(client, csrf, QUESTION).json['sources'] == SOURCES
    data = {'csrf_token': csrf}
    if mutation == 'memory':
        data['memory_text'] = 'Water boils at 100 degrees Celsius.'
    assert client.post('/reset' if mutation == 'reset' else '/update', data=data).status_code in (200, 302)
    assert not app.extensions['karen']['history']
    assert not app.extensions['karen']['turn_sources']
    assert SOURCES[0]['url'] not in client.get('/').text


@pytest.mark.parametrize('mutation', ['reset', 'memory', 'deadline'])
def test_inflight_answer_cannot_restore_sources_after_revision_or_deadline(web_app, mutation):
    app, client, provider, csrf = web_app
    entered, release = threading.Event(), threading.Event()
    original = provider.answer_with_sources

    def slow(*args):
        entered.set()
        assert release.wait(2)
        return original(*args)

    provider.answer_with_sources = slow
    key = 'web-source-inflight-001'
    try:
        response = client.post('/test_chat', json={'user_message': QUESTION}, headers={
            'X-CSRF-Token': csrf, 'X-Request-ID': key, 'Prefer': 'respond-async'})
        assert response.status_code == 202 and entered.wait(1)
        if mutation == 'deadline':
            job = app.extensions['karen']['jobs'].get(key)
            with job.lock:
                job.deadline = time.monotonic() - 1
            assert client.get('/requests/' + key).status_code == 504
        elif mutation == 'reset':
            assert client.post('/reset', data={'csrf_token': csrf}).status_code == 302
        else:
            assert client.post('/update', data={'csrf_token': csrf, 'memory_text': 'Updated public facts.'}).status_code == 200
    finally:
        release.set()
    result = finish(app, client, key)
    assert result.status_code == (504 if mutation == 'deadline' else 409)
    assert not app.extensions['karen']['history']
    assert not app.extensions['karen']['turn_sources']
    assert SOURCES[0]['url'] not in client.get('/').text


def test_tts_failure_does_not_commit_web_sources(web_app):
    app, client, provider, _ = web_app
    provider.tts_fail = True
    response = client.post('/chat', data=pcm(), content_type='audio/wav',
                           headers={'X-Request-ID': 'web-source-tts-fail-001'})
    assert response.status_code == 503
    assert not app.extensions['karen']['history']
    assert not app.extensions['karen']['turn_sources']
    assert SOURCES[0]['url'] not in client.get('/').text


def test_generation_failure_does_not_attach_sources_to_a_previous_answer(web_app):
    app, client, provider, csrf = web_app
    assert post(client, csrf, QUESTION).json['sources'] == SOURCES
    provider.fail = True
    response = post(client, csrf, 'Who won Nobel prize last year?')
    assert response.status_code == 503
    assert len(app.extensions['karen']['history']) == 2
    assert len(app.extensions['karen']['turn_sources']) == 1
    assert SOURCES[0]['url'] in client.get('/').text


@pytest.mark.parametrize('channel', ['text', 'voice'])
def test_redacted_provider_reply_drops_its_links_before_json_history_or_speech(web_app, channel):
    app, client, provider, csrf = web_app
    provider.answers.append((LEGACY_MEMORY, SOURCES))
    if channel == 'text':
        result = post(client, csrf, QUESTION)
        assert result.json['reply'] == PRIVATE_REPLY and result.json['sources'] == []
    else:
        result = client.post('/chat', data=pcm(), content_type='audio/wav',
                             headers={'X-Request-ID': 'web-private-voice-001'})
        assert result.status_code == 200 and provider.spoken == [PRIVATE_REPLY]
        assert result.headers['X-Karen-Research-Topic'] == ''
    assert SOURCES[0]['url'] not in client.get('/').text
    assert not app.extensions['karen']['turn_sources']


def test_unsafe_or_private_citations_are_filtered_and_public_links_are_copied(web_app):
    _, client, provider, csrf = web_app
    safe = {'url': 'https://results.example/checked', 'title': 'Checked result'}
    sources = [
        {'url': 'javascript:alert(1)', 'title': 'Unsafe'},
        {'url': 'https://user:password@results.example/', 'title': 'Credentials'},
        {'url': 'https://results.example/\n', 'title': 'Control character'},
        {'url': 'https://results.example/?q=' + quote(LEGACY_MEMORY), 'title': 'Private URL'},
        {'url': 'https://results.example/biography', 'title': LEGACY_MEMORY},
        safe, safe,
    ]
    provider.answers.append((REPLY, sources))
    response = post(client, csrf, QUESTION)
    assert response.json['sources'] == [safe]
    safe['url'] = 'https://results.example/mutated'
    safe['title'] = 'Mutated title'
    assert 'https://results.example/checked' in client.get('/').text
    assert 'https://results.example/mutated' not in client.get('/').text
    assert client.get('/requests/' + response.json['request_id']).json['sources'][0]['title'] == 'Checked result'


def test_web_source_count_is_bounded(web_app):
    _, client, provider, csrf = web_app
    provider.answers.append((REPLY, [{'url': f'https://results.example/{index}', 'title': str(index)} for index in range(20)]))
    assert len(post(client, csrf, QUESTION).json['sources']) == 8


def test_identity_and_local_research_keep_priority_over_web_provider(web_app):
    _, client, provider, csrf = web_app
    assert post(client, csrf, 'Who built Karen?').json['reply'] == CREATOR_REPLY
    research = post(client, csrf, 'How many pupils must participate in HS Science Working Model?')
    assert research.status_code == 200 and research.json['sources']
    assert research.json['research_topic'] != 'web'
    assert not provider.seen
