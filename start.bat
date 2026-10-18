@echo off
title CampusMind Platform Launcher
echo ======================================================================
echo                  Starting CampusMind Full-Stack Platform
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend API Server (FastAPI on http://127.0.0.1:8000)...
start "CampusMind Backend API" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Starting Frontend Web Client (Vite on http://localhost:5173)...
start "CampusMind Frontend Client" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [3/3] Initializing services and waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo Opening CampusMind in your browser...
start http://localhost:5173

echo.
echo ======================================================================
echo  CampusMind is now running!
echo.
echo  * Frontend Client: http://localhost:5173
echo  * Backend API:     http://127.0.0.1:8000
echo  * Swagger Docs:    http://127.0.0.1:8000/docs
echo.
echo  Demo Accounts (Clickable in UI):
echo  - Student:        23SS1A0535  /  Password123!
echo  - Faculty:        faculty1    /  Password123!
echo  - Administrator:  admin1      /  AdminPassword123!
echo  - Principal:      principal   /  Principal123!
echo ======================================================================
echo.
echo You can close this launcher window. The servers will continue running
echo in their respective windows. To stop them, simply close those windows.
pause
