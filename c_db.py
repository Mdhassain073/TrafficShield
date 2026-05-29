# c_db.py — Create and seed the alerts database with sample data

import sqlite3
import os
from datetime import datetime, timedelta


def seed_database():
    """Create the alerts table and insert sample data (idempotent)."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/alerts.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            ip TEXT,
            anomaly_score REAL,
            reason TEXT,
            timestamp DATETIME
        )
    ''')

    # Only seed if the table is empty
    cur.execute("SELECT COUNT(*) FROM alerts")
    count = cur.fetchone()[0]

    if count == 0:
        sample_data = [
            ("192.168.1.1", 0.98, "High 404 rate", datetime.now() - timedelta(minutes=10)),
            ("10.0.0.5", 0.96, "Burst traffic", datetime.now() - timedelta(minutes=5)),
            ("172.16.0.9", 0.99, "Suspicious POST", datetime.now() - timedelta(minutes=2)),
        ]
        cur.executemany("INSERT INTO alerts VALUES (?, ?, ?, ?)", sample_data)
        conn.commit()
        print(f"✅ Seeded {len(sample_data)} sample alerts.")
    else:
        print(f"ℹ️ Database already has {count} alerts. Skipping seed.")

    conn.close()


if __name__ == "__main__":
    seed_database()
