import csv
import json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

for s, o in zip(samples, sample_outs):
    steps = json.loads(o['steps_json'])
    ev_ids = [step.get('evidence_id') for step in steps if step.get('evidence_id')]
    ops = [f"{step['phase']}:{step['operation']}:{step['resource_id']}" for step in steps]
    print(f"{s['case_id']} | {o['deletion_status']} | Ev: {set(ev_ids)} | Steps: {len(steps)}")
    for step in steps:
        print(f"   {step['step_no']} [{step['phase']}] {step['system_id']} {step['resource_id']} {step['operation']} {step['state']} (ev: {step.get('evidence_id')})")
