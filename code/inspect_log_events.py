import glob, re, os

for fpath in glob.glob('dataset/evidence/logs/*'):
    fname = os.path.basename(fpath)
    print(f"=== {fname} ===")
    with open(fpath, encoding='utf-8', errors='ignore') as f:
        events = set()
        services = set()
        for line in f:
            sm = re.search(r'service[=:]"?([a-zA-Z0-9_]+)"?', line)
            em = re.search(r'event[=:]"?([a-zA-Z0-9_]+)"?', line)
            if sm and em:
                events.add((sm.group(1), em.group(1)))
        for s, e in sorted(events)[:10]:
            print(f"  {s:20} -> {e}")
