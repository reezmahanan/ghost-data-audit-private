import sys, csv
sys.path.append('code')
from test_perfect_samples import PrecisionAuditor

auditor = PrecisionAuditor('dataset')
eval_requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

for req in eval_requests:
    cid = req['case_id']
    st, steps = auditor.audit_case(req)
    if st != 'NOT_APPLICABLE' and len(steps) == 0:
        print(f"{cid}: status={st}, steps={steps}, email={req['email']}")
