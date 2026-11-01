"""Stage diagnostics use fake provider time and never call external services."""
import io

import pytest

from test_app import pcm, setup


@pytest.fixture
def timed(setup, monkeypatch):
    app, client, provider, token = setup
    now = [1024.0]
    monkeypatch.setattr('app.time.monotonic', lambda: now[0])
    for method, seconds in [('transcribe', 0.125), ('answer', 0.25), ('speak', 0.5)]:
        original = getattr(provider, method)

        def operation(*args, original=original, seconds=seconds):
            now[0] += seconds
            return original(*args)

        monkeypatch.setattr(provider, method, operation)
    return app, client, provider, token


def test_voice_timings_survive_multipart_replay_and_result_poll(timed, caplog):
    app, client, provider, token = timed
    headers = {'X-Request-ID': 'voice-latency-1234'}
    first = client.post('/chat', data=pcm(), content_type='audio/wav', headers=headers)
    replay = client.post('/chat', data={'audio': (io.BytesIO(pcm()), 'question.wav')}, headers=headers)
    poll = client.get('/requests/voice-latency-1234')
    expected = 'stt;dur=125, gemini;dur=250, tts;dur=500'
    for response in (first, replay, poll):
        assert response.status_code == 200
        assert response.headers['Server-Timing'] == expected
        assert response.data == b'ID3fake-test-audio'
    assert len(provider.seen) == 1
    for stage, elapsed in [('stt', 125), ('gemini', 250), ('tts', 500)]:
        message = f'request=voice-latency-1234 stage={stage} status=ok elapsed_ms={elapsed}'
        assert caplog.messages.count(message) == 1


def test_text_timings_cover_only_generation_in_json_and_form(timed, caplog):
    app, client, provider, token = timed
    first = client.post('/test_chat', json={'user_message': 'private question'},
                        headers={'X-CSRF-Token': token, 'X-Request-ID': 'text-latency-1234'})
    poll = client.get('/requests/text-latency-1234')
    form = client.post('/test_chat', data={'csrf_token': token, 'user_message': 'another private question'})
    for response in (first, poll, form):
        assert response.status_code == 200
        assert response.headers['Server-Timing'] == 'gemini;dur=250'
    assert form.mimetype == 'text/html'
    assert 'private question' not in caplog.text
    assert 'stage=stt' not in caplog.text and 'stage=tts' not in caplog.text


@pytest.mark.parametrize('failed_stage, flag, expected', [
    ('stt', 'stt_fail', 'stt;dur=125, tts;dur=500'),
    ('gemini', 'fail', 'stt;dur=125, gemini;dur=250, tts;dur=500'),
])
def test_spoken_errors_keep_failed_stage_timing(timed, caplog, failed_stage, flag, expected):
    app, client, provider, token = timed
    setattr(provider, flag, True)
    response = client.post('/chat', data=pcm(), content_type='audio/wav',
                           headers={'X-Request-ID': 'spoken-latency-1234'})
    assert response.status_code == 200
    assert response.headers['X-Karen-Result'] == 'spoken-error'
    assert response.headers['Server-Timing'] == expected
    assert client.get('/requests/spoken-latency-1234').headers['Server-Timing'] == expected
    assert f'request=spoken-latency-1234 stage={failed_stage} status=error elapsed_ms=' in caplog.text
    assert not app.extensions['karen']['history']


@pytest.mark.parametrize('stage, method', [('stt', 'transcribe'), ('gemini', 'answer'), ('tts', 'speak')])
def test_unexpected_stage_failure_logs_timing_without_exception_contents(timed, monkeypatch, caplog,
                                                                        stage, method):
    app, client, provider, token = timed

    def fail(*args):
        raise RuntimeError('private-provider-url-and-key')

    monkeypatch.setattr(provider, method, fail)
    response = client.post('/chat', data=pcm(), content_type='audio/wav',
                           headers={'X-Request-ID': 'failed-latency-1234'})
    assert response.status_code == 500
    assert f'request=failed-latency-1234 stage={stage} status=error elapsed_ms=' in caplog.text
    assert 'private-provider-url-and-key' not in response.text + caplog.text
    assert not app.extensions['karen']['history']
