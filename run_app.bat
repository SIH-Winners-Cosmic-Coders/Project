@echo off
@echo off
title Agri-Care Digital Twin Launcher
:: 0A makes the text Bright Green on a Black background (Classic Hacker/Matrix look)
:: Change to 0B for Aqua, 0E for Light Yellow, or 0F for Bright White
color 0A

echo =================================================================
echo     ___               _       ____               
echo    /   ^|  ____ ______(_)     / __ \____ _________
echo   / /^| ^| / __ `/ ___/ /_____/ / / / __ `/ ___/ _ \
echo  / ___ ^|/ /_/ / /  / /_____/ /_/ / /_/ / /  /  __/
echo /_/  ^|_^|\__, /_/  /_/      \____/\__,_/_/   \___/ 
echo        /____/                                    
echo =================================================================
echo Welcome to the Agri-Care System. Initializing...
echo.

echo Step 1: Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b
)

echo Step 2: Installing dependencies...
pip install -r requirements.txt

echo Step 3: Starting server...
start "Server" cmd /k "python server.py"

echo Step 4: Opening browser...
timeout /t 3
start http://127.0.0.1:8000

echo.
echo Setup complete! The server should be opening in a new window.
pause