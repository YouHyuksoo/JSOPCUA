@echo off
setlocal
echo [INFO] Checking for process on port 8000...

:: Find PID listening on port 8000 and kill it
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo [INFO] Found PID %%a listening on port 8000.
    echo [INFO] Killing process %%a...
    taskkill /F /PID %%a
)

echo [INFO] Operation completed.
endlocal
timeout /t 2 >nul
