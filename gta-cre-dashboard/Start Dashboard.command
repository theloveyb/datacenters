#!/bin/bash
# Double-click this file on Mac to start the dashboard.

clear
echo ""
echo "=================================================="
echo "  GTA CRE Dashboard"
echo "=================================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "  Python is not installed on this computer."
    echo ""
    echo "  To install it:"
    echo "    1. Go to https://www.python.org/downloads/"
    echo "    2. Click the big yellow 'Download Python' button"
    echo "    3. Run the installer"
    echo "    4. Once done, double-click this file again"
    echo ""
    read -p "  Press Enter to close..."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "  Node.js is not installed on this computer."
    echo ""
    echo "  To install it:"
    echo "    1. Go to https://nodejs.org"
    echo "    2. Click the big green 'LTS' download button"
    echo "    3. Run the installer"
    echo "    4. Once done, double-click this file again"
    echo ""
    read -p "  Press Enter to close..."
    exit 1
fi

cd "$(dirname "$0")"
python3 start.py

if [ $? -ne 0 ]; then
    echo ""
    echo "  Something went wrong. Please ask for help."
    echo ""
    read -p "  Press Enter to close..."
fi
