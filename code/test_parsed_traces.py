import glob, re, os, csv

users = list(csv.DictReader(open('dataset/user_identities.csv', encoding='utf-8')))
user_audit = list(csv.DictReader(open('dataset/user_audit_log.csv', encoding='utf-8')))

email_to_uid = {u['email'].lower(): u['user_id'] for u in users}
hash_to_uid = {u['email_hash']: u['user_id'] for u in users if u['email_hash']}
phone_to_uid = {u['phone']: u['user_id'] for u in users if u['phone']}

for a in user_audit:
    uid = a['user_id']
    f, ov, nv = a['field_name'], a['old_value'], a['new_value']
    if f == 'email':
        if ov: email_to_uid[ov.lower()] = uid
        if nv: email_to_uid[nv.lower()] = uid
    elif f == 'email_hash':
        if ov: hash_to_uid[ov] = uid
        if nv: hash_to_uid[nv] = uid
    elif f == 'phone':
        if ov: phone_to_uid[ov] = uid
        if nv: phone_to_uid[nv] = uid

def resolve_user(text):
    if not text or text == 'null': return None
    text_l = text.lower()
    m = re.search(r'user_\d+', text)
    if m: return m.group(0)
    for email, uid in email_to_uid.items():
        if email in text_l: return uid
    for h, uid in hash_to_uid.items():
        if h in text: return uid
    for p, uid in phone_to_uid.items():
        if p in text: return uid
    return None

# Test on evidence_94 and evidence_01
for fid, fpath in [('evidence_94', 'dataset/evidence/logs/resource_lookup_trace_20260926_103856.log'),
                   ('evidence_01', 'dataset/evidence/logs/service_events_ap_south_20260915.log')]:
    traces = {}
    with open(fpath, encoding='utf-8') as f:
        for line in f:
            tm = re.search(r'(tr-[0-9a-zA-Z\-_]+|rb-[0-9a-zA-Z\-_]+)', line)
            if tm:
                tid = tm.group(1)
                traces.setdefault(tid, []).append(line.strip())
                
    print(f"=== {fid}: {len(traces)} traces ===")
    for tid, lines in traces.items():
        blob = " ".join(lines)
        uid = resolve_user(blob)
        res_m = re.findall(r'resource_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_]+)["\']?', blob)
        res_id = res_m[0] if res_m else None
        if uid and res_id:
            print(f"  {tid}: uid={uid} res={res_id} in {blob[:60]}")
