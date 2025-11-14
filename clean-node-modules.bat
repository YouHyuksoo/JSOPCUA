@echo off
REM ============================================
REM Node Modules 정리 스크립트
REM 모노레포에서 중복 설치된 node_modules 정리
REM ============================================

echo.
echo ========================================
echo  Node Modules 정리 시작
echo ========================================
echo.

REM 루트 node_modules 삭제
if exist node_modules (
    echo [1/4] 루트 node_modules 삭제 중...
    rmdir /s /q node_modules
    echo [OK] 루트 node_modules 삭제 완료
) else (
    echo [1/4] 루트 node_modules 없음 (건너뜀)
)

REM admin node_modules 삭제
if exist apps\admin\node_modules (
    echo [2/4] apps\admin\node_modules 삭제 중...
    rmdir /s /q apps\admin\node_modules
    echo [OK] admin node_modules 삭제 완료
) else (
    echo [2/4] admin node_modules 없음 (건너뜀)
)

REM monitor node_modules 삭제
if exist apps\monitor\node_modules (
    echo [3/4] apps\monitor\node_modules 삭제 중...
    rmdir /s /q apps\monitor\node_modules
    echo [OK] monitor node_modules 삭제 완료
) else (
    echo [3/4] monitor node_modules 없음 (건너뜀)
)

REM packages node_modules 삭제
if exist packages\ui\node_modules (
    echo [4/4] packages\ui\node_modules 삭제 중...
    rmdir /s /q packages\ui\node_modules
    echo [OK] ui node_modules 삭제 완료
)
if exist packages\utils\node_modules (
    echo [4/4] packages\utils\node_modules 삭제 중...
    rmdir /s /q packages\utils\node_modules
    echo [OK] utils node_modules 삭제 완료
)

echo.
echo ========================================
echo  정리 완료!
echo ========================================
echo.
echo 다음 명령어를 실행하여 재설치하세요:
echo   npm install
echo.
pause

