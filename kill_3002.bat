@echo off
REM ============================================
REM 포트 3002 사용 프로세스 종료
REM ============================================

echo.
echo ========================================
echo  포트 3002 사용 프로세스 종료
echo ========================================
echo.

REM 포트 3002 사용 프로세스 찾기 및 종료
echo 포트 3002 사용 프로세스 확인 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3002" ^| findstr "LISTENING"') do (
    echo   PID %%a 종료 중...
    taskkill /F /PID %%a 2>nul
    if not errorlevel 1 (
        echo   [OK] PID %%a 종료 완료
    )
)

echo.
echo ========================================
echo  완료!
echo ========================================
echo.
timeout /t 2 >nul
