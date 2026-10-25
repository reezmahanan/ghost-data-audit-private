import csv
import json
import os
import sys

# Ensure code root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auditor import DeletionAuditAgent

def evaluate_samples(dataset_dir='dataset'):
    agent = DeletionAuditAgent(dataset_dir)
    samples_path = os.path.join(dataset_dir, 'sample_deletion_requests.csv')
    true_path = os.path.join(dataset_dir, 'sample_output.csv')
    
    samples = list(csv.DictReader(open(samples_path, encoding='utf-8')))
    true_outputs = {r['case_id']: r for r in csv.DictReader(open(true_path, encoding='utf-8'))}

    total_cases = len(samples)
    status_correct = 0
    step_exact_correct = 0
    
    total_true_steps = 0
    matched_steps = 0
    total_fields = 0
    matched_fields = 0
    sequence_correct = 0

    for s in samples:
        cid = s['case_id']
        pred_st, pred_steps = agent.audit_case(s)
        true_row = true_outputs[cid]
        true_st = true_row['deletion_status']
        true_steps = json.loads(true_row['steps_json'])

        # Case-level status
        if pred_st == true_st:
            status_correct += 1

        # Sequence check
        # Phase order: FINDING -> REMEDIATION -> VERIFICATION
        phases = [step['phase'] for step in pred_steps]
        phase_order = {'FINDING': 0, 'REMEDIATION': 1, 'VERIFICATION': 2}
        is_seq_valid = all(phase_order[phases[i]] <= phase_order[phases[i+1]] for i in range(len(phases)-1))
        if is_seq_valid:
            sequence_correct += 1

        # Step-level exact match
        if pred_steps == true_steps:
            step_exact_correct += 1

        # Field-level accuracy
        # Compare matching steps by (system_id, resource_id, phase)
        true_step_map = {(x['system_id'], x['resource_id'], x['phase']): x for x in true_steps}
        pred_step_map = {(x['system_id'], x['resource_id'], x['phase']): x for x in pred_steps}

        total_true_steps += len(true_steps)
        for k, ts in true_step_map.items():
            if k in pred_step_map:
                matched_steps += 1
                ps = pred_step_map[k]
                # Compare 6 fields: phase, system_id, resource_id, operation, state, evidence_id
                for field in ['phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']:
                    total_fields += 1
                    if ps.get(field) == ts.get(field):
                        matched_fields += 1
            else:
                total_fields += 6 # all 6 fields missed

    status_acc = status_correct / total_cases * 100
    step_acc = matched_steps / total_true_steps * 100
    field_acc = matched_fields / total_fields * 100
    seq_acc = sequence_correct / total_cases * 100

    print("=== Evaluation on Public Sample Dataset ===")
    print(f"Total Cases: {total_cases}")
    print(f"Case-level Status Accuracy: {status_correct}/{total_cases} ({status_acc:.1f}%)")
    print(f"Step-level Exact Accuracy: {step_exact_correct}/{total_cases} ({step_exact_correct/total_cases*100:.1f}%)")
    print(f"Step Retrieval Accuracy: {matched_steps}/{total_true_steps} ({step_acc:.1f}%)")
    print(f"Field-level Accuracy: {matched_fields}/{total_fields} ({field_acc:.1f}%)")
    print(f"Sequence Accuracy: {sequence_correct}/{total_cases} ({seq_acc:.1f}%)")

    return {
        'total_cases': total_cases,
        'status_correct': status_correct,
        'status_acc': status_acc,
        'step_exact_correct': step_exact_correct,
        'step_acc': step_acc,
        'field_acc': field_acc,
        'seq_acc': seq_acc
    }

if __name__ == '__main__':
    evaluate_samples()
