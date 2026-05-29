# app/test_parser.py — Test the log parser

from app.parser import parse_log_file

LOG_FILE = "data/access.log"

records = parse_log_file(LOG_FILE)
print(f"✅ Parsed {len(records)} unique IPs")
for ip, reqs in records.items():
    print(f"  {ip}: {len(reqs)} requests")
