import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

evidence_files = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))

print(f"{'file_id':<12} | {'origin':<35} | {'captured_at':<20} | {'path'}")
print("-" * 100)
for ef in evidence_files:
    print(f"{ef['file_id']:<12} | {ef['origin']:<35} | {ef['captured_at']:<20} | {ef['file_path']}")
