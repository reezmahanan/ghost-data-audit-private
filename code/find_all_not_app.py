import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))

not_app_indicators = [
    'leave the account active', 'not asking for deletion', 'keep the account as it is',
    'do not close the account', 'without removing any of my records',
    'marketing lists only', 'this is an information request, not a request to erase it',
    'leave my profile and purchase history in place', 'i want to continue using the service',
    "don't delete or change anything", 'access my profile and need help resetting',
    'misspelled', 'download my account information', 'copy of last year',
    'stop the promotional emails', 'tell me what personal information you hold'
]

not_app_cases = []
for r in requests:
    txt_lower = r['request_text'].lower()
    for ind in not_app_indicators:
        if ind in txt_lower:
            not_app_cases.append(r['case_id'])
            break

print(f"Total NOT_APPLICABLE identified: {len(not_app_cases)}")
print(not_app_cases)
