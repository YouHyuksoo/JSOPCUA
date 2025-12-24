@echo off
REM ============================================
REM @file start-backend.bat
REM @description
REM JSOPCUA Backend 간편 실행 스크립트
REM
REM 이 스크립트는 Python 가상환경을 활성화하고
REM FastAPI 백엔드 서버를 실행합니다.
REM
REM 초보자 가이드:
REM 1. 가상환경이 없으면 먼저 dev-menu.bat에서 6, 7번 실행
REM 2. 이 파일을 더블클릭하면 백엔드 서버 시작
REM ============================================

chcp 65001 > nul

echo.
echo ========================================
echo  JSOPCUA Backend Server Startup
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 없습니다: backend\.venv
    echo.
    echo 먼저 다음 명령어로 가상환경을 생성하세요:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    echo 또는 dev-menu.bat에서 6, 7번을 실행하세요.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/2] 가상환경 활성화 중...
call .venv\Scripts\activate.bat
echo [완료] 가상환경 활성화됨
echo.

REM Check if api/main.py exists
if not exist "src\api\main.py" (
    echo [오류] src\api\main.py 파일이 없습니다.
    echo.
    echo API 모듈이 아직 구현되지 않았습니다.
    echo 개발 브랜치를 확인하거나 API를 먼저 생성하세요.
    pause
    exit /b 1
)

REM Start FastAPI server
echo [2/2] FastAPI 서버 시작 중...
echo.
echo ========================================
echo  서버 주소: http://localhost:8000
echo  API 문서:  http://localhost:8000/docs
echo  종료하려면 Ctrl+C를 누르세요
echo ========================================
echo.

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [종료] 서버가 중지되었습니다.
pause
