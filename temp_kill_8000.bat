@echo off
echo Checking for process on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Found PID %%a - Killing...
    taskkill /F /PID %%a
)
echo Done.
timeout /t 2 >nul
