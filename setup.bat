@echo off
chcp 65001 >nul
cd /d "%~dp0"
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
    echo [2/4] Installing Python 3.12... (1-2 min)
    echo.

    :: Try winget first with PATH option
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --override "/quiet InstallAllUsers=0 PrependPath=1"

    if errorlevel 1 (
        echo.
        echo [!] Auto install failed. Manual install required.
        echo.
        echo ========================================
        echo   Manual Installation Guide
        echo ========================================
        echo.
        echo 1. Visit: https://www.python.org/downloads/
        echo 2. Click "Download Python 3.12"
        echo 3. Run installer
        echo 4. [IMPORTANT] Check "Add Python to PATH"
        echo 5. Click "Install Now"
        echo 6. Close this window and run setup.bat again
        echo.
        echo ----------------------------------------
        echo Or try running as Administrator:
        echo   Right-click setup.bat - Run as administrator
        echo ----------------------------------------
        echo.
        pause
        exit /b 1
    )

    echo.
    echo [OK] Python installed!
    echo.
    echo ========================================
    echo   [!] RESTART REQUIRED
    echo ========================================
    echo.
    echo Please close this window and:
    echo   1. Close ALL terminal/cmd windows
    echo   2. Run setup.bat again
    echo.
    echo This is needed to refresh PATH.
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
if errorlevel 1 (
    echo [!] pip upgrade failed, trying ensurepip...
    python -m ensurepip --upgrade >nul 2>&1
)
echo [OK] pip ready

:: Install packages
echo.
echo [3/4] Installing packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [!] Some packages failed. Trying with --user flag...
    pip install --user -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [X] Package installation failed.
        echo.
        echo Try manually:
        echo   pip install requests beautifulsoup4 playwright
        echo.
        pause
        exit /b 1
    )
)
echo [OK] Packages installed

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
    if errorlevel 1 (
        echo [!] Playwright install failed. You can install later:
        echo     playwright install chromium
    ) else (
        echo [OK] Playwright installed
    )
)

echo.
echo ========================================
echo   [OK] Setup Complete!
echo ========================================
echo.
echo You can now use these commands in Claude Code:
echo   /search [blogID]  - Scrape blog
echo   /review [blogID]  - Analyze blog
echo   /bloggers         - Manage blog list
echo.
pause
