# test_insert.py — Insert a test alert into the database

import sqlite3
import os
from datetime import datetime

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

cur.execute("INSERT INTO alerts VALUES (?, ?, ?, ?)", (
    "192.168.1.99", 0.97, "Test burst attack", datetime.now()
))

conn.commit()
conn.close()
print("✅ Test alert inserted.")
