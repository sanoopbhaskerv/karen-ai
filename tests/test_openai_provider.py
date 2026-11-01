"""Exercise OpenAI HTTP contracts with isolated memory and no live API calls."""
import json
from pathlib import Path
import threading
import time

import httpx
import pytest

from app import RULES, Providers, create_app
from exhibition_identity import PRIVATE_REPLY, contains_identity
from jobs import ServiceError
from test_app import pcm


REPLY = 'നമസ്കാരം! മഴയെക്കുറിച്ച് പറഞ്ഞു തരാം.'
QUESTION = 'മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?'
AUDIO = b'ID3mock-Malayalam-audio'
TEST_KEY = 'test-secret-never-log-this'


def text_result(text=REPLY):
    return {'output': [{'type': 'message', 'role': 'assistant',
                        'content': [{'type': 'output_text', 'text': text}]}]}


@pytest.fixture
def mocked_openai(tmp_path, monkeypatch):
    calls, client_options = [], []
    responses = []
    original_client = httpx.Client

    def handler(request):
        calls.append(request)
        if responses:
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            if callable(response):
                return response(request)
            return response
        if request.url.path.endswith('/responses'):
            return httpx.Response(200, json=text_result())
        if request.url.path.endswith('/audio/transcriptions'):
            return httpx.Response(200, json={'text': QUESTION})
        raise AssertionError('Unexpected OpenAI route')

    def client(*args, **kwargs):
        client_options.append(dict(kwargs))
        kwargs['transport'] = httpx.MockTransport(handler)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, 'Client', client)
    import gtts
    speech = {'calls': [], 'audio': AUDIO, 'error': None}

    class TTS:
        def __init__(self, **kwargs):
            speech['calls'].append(kwargs)

        def write_to_fp(self, output):
            if speech['error']:
                raise speech['error']
            output.write(speech['audio'])

    monkeypatch.setattr(gtts, 'gTTS', TTS)
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test',
                      'MEMORY_PATH': str(tmp_path / 'memory.txt'),
                      'DEMO_MODE': False, 'AI_PROVIDER': 'openai',
                      'OPENAI_API_KEY': TEST_KEY, 'OPENAI_MODEL': 'gpt-6-luna',
                      'OPENAI_STT_MODEL': 'gpt-transcribe',
                      'KAREN_ADMIN_PASSWORD': '', 'KAREN_DEVICE_TOKEN': '',
                      'KAREN_PUBLIC_UI': False})
    app.extensions['fake_tts'] = speech
    from openai_provider import OpenAIProvider
    provider = OpenAIProvider(app, RULES)
    return app, provider, calls, responses, client_options


def test_answer_preserves_malayalam_context_and_uses_low_latency_configuration(mocked_openai, caplog):
    app, provider, calls, responses, client_options = mocked_openai
    reply = provider.answer('Private exhibition facts', [('user', 'earlier'), ('model', 'previous reply')], QUESTION)
    assert reply == REPLY
    assert len(calls) == 1
    request = calls[0]
    assert request.url == 'https://api.openai.com/v1/responses'
    assert request.headers['Authorization'] == 'Bearer ' + TEST_KEY
    body = json.loads(request.content)
    assert body['model'] == 'gpt-6-luna'
    assert body['reasoning'] == {'effort': 'none'}
    assert body['store'] is False
    assert body['max_output_tokens'] == 1024
    assert 'Malayalam' in body['instructions'] and 'Private exhibition facts' in body['instructions']
    assert [turn['role'] for turn in body['input']] == ['user', 'assistant', 'user']
    assert body['input'][-1]['content'] == QUESTION
    assert provider.diagnostic['status'] == 'ready'
    for secret in (TEST_KEY, 'Private exhibition facts', QUESTION, REPLY):
        assert secret not in caplog.text


def test_transcribe_uploads_original_wav_and_language_hint(mocked_openai, caplog):
    app, provider, calls, responses, client_options = mocked_openai
    wav = pcm()
    assert provider.transcribe(wav) == QUESTION
    assert len(calls) == 1
    request = calls[0]
    assert request.url == 'https://api.openai.com/v1/audio/transcriptions'
    assert request.headers['Content-Type'].startswith('multipart/form-data; boundary=')
    assert b'filename="question.wav"' in request.content
    assert b'audio/wav' in request.content and wav in request.content
    assert b'gpt-transcribe' in request.content
    assert b'name="languages' in request.content and b'name="language"' not in request.content
    assert b'ml' in request.content
    assert TEST_KEY not in caplog.text and QUESTION not in caplog.text


def test_speech_uses_malayalam_gtts_and_no_openai_audio_api(mocked_openai, caplog):
    app, provider, calls, responses, client_options = mocked_openai
    assert provider.speak(REPLY) == AUDIO
    assert not calls
    assert app.extensions['fake_tts']['calls'] == [
        {'text': REPLY, 'lang': 'ml', 'timeout': (5, 15)}]
    assert TEST_KEY not in caplog.text and REPLY not in caplog.text


@pytest.mark.parametrize('status, code', [
    (400, 'model_request'), (401, 'model_auth'), (403, 'model_auth'),
    (404, 'model_not_found'), (429, 'model_quota'),
    (500, 'model_unavailable'), (503, 'model_unavailable'),
])
def test_api_failure_is_sanitized_and_not_silently_retried(mocked_openai, caplog, status, code):
    app, provider, calls, responses, client_options = mocked_openai
    responses.append(httpx.Response(status, json={'error': {
        'message': 'private-question-and-' + TEST_KEY, 'type': 'test_error'}}))
    with pytest.raises(ServiceError) as caught:
        provider.answer('private-memory', [], QUESTION)
    assert caught.value.code == code
    assert len(calls) == 1
    assert provider.diagnostic['status'] == 'degraded'
    for value in ('private-question-and-', TEST_KEY, 'private-memory', QUESTION):
        assert value not in str(caught.value) + caplog.text


@pytest.mark.parametrize('exception, code', [
    (httpx.ReadTimeout('private-timeout-url'), 'model_timeout'),
    (httpx.ConnectError('private-network-url'), 'model_network'),
])
def test_transport_failures_have_a_bounded_single_attempt(mocked_openai, caplog, exception, code):
    app, provider, calls, responses, client_options = mocked_openai
    responses.append(exception)
    with pytest.raises(ServiceError) as caught:
        provider.answer('private-memory', [], QUESTION)
    assert caught.value.code == code
    assert len(calls) == 1
    timeout = calls[0].extensions['timeout']
    assert timeout == {'connect': 5, 'read': 20, 'write': 10, 'pool': 5}
    assert 'private-' not in str(caught.value) + caplog.text


@pytest.mark.parametrize('payload', [{}, {'output': []}, text_result('   ')])
def test_empty_answer_is_rejected(mocked_openai, payload):
    app, provider, calls, responses, client_options = mocked_openai
    responses.append(httpx.Response(200, json=payload))
    with pytest.raises(ServiceError):
        provider.answer('facts', [], QUESTION)


def test_unconfigured_openai_key_fails_before_any_http_call(mocked_openai, caplog):
    app, provider, calls, responses, client_options = mocked_openai
    app.config['OPENAI_API_KEY'] = ''
    with pytest.raises(ServiceError) as caught:
        provider.answer('facts', [], QUESTION)
    assert caught.value.code == 'model_unconfigured'
    assert provider.diagnostic['status'] == 'degraded' and not calls
    assert TEST_KEY not in str(caught.value) + caplog.text


@pytest.mark.parametrize('payload', [{}, {'text': ''}, {'text': '   '}])
def test_empty_transcript_is_rejected(mocked_openai, payload):
    app, provider, calls, responses, client_options = mocked_openai
    responses.append(httpx.Response(200, json=payload))
    with pytest.raises(ServiceError):
        provider.transcribe(pcm())


def test_empty_speech_audio_is_rejected(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    app.extensions['fake_tts']['audio'] = b''
    with pytest.raises(ServiceError) as caught:
        provider.speak(REPLY)
    assert caught.value.code == 'tts_empty'
    assert not calls


def test_speech_failure_is_sanitized_and_does_not_commit_history(mocked_openai, caplog):
    app, provider, calls, responses, client_options = mocked_openai
    app.extensions['fake_tts']['error'] = RuntimeError('private-provider-url-' + TEST_KEY)
    client = app.test_client()
    result = client.post('/chat', data=pcm(), content_type='audio/wav',
                         headers={'X-Request-ID': 'openai-speech-error-123'})
    assert result.status_code == 503
    assert not app.extensions['karen']['history']
    assert 'private-provider-url-' not in result.text + caplog.text
    assert TEST_KEY not in result.text + caplog.text
    assert len(calls) == 2
    poll = client.get('/requests/openai-speech-error-123')
    assert poll.status_code == 503 and len(calls) == 2


@pytest.mark.parametrize('method, payload', [
    ('answer', text_result('   ')),
    ('transcribe', {'text': ''}),
])
def test_invalid_provider_output_marks_health_degraded_after_prior_success(mocked_openai, method, payload):
    app, provider, calls, responses, client_options = mocked_openai
    assert provider.answer('facts', [], QUESTION) == REPLY
    assert provider.diagnostic['status'] == 'ready'
    responses.append(httpx.Response(200, json=payload))
    with pytest.raises(ServiceError):
        if method == 'transcribe':
            provider.transcribe(pcm())
        else:
            getattr(provider, method)('facts', [], QUESTION)
    assert provider.diagnostic['status'] == 'degraded'


def test_openai_voice_uses_recognition_and_text_api_with_malayalam_speech(mocked_openai, monkeypatch):
    app, provider, calls, responses, client_options = mocked_openai

    def unexpected(*args):
        raise AssertionError('The legacy Gemini provider must not run for an OpenAI-selected app')

    for method in ('answer', 'transcribe', 'speak'):
        monkeypatch.setattr(Providers, method, unexpected)
    client = app.test_client()
    response = client.post('/chat', data=pcm(), content_type='audio/wav',
                           headers={'X-Request-ID': 'openai-voice-contract-123'})
    assert response.status_code == 200 and response.mimetype == 'audio/mpeg'
    assert response.headers['X-Karen-Result'] == 'ok' and response.data == AUDIO
    assert len(calls) == 2
    assert [request.url.path for request in calls] == ['/v1/audio/transcriptions', '/v1/responses']
    assert [metric.split(';')[0] for metric in response.headers['Server-Timing'].split(', ')] == ['stt', 'openai', 'tts']
    health = client.get('/health').json
    assert health['provider'] == 'openai' and health['model'] == 'gpt-6-luna'
    assert health['configured'] is True
    assert TEST_KEY not in json.dumps(health)
    assert app.extensions['karen']['history'] == [('user', QUESTION), ('model', REPLY)]
    replay = client.post('/chat', data=pcm(), content_type='audio/wav',
                         headers={'X-Request-ID': 'openai-voice-contract-123'})
    poll = client.get('/requests/openai-voice-contract-123')
    for cached in (replay, poll):
        assert cached.status_code == 200 and cached.data == AUDIO
        assert cached.headers['Server-Timing'] == response.headers['Server-Timing']
    assert len(calls) == 2 and len(app.extensions['karen']['history']) == 2
    assert len(app.extensions['fake_tts']['calls']) == 1
    assert app.extensions['fake_tts']['calls'][0]['text'] == REPLY


def test_text_chat_calls_only_openai_generation(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    client = app.test_client()
    client.get('/')
    with client.session_transaction() as session:
        csrf = session['csrf']
    result = client.post('/test_chat', json={'user_message': QUESTION}, headers={
        'X-CSRF-Token': csrf, 'Accept': 'application/json', 'X-Request-ID': 'openai-text-contract-123'})
    assert result.status_code == 200 and result.json['reply'] == REPLY
    assert [request.url.path for request in calls] == ['/v1/responses']
    assert [metric.split(';')[0] for metric in result.headers['Server-Timing'].split(', ')] == ['openai']
    assert not app.extensions['fake_tts']['calls']


@pytest.mark.parametrize('stage, code, metrics', [
    ('stt', 'stt_unavailable', ['stt', 'tts']),
    ('answer', 'model_unavailable', ['stt', 'openai', 'tts']),
])
def test_openai_failure_returns_labeled_malayalam_apology_without_history(mocked_openai, stage, code, metrics):
    app, provider, calls, responses, client_options = mocked_openai
    if stage == 'answer':
        responses.append(httpx.Response(200, json={'text': QUESTION}))
    responses.append(httpx.Response(503, json={'error': {'message': 'private-provider-error'}}))
    client = app.test_client()
    result = client.post('/chat', data=pcm(), content_type='audio/wav',
                         headers={'X-Request-ID': 'openai-spoken-error-123'})
    assert result.status_code == 200 and result.data == AUDIO
    assert result.headers['X-Karen-Result'] == 'spoken-error'
    assert result.headers['X-Karen-Error'] == code
    assert [metric.split(';')[0] for metric in result.headers['Server-Timing'].split(', ')] == metrics
    assert not app.extensions['karen']['history']
    spoken = app.extensions['fake_tts']['calls']
    assert len(spoken) == 1 and spoken[0]['lang'] == 'ml'
    assert any('\u0d00' <= char <= '\u0d7f' for char in spoken[0]['text'])
    assert len(calls) == (2 if stage == 'answer' else 1)
    poll = client.get('/requests/openai-spoken-error-123')
    assert poll.data == result.data and poll.headers['Server-Timing'] == result.headers['Server-Timing']


def pending_audio_turn(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    entered, release = threading.Event(), threading.Event()

    def wait_for_release(request):
        entered.set()
        assert release.wait(3)
        return httpx.Response(200, json=text_result())

    responses.extend([httpx.Response(200, json={'text': QUESTION}), wait_for_release])
    client = app.test_client()
    client.get('/')
    with client.session_transaction() as session:
        csrf = session['csrf']
    response = client.post('/chat', data=pcm(), content_type='audio/wav', headers={
        'X-Request-ID': 'openai-inflight-contract-123', 'Prefer': 'respond-async'})
    assert response.status_code == 202 and entered.wait(2)
    return client, csrf, release


@pytest.mark.parametrize('mutation', ['reset', 'memory'])
def test_inflight_audio_answer_cannot_restore_changed_conversation(mocked_openai, mutation):
    app, provider, calls, responses, client_options = mocked_openai
    client, csrf, release = pending_audio_turn(mocked_openai)
    try:
        if mutation == 'reset':
            assert client.post('/reset', data={'csrf_token': csrf}).status_code == 302
        else:
            assert client.post('/update', data={'csrf_token': csrf, 'memory_text': 'Updated exhibition facts'}).status_code == 200
    finally:
        release.set()
    job = app.extensions['karen']['jobs'].get('openai-inflight-contract-123')
    job.thread.join(2)
    assert not job.thread.is_alive()
    result = client.get('/requests/openai-inflight-contract-123')
    assert result.status_code == 409 and result.json['code'] == 'conversation_changed'
    assert not app.extensions['karen']['history']


def test_expired_audio_generation_cannot_commit_late_result(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    client, csrf, release = pending_audio_turn(mocked_openai)
    try:
        job = app.extensions['karen']['jobs'].get('openai-inflight-contract-123')
        with job.lock:
            job.deadline = time.monotonic() - 1
        result = client.get('/requests/openai-inflight-contract-123')
        assert result.status_code == 504 and result.json['code'] == 'request_timeout'
    finally:
        release.set()
    job.thread.join(2)
    assert not job.thread.is_alive()
    assert not app.extensions['karen']['history']
    assert len(calls) == 2


def test_speech_size_is_checked_before_history_commit(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    app.extensions['fake_tts']['audio'] = b'x' * 512001
    result = app.test_client().post('/chat', data=pcm(), content_type='audio/wav')
    assert result.status_code == 502 and result.json['code'] == 'audio_too_large'
    assert not app.extensions['karen']['history']
    assert len(calls) == 2


def test_openai_transport_excludes_private_saved_facts_and_history(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    biography = ('The creator studies in Class 9S at PKMMHSS Edarikode. '
                 'His home is Thottasheriyar. Water boils at 100 degrees Celsius.')
    private_history = [('user', 'Does your creator attend PKMMHSS Edarikode?'),
                       ('model', 'His home is Thottasheriyar and he studies in Class 9S.')]
    assert contains_identity(biography)
    assert all(contains_identity(text) for _, text in private_history)
    Path(app.config['MEMORY_PATH']).write_text(biography, encoding='utf-8')
    app.extensions['karen']['history'].extend(private_history)
    client = app.test_client()
    client.get('/')
    with client.session_transaction() as session:
        csrf = session['csrf']
    result = client.post('/test_chat', json={'user_message': QUESTION}, headers={
        'X-CSRF-Token': csrf, 'Accept': 'application/json'})
    assert result.status_code == 200 and len(calls) == 1
    body = json.loads(calls[0].content)
    assert not contains_identity(body['instructions'])
    assert 'Water boils at 100 degrees Celsius.' in body['instructions']
    assert all(not contains_identity(turn['content']) for turn in body['input'])
    assert body['input'][-1]['content'] == QUESTION


def test_generated_private_details_are_filtered_before_json_speech_and_history(mocked_openai):
    app, provider, calls, responses, client_options = mocked_openai
    generated = 'His school is PKMMHSS Edarikode, Class 9S, and his home is Thottasheriyar.'
    assert contains_identity(generated)
    client = app.test_client()
    client.get('/')
    with client.session_transaction() as session:
        csrf = session['csrf']
    responses.append(httpx.Response(200, json=text_result(generated)))
    text = client.post('/test_chat', json={'user_message': QUESTION}, headers={
        'X-CSRF-Token': csrf, 'Accept': 'application/json', 'X-Request-ID': 'openai-private-text-123'})
    assert text.status_code == 200 and text.json['reply'] == PRIVATE_REPLY
    assert not contains_identity(text.text)
    assert client.get('/requests/openai-private-text-123').json['reply'] == PRIVATE_REPLY
    responses.extend([httpx.Response(200, json={'text': QUESTION}),
                      httpx.Response(200, json=text_result(generated))])
    voice = client.post('/chat', data=pcm(), content_type='audio/wav',
                        headers={'X-Request-ID': 'openai-private-voice-123'})
    assert voice.status_code == 200 and voice.headers['X-Karen-Result'] == 'ok'
    assert app.extensions['fake_tts']['calls'] == [
        {'text': PRIVATE_REPLY, 'lang': 'ml', 'timeout': (5, 15)}]
    history = app.extensions['karen']['history']
    assert all(not contains_identity(value) for _, value in history)
    assert history[-1] == ('model', PRIVATE_REPLY)
