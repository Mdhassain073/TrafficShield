# app/parser.py

import re
from datetime import datetime
from collections import defaultdict

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<time>.*?)\] "(?P<method>\w+) (?P<path>\S+) .*?" (?P<status>\d+)'
)

def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        data = match.groupdict()
        try:
            data['time'] = datetime.strptime(data['time'].split()[0], "%d/%b/%Y:%H:%M:%S")
        except Exception as e:
            return None
        return data
    return None

def parse_log_file(path):
    ip_records = defaultdict(list)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parsed = parse_log_line(line)
                if parsed:
                    ip_records[parsed['ip']].append(parsed)
    except Exception as e:
        print(f"[ERROR] Failed to read log file: {e}")
    return ip_records
