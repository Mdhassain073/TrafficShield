# main.py — TrafficShield Entry Point
# Run the dashboard:   python main.py serve
# Run the monitor:     python main.py monitor

import sys
import os

# Fix Windows console encoding for emoji/unicode output
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("")
        print("Commands:")
        print("  serve     Start the web dashboard (FastAPI)")
        print("  monitor   Start the real-time traffic monitor")
        print("  seed      Seed the database with sample alerts")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "serve":
        import uvicorn
        print("Starting TrafficShield Dashboard...")
        uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

    elif command == "monitor":
        print("Starting TrafficShield Monitor...")
        from core.monitor import run_monitor
        run_monitor()

    elif command == "seed":
        print("Seeding database with sample alerts...")
        from c_db import seed_database
        seed_database()

    else:
        print(f"Unknown command: {command}")
        print("Available commands: serve, monitor, seed")
        sys.exit(1)


if __name__ == "__main__":
    main()
