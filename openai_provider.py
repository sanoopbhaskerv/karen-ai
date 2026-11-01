"""OpenAI voice/text adapters retaining the controller's WAV/MP3 protocol."""
import io
import time

import httpx

from jobs import ServiceError
from exhibition_identity import anonymous_history, anonymous_memory, anonymous_reply


class OpenAIProvider:
    generation_stage = 'openai'

    def __init__(self, app, rules):
        self.app, self.rules = app, rules
        self.diagnostic = {'status': 'untested'}

    def _invalid(self, stage, message, code, status=503):
        self.diagnostic = {'status': 'degraded', 'stage': stage, 'code': code}
        self.app.logger.warning('stage=%s code=%s', stage, code)
        return ServiceError(message, code, status)

    def _request(self, stage, path, **kwargs):
        key = self.app.config['OPENAI_API_KEY']
        if not key:
            raise self._invalid(stage, 'Set OPENAI_API_KEY on the server to enable OpenAI.', 'model_unconfigured')
        started = time.monotonic()
        prefix = 'model' if stage == 'openai' else stage
        reason, status_code = None, None
        try:
            # No hidden transport/SDK retries: a slow provider must not turn into
            # another 45-second retry of the same question.
            with httpx.Client(timeout=httpx.Timeout(20, connect=5, write=10, pool=5)) as client:
                response = client.post('https://api.openai.com/v1/' + path,
                                       headers={'Authorization': 'Bearer ' + key}, **kwargs)
            status_code = response.status_code
            if status_code >= 400:
                suffix = {400: 'request', 401: 'auth', 403: 'auth', 404: 'not_found',
                          408: 'timeout', 429: 'quota', 504: 'timeout'}.get(status_code, 'unavailable')
                reason = prefix + '_' + suffix
            else:
                try:
                    return response.json()
                except ValueError:
                    reason = prefix + '_invalid'
        except httpx.TimeoutException:
            reason = prefix + '_timeout'
        except httpx.TransportError:
            reason = prefix + '_network'
        elapsed = max(0, int((time.monotonic() - started) * 1000))
        self.diagnostic = {'status': 'degraded', 'stage': stage, 'code': reason,
                           'provider_code': status_code, 'elapsed_ms': elapsed}
        # Never log an error body, exception string, key, transcript or answer.
        self.app.logger.warning('stage=%s code=%s provider_code=%s elapsed_ms=%d',
                                stage, reason, status_code, elapsed)
        messages = {
            'auth': 'OpenAI rejected access. Check the server key and project permissions.',
            'quota': 'OpenAI credits or rate limit reached. Check Personal API billing.',
            'not_found': 'OpenAI model unavailable for this project.',
            'timeout': 'OpenAI timed out. Please try again.',
            'network': 'Cannot reach OpenAI. Check the server internet connection.',
        }
        suffix = reason.removeprefix(prefix + '_')
        raise ServiceError(messages.get(suffix, 'OpenAI could not complete the request. Please try again.'),
                           reason) from None

    @staticmethod
    def _messages(memory, history, message, rules):
        messages = [{'role': 'system', 'content': rules + anonymous_memory(memory)}]
        messages.extend({'role': 'assistant' if role == 'model' else 'user', 'content': text}
                        for role, text in anonymous_history(history))
        messages.append({'role': 'user', 'content': anonymous_history([('user', message)])[0][1]})
        return messages

    def _ready(self, started):
        self.diagnostic = {'status': 'ready', 'elapsed_ms': max(0, int((time.monotonic() - started) * 1000)),
                           'attempt': 1}

    def answer(self, memory, history, message):
        started = time.monotonic()
        messages = self._messages(memory, history, message, self.rules)
        result = self._request('openai', 'responses', json={
            'model': self.app.config['OPENAI_MODEL'],
            'instructions': messages[0]['content'] + (
                '\nFor this installation, speech recognition and answers use OpenAI; '
                'Malayalam speech output uses Google. This supersedes older project descriptions of the provider. '
                'Keep the reply to two very short sentences, at most 25 Malayalam words.'),
            'input': messages[1:],
            'reasoning': {'effort': 'none'}, 'max_output_tokens': 1024, 'store': False,
        })
        try:
            reply = ''.join(part['text'] for item in result.get('output', []) if item.get('type') == 'message'
                            for part in item.get('content', []) if part.get('type') == 'output_text')
        except (TypeError, KeyError, AttributeError):
            raise self._invalid('openai', 'OpenAI returned an invalid text response.', 'model_invalid') from None
        if not isinstance(reply, str) or not reply.strip():
            raise self._invalid('openai', 'OpenAI returned no text. Please try again.', 'model_empty')
        self._ready(started)
        return anonymous_reply(reply.strip()[:2500])

    def transcribe(self, data):
        result = self._request('stt', 'audio/transcriptions',
                               data={'model': self.app.config['OPENAI_STT_MODEL'], 'languages[]': 'ml'},
                               files={'file': ('question.wav', data, 'audio/wav')})
        transcript = result.get('text') if isinstance(result, dict) else None
        if not isinstance(transcript, str) or not transcript.strip():
            raise self._invalid('stt', 'എനിക്ക് വ്യക്തമായി കേൾക്കാനായില്ല. ദയവായി വീണ്ടും പറയൂ.', 'stt_unrecognized')
        return transcript.strip()

    def speak(self, text):
        # Retain the tested Malayalam voice. OpenAI credits cover recognition
        # and answer generation; MP3 synthesis still uses Google's speech service.
        from gtts import gTTS
        output = io.BytesIO()
        try:
            gTTS(text=text, lang='ml', timeout=(5, 15)).write_to_fp(output)
        except Exception:
            raise self._invalid('tts', 'Speech generation is temporarily unavailable.', 'tts_unavailable') from None
        audio = output.getvalue()
        if not audio:
            raise self._invalid('tts', 'Speech service returned no audio.', 'tts_empty')
        if len(audio) > 512000:
            raise self._invalid('tts', 'Speech response too large. Try a shorter question.', 'audio_too_large', 502)
        return audio
