@echo off
REM ============================================
REM @file dev-menu.bat
REM @description
REM JSOPCUA 개발 환경 통합 메뉴 스크립트
REM
REM 이 스크립트는 개발자가 프로젝트의 다양한 구성요소를
REM 쉽게 실행하고 관리할 수 있도록 통합 메뉴를 제공합니다.
REM
REM 초보자 가이드:
REM 1. **가상환경 설정**: Python 의존성 격리를 위해 필요
REM    - 최초 1회만 설정하면 됨
REM 2. **Backend**: FastAPI 기반 API 서버 (포트 8000)
REM 3. **Admin**: 관리자 패널 Next.js 앱 (포트 3000)
REM 4. **Monitor**: 모니터링 대시보드 Next.js 앱 (포트 3001)
REM
REM @example
REM dev-menu.bat 실행 후 숫자 선택
REM ============================================

chcp 65001 > nul
setlocal EnableDelayedExpansion

:MENU
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            JSOPCUA 개발 환경 통합 메뉴                       ║
echo ║                                                              ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  [Python 환경 설정]                                          ║
echo ║    1. 가상환경 생성 (최초 1회)                               ║
echo ║    2. 의존성 설치 (pip install)                              ║
echo ║    3. 가상환경 활성화 (CMD 창 유지)                          ║
echo ║                                                              ║
echo ║  [Backend 서버]                                              ║
echo ║    4. Backend 서버 실행 (FastAPI - 포트 8000)                ║
echo ║    5. Backend 테스트 실행                                    ║
echo ║                                                              ║
echo ║  [Frontend 앱]                                               ║
echo ║    6. Admin 앱 실행 (Next.js - 포트 3000)                    ║
echo ║    7. Monitor 앱 실행 (Next.js - 포트 3001)                  ║
echo ║    8. 모든 Frontend 앱 동시 실행                             ║
echo ║                                                              ║
echo ║  [전체 실행]                                                 ║
echo ║    9. 전체 개발 환경 실행 (Backend + Admin + Monitor)        ║
echo ║                                                              ║
echo ║  [Node.js 환경]                                              ║
echo ║   10. npm 의존성 설치                                        ║
echo ║   11. 프로젝트 빌드 (Production)                             ║
echo ║                                                              ║
echo ║  [유틸리티]                                                  ║
echo ║   12. 포트 8000 강제 종료 (Backend)                          ║
echo ║   13. 포트 3000 강제 종료 (Admin)                            ║
echo ║   14. 포트 3001 강제 종료 (Monitor)                          ║
echo ║   15. 모든 개발 서버 종료                                    ║
echo ║                                                              ║
echo ║    0. 종료                                                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
set /p choice="선택하세요 (0-15): "

if "%choice%"=="1" goto CREATE_VENV
if "%choice%"=="2" goto INSTALL_DEPS
if "%choice%"=="3" goto ACTIVATE_VENV
if "%choice%"=="4" goto RUN_BACKEND
if "%choice%"=="5" goto RUN_TESTS
if "%choice%"=="6" goto RUN_ADMIN
if "%choice%"=="7" goto RUN_MONITOR
if "%choice%"=="8" goto RUN_ALL_FRONTEND
if "%choice%"=="9" goto RUN_ALL
if "%choice%"=="10" goto NPM_INSTALL
if "%choice%"=="11" goto NPM_BUILD
if "%choice%"=="12" goto KILL_8000
if "%choice%"=="13" goto KILL_3000
if "%choice%"=="14" goto KILL_3001
if "%choice%"=="15" goto KILL_ALL
if "%choice%"=="0" goto EXIT

echo.
echo [오류] 잘못된 선택입니다. 다시 선택해주세요.
timeout /t 2 > nul
goto MENU

REM ============================================
REM Python 가상환경 생성
REM ============================================
:CREATE_VENV
cls
echo.
echo ========================================
echo  Python 가상환경 생성
echo ========================================
echo.

cd /d "%~dp0backend"

if exist ".venv" (
    echo [경고] 가상환경이 이미 존재합니다: backend\.venv
    echo.
    set /p overwrite="덮어쓰시겠습니까? (y/n): "
    if /i "!overwrite!"=="y" (
        echo [정보] 기존 가상환경 삭제 중...
        rmdir /s /q .venv
    ) else (
        echo [취소] 가상환경 생성이 취소되었습니다.
        goto PAUSE_MENU
    )
)

echo [1/2] 가상환경 생성 중...
python -m venv .venv

if errorlevel 1 (
    echo [오류] 가상환경 생성 실패
    echo Python이 설치되어 있는지 확인해주세요.
    goto PAUSE_MENU
)

echo [완료] 가상환경이 생성되었습니다!
echo.
echo [다음 단계] 의존성을 설치하려면 메뉴에서 2번을 선택하세요.
goto PAUSE_MENU

REM ============================================
REM Python 의존성 설치
REM ============================================
:INSTALL_DEPS
cls
echo.
echo ========================================
echo  Python 의존성 설치
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 1번으로 가상환경을 생성해주세요.
    goto PAUSE_MENU
)

echo [1/3] 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo [2/3] pip 업그레이드 중...
python -m pip install --upgrade pip

echo [3/3] 의존성 설치 중...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [오류] 의존성 설치 중 오류가 발생했습니다.
    goto PAUSE_MENU
)

echo.
echo [완료] 모든 Python 의존성이 설치되었습니다!
goto PAUSE_MENU

REM ============================================
REM 가상환경 활성화 (CMD 창 유지)
REM ============================================
:ACTIVATE_VENV
cls
echo.
echo ========================================
echo  Python 가상환경 활성화
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 1번으로 가상환경을 생성해주세요.
    goto PAUSE_MENU
)

echo [정보] 가상환경이 활성화된 새 CMD 창을 엽니다.
echo.
start cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo. && echo [활성화됨] Python 가상환경이 활성화되었습니다. && echo 작업 디렉토리: %~dp0backend && echo."
goto MENU

REM ============================================
REM Backend 서버 실행
REM ============================================
:RUN_BACKEND
cls
echo.
echo ========================================
echo  Backend 서버 실행 (FastAPI)
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 1, 2번으로 환경을 설정해주세요.
    goto PAUSE_MENU
)

echo [정보] Backend 서버를 새 창에서 실행합니다.
echo        URL: http://localhost:8000
echo        API Docs: http://localhost:8000/docs
echo.
start "JSOPCUA Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo. && echo [Backend] FastAPI 서버 시작... && echo. && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
goto MENU

REM ============================================
REM Backend 테스트 실행
REM ============================================
:RUN_TESTS
cls
echo.
echo ========================================
echo  Backend 테스트 실행
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    goto PAUSE_MENU
)

echo [정보] pytest 실행 중...
echo.
call .venv\Scripts\activate.bat
pytest tests\ -v

goto PAUSE_MENU

REM ============================================
REM Admin 앱 실행
REM ============================================
:RUN_ADMIN
cls
echo.
echo ========================================
echo  Admin 앱 실행 (Next.js)
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    goto PAUSE_MENU
)

echo [정보] Admin 앱을 새 창에서 실행합니다.
echo        URL: http://localhost:3000
echo.
start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && echo. && echo [Admin] Next.js 앱 시작... && echo. && npm run dev:admin"
goto MENU

REM ============================================
REM Monitor 앱 실행
REM ============================================
:RUN_MONITOR
cls
echo.
echo ========================================
echo  Monitor 앱 실행 (Next.js)
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    goto PAUSE_MENU
)

echo [정보] Monitor 앱을 새 창에서 실행합니다.
echo        URL: http://localhost:3001
echo.
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && echo. && echo [Monitor] Next.js 앱 시작... && echo. && npm run dev:monitor"
goto MENU

REM ============================================
REM 모든 Frontend 앱 실행
REM ============================================
:RUN_ALL_FRONTEND
cls
echo.
echo ========================================
echo  모든 Frontend 앱 실행
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    goto PAUSE_MENU
)

echo [정보] Admin과 Monitor를 각각 새 창에서 실행합니다.
echo        Admin URL: http://localhost:3000
echo        Monitor URL: http://localhost:3001
echo.

start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && echo. && echo [Admin] Next.js 앱 시작... && echo. && npm run dev:admin"
timeout /t 2 > nul
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && echo. && echo [Monitor] Next.js 앱 시작... && echo. && npm run dev:monitor"
goto MENU

REM ============================================
REM 전체 개발 환경 실행
REM ============================================
:RUN_ALL
cls
echo.
echo ========================================
echo  전체 개발 환경 실행
echo ========================================
echo.

echo [1/3] Backend 서버 시작...
cd /d "%~dp0backend"
if exist ".venv\Scripts\activate.bat" (
    start "JSOPCUA Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo. && echo [Backend] FastAPI 서버 시작... && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo [경고] Backend 가상환경이 없습니다. Backend는 건너뜁니다.
)

timeout /t 3 > nul

echo [2/3] Admin 앱 시작...
cd /d "%~dp0"
if exist "node_modules" (
    start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && echo. && echo [Admin] Next.js 앱 시작... && npm run dev:admin"
) else (
    echo [경고] node_modules가 없습니다. Frontend는 건너뜁니다.
    goto PAUSE_MENU
)

timeout /t 2 > nul

echo [3/3] Monitor 앱 시작...
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && echo. && echo [Monitor] Next.js 앱 시작... && npm run dev:monitor"

echo.
echo ========================================
echo  전체 개발 환경이 시작되었습니다!
echo ========================================
echo.
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Admin:    http://localhost:3000
echo  Monitor:  http://localhost:3001
echo.
goto PAUSE_MENU

REM ============================================
REM npm 의존성 설치
REM ============================================
:NPM_INSTALL
cls
echo.
echo ========================================
echo  npm 의존성 설치
echo ========================================
echo.

cd /d "%~dp0"

echo [정보] npm install 실행 중...
echo       (시간이 다소 소요될 수 있습니다)
echo.
npm install

if errorlevel 1 (
    echo.
    echo [오류] npm install 중 오류가 발생했습니다.
    goto PAUSE_MENU
)

echo.
echo [완료] npm 의존성이 설치되었습니다!
goto PAUSE_MENU

REM ============================================
REM 프로젝트 빌드
REM ============================================
:NPM_BUILD
cls
echo.
echo ========================================
echo  프로젝트 빌드 (Production)
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    goto PAUSE_MENU
)

echo [정보] 프로젝트 빌드 중...
echo.
npm run build

if errorlevel 1 (
    echo.
    echo [오류] 빌드 중 오류가 발생했습니다.
    goto PAUSE_MENU
)

echo.
echo [완료] 빌드가 완료되었습니다!
goto PAUSE_MENU

REM ============================================
REM 포트 8000 강제 종료
REM ============================================
:KILL_8000
cls
echo.
echo ========================================
echo  포트 8000 강제 종료 (Backend)
echo ========================================
echo.

echo [정보] 포트 8000을 사용 중인 프로세스 검색 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [찾음] PID: %%a
    echo [종료] 프로세스 종료 중...
    taskkill /F /PID %%a
    echo [완료] 프로세스가 종료되었습니다.
    goto PAUSE_MENU
)
echo [정보] 포트 8000을 사용 중인 프로세스가 없습니다.
goto PAUSE_MENU

REM ============================================
REM 포트 3000 강제 종료
REM ============================================
:KILL_3000
cls
echo.
echo ========================================
echo  포트 3000 강제 종료 (Admin)
echo ========================================
echo.

echo [정보] 포트 3000을 사용 중인 프로세스 검색 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo [찾음] PID: %%a
    echo [종료] 프로세스 종료 중...
    taskkill /F /PID %%a
    echo [완료] 프로세스가 종료되었습니다.
    goto PAUSE_MENU
)
echo [정보] 포트 3000을 사용 중인 프로세스가 없습니다.
goto PAUSE_MENU

REM ============================================
REM 포트 3001 강제 종료
REM ============================================
:KILL_3001
cls
echo.
echo ========================================
echo  포트 3001 강제 종료 (Monitor)
echo ========================================
echo.

echo [정보] 포트 3001을 사용 중인 프로세스 검색 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do (
    echo [찾음] PID: %%a
    echo [종료] 프로세스 종료 중...
    taskkill /F /PID %%a
    echo [완료] 프로세스가 종료되었습니다.
    goto PAUSE_MENU
)
echo [정보] 포트 3001을 사용 중인 프로세스가 없습니다.
goto PAUSE_MENU

REM ============================================
REM 모든 개발 서버 종료
REM ============================================
:KILL_ALL
cls
echo.
echo ========================================
echo  모든 개발 서버 종료
echo ========================================
echo.

echo [1/3] 포트 8000 (Backend) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 8000 정리됨

echo [2/3] 포트 3000 (Admin) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 3000 정리됨

echo [3/3] 포트 3001 (Monitor) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 3001 정리됨

echo.
echo [완료] 모든 개발 서버가 종료되었습니다.
goto PAUSE_MENU

REM ============================================
REM 공통 일시 정지 후 메뉴 복귀
REM ============================================
:PAUSE_MENU
echo.
pause
goto MENU

REM ============================================
REM 종료
REM ============================================
:EXIT
echo.
echo 개발 메뉴를 종료합니다. 안녕히 가세요!
echo.
endlocal
exit /b 0
