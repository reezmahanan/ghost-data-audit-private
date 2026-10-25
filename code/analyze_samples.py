import csv
import json

users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_by_email = {}
user_by_id = {}
for u in users:
    user_by_email[u['email'].lower()] = u
    user_by_id[u['user_id']] = u

audit_logs = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))
email_to_user_history = {}
for a in audit_logs:
    if a['field_name'] == 'email':
        email_to_user_history[a['old_value'].lower()] = a['user_id']
        email_to_user_history[a['new_value'].lower()] = a['user_id']

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

for s, out in zip(samples[:10], sample_outs[:10]):
    req_email = s['email'].lower()
    user = user_by_email.get(req_email)
    uid = user['user_id'] if user else email_to_user_history.get(req_email)
    print(f"Case: {s['case_id']}, Email: {req_email}, UserID: {uid}, Reported: {s['reported_status']}, Status: {out['deletion_status']}")
    steps = json.loads(out['steps_json'])
    for step in steps:
        print("   ", step)
