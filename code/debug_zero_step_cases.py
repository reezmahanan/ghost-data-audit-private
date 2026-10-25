import sys, csv
sys.path.append('code')
from test_perfect_samples import PrecisionAuditor

auditor = PrecisionAuditor('dataset')
eval_requests = {r['case_id']: r for r in csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8'))}

for cid in ['case_61', 'case_63']:
    req = eval_requests[cid]
    print(f"=== {cid} ===")
    print(req)
    uid = auditor.indexer.email_to_uid.get(req['email'].lower())
    print("UID:", uid)
    # Check observations
    obs = [o for o in auditor.indexer.observations if o['user_id'] == uid]
    print("Observations:", obs)
