import csv
import json

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))
ev_files = {r['file_id']: r for r in csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8'))}

for s, o in zip(samples, sample_outs):
    steps = json.loads(o['steps_json'])
    ev_ids = sorted(list(set(step.get('evidence_id') for step in steps if step.get('evidence_id'))))
    ev_info = [(eid, ev_files[eid]['file_path'], ev_files[eid]['captured_at']) for eid in ev_ids]
    print(f"{s['case_id']} (audit: {s['audit_at']}) -> {ev_info}")
