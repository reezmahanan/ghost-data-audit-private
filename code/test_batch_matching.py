import csv, json
from datetime import datetime

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
worker_acts = [a for a in activities if a['source_system'] == 'deletion_worker']

# Break worker_acts into batches by account_service DELETE_RECORD
batches = []
curr_batch = None

for a in worker_acts:
    if a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD':
        if curr_batch:
            batches.append(curr_batch)
        curr_batch = {'primary': a, 'actions': [a]}
    else:
        if curr_batch:
            curr_batch['actions'].append(a)
if curr_batch:
    batches.append(curr_batch)

print(f"Total batches formed: {len(batches)}")

# Match each sample to a batch
# Criteria: batch event_time is within 2.5 hours of reported_at
# and reported_result of primary matches reported_status expectation
# and any resource in the batch that appears in evidence for that user matches that user!

from evidence_indexer import EvidenceIndexer
indexer = EvidenceIndexer('dataset')

perfect_matches = 0
for s in samples:
    cid = s['case_id']
    req_email = s['email'].lower()
    rep_at = s['reported_at']
    rep_dt = datetime.fromisoformat(rep_at.replace('Z', '+00:00'))
    uid = indexer.email_to_uid.get(req_email) or indexer.resolve_user(req_email)
    
    # User's known resources from evidence
    user_obs = [o for o in indexer.observations if o['user_id'] == uid]
    user_res_known = set(o['resource_id'] for o in user_obs)
    
    # Find candidate batches
    candidates = []
    for b in batches:
        b_dt = datetime.fromisoformat(b['primary']['event_time'].replace('Z', '+00:00'))
        diff_h = abs((b_dt - rep_dt).total_seconds()) / 3600.0
        if diff_h <= 3.0:
            b_res = set(act['resource_id'] for act in b['actions'])
            # Score candidate: overlap with known user resources + closeness in time
            overlap = len(b_res.intersection(user_res_known))
            candidates.append((overlap, -diff_h, b))
            
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    true_res = set(x['resource_id'] for x in true_steps)
    
    if candidates:
        best_b = candidates[0][2]
        best_res = set(act['resource_id'] for act in best_b['actions'])
        # Also add audit_record for the user
        audit_records = [o['resource_id'] for o in user_obs if o['system_id'] == 'security_service']
        for ar in audit_records:
            best_res.add(ar)
            
        diff_from_true = true_res.symmetric_difference(best_res)
        if len(diff_from_true) == 0:
            perfect_matches += 1
            print(f"MATCH: {cid} -> {best_b['primary']['resource_id']} | overlap={candidates[0][0]}")
        else:
            print(f"DIFF: {cid} | diff={diff_from_true} | best_primary={best_b['primary']['resource_id']}")
    else:
        print(f"NO CANDIDATE: {cid}")

print(f"\nPerfect resource set matches: {perfect_matches} / {len(samples)}")
