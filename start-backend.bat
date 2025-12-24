@echo off
REM ============================================
REM JSOPCUA Backend Startup Script
REM ============================================
REM This script activates the virtual environment
REM and starts the FastAPI backend server
REM ============================================

echo.
echo ========================================
echo  JSOPCUA Backend Server Startup
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at backend\.venv
    echo Please create it first with: python -m venv .venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo Copying from .env.example...
    copy .env.example .env
    echo [INFO] Please edit backend\.env with your configuration
    echo.
)

REM Check for essential environment variables in .env
findstr /C:"ORACLE_USERNAME=" ".env" > nul
if errorlevel 1 (
    echo [ERROR] Essential environment variable ORACLE_USERNAME is not set in .env
    pause
    exit /b 1
)

REM Check if database exists
if not exist "config\scada.db" (
    echo [WARNING] Database not found at config\scada.db
    echo [INFO] You may need to run: python src/scripts/init_database.py
    echo.
)

REM Start FastAPI server
echo [2/3] Starting FastAPI server...
echo.
echo ========================================
echo  Server starting on http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start uvicorn in development mode with auto-reload
uvicorn src.api.main:app --reload

REM If python command fails, show error
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start backend server
    echo Check the error messages above
    pause
    exit /b 1
)

REM This line runs when server is stopped
echo.
echo [3/3] Server stopped
pause
