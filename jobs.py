"""Bounded, process-local requests for the single exhibition conversation."""
import hashlib
import re
import secrets
import threading
import time
from dataclasses import dataclass, field


class ServiceError(Exception):
    def __init__(self, message, code='service_error', status=503):
        super().__init__(message)
        self.code, self.status = code, status


@dataclass
class Result:
    body: object
    status: int = 200
    headers: dict = field(default_factory=dict)


class Job:
    def __init__(self, key, digest, timeout, kind=None):
        self.key, self.digest = key, digest
        self.kind = kind
        self.deadline = time.monotonic() + timeout
        self.lock = threading.RLock()
        self.done = threading.Event()
        self.result = None
        self.finished_at = None
        self.thread = None
        self.active = True

    def check(self):
        if time.monotonic() >= self.deadline:
            raise ServiceError('Request deadline exceeded. Start a new question.', 'request_timeout', 504)

    def finish(self, result):
        with self.lock:
            if self.result is None:
                self.result = result
                self.finished_at = time.monotonic()
                self.done.set()

    def poll(self):
        with self.lock:
            if self.result is None and time.monotonic() >= self.deadline:
                self.finish(Result({'error': 'Request deadline exceeded. Start a new question.',
                                    'code': 'request_timeout'}, 504))
            return self.result


class Jobs:
    """One running worker; no unbounded queue or implicit POST retries.

    Retain results for ten minutes so a lost response can be retrieved without
    sending the question to Gemini again. A slow timed-out worker keeps the slot
    until it exits; it must check its deadline before committing conversation.
    """
    def __init__(self, logger, timeout=140, ttl=600, capacity=64):
        self.logger, self.timeout, self.ttl, self.capacity = logger, timeout, ttl, capacity
        self.lock = threading.RLock()
        self.items = {}

    def submit(self, kind, payload, key, operation):
        key = key or secrets.token_hex(16)
        if not re.fullmatch(r'[A-Za-z0-9-]{8,80}', key):
            raise ServiceError('Use an 8–80 character alphanumeric request ID.', 'invalid_request_id', 400)
        digest = hashlib.sha256(kind.encode() + b'\0' + payload).digest()
        with self.lock:
            now = time.monotonic()
            for old_key, job in list(self.items.items()):
                if job.finished_at is not None and now - job.finished_at > self.ttl and not job.thread.is_alive():
                    del self.items[old_key]
            if key in self.items:
                job = self.items[key]
                if job.digest != digest:
                    raise ServiceError('Request ID already belongs to a different question.', 'request_conflict', 409)
                return job
            if any(job.active for job in self.items.values()) or len(self.items) >= self.capacity:
                raise ServiceError('Karen is busy. Wait for the current request to finish.', 'busy', 503)
            job = Job(key, digest, self.timeout, kind)
            self.items[key] = job

            def run():
                started = time.monotonic()
                try:
                    result = operation(job)
                    if job.result is None:
                        job.check()
                except ServiceError as exc:
                    result = Result({'error': str(exc), 'code': exc.code}, exc.status)
                except Exception as exc:
                    # Never log exception strings: provider URLs may contain keys.
                    self.logger.error('request=%s stage=request code=internal_error error_type=%s', key, type(exc).__name__)
                    result = Result({'error': 'Unexpected server error. Check the Python console.', 'code': 'internal_error'}, 500)
                job.active = False
                job.finish(result)
                self.logger.info('request=%s stage=%s status=%s elapsed_ms=%d', key, kind, job.result.status,
                                 (time.monotonic() - started) * 1000)

            job.thread = threading.Thread(target=run, name='karen-request', daemon=True)
            job.thread.start()
            return job

    def get(self, key):
        with self.lock:
            job = self.items.get(key)
            if job and job.finished_at is not None and time.monotonic() - job.finished_at > self.ttl:
                return None
            return job
