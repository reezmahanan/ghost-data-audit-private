import csv
import os

files = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))
print(f"Total evidence files: {len(files)}")

types = {}
for f in files:
    ext = os.path.splitext(f['file_path'])[1].lower()
    types[ext] = types.get(ext, 0) + 1

print("By extension:", types)

origins = {}
for f in files:
    origins[f['origin']] = origins.get(f['origin'], 0) + 1

print("\nBy origin:")
for orig, count in sorted(origins.items(), key=lambda x: -x[1]):
    print(f"  {orig}: {count}")
