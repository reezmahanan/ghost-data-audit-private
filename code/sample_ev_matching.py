import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load samples
samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))
ev_manifest = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))
ev_by_id = {r['file_id']: r for r in ev_manifest}

print(f"Total samples: {len(samples)}")
for s, o in zip(samples, sample_outs):
    audit_at = s['audit_at']
    steps = json.loads(o['steps_json'])
    ev_used = sorted(list(set(step.get('evidence_id') for step in steps if step.get('evidence_id'))))
    
    # Check what evidence files were captured <= audit_at
    valid_ev = [e for e in ev_manifest if e['captured_at'] <= audit_at]
    valid_ev.sort(key=lambda x: x['captured_at'], reverse=True)
    latest_3 = [e['file_id'] + '(' + e['captured_at'] + ')' for e in valid_ev[:3]]
    print(f"{s['case_id']}: audit_at={audit_at} | Used: {ev_used} | Latest available: {latest_3}")
