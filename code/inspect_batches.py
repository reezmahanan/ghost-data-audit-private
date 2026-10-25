import csv

acts = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
worker_acts = [a for a in acts if a['source_system'] == 'deletion_worker']

print(f"Total worker acts: {len(worker_acts)}")
# How many account_service DELETE_RECORD acts?
acc_acts = [a for a in worker_acts if a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD']
print(f"Total account_service DELETE_RECORD acts: {len(acc_acts)}")

# Check sequence between consecutive account_service DELETE_RECORD acts
for i in range(len(acc_acts) - 1):
    a1 = acc_acts[i]
    a2 = acc_acts[i+1]
    idx1 = worker_acts.index(a1)
    idx2 = worker_acts.index(a2)
    sub_acts = worker_acts[idx1:idx2]
    # print first 5 batches
    if i < 5:
        print(f"--- Batch {i+1} ({a1['resource_id']}) ---")
        for sa in sub_acts:
            print(f"   {sa['event_time']} | {sa['target_system']:20} | {sa['resource_id']:15} | {sa['event_type']:20} | {sa['reported_result']}")
