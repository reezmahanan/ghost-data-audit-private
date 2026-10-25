import csv, json
from test_perfect_samples import PrecisionAuditor

auditor = PrecisionAuditor('dataset')
eval_requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

status_counts = {}
empty_steps_count = 0
step_counts = []

for req in eval_requests:
    cid = req['case_id']
    st, steps = auditor.audit_case(req)
    status_counts[st] = status_counts.get(st, 0) + 1
    if len(steps) == 0:
        empty_steps_count += 1
    step_counts.append(len(steps))

print(f"Total evaluated requests: {len(eval_requests)}")
print(f"Status distribution: {status_counts}")
print(f"Empty steps count: {empty_steps_count} (should match NOT_APPLICABLE)")
print(f"Avg steps per case: {sum(step_counts)/len(step_counts):.2f}")
print(f"Min steps: {min(step_counts)}, Max steps: {max(step_counts)}")
