import csv, json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

anonymize_acts = [a for a in activities if a['source_system'] == 'deletion_worker' and a['target_system'] == 'analytics_platform' and a['event_type'] == 'ANONYMIZE_RECORD']

for s in samples:
    cid = s['case_id']
    req_at = s['requested_at']
    rep_at = s['reported_at']
    
    true_steps = json.loads(true_outputs[cid]['steps_json'])
    true_analytics = [x for x in true_steps if x['system_id'] == 'analytics_platform' and x['operation'] == 'VERIFY_RECORD_ANONYMIZED']
    if true_analytics:
        res = true_analytics[0]['resource_id']
        ev = true_analytics[0]['evidence_id']
        # Find matching act
        matching_acts = [a for a in anonymize_acts if a['resource_id'] == res]
        print(f"{cid}: True={res} ({ev}) | Act={matching_acts[0]['event_time'] if matching_acts else 'NONE'}")
