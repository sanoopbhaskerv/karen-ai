"""Credential-based tenant routing with isolated apps and persistent registration."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading

from flask import jsonify, request
from werkzeug.datastructures import Authorization
from werkzeug.wrappers import Response


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class ClientRegistry:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(descriptor)
        self.path.chmod(0o600)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY, profile TEXT NOT NULL, '
                       'device_hash TEXT UNIQUE NOT NULL, admin_hash TEXT NOT NULL)')
        self.path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def register(self, profile):
        if not isinstance(profile, dict):
            raise ValueError('Client profile must be an object.')
        allowed = {'id', 'name', 'grade', 'location', 'controller', 'language', 'science_context'}
        if set(profile) - allowed:
            raise ValueError('Unknown client profile fields.')
        identifier = profile.get('id', '')
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]{2,47}', identifier) or identifier == 'default':
            raise ValueError('Use a unique lowercase client id, 3–48 characters; default is reserved.')
        if profile.get('language') not in ('ml', 'en'):
            raise ValueError('Language must be ml or en.')
        if profile.get('controller') not in ('esp32', 'esp32_s3'):
            raise ValueError('Controller must be esp32 or esp32_s3.')
        if type(profile.get('science_context')) is not bool:
            raise ValueError('science_context must be true or false.')
        if type(profile.get('grade')) is not int or not 1 <= profile['grade'] <= 12:
            raise ValueError('Grade must be between 1 and 12.')
        for key in ('name', 'location'):
            if not isinstance(profile.get(key), str) or not 1 <= len(profile[key].strip()) <= 160:
                raise ValueError('Name and location must contain 1–160 characters.')
        token, password = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.connect() as db:
            # Bound per-process app/job resources; expand only with a shared job store.
            if db.execute('SELECT count(*) FROM clients').fetchone()[0] >= 32:
                raise ValueError('This single-worker installation supports at most 32 registered clients.')
            try:
                db.execute('INSERT INTO clients VALUES (?, ?, ?, ?)',
                           (identifier, json.dumps(profile), digest(token), digest(password)))
            except sqlite3.IntegrityError:
                raise ValueError('Client id already registered.') from None
        return {'client': profile, 'device_token': token, 'admin_username': identifier,
                'admin_password': password, 'browser_path': '/clients/' + identifier + '/'}

    def get(self, identifier=None, token=None):
        with self.connect() as db:
            if token is not None:
                return db.execute('SELECT * FROM clients WHERE device_hash=?', (digest(token),)).fetchone()
            return db.execute('SELECT * FROM clients WHERE id=?', (identifier,)).fetchone()

    def profiles(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute('SELECT profile FROM clients ORDER BY id')]


def create_service(config=None, provider_factory=None):
    from app import create_app
    root = create_app({**(config or {}), 'BILINGUAL_INPUT': True})
    registry = ClientRegistry(root.config.get('CLIENT_REGISTRY_PATH') or
                              os.getenv('CLIENT_REGISTRY_PATH', str(Path(root.config['MEMORY_PATH']).parent / 'clients.sqlite3')))
    apps, lock = {}, threading.RLock()
    original = root.wsgi_app
    root.extensions['clients'] = {'registry': registry, 'apps': apps}

    def owner():
        auth = request.authorization
        expected = root.config['KAREN_ADMIN_PASSWORD']
        return bool(expected and auth and auth.type.lower() == 'basic' and
                    secrets.compare_digest((auth.username or '').encode(), root.config['KAREN_ADMIN_USERNAME'].encode()) and
                    secrets.compare_digest((auth.password or '').encode(), expected.encode()))

    @root.route('/api/clients', methods=['GET', 'POST'])
    def clients():
        if not owner():
            return jsonify(error='Owner authentication required.'), 401
        if request.method == 'GET':
            return jsonify(clients=registry.profiles())
        try:
            result = registry.register(request.get_json(silent=True))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(result), 201

    def dispatch(environ, start_response):
        auth = Authorization.from_header(environ.get('HTTP_AUTHORIZATION'))
        token = auth.token if auth and auth.type.lower() == 'bearer' else None
        row = registry.get(token=token) if token else None
        if auth and auth.type.lower() == 'bearer' and row is None:
            legacy = root.config['KAREN_DEVICE_TOKEN']
            if not token or not legacy or not secrets.compare_digest(token.encode(), legacy.encode()):
                return Response('Unknown device credential', status=401)(environ, start_response)
        path = environ.get('PATH_INFO', '/')
        mounted = re.match(r'^/clients/([a-z][a-z0-9-]{2,47})(/.*|$)', path)
        claimed = environ.get('HTTP_X_CLIENT_ID')
        if path.startswith('/clients/') and not mounted:
            return Response('Unknown client', status=404)(environ, start_response)
        if mounted:
            target = mounted.group(1)
            if token and (row is None or row['id'] != target):
                return Response('Client credential mismatch', status=403)(environ, start_response)
            row = registry.get(identifier=target)
            if row is None:
                return Response('Unknown client', status=404)(environ, start_response)
            if not mounted.group(2):
                # Resolve relative browser assets/forms under the mount.
                return Response('', status=308, headers={'Location': path + '/'})(environ, start_response)
        if claimed and claimed != (row['id'] if row else 'default'):
            return Response('Client credential mismatch', status=403)(environ, start_response)
        if row is None:
            return original(environ, start_response)
        # Registry administration is only available to the installation owner.
        if path.startswith('/api/'):
            return Response('Forbidden', status=403)(environ, start_response)
        with lock:
            identifier = row['id']
            child = apps.get(identifier)
            if child is None:
                profile = json.loads(row['profile'])
                tenant_config = dict(root.config)
                tenant_config.update(CLIENT_PROFILE=profile, CLIENT_ID=identifier,
                    REPLY_LANGUAGE=profile['language'], SCIENCE_CONTEXT=profile['science_context'],
                    MEMORY_PATH=str(registry.path.parent / 'clients' / identifier / 'memory.txt'),
                    KAREN_DEVICE_TOKEN=row['device_hash'], DEVICE_TOKEN_HASHED=True,
                    KAREN_ADMIN_USERNAME=identifier, KAREN_ADMIN_PASSWORD=row['admin_hash'], ADMIN_PASSWORD_HASHED=True,
                    KAREN_PUBLIC_UI=False, SESSION_COOKIE_NAME='karen_' + identifier,
                    SECRET_KEY=digest(root.config['SECRET_KEY'] + ':' + identifier), JOB_CAPACITY=16)
                provider = provider_factory(profile) if provider_factory else None
                child = create_app(tenant_config, provider)
                apps[identifier] = child
        if mounted:
            environ = dict(environ)
            environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '') + '/clients/' + identifier
            environ['PATH_INFO'] = mounted.group(2) or '/'
        return child(environ, start_response)

    root.wsgi_app = dispatch
    return root
