import csv
import json
import sys
from step_sorter import sort_steps

sys.stdout.reconfigure(encoding='utf-8')

with open('dataset/sample_output.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

all_matched = True
for r in rows:
    steps = json.loads(r['steps_json'])
    re_sorted = sort_steps([dict(s) for s in steps])
    for s1, s2 in zip(steps, re_sorted):
        t1 = (s1['step_no'], s1['phase'], s1['system_id'], s1['resource_id'], s1['operation'], s1['state'])
        t2 = (s2['step_no'], s2['phase'], s2['system_id'], s2['resource_id'], s2['operation'], s2['state'])
        if t1 != t2:
            print(f"Mismatch in {r['case_id']}:\n  Orig: {t1}\n  Sort: {t2}")
            all_matched = False
            break

if all_matched:
    print("ALL 32 sample cases match sort_steps ORDER and STEP_NO 100% PERFECTLY!")
