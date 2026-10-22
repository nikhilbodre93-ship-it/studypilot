@echo off
title StudyPilot - Live Public Tunnel Launcher
echo ======================================================================
echo             StudyPilot - Live Public Internet Deployment
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend Server (FastAPI on port 8000)...
start "StudyPilot Backend" cmd /k "cd /d "%~dp0backend" && if exist .venv\Scripts\python.exe (.venv\Scripts\python run.py) else (echo Creating virtualenv... && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && .venv\Scripts\python run.py)"

echo [2/3] Starting Frontend Dev Server (Vite on port 5173)...
start "StudyPilot Frontend" cmd /k "cd /d "%~dp0frontend" && set PATH=C:\Program Files\nodejs;%PATH% && if not exist node_modules (echo Installing frontend packages... && npm install) && npm run dev"

echo [3/3] Launching Cloudflare Public Tunnel...
echo Waiting 4 seconds for servers to initialize...
timeout /t 4 >nul

echo.
echo ======================================================================
echo Look for your public URL below (https://*.trycloudflare.com):
echo ======================================================================
echo.
cloudflared.exe tunnel --url http://localhost:5173
pause
