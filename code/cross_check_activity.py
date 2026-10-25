import csv
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_by_email = {u['email'].lower(): u for u in users}
user_by_id = {u['user_id']: u for u in users}

audit_logs = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))
email_to_uid = {u['email'].lower(): u['user_id'] for u in users}
for a in audit_logs:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

system_activity = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

for s, o in zip(samples[:10], sample_outs[:10]):
    req_email = s['email'].lower()
    uid = email_to_uid.get(req_email)
    steps = json.loads(o['steps_json'])
    print(f"\n--- {s['case_id']} ({uid}) Status: {o['deletion_status']} ---")
    
    # Check all system activities matching any resource in steps
    step_res = set(step['resource_id'] for step in steps)
    matching_acts = [act for act in system_activity if act['resource_id'] in step_res]
    for act in matching_acts:
        print(f"  ACT: {act['event_time']} | {act['event_type']} | {act['source_system']} -> {act['target_system']} | res={act['resource_id']} | res_code={act['reported_result']}")
