# core/monitor.py

import time
import requests
import os
import sqlite3
from datetime import datetime

from app.parser import parse_log_file
from app.features import extract_features
from app.detector import TrafficDetector
from app.config import ALERT_THRESHOLD, EMAIL_ALERT_THRESHOLD
from core.emailer import send_alert_email

# Remote log URL — configure in .env file
REMOTE_LOG_URL = os.getenv("REMOTE_LOG_URL", "")
TEMP_FILE = "data/remote_access.log"
ALERT_DB = "data/alerts.db"
WHITELIST_FILE = "data/whitelist.txt"
BLACKLIST_FILE = "data/blacklist.txt"


def load_ip_list(filepath):
    """Load IPs from a whitelist/blacklist file."""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, "r") as f:
        return set(line.strip() for line in f if line.strip())


def fetch_log_file():
    """Fetch access log from remote server."""
    if not REMOTE_LOG_URL:
        print("[WARN] REMOTE_LOG_URL not set in .env — using local data/access.log")
        return False
    try:
        print(f"Fetching: {REMOTE_LOG_URL}")
        r = requests.get(REMOTE_LOG_URL, timeout=30)
        print(f"HTTP Status: {r.status_code}")
        if r.status_code == 200:
            os.makedirs("data", exist_ok=True)
            with open(TEMP_FILE, "w") as f:
                f.write(r.text)
            return True
    except Exception as e:
        print(f"[ERROR] Could not fetch log: {e}")
    return False


def save_alerts(alerts):
    """Save detected alerts to SQLite database."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(ALERT_DB)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            ip TEXT,
            anomaly_score REAL,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    for ip, score in alerts:
        reason = "Suspicious behavior detected"
        cur.execute(
            "INSERT INTO alerts (ip, anomaly_score, reason, timestamp) VALUES (?, ?, ?, ?)",
            (ip, score, reason, datetime.now())
        )
    conn.commit()
    conn.close()


def run_monitor(interval=10):
    """Main monitoring loop — fetch, parse, detect, alert."""
    print("🚀 TrafficShield Monitor started.")
    seen_ips = set()

    while True:
        # Load whitelist/blacklist each cycle so changes take effect immediately
        whitelisted = load_ip_list(WHITELIST_FILE)
        blacklisted = load_ip_list(BLACKLIST_FILE)

        if not fetch_log_file():
            print("⚠️ Failed to fetch log. Retrying...")
            time.sleep(interval)
            continue

        records = parse_log_file(TEMP_FILE)

        # Filter out whitelisted and already-blacklisted IPs before analysis
        filtered_records = {
            ip: reqs for ip, reqs in records.items()
            if ip not in whitelisted and ip not in blacklisted
        }

        print(f"✅ Parsed {sum(len(v) for v in records.values())} requests from {len(records)} IPs")
        print(f"📋 After filtering: {len(filtered_records)} IPs to analyze "
              f"(skipped {len(whitelisted)} whitelisted, {len(blacklisted)} blacklisted)")

        features_df = extract_features(filtered_records)
        print(f"📊 Feature DataFrame:\n{features_df}\n")

        if features_df.empty:
            print("⏳ No significant traffic yet...")
            time.sleep(interval)
            continue

        detector = TrafficDetector()
        alerts = detector.detect_suspicious(features_df)

        print(f"🔍 Detection result: {alerts}")

        new_alerts = [(ip, score) for ip, score in alerts if ip not in seen_ips]

        if new_alerts:
            print(f"🚨 New threats detected: {new_alerts}")
            save_alerts(new_alerts)
            seen_ips.update(ip for ip, _ in new_alerts)

            # Send email for high-severity alerts
            for ip, score in new_alerts:
                if score >= EMAIL_ALERT_THRESHOLD:
                    send_alert_email(ip, score)
        else:
            print("✅ No new suspicious IPs.")

        time.sleep(interval)


if __name__ == "__main__":
    run_monitor()
