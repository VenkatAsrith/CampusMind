@echo off
title CampusMind Test Suite Runner
echo ======================================================================
echo                  Running CampusMind Automated Tests
echo ======================================================================
echo.

cd /d "%~dp0backend"
echo [1/2] Running Backend Pytest Suite (45 tests)...
call .venv\Scripts\python -m pytest -v tests

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Backend tests failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
cd /d "%~dp0frontend"
echo [2/2] Running Frontend Vitest Suite...
call npm test

echo.
echo ======================================================================
echo  All Tests Passed Successfully!
echo ======================================================================
echo.
pause
