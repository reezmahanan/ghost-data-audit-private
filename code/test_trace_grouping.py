import re

traces = {} # trace_id -> list of lines

with open('dataset/evidence/logs/operations_stream_me_central_20260203.log', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'tr-[0-9a-fA-F]+', line)
        if m:
            tid = m.group(0)
            if tid not in traces:
                traces[tid] = []
            traces[tid].append(line.strip())

print(f"Found {len(traces)} traces in log.")
resolved = 0
for tid, lines in traces.items():
    blob = " ".join(lines)
    # Check if there is both an email/user and a resource_id
    has_user = '@' in blob or 'user_' in blob
    res_m = re.findall(r'resource_id="?([a-zA-Z0-9_]+)"?', blob)
    if has_user and res_m:
        resolved += 1

print(f"Traces with both user and resource_id: {resolved}")
