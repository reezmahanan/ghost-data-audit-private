import csv, json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

for s in samples[10:]:
    cid = s['case_id']
    req_at = s['requested_at']
    rep_at = s['reported_at']
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    resources = set(x['resource_id'] for x in true_steps)
    print(f"=== {cid} ({s['reported_status']}) rep={rep_at} ===")
    print(f"  Target resources: {resources}")
    matched_acts = [a for a in activities if a['resource_id'] in resources]
    for a in matched_acts:
        print(f"    Act {a['activity_id']} at {a['event_time']}: {a['source_system']} -> {a['target_system']} {a['resource_id']} ({a['event_type']}, {a['reported_result']})")
