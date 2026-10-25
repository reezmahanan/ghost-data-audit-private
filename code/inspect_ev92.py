import json

data = json.load(open('dataset/evidence/records/service_resource_export_20260915_114455.json', encoding='utf-8'))
se = data['service_exports']

for svc, val in se.items():
    print(f"=== {svc} ===")
    for k, item_list in val.items():
        print(f"  {k}: {len(item_list)} items")
        if item_list:
            print("    Sample:", item_list[0])
