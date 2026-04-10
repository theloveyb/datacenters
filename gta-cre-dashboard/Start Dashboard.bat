@echo off
title GTA CRE Dashboard

echo.
echo ==================================================
echo   GTA CRE Dashboard
echo ==================================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   Python is not installed on this computer.
    echo.
    echo   To install it:
    echo     1. Go to https://www.python.org/downloads/
    echo     2. Click the big yellow "Download Python" button
    echo     3. Run the installer
    echo     4. IMPORTANT: Check the box that says "Add Python to PATH"
    echo     5. Click "Install Now"
    echo     6. Once done, double-click this file again
    echo.
    pause
    exit /b 1
)

:: Check for Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo   Node.js is not installed on this computer.
    echo.
    echo   To install it:
    echo     1. Go to https://nodejs.org
    echo     2. Click the big green "LTS" download button
    echo     3. Run the installer and click Next through it
    echo     4. Once done, double-click this file again
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"
python start.py

if %errorlevel% neq 0 (
    echo.
    echo Something went wrong. Please ask for help.
    echo.
    pause
)
