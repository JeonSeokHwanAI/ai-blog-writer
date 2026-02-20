@echo off
chcp 65001 >nul
echo ========================================
echo   AI Blog Writer - Setup
echo ========================================
echo.

:: Python check
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed.
    echo.
    echo [2/4] Installing Python... (1-2 min)
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo [!] Auto install failed. Manual install required.
        echo.
        echo Option 1: Run as Administrator
        echo    - Right-click setup.bat - Run as administrator
        echo.
        echo Option 2: Manual install
        echo    - Visit https://www.python.org/downloads/
        echo    - Click "Download Python"
        echo    - IMPORTANT: Check "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Python installed!
    echo.
    echo [!] Please restart terminal and run setup.bat again.
    echo.
    pause
    exit /b 0
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% found

:: pip upgrade
echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip ready

:: Install packages
echo.
echo [3/4] Installing packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [!] Some packages failed. Try:
    echo   pip install --user -r requirements.txt
    pause
    exit /b 1
)

:: Playwright
echo.
echo [4/4] Playwright browser install (optional)
echo.
echo /monthly feature requires Playwright.
echo This will download ~200MB.
echo.
set /p INSTALL_PW="Install Playwright? (Y/N): "
if /i "%INSTALL_PW%"=="Y" (
    echo.
    echo Installing Chromium...
    playwright install chromium
    echo [OK] Playwright installed
)

echo.
echo ========================================
echo   [OK] Setup Complete!
echo ========================================
echo.
echo You can now use these commands in Claude Code:
echo   /search [blogID]  - Scrape blog
echo   /review [blogID]  - Analyze blog
echo   /setup check      - Check environment
echo.
pause
