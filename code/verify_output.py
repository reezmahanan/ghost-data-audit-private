import csv
import json
import sys

ALLOWED_STATUSES = {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}
ALLOWED_PHASES = {'FINDING', 'REMEDIATION', 'VERIFICATION'}
ALLOWED_FINDING_OPS = {'REPORT_REMAINING_RECORD', 'REPORT_EXPOSED_PII', 'REPORT_ACTIVE_DATA_FLOW', 'REPORT_RESTORE_RISK'}
ALLOWED_REMEDIATION_OPS = {'DISABLE_DATA_FLOW', 'BLOCK_RESTORE', 'DELETE_RECORD', 'REDACT_RECORD', 'ANONYMIZE_RECORD'}
ALLOWED_VERIFICATION_OPS = {'VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT', 'VERIFY_RECORD_REDACTED', 'VERIFY_RECORD_ANONYMIZED', 'VERIFY_DATA_FLOW_DISABLED', 'VERIFY_RESTORE_BLOCKED'}
ALLOWED_STATES = {'PRESENT', 'ABSENT', 'ACTIVE', 'DISABLED', 'BLOCKED', 'REDACTED', 'ANONYMIZED'}

def verify_output(csv_path='output.csv'):
    print(f"Verifying {csv_path}...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    if len(reader) != 518:
        print(f"FAILED: Expected 518 data rows, got {len(reader)}")
        return False
    print(f"PASS: Exactly 518 data rows found.")

    # Check header
    with open(csv_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
    if header != "case_id,deletion_status,steps_json":
        print(f"FAILED: Invalid header: {header}")
        return False
    print(f"PASS: Exact header: {header}")

    # Check ordering and row structure
    case_ids = [r['case_id'] for r in reader]
    expected_cids = [f"case_{i}" for i in range(33, 551)]
    if case_ids != expected_cids:
        print(f"FAILED: Case IDs not sorted or missing. First mismatch at: {[c for c, e in zip(case_ids, expected_cids) if c != e][:5]}")
        return False
    print(f"PASS: Correct sorted case IDs from case_33 to case_550.")

    for idx, r in enumerate(reader):
        cid = r['case_id']
        st = r['deletion_status']
        if st not in ALLOWED_STATUSES:
            print(f"FAILED: Invalid status {st} in {cid}")
            return False

        try:
            steps = json.loads(r['steps_json'])
        except Exception as e:
            print(f"FAILED: Invalid JSON in {cid}: {e}")
            return False

        if st == 'NOT_APPLICABLE':
            if len(steps) != 0:
                print(f"FAILED: NOT_APPLICABLE must have empty steps array in {cid}")
                return False
        else:
            if len(steps) == 0:
                print(f"FAILED: {st} must have non-empty steps array in {cid}")
                return False

            # Check consecutive step_no from 1
            for i, s in enumerate(steps):
                if s.get('step_no') != i + 1:
                    print(f"FAILED: step_no not consecutive in {cid}: step {i} has step_no {s.get('step_no')}")
                    return False
                
                phase = s.get('phase')
                if phase not in ALLOWED_PHASES:
                    print(f"FAILED: invalid phase {phase} in {cid}")
                    return False
                
                op = s.get('operation')
                if phase == 'FINDING' and op not in ALLOWED_FINDING_OPS:
                    print(f"FAILED: invalid finding op {op} in {cid}")
                    return False
                elif phase == 'REMEDIATION' and op not in ALLOWED_REMEDIATION_OPS:
                    print(f"FAILED: invalid remediation op {op} in {cid}")
                    return False
                elif phase == 'VERIFICATION' and op not in ALLOWED_VERIFICATION_OPS:
                    print(f"FAILED: invalid verification op {op} in {cid}")
                    return False

                state = s.get('state')
                if state not in ALLOWED_STATES:
                    print(f"FAILED: invalid state {state} in {cid}")
                    return False

                ev = s.get('evidence_id')
                if ev is None:
                    print(f"FAILED: evidence_id is None in {cid}")
                    return False

                if st == 'COMPLETE':
                    if phase != 'VERIFICATION':
                        print(f"FAILED: COMPLETE case cannot have phase {phase} in {cid}")
                        return False
                    if not ev:
                        print(f"FAILED: COMPLETE verification must have non-empty evidence_id in {cid}: {s}")
                        return False
                elif st == 'INCOMPLETE':
                    if phase in ('REMEDIATION', 'VERIFICATION') and ev != '':
                        print(f"FAILED: INCOMPLETE future step must have empty evidence_id in {cid}: {s}")
                        return False
                    if phase == 'FINDING' and not ev:
                        print(f"FAILED: INCOMPLETE finding must cite non-empty evidence_id in {cid}: {s}")
                        return False

    print("ALL 518 ROWS PASSED 100% OF VALIDATION CHECKS!")
    return True

if __name__ == '__main__':
    verify_output('output.csv')
