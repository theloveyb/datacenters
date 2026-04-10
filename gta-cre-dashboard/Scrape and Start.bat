@echo off
title GTA CRE Dashboard - Scraping Listings

echo.
echo ==================================================
echo   GTA CRE Dashboard — Fetching Fresh Listings
echo   This will take a few minutes.
echo ==================================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   Python is not installed. Double-click "Start Dashboard" first
    echo   for installation instructions.
    pause
    exit /b 1
)

:: Check for Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo   Node.js is not installed. Double-click "Start Dashboard" first
    echo   for installation instructions.
    pause
    exit /b 1
)

cd /d "%~dp0"
python start.py --scrape

if %errorlevel% neq 0 (
    echo.
    echo Something went wrong. Please ask for help.
    echo.
    pause
)
