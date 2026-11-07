"""Inspect or delete the exact temporary AWS resources recorded for this test.

Default is a dry run. --execute verifies account and resource identities first.
Automatic server/DNS/IP deletion is also installed in AWS EventBridge Scheduler.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, default=ROOT / 'deploy/aws-test-state.json')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    state = json.loads(args.state.read_text())
    print(f"Test: {state['domain']} | account={state['account']} | expires={state['expires_at']}")
    print('Delete test instance, its DNS A record and static IP; remove its cleanup schedules, SSH key and IAM role.')
    if not args.execute:
        print('Dry run only. Back up permanent memory before using --execute.')
        return

    def aws(service, operation, *options, missing_ok=False):
        result = subprocess.run(['aws', '--profile', state['profile'], '--region', state['region'],
                                 service, operation, *options, '--output', 'json'],
                                capture_output=True, text=True)
        if result.returncode:
            if missing_ok and any(code in result.stderr for code in (
                    'NotFoundException', 'NoSuchEntity', 'ResourceNotFoundException')):
                return None
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout) if result.stdout.strip() else {}

    identity = aws('sts', 'get-caller-identity')
    if identity['Account'] != state['account']:
        raise RuntimeError('AWS account differs from recorded test account; nothing deleted.')
    instance = aws('lightsail', 'get-instance', '--instance-name', state['instance_name'], missing_ok=True)
    ip = aws('lightsail', 'get-static-ip', '--static-ip-name', state['static_ip_name'], missing_ok=True)
    if instance and instance['instance']['arn'] != state['instance_arn']:
        raise RuntimeError('Instance identity changed; nothing deleted.')
    if ip and ip['staticIp']['arn'] != state['static_ip_arn']:
        raise RuntimeError('Static IP identity changed; nothing deleted.')
    records = aws('route53', 'list-resource-record-sets', '--hosted-zone-id', state['hosted_zone_id'])
    matches = [record for record in records['ResourceRecordSets']
               if record['Name'] == state['record']['Name'] and record['Type'] == 'A']
    if matches and matches != [state['record']]:
        raise RuntimeError('DNS record changed; nothing deleted.')
    if matches:
        change = {'Changes': [{'Action': 'DELETE', 'ResourceRecordSet': state['record']}]}
        aws('route53', 'change-resource-record-sets', '--hosted-zone-id', state['hosted_zone_id'],
            '--change-batch', json.dumps(change))
    if instance:
        aws('lightsail', 'delete-instance', '--instance-name', state['instance_name'])
    if ip:
        deadline = time.monotonic() + 180
        while ip['staticIp']['isAttached']:
            if time.monotonic() >= deadline:
                raise RuntimeError('Instance is still deleting. Cleanup schedules retained; retry later.')
            time.sleep(3)
            ip = aws('lightsail', 'get-static-ip', '--static-ip-name', state['static_ip_name'])
        aws('lightsail', 'release-static-ip', '--static-ip-name', state['static_ip_name'])
    for item in state['cleanup_schedules']:
        aws('scheduler', 'delete-schedule', '--name', item['name'], missing_ok=True)
    aws('scheduler', 'delete-schedule', '--name', 'sreehariv-karen-cleanup-smoke', missing_ok=True)
    aws('lightsail', 'delete-key-pair', '--key-pair-name', state['ssh_key_name'], missing_ok=True)
    role = aws('iam', 'get-role', '--role-name', state['cleanup_role_name'], missing_ok=True)
    if role:
        for policy in aws('iam', 'list-role-policies', '--role-name', state['cleanup_role_name'])['PolicyNames']:
            aws('iam', 'delete-role-policy', '--role-name', state['cleanup_role_name'], '--policy-name', policy)
        aws('iam', 'delete-role', '--role-name', state['cleanup_role_name'])
    print('Temporary AWS resources deleted. Local credentials and downloaded backups are preserved.')


if __name__ == '__main__':
    main()
