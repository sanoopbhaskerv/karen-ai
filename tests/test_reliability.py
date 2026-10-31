import io
import threading
import time
from types import SimpleNamespace

import pytest

from app import create_app, Providers, ServiceError
from test_app import Fake, pcm, setup  # reuse the original provider/isolated memory fixture


def submit(c, token, text='hello', key='request-1234', asynchronous=False):
    headers = {'X-CSRF-Token': token, 'Accept': 'application/json', 'X-Request-ID': key}
    if asynchronous:
        headers['Prefer'] = 'respond-async'
    return c.post('/test_chat', json={'user_message': text}, headers=headers)


def finish(app, c, key='request-1234'):
    job = app.extensions['karen']['jobs'].get(key)
    job.thread.join(2)
    assert not job.thread.is_alive()
    return c.get('/requests/' + key)


def test_replayed_post_and_poll_do_not_duplicate_turn(setup):
    app, c, p, token = setup
    first = submit(c, token)
    again = submit(c, token)
    assert first.json == again.json == c.get('/requests/request-1234').json
    assert len(p.seen) == 1
    assert len(app.extensions['karen']['history']) == 2
    assert submit(c, token, 'different').status_code == 409


def test_concurrent_duplicate_reuses_pending_job_and_dashboard_stays_responsive(setup):
    app, c, p, token = setup
    entered, release = threading.Event(), threading.Event()
    original = p.answer
    def slow(*args):
        entered.set()
        assert release.wait(2)
        return original(*args)
    p.answer = slow
    try:
        first = submit(c, token, asynchronous=True)
        assert first.status_code == 202 and entered.wait(1)
        assert submit(c, token, asynchronous=True).status_code == 202
        assert submit(c, token, key='another-1234', asynchronous=True).json['code'] == 'busy'
        assert c.get('/').status_code == c.get('/health').status_code == 200
    finally:
        release.set()
    assert finish(app, c).status_code == 200
    assert len(p.seen) == 1


@pytest.mark.parametrize('mutation', ['reset', 'memory'])
def test_reset_or_memory_edit_cannot_be_undone_by_inflight_answer(setup, mutation):
    app, c, p, token = setup
    entered, release = threading.Event(), threading.Event()
    original = p.answer
    def slow(*args):
        entered.set(); assert release.wait(2)
        return original(*args)
    p.answer = slow
    try:
        submit(c, token, asynchronous=True); assert entered.wait(1)
        if mutation == 'reset':
            c.post('/reset', data={'csrf_token': token})
        else:
            c.post('/update', data={'csrf_token': token, 'memory_text': 'Updated facts'})
    finally:
        release.set()
    assert finish(app, c).json['code'] == 'conversation_changed'
    assert not app.extensions['karen']['history']


def test_request_deadline_never_commits_late_result(setup):
    app, c, p, token = setup
    entered, release = threading.Event(), threading.Event()
    original = p.answer
    def slow(*args):
        entered.set()
        assert release.wait(2)
        return original(*args)
    p.answer = slow
    try:
        assert submit(c, token, asynchronous=True).status_code == 202
        assert entered.wait(1)
        # Expire a known-running request explicitly. A 10 ms real-time wait can
        # wake just before its deadline on Windows and legitimately return 202.
        job = app.extensions['karen']['jobs'].get('request-1234')
        with job.lock:
            job.deadline = time.monotonic() - 1
        response = c.get('/requests/request-1234')
        assert response.status_code == 504
        assert response.json['code'] == 'request_timeout'
        assert submit(c, token, key='different-1234', asynchronous=True).json['code'] == 'busy'
    finally:
        release.set()
    assert finish(app, c).status_code == 504
    assert not app.extensions['karen']['history']


def test_voice_replay_returns_same_mp3_without_new_stt_or_turn(setup):
    app, c, p, token = setup
    headers = {'X-Request-ID': 'voice-12345'}
    first = c.post('/chat', data=pcm(), content_type='audio/wav', headers=headers)
    second = c.post('/chat', data={'audio': (io.BytesIO(pcm()), 'question.wav')}, headers=headers)
    assert first.status_code == second.status_code == 200
    assert first.data == second.data == c.get('/requests/voice-12345').data
    assert len(p.seen) == 1


def test_tts_failure_does_not_commit_an_unheard_turn(setup):
    app, c, p, token = setup
    p.tts_fail = True
    response = c.post('/chat', data=pcm(), content_type='audio/wav', headers={'X-Request-ID': 'voice-12345'})
    assert response.status_code == 503
    assert not app.extensions['karen']['history']
    p.tts_fail = False
    assert c.get('/requests/voice-12345').status_code == 503


def test_unknown_request_invalid_id_and_nonobject_json(setup):
    app, c, p, token = setup
    assert c.get('/requests/unknown-1234').status_code == 404
    assert submit(c, token, key='bad').status_code == 400
    assert c.post('/test_chat', json=['hello'], headers={'X-CSRF-Token': token}).status_code == 400


@pytest.mark.parametrize('provider_code, expected, attempts', [
    (504, 'model_timeout', 2), (503, 'model_unavailable', 2),
    (403, 'model_auth', 1), (404, 'model_not_found', 1), (429, 'model_quota', 1),
])
def test_gemini_classifies_and_bounds_retries_without_logging_secret(setup, monkeypatch, caplog,
                                                                    provider_code, expected, attempts):
    from google import genai
    app, c, p, token = setup
    app.config['GEMINI_API_KEY'] = 'secret-that-must-never-be-logged'
    calls = []
    class Problem(Exception):
        code = provider_code
    class Client:
        def __init__(self, **kwargs):
            assert kwargs['http_options'].timeout == 45000
            assert kwargs['http_options'].retry_options.attempts == 1
            self.models = self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            raise Problem('URL includes secret-that-must-never-be-logged')
    monkeypatch.setattr(genai, 'Client', Client)
    monkeypatch.setattr('app.time.sleep', lambda _: None)
    provider = Providers(app)
    with pytest.raises(ServiceError) as error:
        provider.answer('private facts', [], 'private question')
    assert error.value.code == expected
    assert len(calls) == attempts
    assert provider.diagnostic['provider_code'] == provider_code
    assert expected in caplog.text
    for value in ('secret-that-must-never-be-logged', 'private facts', 'private question'):
        assert value not in caplog.text


def test_transient_gemini_error_retries_same_context_once(setup, monkeypatch):
    from google import genai
    app, c, p, token = setup
    app.config['GEMINI_API_KEY'] = 'test-not-real'
    calls = []
    class Temporary(Exception): code = 503
    class Client:
        def __init__(self, **kwargs): self.models = self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1: raise Temporary()
            return SimpleNamespace(text='മലയാളം')
    monkeypatch.setattr(genai, 'Client', Client)
    monkeypatch.setattr('app.time.sleep', lambda _: None)
    assert Providers(app).answer('facts', [('user', 'first'), ('model', 'reply')], 'next') == 'മലയാളം'
    assert calls[0]['contents'] == calls[1]['contents']


def test_health_distinguishes_untested_from_ready(setup):
    app, c, p, token = setup
    assert c.get('/health').json['gemini']['status'] == 'untested'
    assert c.get('/health').json['request_timeout_seconds'] == 140


def test_large_audio_is_rejected_before_committing_turn(setup):
    app, c, p, token = setup
    p.speak = lambda text: b'x' * 512001
    result = c.post('/chat', data=pcm(), content_type='audio/wav')
    assert result.status_code == 502
    assert result.json['code'] == 'audio_too_large'
    assert not app.extensions['karen']['history']


def test_unexpected_exception_does_not_leak_into_response_or_console(setup, caplog):
    app, c, p, token = setup
    def broken(*args): raise RuntimeError('secret-url-and-private-question')
    p.answer = broken
    result = submit(c, token)
    assert result.status_code == 500 and result.json['code'] == 'internal_error'
    assert 'secret-url-and-private-question' not in result.text + caplog.text
    assert not app.extensions['karen']['history']


def test_result_retention_and_capacity_are_bounded(setup, monkeypatch):
    app, c, p, token = setup
    jobs = app.extensions['karen']['jobs']
    jobs.capacity = 1
    assert submit(c, token).status_code == 200
    jobs.get('request-1234').thread.join(1)
    assert submit(c, token, key='next-question').json['code'] == 'busy'
    now = time.monotonic()
    monkeypatch.setattr('jobs.time.monotonic', lambda: now + 601)
    assert c.get('/requests/request-1234').status_code == 404
    assert submit(c, token, key='next-question').status_code == 200
    assert len(jobs.items) == 1
