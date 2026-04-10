#!/bin/bash
# Double-click this file on Mac to scrape fresh listings and start the dashboard.

clear
echo ""
echo "=================================================="
echo "  GTA CRE Dashboard — Fetching Fresh Listings"
echo "  This will take a few minutes."
echo "=================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "  Python is not installed. Double-click 'Start Dashboard' first"
    echo "  for installation instructions."
    read -p "  Press Enter to close..."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "  Node.js is not installed. Double-click 'Start Dashboard' first"
    echo "  for installation instructions."
    read -p "  Press Enter to close..."
    exit 1
fi

cd "$(dirname "$0")"
python3 start.py --scrape

if [ $? -ne 0 ]; then
    echo ""
    echo "  Something went wrong. Please ask for help."
    echo ""
    read -p "  Press Enter to close..."
fi
