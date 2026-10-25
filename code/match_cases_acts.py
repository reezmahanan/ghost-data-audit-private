import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('dataset/system_activity.csv', encoding='utf-8') as f:
    acts = [r for r in csv.DictReader(f) if r['target_system'] == 'account_service' and r['event_type'] == 'DELETE_RECORD']

with open('dataset/sample_deletion_requests.csv', encoding='utf-8') as f:
    samples = list(csv.DictReader(f))

for s in samples[:15]:
    req_at = s['requested_at']
    rep_at = s['reported_at']
    # find acts where event_time is near req_at / rep_at (e.g. within 2 hours of rep_at)
    matching = [a for a in acts if a['event_time'] <= rep_at and a['event_time'] >= req_at]
    if not matching:
        # Check within same day
        matching = [a for a in acts if a['event_time'][:10] == rep_at[:10]]
    print(f"{s['case_id']}: req={req_at}, rep={rep_at} -> matches: {[m['resource_id'] for m in matching]}")
