import csv
import json
import re
import sys
from evidence_indexer import EvidenceIndexer

sys.stdout.reconfigure(encoding='utf-8')

indexer = EvidenceIndexer()
system_activity = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))

# Check all activities
print(f"Total system activities: {len(system_activity)}")

# For each activity, see if we can resolve the user
act_to_user = {}
for act in system_activity:
    act_text = f"{act['activity_id']} {act['event_type']} {act['source_system']} {act['target_system']} {act['resource_id']} {act['details']}"
    uid = indexer.resolve_user(act_text)
    if uid:
        act_to_user[act['activity_id']] = uid

print(f"Directly resolved {len(act_to_user)} activities by text.")
