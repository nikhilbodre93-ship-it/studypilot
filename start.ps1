# StudyPilot PowerShell Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "                     StudyPilot AI Learning Platform" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend
Write-Host "`n[1/3] Starting Backend Server (FastAPI on port 8000)..." -ForegroundColor Green
$backendCmd = "cd `"$scriptDir\backend`"; if (Test-Path '.\.venv\Scripts\python.exe') { .\.venv\Scripts\python run.py } else { python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt; .\.venv\Scripts\python run.py }"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# 2. Start Frontend
Write-Host "[2/3] Starting Frontend Dev Server (Vite on port 5173)..." -ForegroundColor Green
$frontendCmd = "`$env:PATH = 'C:\Program Files\nodejs;' + `$env:PATH; cd `"$scriptDir\frontend`"; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

# 3. Open Browser
Write-Host "[3/3] Opening StudyPilot in your default browser..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "StudyPilot is running!" -ForegroundColor Yellow
Write-Host "- Web App:     http://localhost:5173"
Write-Host "- Backend API: http://localhost:8000"
Write-Host "- API Docs:    http://localhost:8000/docs"
Write-Host "`nDemo Credentials:" -ForegroundColor Yellow
Write-Host "- Email:    demo@studypilot.io"
Write-Host "- Password: StudyPilot2026!"
Write-Host "======================================================================`n" -ForegroundColor Cyan
