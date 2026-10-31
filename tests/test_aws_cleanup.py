"""The manual cleanup must refuse changed identities before deleting anything."""
import json
import sys
from types import SimpleNamespace
import pytest
from scripts import cleanup_aws_test


@pytest.fixture
def cleanup(tmp_path, monkeypatch):
    state = {'profile': 'test', 'region': 'ap-south-1', 'account': '123456789012',
             'domain': 'karen.example.test', 'expires_at': '2026-11-07T14:10:00+00:00',
             'instance_name': 'test-instance', 'instance_arn': 'instance-arn',
             'static_ip_name': 'test-ip', 'static_ip_arn': 'ip-arn',
             'record': {'Name': 'karen.example.test.', 'Type': 'A', 'TTL': 60,
                        'ResourceRecords': [{'Value': '192.0.2.10'}]},
             'hosted_zone_id': 'test-zone', 'cleanup_schedules': [{'name': 'test-cleanup'}],
             'ssh_key_name': 'test-key', 'cleanup_role_name': 'test-role'}
    path = tmp_path / 'state.json'
    path.write_text(json.dumps(state))
    monkeypatch.setattr(sys, 'argv', ['cleanup_aws_test.py', '--state', str(path), '--execute'])
    responses = {'get-caller-identity': {'Account': state['account']},
                 'get-instance': {'instance': {'arn': state['instance_arn']}},
                 'get-static-ip': {'staticIp': {'arn': state['static_ip_arn'], 'isAttached': False}},
                 'list-resource-record-sets': {'ResourceRecordSets': [state['record']]},
                 'get-role': {'Role': {}}, 'list-role-policies': {'PolicyNames': ['test-policy']}}
    calls = []
    def run(command, **kwargs):
        operation = command[6]
        calls.append(operation)
        return SimpleNamespace(returncode=0, stdout=json.dumps(responses.get(operation, {})), stderr='')
    monkeypatch.setattr(cleanup_aws_test.subprocess, 'run', run)
    return responses, calls


def test_dry_run_never_contacts_aws(cleanup, monkeypatch):
    responses, calls = cleanup
    monkeypatch.setattr(sys, 'argv', sys.argv[:-1])
    cleanup_aws_test.main()
    assert calls == []


@pytest.mark.parametrize('mutation', ['account', 'instance', 'ip', 'dns'])
def test_changed_ownership_prevents_all_deletes(cleanup, mutation):
    responses, calls = cleanup
    if mutation == 'account':
        responses['get-caller-identity']['Account'] = 'different-account'
    elif mutation == 'instance':
        responses['get-instance']['instance']['arn'] = 'different-instance'
    elif mutation == 'ip':
        responses['get-static-ip']['staticIp']['arn'] = 'different-ip'
    else:
        responses['list-resource-record-sets']['ResourceRecordSets'][0]['ResourceRecords'][0]['Value'] = '192.0.2.99'
    with pytest.raises(RuntimeError):
        cleanup_aws_test.main()
    assert not any(operation.startswith(('delete-', 'release-', 'change-')) for operation in calls)


def test_cleanup_retains_automatic_schedules_until_billable_resources_removed(cleanup):
    responses, calls = cleanup
    cleanup_aws_test.main()
    assert calls.index('release-static-ip') < calls.index('delete-schedule')
    assert calls.index('delete-instance') < calls.index('release-static-ip')
    assert calls[-1] == 'delete-role'
