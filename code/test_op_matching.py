import csv, json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
activities = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

act_by_res = {a['resource_id']: a for a in activities if a['source_system'] == 'deletion_worker'}

for s in samples:
    cid = s['case_id']
    steps = json.loads(true_outputs[cid]['steps_json'])
    findings = [x for x in steps if x['phase'] == 'FINDING']
    for f in findings:
        res = f['resource_id']
        op = f['operation']
        act = act_by_res.get(res)
        act_op = act['event_type'] if act else 'NONE'
        print(f"{cid} {res}: Finding op={op} | Act op={act_op}")
