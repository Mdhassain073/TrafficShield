# core/emailer.py — Send email alerts for high-severity anomalies

import smtplib
from email.message import EmailMessage
from app.config import ADMIN_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD


def send_alert_email(ip, score):
    """Send an email alert when a suspicious IP is detected."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"⚠️ SMTP not configured — skipping email for IP {ip}")
        return

    msg = EmailMessage()
    msg['Subject'] = f'🚨 TrafficShield Alert: Suspicious IP {ip}'
    msg['From'] = SMTP_USERNAME
    msg['To'] = ADMIN_EMAIL

    msg.set_content(f"""\
A suspicious IP was detected by TrafficShield.

IP Address: {ip}
Anomaly Score: {score:.3f}

Please review this on your dashboard.

— TrafficShield
""")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f"📧 Email sent for IP {ip}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
