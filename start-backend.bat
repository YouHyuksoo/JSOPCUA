@echo off
chcp 65001 > nul

echo.
echo ========================================
echo  JSOPCUA Backend Server Startup
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo [1/2] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

if not exist "src\api\main.py" (
    echo [ERROR] src\api\main.py not found
    pause
    exit /b 1
)

echo [2/2] Starting FastAPI server...
echo.
echo ========================================
echo  URL: http://localhost:8000
echo  API: http://localhost:8000/docs
echo  Press Ctrl+C to stop
echo ========================================
echo.

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [STOPPED] Server stopped
pause
