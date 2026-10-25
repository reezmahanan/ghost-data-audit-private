import csv, re

acts = list(csv.DictReader(open('dataset/system_activity.csv', encoding='utf-8')))
link_acts = [a for a in acts if a['event_type'] == 'LINK_RESOURCE_IDENTITY']

ev_files = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))

for a in link_acts:
    res = a['resource_id']
    t_sys = a['target_system']
    t_time = a['event_time']
    details = a['details']
    # find evidence file
    matching_evs = []
    for ef in ev_files:
        # check if origin matches or file path contains sys
        if ef['origin'] == t_sys or t_sys in ef['origin']:
            matching_evs.append(ef['file_id'])
    print(f"{a['activity_id']} ({t_time}): {t_sys} {res} | evs={matching_evs} | {details}")
