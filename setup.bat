@echo off
chcp 65001 >nul
echo ========================================
echo   AI Blog Writer - 환경 설정
echo ========================================
echo.

:: Python 확인
echo [1/4] Python 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo [2/4] Python 자동 설치 중... (1-2분 소요)
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo ⚠️ 자동 설치 실패. 수동 설치가 필요합니다.
        echo.
        echo 방법 1: 관리자 권한으로 이 파일 다시 실행
        echo    - setup.bat 우클릭 → "관리자 권한으로 실행"
        echo.
        echo 방법 2: 직접 설치
        echo    - https://www.python.org/downloads/ 접속
        echo    - "Download Python" 클릭
        echo    - 설치 시 "Add Python to PATH" 반드시 체크!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Python 설치 완료!
    echo.
    echo ⚠️ 터미널을 재시작해야 Python이 인식됩니다.
    echo    이 창을 닫고 setup.bat을 다시 실행해주세요.
    echo.
    pause
    exit /b 0
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo ✅ Python %PYVER% 확인됨

:: pip 확인 및 업그레이드
echo.
echo [2/4] pip 확인 및 업그레이드...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip 준비 완료

:: 패키지 설치
echo.
echo [3/4] 필수 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ⚠️ 일부 패키지 설치 실패. 권한 문제일 수 있습니다.
    echo 다음 명령어로 재시도해보세요:
    echo   pip install --user -r requirements.txt
    pause
    exit /b 1
)

:: Playwright 설치 안내
echo.
echo [4/4] Playwright 브라우저 설치 (선택)
echo.
echo /monthly 기능(이달의 블로그)을 사용하려면 Playwright가 필요합니다.
echo 약 200MB를 다운로드합니다.
echo.
set /p INSTALL_PW="Playwright를 설치할까요? (Y/N): "
if /i "%INSTALL_PW%"=="Y" (
    echo.
    echo Chromium 브라우저 설치 중...
    playwright install chromium
    echo ✅ Playwright 설치 완료
)

echo.
echo ========================================
echo   ✅ 설치 완료!
echo ========================================
echo.
echo 이제 Claude Code에서 다음 명령어를 사용할 수 있습니다:
echo   /search [블로그ID]  - 블로그 스크래핑
echo   /review [블로그ID]  - 블로그 분석
echo   /setup check        - 환경 점검
echo.
pause
