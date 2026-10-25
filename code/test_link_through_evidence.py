import csv, json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

from evidence_indexer import EvidenceIndexer
indexer = EvidenceIndexer('dataset')

for s in samples[10:]:
    cid = s['case_id']
    req_email = s['email'].lower()
    uid = indexer.email_to_uid.get(req_email) or indexer.resolve_user(req_email)
    user_obs = [o for o in indexer.observations if o['user_id'] == uid]
    obs_res = set(o['resource_id'] for o in user_obs)
    
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    true_res = set(x['resource_id'] for x in true_steps)
    
    # In system_activity, find activities matching any of obs_res
    matched_acts = [a for a in activities if a['resource_id'] in obs_res]
    
    # Find all batches containing these matched_acts
    # Look at the primary account in those batches
    print(f"{cid} ({uid}) | obs_res={obs_res}")
    print(f"  true_res={true_res}")
    for a in matched_acts:
        print(f"    act: {a['activity_id']} {a['source_system']}->{a['target_system']} {a['resource_id']} at {a['event_time']}")
