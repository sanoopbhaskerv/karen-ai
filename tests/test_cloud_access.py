"""Hosted access boundaries, using isolated memory and no live providers."""
import base64
import pytest
from app import create_app
from test_app import Fake, pcm
from scripts.firmware import redact_output
from scripts.bootstrap import private_values, sanitized
from scripts.doctor import Doctor


@pytest.fixture
def cloud(tmp_path):
    provider = Fake()
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test',
                      'MEMORY_PATH': str(tmp_path / 'memory.txt'), 'DEMO_MODE': False,
                      'KAREN_ADMIN_USERNAME': 'karen', 'KAREN_ADMIN_PASSWORD': 'test-admin-password',
                      'KAREN_DEVICE_TOKEN': 'test-device-token', 'SESSION_COOKIE_SECURE': True}, provider)
    return app, app.test_client(), provider


def basic(password='test-admin-password'):
    value = base64.b64encode(('karen:' + password).encode()).decode()
    return {'Authorization': 'Basic ' + value}


def device(token='test-device-token'):
    return {'Authorization': 'Bearer ' + token}


@pytest.mark.parametrize('path,method', [('/', 'get'), ('/static/app.js', 'get'),
    ('/chat', 'post'), ('/test_chat', 'post'), ('/update', 'post'), ('/reset', 'post'),
    ('/requests/unknown-1234', 'get')])
def test_public_requests_cannot_read_or_mutate(cloud, path, method):
    app, client, provider = cloud
    response = getattr(client, method)(path)
    assert response.status_code == 401
    assert response.headers['WWW-Authenticate'].startswith('Basic ')
    assert response.headers['Cache-Control'] == 'no-store'
    assert not provider.seen and not app.extensions['karen']['history']


def test_health_is_public_and_contains_no_credentials(cloud):
    app, client, provider = cloud
    response = client.get('/health')
    assert response.status_code == 200 and response.json['status'] == 'ok'
    assert 'test-admin-password' not in response.text
    assert 'test-device-token' not in response.text


def test_hosted_guides_are_linked_protected_and_use_hashed_inline_content(cloud):
    app, client, provider = cloud
    dashboard = client.get('/', headers=basic()).text
    for filename in ('cloud-use-malayalam.html', 'windows-setup-malayalam.html',
                     'windows-wifi-change-malayalam.html'):
        url = '/docs/' + filename
        assert url in dashboard
        assert client.get(url).status_code == 401
        assert client.get(url, headers=device()).status_code == 403
        response = client.get(url, headers=basic())
        assert response.status_code == 200 and response.mimetype == 'text/html'
        policy = response.headers['Content-Security-Policy']
        assert "'sha256-" in policy and 'unsafe-inline' not in policy
    assert client.get('/docs/cloud-root-ca.pem', headers=basic()).text.count('BEGIN CERTIFICATE') == 2
    assert client.get('/docs/../.env', headers=basic()).status_code == 404
    assert client.get('/docs/unknown.html', headers=basic()).status_code == 404
    assert client.get('/READMEMALAYALAM.md', headers=basic()).status_code == 200


def test_admin_can_chat_but_csrf_is_still_required(cloud):
    app, client, provider = cloud
    response = client.get('/', headers=basic())
    assert response.status_code == 200
    assert 'Secure;' in response.headers['Set-Cookie']
    assert client.get('/', headers=basic('wrong')).status_code == 401
    assert client.post('/test_chat', json={'user_message': 'hi'}, headers=basic()).status_code == 403
    with client.session_transaction() as session:
        csrf = session['csrf']
    headers = {**basic(), 'X-CSRF-Token': csrf}
    response = client.post('/test_chat', json={'user_message': 'hi'}, headers=headers)
    assert response.status_code == 200 and len(provider.seen) == 1


@pytest.mark.parametrize('path,method', [('/', 'get'), ('/update', 'post'),
    ('/reset', 'post'), ('/test_chat', 'post'), ('/static/app.js', 'get')])
def test_board_token_cannot_access_dashboard_or_admin_actions(cloud, path, method):
    app, client, provider = cloud
    assert getattr(client, method)(path, headers=device()).status_code == 403
    assert not provider.seen


def test_board_token_authenticates_submission_and_poll(cloud):
    app, client, provider = cloud
    assert client.post('/chat', data=pcm(), content_type='audio/wav', headers=device('wrong')).status_code == 401
    headers = {**device(), 'X-Request-ID': 'cloud-voice-123', 'Prefer': 'respond-async'}
    response = client.post('/chat', data=pcm(), content_type='audio/wav', headers=headers)
    assert response.status_code in (200, 202)
    app.extensions['karen']['jobs'].get('cloud-voice-123').thread.join(2)
    assert client.get('/requests/cloud-voice-123').status_code == 401
    result = client.get('/requests/cloud-voice-123', headers=device())
    assert result.status_code == 200 and result.headers['X-Karen-Result'] == 'ok'
    assert result.data == b'ID3fake-test-audio' and len(provider.seen) == 1


def test_board_token_cannot_read_browser_text_results(cloud):
    app, client, provider = cloud
    client.get('/', headers=basic())
    with client.session_transaction() as session:
        csrf = session['csrf']
    response = client.post('/test_chat', json={'user_message': 'hi'}, headers={
        **basic(), 'X-CSRF-Token': csrf, 'X-Request-ID': 'cloud-text-123'})
    assert response.status_code == 200
    assert client.get('/requests/cloud-text-123', headers=device()).status_code == 403


@pytest.mark.parametrize('authorization', ['Basic !!!', 'Bearer', 'Bearer wrong', 'Digest test'])
def test_malformed_credentials_fail_closed(cloud, authorization):
    app, client, provider = cloud
    assert client.get('/', headers={'Authorization': authorization}).status_code == 401


def test_partial_cloud_configuration_fails_closed(tmp_path):
    with pytest.raises(ValueError, match='KAREN_ADMIN_PASSWORD'):
        create_app({'MEMORY_PATH': str(tmp_path / 'memory.txt'),
                    'KAREN_ADMIN_PASSWORD': '', 'KAREN_DEVICE_TOKEN': 'device'})


def test_device_token_is_redacted_in_firmware_and_diagnostic_logs(tmp_path, capsys):
    secret = 'private-device-token'
    config = '#define KAREN_DEVICE_TOKEN "' + secret + '"\n'
    path = tmp_path / 'firmware/karen_ai/config.h'
    path.parent.mkdir(parents=True)
    path.write_text(config)
    output = config + 'compiler expansion: ' + secret
    assert secret not in redact_output(output, config, {})
    assert secret not in sanitized(output, private_values(tmp_path))
    Doctor(tmp_path).write(output)
    assert secret not in capsys.readouterr().out
    assert secret not in (tmp_path / '.tools/doctor.log').read_text()
