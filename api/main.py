from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3
import os
import shutil
import csv
from io import StringIO

app = FastAPI(title="TrafficShield", description="AI-Powered Traffic Anomaly Detection")

# Mount static and templates
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")

# File paths
DB_PATH = "data/alerts.db"
LOG_PATH = "data/access.log"
WHITELIST = "data/whitelist.txt"
BLACKLIST = "data/blacklist.txt"

# Paths to skip in access log middleware (avoid polluting logs with static/internal requests)
SKIP_LOG_PATHS = {"/static", "/favicon.ico", "/api/alerts-data"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Render the main dashboard with all alerts."""
    if not os.path.exists(DB_PATH):
        return templates.TemplateResponse("dashboard.html", {"request": request, "alerts": []})

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT ip, anomaly_score, reason, timestamp FROM alerts ORDER BY timestamp DESC")
        alerts = cur.fetchall()
        print(f"📊 [Dashboard] Loaded {len(alerts)} alerts")
    except Exception as e:
        conn.close()
        return HTMLResponse(f"<h2>Error reading alerts: {e}</h2>", status_code=500)

    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "alerts": alerts})


@app.get("/api/alerts-data")
def alerts_data():
    """JSON API endpoint for chart data — returns latest alerts for Chart.js."""
    if not os.path.exists(DB_PATH):
        return JSONResponse({"labels": [], "scores": []})

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT ip, anomaly_score FROM alerts ORDER BY timestamp DESC LIMIT 10"
        )
        rows = cur.fetchall()
    except Exception:
        rows = []
    finally:
        conn.close()

    labels = [row[0] for row in rows]
    scores = [round(row[1], 3) for row in rows]

    return JSONResponse({"labels": labels, "scores": scores})


@app.post("/block")
def block_ip(ip: str = Form(...)):
    """Add an IP to the blacklist."""
    os.makedirs("data", exist_ok=True)
    # Avoid duplicate entries
    existing = set()
    if os.path.exists(BLACKLIST):
        with open(BLACKLIST, "r") as f:
            existing = set(line.strip() for line in f if line.strip())
    if ip not in existing:
        with open(BLACKLIST, "a") as f:
            f.write(ip + "\n")
    return RedirectResponse(url="/", status_code=303)


@app.post("/whitelist")
def whitelist_ip(ip: str = Form(...)):
    """Add an IP to the whitelist."""
    os.makedirs("data", exist_ok=True)
    # Avoid duplicate entries
    existing = set()
    if os.path.exists(WHITELIST):
        with open(WHITELIST, "r") as f:
            existing = set(line.strip() for line in f if line.strip())
    if ip not in existing:
        with open(WHITELIST, "a") as f:
            f.write(ip + "\n")
    return RedirectResponse(url="/", status_code=303)


@app.post("/upload-log")
def upload_log(file: UploadFile = File(...)):
    """Upload a custom access log file."""
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return RedirectResponse(url="/", status_code=303)


@app.get("/view-log")
def view_log():
    """View the raw access log contents."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            content = f.read()
        return HTMLResponse(f"<pre>{content}</pre>")
    return HTMLResponse("<h2>No log file uploaded or available.</h2>")


@app.get("/export-alerts")
def export_alerts():
    """Export all alerts as a downloadable CSV file."""
    if not os.path.exists(DB_PATH):
        return HTMLResponse("<h2>No alerts database found.</h2>", status_code=404)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ip, anomaly_score, reason, timestamp FROM alerts")
    rows = cur.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["IP", "Anomaly Score", "Reason", "Timestamp"])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=alerts.csv"
    })


@app.middleware("http")
async def log_ip_to_access_log(request: Request, call_next):
    """Log incoming requests to access.log, skipping static files and internal API calls."""
    path = request.url.path

    # Skip logging for static files and internal endpoints
    if any(path.startswith(skip) for skip in SKIP_LOG_PATHS):
        return await call_next(request)

    ip = request.headers.get("X-Forwarded-For") or request.client.host
    method = request.method
    now = datetime.now().strftime("[%d/%b/%Y:%H:%M:%S +0000]")
    log_line = f'{ip} - - {now} "{method} {path} HTTP/1.1" 200\n'

    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(log_line)

    return await call_next(request)
