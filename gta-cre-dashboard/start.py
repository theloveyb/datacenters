#!/usr/bin/env python3
"""One-command launcher for the GTA CRE Dashboard.

Usage:
    python start.py              # Build frontend, seed DB, start server on port 8000
    python start.py --scrape     # Also run scrapers before starting
    python start.py --port 3000  # Use a different port

Opens http://localhost:8000 in your browser automatically.
"""

import argparse
import os
import subprocess
import sys
import webbrowser
import threading

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


def run(cmd, cwd=None, check=True):
    """Run a shell command and stream output."""
    print(f"\n>>> {cmd}")
    return subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR, check=check)


def check_python_deps():
    """Install Python dependencies if needed."""
    try:
        import fastapi
        import uvicorn
        import requests
        import bs4
    except ImportError:
        print("Installing Python dependencies...")
        run(f"{sys.executable} -m pip install -q -r requirements.txt")


def build_frontend():
    """Install npm deps and build the React frontend if not already built."""
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if not os.path.isdir(node_modules):
        print("Installing frontend dependencies...")
        run("npm install", cwd=FRONTEND_DIR)

    if not os.path.isdir(DIST_DIR) or not os.path.isfile(os.path.join(DIST_DIR, "index.html")):
        print("Building frontend...")
        run("npm run build", cwd=FRONTEND_DIR)
    else:
        print("Frontend already built. Delete frontend/dist to rebuild.")


def seed_database():
    """Initialize DB and seed brokerages."""
    print("Initializing database...")
    # Import here after deps are installed
    sys.path.insert(0, PROJECT_DIR)
    from backend.database import init_db
    init_db()

    from seed_brokerages import seed
    seed()


def run_scrapers():
    """Run the scraper orchestrator."""
    print("\nRunning scrapers (this may take a few minutes)...")
    run(f"{sys.executable} run_scraper.py")


def start_server(port):
    """Start the FastAPI server."""
    print(f"\n{'='*50}")
    print(f"  Dashboard ready at: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*50}\n")

    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    run(f"{sys.executable} -m uvicorn backend.main:app --host 0.0.0.0 --port {port}", check=False)


def main():
    parser = argparse.ArgumentParser(description="GTA CRE Dashboard Launcher")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--scrape", action="store_true", help="Run scrapers before starting")
    parser.add_argument("--skip-build", action="store_true", help="Skip frontend build")
    args = parser.parse_args()

    os.chdir(PROJECT_DIR)

    print("=" * 50)
    print("  GTA CRE Dashboard — Setup & Launch")
    print("=" * 50)

    check_python_deps()

    if not args.skip_build:
        build_frontend()

    seed_database()

    if args.scrape:
        run_scrapers()

    start_server(args.port)


if __name__ == "__main__":
    main()
