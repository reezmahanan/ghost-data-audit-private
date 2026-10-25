import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

for r in requests:
    cid_num = int(r['case_id'].split('_')[1])
    if cid_num >= 525:
        print(f"{r['case_id']} | {r['reported_status']} | {r['request_text']}")
