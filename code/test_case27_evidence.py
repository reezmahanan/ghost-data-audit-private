import csv, os

samples = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8'))}
c27 = samples['case_27']
print('case_27:', c27)

# Search for case_27 email and resources in all evidence files
email = c27['email']
res_list = ['account_3866', 'analytics_4574', 'support_4707', 'data_flow_2295', 'backup_5970', 'audit_record_3830']

for root, dirs, files in os.walk('dataset/evidence'):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
                matches = [r for r in res_list if r in txt]
                if email in txt or matches:
                    print(f"In {f}: email_in={email in txt}, matched={matches}")
        except:
            pass
