#!/usr/bin/env python3
"""One-command launcher for the GTA CRE Dashboard.

Double-click this file, or run:
    python start.py

That's it. Everything else is handled automatically.
"""

import argparse
import os
import shutil
import subprocess
import sys
import threading
import webbrowser

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


def log(msg):
    print(f"  {msg}")


def run(cmd, cwd=None, check=True):
    """Run a shell command and stream output."""
    return subprocess.run(
        cmd, shell=True, cwd=cwd or PROJECT_DIR, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def check_prerequisites():
    """Check that Python and Node.js are available, and guide if not."""
    # Python is obviously here since we're running
    log("Python found: " + sys.executable)

    # Check for Node.js / npm
    if not shutil.which("npm"):
        print("\n" + "=" * 50)
        print("  Node.js is required but not installed.")
        print()
        print("  Please install it from: https://nodejs.org")
        print("  (Download the LTS version, run the installer,")
        print("   then come back and run this script again.)")
        print("=" * 50)
        input("\nPress Enter to exit...")
        sys.exit(1)

    log("Node.js found: " + (shutil.which("node") or "npm available"))


def install_python_deps():
    """Install Python packages automatically."""
    needs_install = False
    for pkg in ["fastapi", "uvicorn", "requests", "bs4", "lxml"]:
        try:
            __import__(pkg)
        except ImportError:
            needs_install = True
            break

    if needs_install:
        log("Installing Python packages (one-time)...")
        result = run(f"{sys.executable} -m pip install -r requirements.txt")
        if result.returncode != 0:
            # Try with --user flag (works on systems where global install is blocked)
            log("Retrying with --user flag...")
            result = run(f"{sys.executable} -m pip install --user -r requirements.txt")
        if result.returncode != 0:
            print(result.stdout)
            print("Failed to install Python packages.")
            print("Please open Terminal and run:")
            print(f"  pip3 install -r {os.path.join(PROJECT_DIR, 'requirements.txt')}")
            input("\nPress Enter to exit...")
            sys.exit(1)
        log("Python packages installed.")
    else:
        log("Python packages already installed.")


def build_frontend():
    """Install npm packages and build the React dashboard."""
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if not os.path.isdir(node_modules):
        log("Installing frontend packages (one-time, may take a minute)...")
        result = run("npm install", cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print(result.stdout)
            print("Failed to install frontend packages.")
            input("\nPress Enter to exit...")
            sys.exit(1)

    if not os.path.isdir(DIST_DIR) or not os.path.isfile(os.path.join(DIST_DIR, "index.html")):
        log("Building dashboard...")
        result = run("npm run build", cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print(result.stdout)
            print("Failed to build frontend.")
            input("\nPress Enter to exit...")
            sys.exit(1)
        log("Dashboard built.")
    else:
        log("Dashboard already built.")


def setup_database():
    """Create the database and seed brokerages."""
    sys.path.insert(0, PROJECT_DIR)
    from backend.database import init_db, get_connection
    init_db()

    # Check if already seeded
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as c FROM brokers").fetchone()["c"]
    conn.close()

    if count == 0:
        log("Setting up database with brokerage list...")
        from seed_brokerages import seed
        seed()
    else:
        log(f"Database ready ({count} brokers on file).")


def run_scrapers():
    """Run all scrapers to populate the database."""
    log("Scraping listings from all brokerages...")
    log("(This may take a few minutes — fetching from 12 websites)")
    run(f"{sys.executable} run_scraper.py", check=False)


def start_server(port):
    """Start the web server and open the browser."""
    print()
    print("=" * 50)
    print()
    print(f"  Dashboard is live at:")
    print(f"  http://localhost:{port}")
    print()
    print(f"  Leave this window open.")
    print(f"  Close it or press Ctrl+C to stop.")
    print()
    print("=" * 50)
    print()

    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # Run uvicorn as a subprocess using the same Python that ran this script
    # This avoids import errors when packages were installed during this session
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", "0.0.0.0", "--port", str(port), "--log-level", "warning"],
            cwd=PROJECT_DIR,
        )
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


def main():
    parser = argparse.ArgumentParser(description="GTA CRE Dashboard")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--scrape", action="store_true", help="Fetch fresh listings before starting")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    os.chdir(PROJECT_DIR)

    print()
    print("=" * 50)
    print("  GTA CRE Dashboard")
    print("  Setting up (first run takes ~1 minute)...")
    print("=" * 50)
    print()

    check_prerequisites()
    install_python_deps()

    if not args.skip_build:
        build_frontend()

    setup_database()

    # Check if DB has any listings
    sys.path.insert(0, PROJECT_DIR)
    from backend.database import get_connection
    conn = get_connection()
    listing_count = conn.execute("SELECT COUNT(*) as c FROM listings").fetchone()["c"]
    conn.close()

    if listing_count == 0 and not args.scrape:
        print()
        print("-" * 50)
        print("  Your database is empty (no listings yet).")
        print("  To fetch listings, stop this and run:")
        print(f"    python start.py --scrape")
        print("  Or run the scraper separately anytime:")
        print(f"    python run_scraper.py")
        print("-" * 50)

    if args.scrape:
        run_scrapers()

    start_server(args.port)


if __name__ == "__main__":
    main()
