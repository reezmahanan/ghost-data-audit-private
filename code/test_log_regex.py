import os, re, glob, json

pattern = re.compile(r'resource_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_]+)["\']?')
old_pattern = re.compile(r'resource_id="?([a-zA-Z0-9_]+)"?')

for logpath in glob.glob('dataset/evidence/logs/*'):
    with open(logpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        m_old = old_pattern.findall(content)
        m_new = pattern.findall(content)
        if len(m_new) != len(m_old):
            print(f"{os.path.basename(logpath)}: old={len(m_old)}, new={len(m_new)}")
