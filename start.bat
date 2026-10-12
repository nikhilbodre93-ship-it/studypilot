@echo off
title StudyPilot Launcher
echo ======================================================================
echo                      StudyPilot AI Learning Platform
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend Server (FastAPI on port 8000)...
start "StudyPilot Backend" cmd /k "cd /d "%~dp0backend" && if exist .venv\Scripts\python.exe (.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000) else (echo Creating virtualenv... && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && .venv\Scripts\python -m uvicorn app.main:app --reload --port 8000)"

echo [2/3] Starting Frontend Dev Server (Vite on port 5173)...
start "StudyPilot Frontend" cmd /k "cd /d "%~dp0frontend" && set PATH=C:\Program Files\nodejs;%PATH% && if not exist node_modules (echo Installing frontend packages... && npm install) && npm run dev"

echo [3/3] Opening StudyPilot in your browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ======================================================================
echo StudyPilot is running!
echo - Web App:     http://localhost:5173
echo - Backend API: http://localhost:8000
echo - API Docs:    http://localhost:8000/docs
echo.
echo Demo Accounts:
echo - Email:    demo@studypilot.io
echo - Password: StudyPilot2026!
echo.
echo (Keep the backend and frontend terminal windows open while using the app)
echo ======================================================================
pause
