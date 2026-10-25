import csv
import json
import sys
from evidence_indexer import EvidenceIndexer

sys.stdout.reconfigure(encoding='utf-8')

indexer = EvidenceIndexer()
samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

correct_cases = 0
total_cases = len(samples)

for s, o in zip(samples, sample_outs):
    cid = s['case_id']
    req_email = s['email'].lower()
    uid = indexer.email_to_uid.get(req_email)
    audit_at = s['audit_at']
    true_status = o['deletion_status']
    true_steps = json.loads(o['steps_json'])
    
    # Filter observations for this user up to audit_at
    user_obs = [obs for obs in indexer.observations if obs['user_id'] == uid and obs['captured_at'] <= audit_at]
    # Sort by captured_at descending
    user_obs.sort(key=lambda x: x['captured_at'], reverse=True)
    
    # Print comparison
    true_res = [(st['system_id'], st['resource_id'], st['phase'], st['operation'], st.get('evidence_id')) for st in true_steps]
    obs_res = [(o['system_id'], o['resource_id'], o['obs_type'], o['file_id']) for o in user_obs]
    
    print(f"\nCase {cid} ({uid}) | Target: {true_status}")
    print("  True steps:")
    for tr in true_res:
        print("   ", tr)
    print("  Available observations:")
    seen = set()
    for ob in obs_res:
        k = (ob[0], ob[1], ob[2])
        if k not in seen:
            print("   ", ob)
            seen.add(k)
