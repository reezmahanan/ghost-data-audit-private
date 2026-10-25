import csv, json
from datetime import datetime

# 1. Load users & identities
users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_audit = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))

email_to_uid = {u['email'].lower(): u['user_id'] for u in users}
hash_to_uid = {u['email_hash']: u['user_id'] for u in users if u['email_hash']}
phone_to_uid = {u['phone']: u['user_id'] for u in users if u['phone']}

for a in user_audit:
    uid = a['user_id']
    f, ov, nv = a['field_name'], a['old_value'], a['new_value']
    if f == 'email':
        if ov: email_to_uid[ov.lower()] = uid
        if nv: email_to_uid[nv.lower()] = uid
    elif f == 'email_hash':
        if ov: hash_to_uid[ov] = uid
        if nv: hash_to_uid[nv] = uid
    elif f == 'phone':
        if ov: phone_to_uid[ov] = uid
        if nv: phone_to_uid[nv] = uid

from evidence_indexer import EvidenceIndexer
indexer = EvidenceIndexer('dataset')

# Map observed resources to users
res_to_uid = {}
for o in indexer.observations:
    res = o['resource_id']
    uid = o['user_id']
    if uid:
        res_to_uid[res] = uid

# Build batches
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
worker_acts = [a for a in activities if a['source_system'] == 'deletion_worker']

batches = []
curr = None
for a in worker_acts:
    if a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD':
        if curr: batches.append(curr)
        curr = {'primary': a, 'actions': [a], 'resources': {a['resource_id']}}
    else:
        if curr:
            curr['actions'].append(a)
            curr['resources'].add(a['resource_id'])
if curr: batches.append(curr)

# For each batch, resolve uid from res_to_uid
for b in batches:
    uids = set()
    for r in b['resources']:
        if r in res_to_uid:
            uids.add(res_to_uid[r])
    b['uids'] = uids

# Test on 32 samples
samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}

resolved_count = 0
for s in samples:
    cid = s['case_id']
    email = s['email'].lower()
    uid = email_to_uid.get(email) or indexer.resolve_user(email)
    
    # Find matching batch
    matching_batches = [b for b in batches if uid in b['uids']]
    if matching_batches:
        b = matching_batches[0]
        resolved_count += 1
        true_steps = json.loads(true_outputs[cid]['steps_json'])
        true_res = set(x['resource_id'] for x in true_steps)
        print(f"MATCH: {cid} ({uid}) -> batch primary {b['primary']['resource_id']} | overlap={len(true_res.intersection(b['resources']))}/{len(true_res)}")
    else:
        print(f"NO MATCH: {cid} ({uid})")

print(f"\nResolved by batch evidence: {resolved_count} / {len(samples)}")
