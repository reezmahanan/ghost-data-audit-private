import sys, csv
from datetime import datetime
sys.path.append('code')
from test_perfect_samples import PrecisionAuditor

auditor = PrecisionAuditor('dataset')
eval_requests = {r['case_id']: r for r in csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8'))}

for cid in ['case_61', 'case_63']:
    req = eval_requests[cid]
    req_dt = datetime.fromisoformat(req['requested_at'].replace('Z', '+00:00'))
    rep_dt = datetime.fromisoformat(req['reported_at'].replace('Z', '+00:00'))
    print(f"=== {cid} === {req['email']} ({req['reported_status']})")
    print(f"Window: {req['requested_at']} to {req['reported_at']}")
    matching_batches = []
    for b in auditor.batches:
        b_dt = datetime.fromisoformat(b['primary']['event_time'].replace('Z', '+00:00'))
        if req_dt <= b_dt <= rep_dt:
            matching_batches.append(b)
    print(f"Matching batches count: {len(matching_batches)}")
    for b in matching_batches[:5]:
        print("  Batch:", b['primary']['event_time'], b['primary']['resource_id'], b['primary']['reported_result'], "resources:", b['resources'])
