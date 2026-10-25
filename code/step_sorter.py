import csv
import json
import os
import re
import sqlite3
import sys

# Define Operation Order Rankings
FINDING_OPS = {
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4
}

REMEDIATION_OPS = {
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5
}

VERIFICATION_OPS = {
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6
}

def sort_steps(steps):
    def step_key(s):
        phase_rank = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}[s['phase']]
        if s['phase'] == 'FINDING':
            op_rank = FINDING_OPS.get(s['operation'], 99)
        elif s['phase'] == 'REMEDIATION':
            op_rank = REMEDIATION_OPS.get(s['operation'], 99)
        else:
            op_rank = VERIFICATION_OPS.get(s['operation'], 99)
        return (phase_rank, op_rank, s['system_id'], s['resource_id'])

    sorted_steps = sorted(steps, key=step_key)
    for i, s in enumerate(sorted_steps, 1):
        s['step_no'] = i
    return sorted_steps

print("Step sorting logic defined successfully.")
