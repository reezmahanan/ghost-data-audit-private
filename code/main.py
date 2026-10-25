import argparse
import csv
import json
import os
import sys
from auditor import DeletionAuditAgent

sys.stdout.reconfigure(encoding='utf-8')

def parse_args():
    parser = argparse.ArgumentParser(description="Ghost Data Still Exists - Deletion Audit Agent")
    parser.add_argument("--input", default="dataset/deletion_requests.csv", help="Path to input deletion requests CSV")
    parser.add_argument("--output", default="output.csv", help="Path to output CSV file")
    parser.add_argument("--dataset", default="dataset", help="Path to dataset directory")
    return parser.parse_args()

def case_sort_key(cid):
    m = cid.split('_')
    if len(m) == 2 and m[1].isdigit():
        return int(m[1])
    return cid

def main():
    args = parse_args()
    input_file = args.input
    output_file = args.output
    dataset_dir = args.dataset

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Initializing DeletionAuditAgent with dataset dir: {dataset_dir}...")
    agent = DeletionAuditAgent(dataset_dir)

    print(f"Reading requests from: {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    print(f"Auditing {len(reader)} requests...")
    results = []
    status_summary = {}

    for idx, row in enumerate(reader):
        cid = row['case_id']
        status, steps = agent.audit_case(row)
        status_summary[status] = status_summary.get(status, 0) + 1
        steps_json_str = json.dumps(steps, separators=(',', ':'))
        results.append({
            'case_id': cid,
            'deletion_status': status,
            'steps_json': steps_json_str
        })
        if (idx + 1) % 50 == 0 or (idx + 1) == len(reader):
            print(f"  Processed {idx + 1}/{len(reader)} cases...")

    # Sort results by case_id
    results.sort(key=lambda r: case_sort_key(r['case_id']))

    # Write output CSV
    print(f"Writing {len(results)} rows to: {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['case_id', 'deletion_status', 'steps_json'])
        for r in results:
            writer.writerow([r['case_id'], r['deletion_status'], r['steps_json']])

    print("Audit completed successfully!")
    print(f"Summary of results: {status_summary}")
    print(f"Output saved to: {output_file}")

if __name__ == '__main__':
    main()
