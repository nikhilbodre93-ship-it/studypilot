@echo off
title StudyPilot - Live Public Tunnel Launcher
echo ======================================================================
echo             StudyPilot - Live Public Internet Deployment
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Frontend Production Build...
if not exist "frontend\dist\index.html" (
    echo Building frontend production assets...
    cd /d "%~dp0frontend"
    set PATH=C:\Program Files\nodejs;%PATH%
    call npm run build
    cd /d "%~dp0"
)

echo [2/3] Starting StudyPilot Server (FastAPI + React UI on port 8000)...
start "StudyPilot Server" cmd /k "cd /d "%~dp0backend" && if exist .venv\Scripts\python.exe (.venv\Scripts\python run.py) else (echo Creating virtualenv... && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && .venv\Scripts\python run.py)"

echo Waiting 5 seconds for the server to initialize...
timeout /t 5 >nul

echo.
echo [3/3] Launching Cloudflare Public Internet Tunnel...
echo ======================================================================
echo Look for your public URL below (https://*.trycloudflare.com):
echo ======================================================================
echo.
cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
