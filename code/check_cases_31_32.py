import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('dataset/system_activity.csv', encoding='utf-8') as f:
    acts = [r for r in csv.DictReader(f) if r['target_system'] == 'account_service' and r['event_type'] == 'DELETE_RECORD']

with open('dataset/sample_deletion_requests.csv', encoding='utf-8') as f:
    samples = list(csv.DictReader(f))

# Let's inspect case_31 and case_32
for s in samples[30:]:
    print(s)
    # acts around reported_at
    rep_at = s['reported_at']
    for a in acts:
        if a['event_time'][:13] == rep_at[:13]:
            print("  ", a)
