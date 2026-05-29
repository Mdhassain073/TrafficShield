# app/features.py

import numpy as np
import pandas as pd
from collections import Counter
from app.config import SESSION_TIMEOUT


def extract_features(ip_records):
    """Extract behavioral features from grouped IP request records."""
    rows = []
    print(f"📦 Extracting features from {len(ip_records)} IPs")

    for ip, records in ip_records.items():
        print(f"🔍 IP {ip} has {len(records)} requests")
        if len(records) < 2:
            print(f"⏩ Skipping {ip} — too few requests")
            continue

        records.sort(key=lambda x: x['time'])
        times = [r['time'] for r in records]
        methods = Counter([r['method'] for r in records])
        statuses = Counter([r['status'] for r in records])
        paths = Counter([r['path'] for r in records])

        intervals = [(t2 - t1).total_seconds() for t1, t2 in zip(times[:-1], times[1:])] or [0]

        session_count = 1
        for i in range(1, len(times)):
            if (times[i] - times[i - 1]).total_seconds() > SESSION_TIMEOUT:
                session_count += 1

        burst_count = 0
        for i in range(1, len(times)):
            if (times[i] - times[i - 1]).total_seconds() < 1:
                burst_count += 1

        row = {
            "ip": ip,
            "request_count": len(records),
            "mean_interval": np.mean(intervals),
            "std_interval": np.std(intervals),
            "GET_ratio": methods.get("GET", 0) / len(records),
            "POST_ratio": methods.get("POST", 0) / len(records),
            "status_200_ratio": statuses.get("200", 0) / len(records),
            "status_404_ratio": statuses.get("404", 0) / len(records),
            "status_500_ratio": statuses.get("500", 0) / len(records),
            "unique_paths": len(paths),
            "session_count": session_count,
            "burst_rate": burst_count / len(records),
        }
        rows.append(row)

    if not rows:
        print("⚠️ No valid IPs with enough records — returning empty DataFrame")
        return pd.DataFrame()

    df = pd.DataFrame(rows).set_index("ip")
    return df
