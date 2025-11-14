@echo off
REM ============================================
REM 의존성 재설치 스크립트
REM 모노레포 workspaces를 사용하여 중앙 집중식 설치
REM ============================================

echo.
echo ========================================
echo  의존성 재설치 시작
echo ========================================
echo.

REM 루트에서 npm install 실행 (workspaces 자동 처리)
echo [1/1] 루트에서 npm install 실행 중...
echo       (workspaces가 자동으로 모든 앱의 의존성을 설치합니다)
echo.

npm install

if errorlevel 1 (
    echo.
    echo [ERROR] npm install 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo  설치 완료!
echo ========================================
echo.
echo 확인 사항:
echo   - 루트에 node_modules가 생성되었는지 확인
echo   - 각 앱의 node_modules는 심볼릭 링크로 연결됩니다
echo.
pause

