import csv, json
for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')):
    steps = json.loads(r['steps_json'])
    for s in steps:
        if s['phase'] == 'FINDING':
            assert s['evidence_id'] != '', f"Empty evidence_id on finding: {s} in {r['case_id']}"
print("All findings have non-empty evidence_id!")
