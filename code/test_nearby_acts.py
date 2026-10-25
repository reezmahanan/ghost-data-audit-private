import csv, json
from datetime import datetime

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
worker_acts = [a for a in activities if a['source_system'] == 'deletion_worker']

for s in samples:
    cid = s['case_id']
    req_at = s['requested_at']
    rep_at = s['reported_at']
    rep_dt = datetime.fromisoformat(rep_at.replace('Z', '+00:00'))
    
    # Filter acts within 3 hours before or after rep_at
    nearby_acts = []
    for a in worker_acts:
        a_dt = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))
        diff_hours = abs((a_dt - rep_dt).total_seconds()) / 3600.0
        if diff_hours <= 2.5:
            nearby_acts.append((diff_hours, a))
            
    nearby_acts.sort(key=lambda x: x[0])
    
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    true_res = set(x['resource_id'] for x in true_steps)
    
    act_res = set(a['resource_id'] for _, a in nearby_acts)
    
    # Check overlap
    print(f"{cid} ({rep_at}): true_res={true_res}")
    print(f"   nearby_act_res={act_res}")
    print(f"   intersection={true_res.intersection(act_res)}")
