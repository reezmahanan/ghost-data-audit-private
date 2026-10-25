import csv
import json

users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_by_email = {}
user_by_id = {}
for u in users:
    user_by_email[u['email'].lower()] = u
    user_by_id[u['user_id']] = u

audit_logs = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))
user_history = {}
for a in audit_logs:
    uid = a['user_id']
    if uid not in user_history:
        user_history[uid] = []
    user_history[uid].append(a)

email_to_uid = {}
for u in users:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_logs:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

for s, o in zip(samples, sample_outs):
    req_email = s['email'].lower()
    uid = email_to_uid.get(req_email)
    user = user_by_id.get(uid)
    steps = json.loads(o['steps_json'])
    resources = [(step['system_id'], step['resource_id'], step['phase'], step['operation'], step['state'], step.get('evidence_id')) for step in steps]
    print(f"\n=== Case: {s['case_id']} | User: {uid} | Status: {o['deletion_status']} ===")
    print(f"Req: email={req_email}, requested_at={s['requested_at']}, reported={s['reported_status']}@{s['reported_at']}, audit_at={s['audit_at']}")
    for r in resources:
        print(f"   {r}")
