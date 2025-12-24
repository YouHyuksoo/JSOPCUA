@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:MENU
cls
echo.
echo ========================================================================
echo                    JSOPCUA Management Tool (v1.0)
echo ========================================================================
echo.
echo   [Setup]
echo     1. Git Clone (Download Source)
echo     2. Full Initial Setup (Python + Node + PM2)
echo.
echo   [Update]
echo     3. Full Upgrade (Git Pull + Install + Build + Restart)
echo.
echo   [Git]
echo     4. Git Pull
echo     5. Git Force Pull (Reset local changes)
echo.
echo   [Python]
echo     6. Create Virtual Environment
echo     7. Install Python Dependencies (pip install)
echo     8. Activate Virtual Environment (New CMD)
echo.
echo   [Node.js]
echo     9. npm install
echo    10. npm run build (Production)
echo.
echo   [Dev Server - Opens in new window]
echo    11. Backend Dev Server (FastAPI - Port 8000)
echo    12. Admin Dev Server (Next.js - Port 3000)
echo    13. Monitor Dev Server (Next.js - Port 3001)
echo    14. Start All Dev Servers
echo.
echo   [PM2 Production]
echo    15. PM2 Start
echo    16. PM2 Restart
echo    17. PM2 Stop
echo    18. PM2 Status
echo    19. PM2 Logs
echo    20. Auto Startup Registration
echo.
echo   [Utility]
echo    21. Kill All Dev Ports (8000, 3000, 3001)
echo    22. Run Backend Tests
echo.
echo     0. Exit
echo.
echo ========================================================================
set /p choice="Select (0-22): "

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
echo [ERROR] Invalid selection
timeout /t 2 > nul
goto MENU

:CLONE
cls
echo ========================================================
echo        Git Clone
echo ========================================================
echo.
git clone https://github.com/YouHyuksoo/JSOPCUA.git
echo.
echo [INFO] Download complete!
echo [INFO] Move this file into JSOPCUA folder and run option 2
pause
goto MENU

:INITIAL_SETUP
cls
echo ========================================================
echo        Full Initial Setup
echo ========================================================
echo.
echo [WARNING] Run as Administrator!
echo.
pause

echo.
echo [1/6] Creating Python virtual environment...
cd /d "%~dp0backend"
if not exist ".venv" (
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create venv
        pause
        goto MENU
    )
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

echo.
echo [2/6] Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip install failed
    pause
    goto MENU
)
echo [OK] Python dependencies installed

echo.
echo [3/6] Installing Node.js dependencies...
cd /d "%~dp0"
call npm install --legacy-peer-deps
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm install failed
    pause
    goto MENU
)
echo [OK] Node.js dependencies installed

echo.
echo [4/6] Building project...
call npm run build
echo [OK] Build complete

echo.
echo [5/6] Installing PM2...
call npm install -g pm2 pm2-windows-startup
call pm2-startup install
echo [OK] PM2 installed

echo.
echo [6/6] Starting PM2 servers...
call pm2 start ecosystem.config.js
call pm2 save
echo [OK] Servers started

echo.
echo ========================================================
echo  Setup Complete!
echo ========================================================
echo.
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Admin:    http://localhost:3000
echo  Monitor:  http://localhost:3001
echo.
pause
goto MENU

:FULL_UPGRADE
cls
echo ========================================================
echo        Full Upgrade
echo ========================================================
echo.
echo 1. Git pull...
git pull

echo.
echo 2. Python dependencies...
cd /d "%~dp0backend"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo [WARNING] No Python venv found
)

echo.
echo 3. Node.js dependencies...
cd /d "%~dp0"
call npm install --legacy-peer-deps

echo.
echo 4. Building...
call npm run build

echo.
echo 5. Restarting PM2...
call pm2 restart ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Starting new PM2 process...
    call pm2 start ecosystem.config.js
)
call pm2 save

echo.
echo [OK] Full upgrade complete!
pause
goto MENU

:GIT_PULL
cls
echo ========================================================
echo        Git Pull
echo ========================================================
cd /d "%~dp0"
git pull
pause
goto MENU

:FORCE_GIT_PULL
cls
echo ========================================================
echo        Git Force Pull
echo ========================================================
echo.
echo [WARNING] All local changes will be lost!
echo.
set /p confirm="Continue? (Y/N): "
if /i "%confirm%" neq "Y" goto MENU

cd /d "%~dp0"
git fetch --all
git reset --hard origin/main
echo [OK] Force pull complete
pause
goto MENU

:CREATE_VENV
cls
echo ========================================================
echo        Create Python Virtual Environment
echo ========================================================
echo.
cd /d "%~dp0backend"

if exist ".venv" (
    echo [WARNING] Virtual environment already exists
    set /p overwrite="Overwrite? (Y/N): "
    if /i "!overwrite!"=="Y" (
        rmdir /s /q .venv
    ) else (
        goto MENU
    )
)

echo Creating virtual environment...
python -m venv .venv
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create venv
) else (
    echo [OK] Virtual environment created
    echo [NEXT] Run option 7 to install dependencies
)
pause
goto MENU

:INSTALL_PY_DEPS
cls
echo ========================================================
echo        Install Python Dependencies
echo ========================================================
echo.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No virtual environment found
    echo Run option 6 first
    pause
    goto MENU
)

echo [1/3] Activating venv...
call .venv\Scripts\activate.bat

echo [2/3] Upgrading pip...
python -m pip install --upgrade pip

echo [3/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [OK] All dependencies installed
pause
goto MENU

:ACTIVATE_VENV
cls
echo ========================================================
echo        Activate Virtual Environment
echo ========================================================
echo.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No virtual environment found
    pause
    goto MENU
)

echo Opening new CMD with activated venv...
start cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && echo [OK] Virtual environment activated && echo."
goto MENU

:NPM_INSTALL
cls
echo ========================================================
echo        npm install
echo ========================================================
echo.
cd /d "%~dp0"
call npm install --legacy-peer-deps
echo.
echo [OK] npm install complete
pause
goto MENU

:NPM_BUILD
cls
echo ========================================================
echo        npm run build
echo ========================================================
echo.
cd /d "%~dp0"
call npm run build
pause
goto MENU

:DEV_BACKEND
cls
echo ========================================================
echo        Backend Dev Server (FastAPI)
echo ========================================================
echo.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No virtual environment
    pause
    goto MENU
)

echo Starting Backend server in new window...
echo URL: http://localhost:8000
echo API: http://localhost:8000/docs
start "JSOPCUA Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
goto MENU

:DEV_ADMIN
cls
echo ========================================================
echo        Admin Dev Server (Next.js)
echo ========================================================
echo.
cd /d "%~dp0"

if not exist "node_modules" (
    echo [ERROR] node_modules not found. Run npm install first.
    pause
    goto MENU
)

echo Starting Admin in new window...
echo URL: http://localhost:3000
start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && npm run dev:admin"
goto MENU

:DEV_MONITOR
cls
echo ========================================================
echo        Monitor Dev Server (Next.js)
echo ========================================================
echo.
cd /d "%~dp0"

if not exist "node_modules" (
    echo [ERROR] node_modules not found. Run npm install first.
    pause
    goto MENU
)

echo Starting Monitor in new window...
echo URL: http://localhost:3001
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && npm run dev:monitor"
goto MENU

:DEV_ALL
cls
echo ========================================================
echo        Start All Dev Servers
echo ========================================================
echo.

echo [1/3] Starting Backend...
cd /d "%~dp0backend"
if exist ".venv\Scripts\activate.bat" (
    start "JSOPCUA Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo [WARNING] No Backend venv
)

timeout /t 3 > nul

echo [2/3] Starting Admin...
cd /d "%~dp0"
if exist "node_modules" (
    start "JSOPCUA Admin" cmd /k "cd /d %~dp0 && npm run dev:admin"
) else (
    echo [WARNING] No node_modules
    pause
    goto MENU
)

timeout /t 2 > nul

echo [3/3] Starting Monitor...
start "JSOPCUA Monitor" cmd /k "cd /d %~dp0 && npm run dev:monitor"

echo.
echo ========================================================
echo  All servers started!
echo ========================================================
echo.
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Admin:    http://localhost:3000
echo  Monitor:  http://localhost:3001
echo.
pause
goto MENU

:PM2_START
cls
echo ========================================================
echo        PM2 Start
echo ========================================================
echo.
cd /d "%~dp0"
call pm2 start ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Restarting...
    call pm2 restart ecosystem.config.js
)
call pm2 save
echo [OK] PM2 started
pause
goto MENU

:PM2_RESTART
cls
echo ========================================================
echo        PM2 Restart
echo ========================================================
echo.
cd /d "%~dp0"
call pm2 restart ecosystem.config.js
IF %ERRORLEVEL% NEQ 0 (
    call pm2 start ecosystem.config.js
    call pm2 save
)
echo [OK] PM2 restarted
pause
goto MENU

:PM2_STOP
cls
echo ========================================================
echo        PM2 Stop
echo ========================================================
echo.
cd /d "%~dp0"
call pm2 stop all
echo [OK] PM2 stopped
pause
goto MENU

:PM2_STATUS
cls
echo ========================================================
echo        PM2 Status
echo ========================================================
echo.
call pm2 list
pause
goto MENU

:PM2_LOGS
cls
echo ========================================================
echo        PM2 Logs (Ctrl+C to exit)
echo ========================================================
echo.
call pm2 logs
pause
goto MENU

:AUTO_STARTUP
cls
echo ========================================================
echo        Auto Startup Registration
echo ========================================================
echo.
echo [WARNING] Run as Administrator!
echo.

echo 1. Checking PM2 Windows Startup...
call npm list -g pm2-windows-startup > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing pm2-windows-startup...
    call npm install -g pm2-windows-startup
)

echo.
echo 2. Registering startup...
call pm2-startup install

echo.
echo 3. Saving current processes...
call pm2 save
echo.
echo [OK] Auto startup configured
pause
goto MENU

:KILL_ALL_PORTS
cls
echo ========================================================
echo        Kill All Dev Ports
echo ========================================================
echo.

echo [1/3] Killing port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a
    taskkill /F /PID %%a > nul 2>&1
)
echo [OK] Port 8000 cleared

echo [2/3] Killing port 3000 (Admin)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a
    taskkill /F /PID %%a > nul 2>&1
)
echo [OK] Port 3000 cleared

echo [3/3] Killing port 3001 (Monitor)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING" 2^>nul') do (
    echo       PID %%a
    taskkill /F /PID %%a > nul 2>&1
)
echo [OK] Port 3001 cleared

echo.
echo [OK] All ports cleared
pause
goto MENU

:RUN_TESTS
cls
echo ========================================================
echo        Run Backend Tests
echo ========================================================
echo.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No virtual environment
    pause
    goto MENU
)

echo Running pytest...
call .venv\Scripts\activate.bat
pytest tests\ -v
pause
goto MENU

:END
echo.
echo Goodbye!
echo.
endlocal
exit /b 0
