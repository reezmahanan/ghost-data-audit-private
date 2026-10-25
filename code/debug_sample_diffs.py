import sys, csv, json
sys.path.append('code')
from auditor import DeletionAuditor

auditor = DeletionAuditor()
samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
true_outputs = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}

for s in samples:
    cid = s['case_id']
    pred_st, pred_steps = auditor.audit_case(s)
    true_row = true_outputs[cid]
    true_st = true_row['deletion_status']
    true_steps = json.loads(true_row['steps_json'])
    
    st_match = pred_st == true_st
    steps_match = pred_steps == true_steps
    
    if not steps_match:
        print(f"=== {cid} === pred_st={pred_st} (true={true_st}) | n_pred={len(pred_steps)} n_true={len(true_steps)}")
        p_set = [(x['phase'], x['system_id'], x['resource_id'], x['operation'], x['evidence_id']) for x in pred_steps]
        t_set = [(x['phase'], x['system_id'], x['resource_id'], x['operation'], x['evidence_id']) for x in true_steps]
        extra = [x for x in p_set if x not in t_set]
        missing = [x for x in t_set if x not in p_set]
        if extra:
            print("  EXTRA in pred:")
            for x in extra: print("   +", x)
        if missing:
            print("  MISSING in pred:")
            for x in missing: print("   -", x)
