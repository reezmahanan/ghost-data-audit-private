import csv

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
evals = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))
all_requests = samples + evals

print(f"Total requests: {len(all_requests)}")

from auditor import DeletionAuditor
auditor = DeletionAuditor()

del_requests = [r for r in all_requests if not auditor.is_not_applicable(r['request_text'])]
not_app_requests = [r for r in all_requests if auditor.is_not_applicable(r['request_text'])]

print(f"Non-deletion (NOT_APPLICABLE) requests: {len(not_app_requests)}")
print(f"Deletion requests: {len(del_requests)}")

# Status breakdown of deletion requests
status_counts = {}
for r in del_requests:
    st = r['reported_status']
    status_counts[st] = status_counts.get(st, 0) + 1
print(f"Reported status counts: {status_counts}")
