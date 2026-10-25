import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

for r in requests:
    txt = r['request_text']
    # Check if user explicitly asks to keep account, or not delete
    txt_lower = txt.lower()
    if any(phrase in txt_lower for phrase in [
        'leave the account active', 'keep the account', 'leave my profile', 'continue using',
        'do not delete', 'don\'t delete', 'portable format', 'copy of last year', 'replace it with the new one',
        'export', 'download', 'update', 'change the email', 'opt-out', 'opt out', 'newsletter',
        'marketing email', 'rectify', 'correct my', 'access my'
    ]):
        print(f"{r['case_id']} | {r['email']} | {txt}")
