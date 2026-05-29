# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Session timeout (in seconds)
SESSION_TIMEOUT = 300

# Thresholds for detection
MODEL_CONTAMINATION = 0.03
ALERT_THRESHOLD = 0.5

# Email alert settings (loaded from .env for security)
EMAIL_ALERT_THRESHOLD = 0.98
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
