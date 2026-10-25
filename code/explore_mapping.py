import csv, json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

# Group deletion_worker activities
worker_acts = [a for a in activities if a['source_system'] == 'deletion_worker']

for s in samples:
    cid = s['case_id']
    req_at = s['requested_at']
    rep_at = s['reported_at']
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    resources = set(x['resource_id'] for x in true_steps)
    
    # Let's find all worker acts that match these resources
    matched = [a for a in worker_acts if a['resource_id'] in resources]
    act_times = [a['event_time'] for a in matched]
    print(f"{cid}: req={req_at[:16]} rep={rep_at[:16]} | n_res={len(resources)} | act_times={act_times}")
