# 🛡️ TrafficShield

**AI-Powered Network Traffic Anomaly Detection System**

TrafficShield is a real-time network traffic monitoring and anomaly detection tool that uses **Machine Learning (Isolation Forest)** to identify suspicious IP addresses from web server access logs. It features a live web dashboard built with FastAPI, automated email alerting, and IP blacklist/whitelist management.

---

## 📌 Features

- **Log Parsing** — Parses Apache/Nginx-style access logs and groups requests by IP address
- **Feature Engineering** — Extracts behavioral features per IP: request count, timing intervals, HTTP method ratios, status code distribution, session count, burst rate, and more
- **ML-Based Anomaly Detection** — Uses scikit-learn's `IsolationForest` to score and flag suspicious IPs
- **Real-Time Monitoring** — Continuously fetches remote logs, analyzes traffic, and stores alerts in a SQLite database
- **Web Dashboard** — A FastAPI-powered dashboard to view alerts, block/whitelist IPs, upload logs, view raw logs, and export alerts as CSV
- **Email Alerts** — Sends SMTP email notifications when high-severity anomalies are detected
- **IP Management** — Block or whitelist IPs directly from the dashboard; filtered IPs are excluded from future analysis
- **Auto-Refresh Dashboard** — The dashboard auto-refreshes every 10 seconds for live updates
- **Dynamic Chart** — Real-time Chart.js bar chart showing anomaly scores from the database

---

## 🏗️ Project Structure

```
trafficshield/
├── api/                        # Web API & Dashboard
│   ├── __init__.py
│   ├── main.py                 # FastAPI app — routes, middleware, dashboard
│   ├── static/
│   │   ├── script.js           # Chart.js — fetches real data from /api/alerts-data
│   │   └── style.css           # Dark-themed dashboard styling
│   └── templates/
│       └── dashboard.html      # Jinja2 dashboard template
│
├── app/                        # Core Application Logic
│   ├── __init__.py
│   ├── config.py               # Configuration — thresholds, email settings (via .env)
│   ├── detector.py             # TrafficDetector class (Isolation Forest ML model)
│   ├── features.py             # Feature extraction from parsed log data
│   ├── parser.py               # Regex-based access log parser
│   ├── test_parser.py          # Test script for log parser
│   └── test_features.py        # Test script for feature extraction
│
├── core/                       # Backend Services
│   ├── __init__.py
│   ├── monitor.py              # Main monitoring loop — fetch, parse, detect, alert
│   └── emailer.py              # SMTP email alert sender
│
├── data/                       # Runtime Data (gitignored except txt files)
│   ├── blacklist.txt           # Blocked IP addresses
│   └── whitelist.txt           # Whitelisted IP addresses
│
├── .env.example                # Template for environment variable setup
├── .gitignore                  # Git ignore rules
├── c_db.py                     # Script to create DB and seed sample alert data
├── test_insert.py              # Script to insert a test alert into the database
├── main.py                     # CLI entry point (serve / monitor / seed)
├── requirement.txt             # Python dependencies
└── README.md                   # This file
```

---

## ⚙️ How It Works

### 1. Log Parsing (`app/parser.py`)
Reads access log files line-by-line using a regex pattern to extract:
- **IP Address**, **Timestamp**, **HTTP Method**, **Request Path**, **Status Code**

Groups all requests by source IP.

### 2. Feature Extraction (`app/features.py`)
For each IP, computes behavioral features:

| Feature | Description |
|---|---|
| `request_count` | Total number of requests |
| `mean_interval` | Average time between consecutive requests |
| `std_interval` | Standard deviation of request intervals |
| `GET_ratio` | Proportion of GET requests |
| `POST_ratio` | Proportion of POST requests |
| `status_200_ratio` | Proportion of 200 OK responses |
| `status_404_ratio` | Proportion of 404 Not Found responses |
| `status_500_ratio` | Proportion of 500 Server Error responses |
| `unique_paths` | Number of unique URL paths accessed |
| `session_count` | Number of distinct browsing sessions (300s timeout) |
| `burst_rate` | Fraction of requests occurring within 1 second of each other |

### 3. Anomaly Detection (`app/detector.py`)
Uses **Isolation Forest** (an unsupervised ML algorithm) to:
- Train on the extracted feature matrix
- Compute anomaly scores per IP
- Flag IPs with `label == -1` and `score > threshold` as suspicious

### 4. Monitoring Loop (`core/monitor.py`)
Runs continuously in a loop:
1. **Loads** whitelist/blacklist to filter known IPs
2. **Fetches** access logs from a configurable remote URL
3. **Parses** the log file
4. **Extracts** features from IP traffic
5. **Detects** anomalies using the ML model
6. **Saves** new alerts to the SQLite database
7. **Sends email** for high-severity detections
8. Repeats every 10 seconds

### 5. Web Dashboard (`api/main.py`)
Provides a FastAPI web interface with:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard — displays all alerts with actions |
| `/api/alerts-data` | GET | JSON API — alert data for Chart.js |
| `/block` | POST | Add an IP to the blacklist |
| `/whitelist` | POST | Add an IP to the whitelist |
| `/upload-log` | POST | Upload a custom access log file |
| `/view-log` | GET | View raw contents of the access log |
| `/export-alerts` | GET | Download all alerts as a CSV file |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trafficshield.git
cd trafficshield

# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirement.txt
```

### Configuration

```bash
# Copy the example .env file
cp .env.example .env      # Linux/macOS
copy .env.example .env     # Windows

# Edit .env with your settings:
#   SMTP credentials (for email alerts)
#   REMOTE_LOG_URL (URL to fetch access logs from)
```

### Seed the Database (optional)

```bash
python main.py seed
```

Creates `data/alerts.db` with sample alert data for testing the dashboard.

### Run the Dashboard

```bash
python main.py serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Run the Traffic Monitor

```bash
python main.py monitor
```

Starts the real-time monitoring loop that fetches logs, runs anomaly detection, and saves alerts.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework for the dashboard API |
| `uvicorn` | ASGI server to run FastAPI |
| `jinja2` | HTML templating for the dashboard |
| `aiofiles` | Async file serving for static files |
| `python-multipart` | Form/file upload support |
| `numpy` | Numerical computations |
| `pandas` | Data manipulation and feature DataFrames |
| `scikit-learn` | Isolation Forest ML model |
| `requests` | HTTP client for fetching remote logs |
| `python-dotenv` | Load environment variables from `.env` |

---

## 🔧 Configuration

All sensitive configuration is managed via the `.env` file (see `.env.example`):

```env
# SMTP Email Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAIL=your_email@gmail.com

# Remote Log Source
REMOTE_LOG_URL=https://your-server.com/logs/access.log
```

Detection thresholds in `app/config.py`:

```python
SESSION_TIMEOUT = 300           # Session gap threshold (seconds)
MODEL_CONTAMINATION = 0.03      # Isolation Forest contamination rate
ALERT_THRESHOLD = 0.5           # Minimum anomaly score to trigger alert
EMAIL_ALERT_THRESHOLD = 0.98    # Score threshold for email notifications
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI |
| **ML Engine** | scikit-learn (Isolation Forest) |
| **Database** | SQLite |
| **Frontend** | HTML, CSS, Jinja2, Chart.js |
| **Monitoring** | Python (requests + polling loop) |
| **Alerting** | SMTP (email via smtplib) |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
