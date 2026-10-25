import csv

requests = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))
print(f"Total requests: {len(requests)}")

intents = []
for r in requests:
    text = r['request_text']
    # Check for keywords indicating non-deletion (access, correction, export, opt-out, etc.)
    # Let's inspect some samples
