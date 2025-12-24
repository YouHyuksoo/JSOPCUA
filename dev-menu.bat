@echo off
REM ============================================
REM @file dev-menu.bat
REM @description
REM JSOPCUA 개발 환경 통합 관리 도구
REM
REM 이 스크립트는 개발자가 프로젝트의 다양한 구성요소를
REM 쉽게 실행하고 관리할 수 있도록 통합 메뉴를 제공합니다.
REM
REM 초보자 가이드:
REM 1. **Git Clone**: 최초 소스 다운로드
REM 2. **Python 가상환경**: Backend 의존성 격리
REM 3. **PM2**: 프로덕션 서버 프로세스 관리
REM 4. **Backend**: FastAPI 기반 API 서버 (포트 8000)
REM 5. **Admin**: 관리자 패널 Next.js 앱 (포트 3000)
REM 6. **Monitor**: 모니터링 대시보드 Next.js 앱 (포트 3001)
REM
REM @example
REM dev-menu.bat 실행 후 숫자 선택
REM ============================================

chcp 65001 > nul
setlocal EnableDelayedExpansion

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║         JSOPCUA 통합 관리 도구 (v1.0)                              ║
echo ║                                                                    ║
echo ╠════════════════════════════════════════════════════════════════════╣
echo ║                                                                    ║
echo ║  [설치 및 초기 설정]                                               ║
echo ║    1. 프로젝트 소스 다운로드 (Git Clone)                           ║
echo ║    2. 전체 환경 초기 세팅 (Python + Node + PM2 + 시작프로그램)     ║
echo ║                                                                    ║
echo ║  [업데이트 및 배포]                                                ║
echo ║    3. 전체 업그레이드 (Git Pull + Install + Build + Restart)       ║
echo ║                                                                    ║
echo ║  [Git 작업]                                                        ║
echo ║    4. 소스 가져오기 (Git Pull)                                     ║
echo ║    5. 소스 강제 가져오기 (Force Pull - 로컬 변경 삭제)             ║
echo ║                                                                    ║
echo ║  [Python 환경 설정]                                                ║
echo ║    6. Python 가상환경 생성                                         ║
echo ║    7. Python 의존성 설치 (pip install)                             ║
echo ║    8. 가상환경 활성화 (새 CMD 창)                                  ║
echo ║                                                                    ║
echo ║  [Node.js 환경]                                                    ║
echo ║    9. npm 의존성 설치                                              ║
echo ║   10. 프로젝트 빌드 (Production)                                   ║
echo ║                                                                    ║
echo ║  [개발 모드 실행 - 각각 새 창에서 실행]                            ║
echo ║   11. Backend 개발 서버 (FastAPI - 포트 8000)                      ║
echo ║   12. Admin 개발 서버 (Next.js - 포트 3000)                        ║
echo ║   13. Monitor 개발 서버 (Next.js - 포트 3001)                      ║
echo ║   14. 전체 개발 환경 실행 (Backend + Admin + Monitor)              ║
echo ║                                                                    ║
echo ║  [PM2 프로덕션 서버 관리]                                          ║
echo ║   15. PM2 서버 시작                                                ║
echo ║   16. PM2 서버 재시작                                              ║
echo ║   17. PM2 서버 중지                                                ║
echo ║   18. PM2 서버 상태 확인                                           ║
echo ║   19. PM2 실시간 로그 보기                                         ║
echo ║   20. 윈도우 시작 프로그램 등록 (Auto Startup)                     ║
echo ║                                                                    ║
echo ║  [유틸리티]                                                        ║
echo ║   21. 개발 서버 포트 강제 종료 (8000, 3000, 3001)                  ║
echo ║   22. Backend 테스트 실행                                          ║
echo ║                                                                    ║
echo ║    0. 종료                                                         ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
set /p choice="원하는 작업의 번호를 입력하세요 (0-22): "

if "%choice%"=="1" goto CLONE
if "%choice%"=="2" goto INITIAL_SETUP
if "%choice%"=="3" goto FULL_UPGRADE
if "%choice%"=="4" goto GIT_PULL
if "%choice%"=="5" goto FORCE_GIT_PULL
if "%choice%"=="6" goto CREATE_VENV
if "%choice%"=="7" goto INSTALL_PY_DEPS
if "%choice%"=="8" goto ACTIVATE_VENV
if "%choice%"=="9" goto NPM_INSTALL
if "%choice%"=="10" goto NPM_BUILD
if "%choice%"=="11" goto DEV_BACKEND
if "%choice%"=="12" goto DEV_ADMIN
if "%choice%"=="13" goto DEV_MONITOR
if "%choice%"=="14" goto DEV_ALL
if "%choice%"=="15" goto PM2_START
if "%choice%"=="16" goto PM2_RESTART
if "%choice%"=="17" goto PM2_STOP
if "%choice%"=="18" goto PM2_STATUS
if "%choice%"=="19" goto PM2_LOGS
if "%choice%"=="20" goto AUTO_STARTUP
if "%choice%"=="21" goto KILL_ALL_PORTS
if "%choice%"=="22" goto RUN_TESTS
if "%choice%"=="0" goto END

echo.
echo [오류] 잘못된 선택입니다. 다시 선택해주세요.
timeout /t 2 > nul
goto MENU

REM ============================================
REM 프로젝트 소스 다운로드 (Git Clone)
REM ============================================
:CLONE
cls
echo ========================================================
echo        프로젝트 소스 다운로드 (Git Clone)
echo ========================================================
echo.
echo 깃허브에서 최신 소스 코드를 현재 폴더로 가져옵니다.
echo (주의: 이미 폴더가 있다면 에러가 날 수 있습니다)
echo.
git clone https://github.com/YouHyuksoo/JSOPCUA.git
echo.
echo [알림] 다운로드가 완료되었습니다!
echo [중요] 생성된 'JSOPCUA' 폴더 안으로 이 파일을 이동시킨 후
echo        다시 실행해서 '2. 전체 환경 초기 세팅'을 진행해주세요.
echo.
pause
goto MENU

REM ============================================
REM 전체 환경 초기 세팅
REM ============================================
:INITIAL_SETUP
cls
echo ========================================================
echo        전체 환경 초기 세팅 (Initial Setup)
echo ========================================================
echo.
echo [주의] 반드시 '관리자 권한'으로 실행해야 합니다!
echo.
echo 다음 작업을 순서대로 진행합니다:
echo   1. Python 가상환경 생성 및 의존성 설치
echo   2. Node.js 의존성 설치 및 빌드
echo   3. PM2 설치 및 윈도우 시작 프로그램 등록
echo   4. PM2로 서버 시작
echo.
pause

echo.
echo ========================================
echo [1/6] Python 가상환경 생성 중...
echo ========================================
cd /d "%~dp0backend"
if not exist ".venv" (
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [오류] Python 가상환경 생성 실패! Python이 설치되어 있는지 확인하세요.
        pause
        goto MENU
    )
    echo [성공] 가상환경 생성 완료
) else (
    echo [알림] 가상환경이 이미 존재합니다. 건너뜁니다.
)

echo.
echo ========================================
echo [2/6] Python 의존성 설치 중...
echo ========================================
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [오류] Python 의존성 설치 실패!
    pause
    goto MENU
)
echo [성공] Python 의존성 설치 완료

echo.
echo ========================================
echo [3/6] Node.js 의존성 설치 중...
echo ========================================
cd /d "%~dp0"
call npm install --legacy-peer-deps
IF %ERRORLEVEL% NEQ 0 (
    echo [오류] npm install 실패! Node.js가 설치되어 있는지 확인하세요.
    pause
    goto MENU
)
echo [성공] Node.js 의존성 설치 완료

echo.
echo ========================================
echo [4/6] 프로젝트 빌드 중...
echo ========================================
call npm run build
IF %ERRORLEVEL% NEQ 0 (
    echo [경고] 빌드 중 일부 오류가 발생했습니다. 계속 진행합니다.
)
echo [완료] 빌드 완료

echo.
echo ========================================
echo [5/6] PM2 및 윈도우 시작 도구 설치 중...
echo ========================================
call npm install -g pm2 pm2-windows-startup
IF %ERRORLEVEL% NEQ 0 (
    echo [오류] PM2 설치 실패!
    pause
    goto MENU
)
call pm2-startup install
echo [완료] PM2 설치 완료

echo.
echo ========================================
echo [6/6] PM2로 서버 시작 중...
echo ========================================
call pm2 start ecosystem.config.js
call pm2 save
echo [완료] 서버 시작 완료

echo.
echo ========================================================
echo  초기 설정이 완료되었습니다!
echo ========================================================
echo.
echo  Backend API:  http://localhost:8000
echo  API Docs:     http://localhost:8000/docs
echo  Admin:        http://localhost:3000
echo  Monitor:      http://localhost:3001
echo.
pause
goto MENU

REM ============================================
REM 전체 업그레이드
REM ============================================
:FULL_UPGRADE
cls
echo ========================================================
echo        전체 업그레이드 (Full Upgrade)
echo ========================================================
echo.
echo 1. 소스 코드 가져오는 중...
git pull

echo.
echo 2. Python 의존성 업데이트 중...
cd /d "%~dp0backend"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo [경고] Python 가상환경이 없습니다. 건너뜁니다.
)

echo.
echo 3. Node.js 의존성 설치 중...
cd /d "%~dp0"
call npm install --legacy-peer-deps

echo.
echo 4. 프로젝트 빌드 중...
call npm run build

echo.
echo 5. PM2 서버 재시작 중...
call pm2 restart ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    echo [알림] 실행 중인 프로세스가 없습니다. 새로 시작합니다.
    call pm2 start ecosystem.config.js
)
call pm2 save

echo.
echo ========================================================
echo  전체 업그레이드가 완료되었습니다!
echo ========================================================
pause
goto MENU

REM ============================================
REM 소스 가져오기 (Git Pull)
REM ============================================
:GIT_PULL
cls
echo ========================================================
echo        소스 코드 가져오기 (Git Pull)
echo ========================================================
cd /d "%~dp0"
git pull
IF %ERRORLEVEL% NEQ 0 (
    echo [오류] Git Pull 실패!
) else (
    echo [성공] 최신 소스를 가져왔습니다.
)
pause
goto MENU

REM ============================================
REM 소스 강제 가져오기 (Force Pull)
REM ============================================
:FORCE_GIT_PULL
cls
echo ========================================================
echo        소스 강제 가져오기 (Git Force Pull)
echo ========================================================
echo.
echo [경고] 로컬에서 수정한 모든 변경사항이 사라집니다!
echo        정말로 진행하시겠습니까? (서버의 최신 소스로 덮어씁니다)
echo.
set /p confirm="진행하려면 'Y'를 입력하세요: "
if /i "%confirm%" neq "Y" goto MENU

cd /d "%~dp0"
echo.
echo 1. 원격 저장소 정보 가져오기 (Fetch)...
git fetch --all
echo.
echo 2. 로컬 변경사항 초기화 및 덮어쓰기 (Reset --hard)...
git reset --hard origin/main
IF %ERRORLEVEL% NEQ 0 (
    echo [오류] 강제 업데이트 실패!
) else (
    echo [성공] 최신 소스로 강제 업데이트되었습니다.
)
pause
goto MENU

REM ============================================
REM Python 가상환경 생성
REM ============================================
:CREATE_VENV
cls
echo ========================================================
echo        Python 가상환경 생성
echo ========================================================
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
        pause
        goto MENU
    )
)

echo [작업] 가상환경 생성 중...
python -m venv .venv

IF %ERRORLEVEL% NEQ 0 (
    echo [오류] 가상환경 생성 실패! Python이 설치되어 있는지 확인하세요.
) else (
    echo [성공] 가상환경이 생성되었습니다!
    echo.
    echo [다음 단계] 메뉴에서 7번을 선택하여 의존성을 설치하세요.
)
pause
goto MENU

REM ============================================
REM Python 의존성 설치
REM ============================================
:INSTALL_PY_DEPS
cls
echo ========================================================
echo        Python 의존성 설치 (pip install)
echo ========================================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 6번으로 가상환경을 생성해주세요.
    pause
    goto MENU
)

echo [1/3] 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo [2/3] pip 업그레이드 중...
python -m pip install --upgrade pip

echo [3/3] 의존성 설치 중...
pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo [오류] 의존성 설치 중 오류가 발생했습니다.
) else (
    echo.
    echo [성공] 모든 Python 의존성이 설치되었습니다!
)
pause
goto MENU

REM ============================================
REM 가상환경 활성화 (새 CMD 창)
REM ============================================
:ACTIVATE_VENV
cls
echo ========================================================
echo        Python 가상환경 활성화
echo ========================================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 6번으로 가상환경을 생성해주세요.
    pause
    goto MENU
)

echo [정보] 가상환경이 활성화된 새 CMD 창을 엽니다.
start cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo. && echo [활성화됨] Python 가상환경이 활성화되었습니다. && echo 작업 디렉토리: %~dp0backend && echo."
goto MENU

REM ============================================
REM npm 의존성 설치
REM ============================================
:NPM_INSTALL
cls
echo ========================================================
echo        npm 의존성 설치 (npm install)
echo ========================================================
echo.

cd /d "%~dp0"
call npm install --legacy-peer-deps

IF %ERRORLEVEL% NEQ 0 (
    echo [오류] npm install 실패!
) else (
    echo [성공] 라이브러리 설치 완료.
)
pause
goto MENU

REM ============================================
REM 프로젝트 빌드
REM ============================================
:NPM_BUILD
cls
echo ========================================================
echo        프로젝트 빌드 (npm run build)
echo ========================================================
echo 시간이 조금 걸릴 수 있습니다...

cd /d "%~dp0"
call npm run build

IF %ERRORLEVEL% NEQ 0 (
    echo [오류] 빌드 실패!
) else (
    echo [성공] 빌드 완료.
)
pause
goto MENU

REM ============================================
REM 개발 모드 - Backend 실행
REM ============================================
:DEV_BACKEND
cls
echo ========================================================
echo        Backend 개발 서버 실행 (FastAPI)
echo ========================================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 메뉴 6, 7번으로 환경을 설정해주세요.
    pause
    goto MENU
)

echo [정보] Backend 서버를 새 창에서 실행합니다.
echo        URL: http://localhost:8000
echo        API Docs: http://localhost:8000/docs
echo.
start "JSOPCUA Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo. && echo [Backend] FastAPI 서버 시작... && echo. && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
goto MENU

REM ============================================
REM 개발 모드 - Admin 실행
REM ============================================
:DEV_ADMIN
cls
echo ========================================================
echo        Admin 개발 서버 실행 (Next.js)
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    pause
    goto MENU
)

echo [정보] Admin 앱을 새 창에서 실행합니다.
echo        URL: http://localhost:3000
echo.
start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && echo. && echo [Admin] Next.js 앱 시작... && echo. && npm run dev:admin"
goto MENU

REM ============================================
REM 개발 모드 - Monitor 실행
REM ============================================
:DEV_MONITOR
cls
echo ========================================================
echo        Monitor 개발 서버 실행 (Next.js)
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [경고] node_modules가 없습니다. npm install을 먼저 실행해주세요.
    pause
    goto MENU
)

echo [정보] Monitor 앱을 새 창에서 실행합니다.
echo        URL: http://localhost:3001
echo.
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && echo. && echo [Monitor] Next.js 앱 시작... && echo. && npm run dev:monitor"
goto MENU

REM ============================================
REM 개발 모드 - 전체 실행
REM ============================================
:DEV_ALL
cls
echo ========================================================
echo        전체 개발 환경 실행
echo ========================================================
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
    pause
    goto MENU
)

timeout /t 2 > nul

echo [3/3] Monitor 앱 시작...
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && echo. && echo [Monitor] Next.js 앱 시작... && npm run dev:monitor"

echo.
echo ========================================================
echo  전체 개발 환경이 시작되었습니다!
echo ========================================================
echo.
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Admin:    http://localhost:3000
echo  Monitor:  http://localhost:3001
echo.
pause
goto MENU

REM ============================================
REM PM2 서버 시작
REM ============================================
:PM2_START
cls
echo ========================================================
echo        PM2 서버 시작
echo ========================================================
echo.

cd /d "%~dp0"
call pm2 start ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    echo [알림] 이미 실행 중이거나 오류가 발생했습니다. 재시작을 시도합니다.
    call pm2 restart ecosystem.config.js
)
call pm2 save
echo.
echo [성공] 서버 시작 명령이 완료되었습니다.
echo [알림] 현재 실행 중인 프로세스가 윈도우 시작 시 자동 실행되도록 저장되었습니다.
pause
goto MENU

REM ============================================
REM PM2 서버 재시작
REM ============================================
:PM2_RESTART
cls
echo ========================================================
echo        PM2 서버 재시작
echo ========================================================
echo.

cd /d "%~dp0"
call pm2 restart ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    echo [알림] 실행 중인 프로세스가 없습니다. 새로 시작합니다.
    call pm2 start ecosystem.config.js
    call pm2 save
) else (
    echo [성공] 서버가 재시작되었습니다.
)
pause
goto MENU

REM ============================================
REM PM2 서버 중지
REM ============================================
:PM2_STOP
cls
echo ========================================================
echo        PM2 서버 중지
echo ========================================================
echo.

cd /d "%~dp0"
call pm2 stop all
echo [알림] 모든 PM2 프로세스가 중지되었습니다.
pause
goto MENU

REM ============================================
REM PM2 서버 상태 확인
REM ============================================
:PM2_STATUS
cls
echo ========================================================
echo        PM2 서버 상태 확인
echo ========================================================
echo.

call pm2 list
pause
goto MENU

REM ============================================
REM PM2 실시간 로그 보기
REM ============================================
:PM2_LOGS
cls
echo ========================================================
echo        PM2 실시간 로그 보기
echo ========================================================
echo 로그를 종료하려면 Ctrl+C를 누르세요.
echo.

call pm2 logs
pause
goto MENU

REM ============================================
REM 윈도우 시작 프로그램 등록
REM ============================================
:AUTO_STARTUP
cls
echo ========================================================
echo        윈도우 시작 프로그램 등록 (Auto Startup)
echo ========================================================
echo.
echo [주의] 반드시 '관리자 권한'으로 실행해야 합니다!
echo.

echo 1. PM2 Windows Startup 도구 설치 확인...
call npm list -g pm2-windows-startup > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [알림] 도구가 없어 설치합니다...
    call npm install -g pm2-windows-startup
)

echo.
echo 2. 시작 프로그램 등록 실행...
call pm2-startup install
IF %ERRORLEVEL% NEQ 0 (
    echo [알림] 이미 등록되어 있거나 권한 문제일 수 있습니다.
) else (
    echo [성공] 윈도우 시작 프로그램에 등록되었습니다.
)

echo.
echo 3. 현재 실행 중인 프로세스 목록 저장...
call pm2 save
echo.
echo 설정이 완료되었습니다! 이제 재부팅 시 서버가 자동 실행됩니다.
pause
goto MENU

REM ============================================
REM 개발 서버 포트 강제 종료
REM ============================================
:KILL_ALL_PORTS
cls
echo ========================================================
echo        개발 서버 포트 강제 종료
echo ========================================================
echo.

echo [1/3] 포트 8000 (Backend) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a 종료
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 8000 정리됨

echo [2/3] 포트 3000 (Admin) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a 종료
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 3000 정리됨

echo [3/3] 포트 3001 (Monitor) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a 종료
    taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 포트 3001 정리됨

echo.
echo [완료] 모든 개발 서버 포트가 정리되었습니다.
pause
goto MENU

REM ============================================
REM Backend 테스트 실행
REM ============================================
:RUN_TESTS
cls
echo ========================================================
echo        Backend 테스트 실행
echo ========================================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    pause
    goto MENU
)

echo [정보] pytest 실행 중...
echo.
call .venv\Scripts\activate.bat
pytest tests\ -v

pause
goto MENU

REM ============================================
REM 종료
REM ============================================
:END
echo.
echo 관리 도구를 종료합니다. 안녕히 가세요!
echo.
endlocal
exit /b 0
