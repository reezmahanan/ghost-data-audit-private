import csv

acts = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
acc_acts = [a for a in acts if a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD']
print(f"Total account_service DELETE_RECORD acts: {len(acc_acts)}")

# Check if details field contains any hint
for a in acc_acts[:10]:
    print(a['activity_id'], a['event_time'], a['resource_id'], a['reported_result'], a['details'])
