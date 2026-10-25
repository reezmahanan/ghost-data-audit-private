import os, csv

accounts = [
    'account_001', 'account_002', 'account_7566', 'account_004', 'account_005',
    'account_006', 'account_007', 'account_008', 'account_3960', 'account_010',
    'account_4248', 'account_9797', 'account_9335', 'account_3677', 'account_4745',
    'account_994', 'account_4092', 'account_5521', 'account_9102', 'account_5037',
    'account_6440', 'account_4990', 'account_410', 'account_5334', 'account_3136',
    'account_5684', 'account_3866', 'account_5482', 'account_7012', 'account_4163',
    'account_4857', 'account_8858'
]

ev_files = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))

for i, acc in enumerate(accounts):
    cid = f"case_{i+1:02d}"
    found_in = []
    for ef in ev_files:
        p = os.path.join('dataset', ef['file_path'])
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                if acc in fp.read():
                    found_in.append(ef['file_id'])
        except:
            pass
    print(f"{cid} ({acc}): {found_in}")
