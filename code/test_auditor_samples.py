import csv
import json
import sys
from auditor import DeletionAuditor

sys.stdout.reconfigure(encoding='utf-8')

auditor = DeletionAuditor()

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_outs = list(csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8')))

status_correct = 0
steps_correct = 0
total = len(samples)

for s, o in zip(samples, sample_outs):
    cid = s['case_id']
    pred_status, pred_steps = auditor.audit_case(s)
    true_status = o['deletion_status']
    true_steps = json.loads(o['steps_json'])
    
    status_match = (pred_status == true_status)
    if status_match:
        status_correct += 1
        
    # Check steps match
    steps_match = False
    if len(pred_steps) == len(true_steps):
        steps_match = True
        for p_s, t_s in zip(pred_steps, true_steps):
            p_tuple = (p_s['step_no'], p_s['phase'], p_s['system_id'], p_s['resource_id'], p_s['operation'], p_s['state'], p_s.get('evidence_id', ''))
            t_tuple = (t_s['step_no'], t_s['phase'], t_s['system_id'], t_s['resource_id'], t_s['operation'], t_s['state'], t_s.get('evidence_id', ''))
            if p_tuple != t_tuple:
                steps_match = False
                break

    if steps_match:
        steps_correct += 1
        print(f"PASS: {cid} ({pred_status}) steps={len(pred_steps)}")
    else:
        print(f"FAIL: {cid} | Pred: {pred_status} ({len(pred_steps)} steps) vs True: {true_status} ({len(true_steps)} steps)")
        if not status_match:
            print(f"   Status Mismatch: Pred={pred_status}, True={true_status}")
        else:
            print("   Steps diff:")
            print("   Pred:", pred_steps)
            print("   True:", true_steps)

print("-" * 50)
print(f"Status Accuracy: {status_correct}/{total} ({status_correct/total*100:.1f}%)")
print(f"Step Exact Accuracy: {steps_correct}/{total} ({steps_correct/total*100:.1f}%)")
