@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   AI Blog Writer - Update
echo ========================================
echo.

:: Git check
echo [1/4] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [X] Git is not installed.
    echo.
    echo ========================================
    echo   Git Installation Guide
    echo ========================================
    echo.
    echo 1. Visit: https://git-scm.com/downloads
    echo 2. Download and install for your OS
    echo 3. Restart terminal/VSCode
    echo 4. Run update.bat again
    echo.
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('git --version') do set GITVER=%%i
echo [OK] Git %GITVER% found

:: Check if git repo exists
echo.
echo [2/4] Checking git repository...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [!] Git not initialized. Setting up...
    echo.
    git init
    git remote add origin https://github.com/JeonSeokHwanAI/ai-blog-writer.git
    git fetch origin
    git reset origin/main
    echo.
    echo [OK] Git connected to ai-blog-writer
) else (
    echo [OK] Git repository found
)

:: Pull latest
echo.
echo [3/4] Downloading latest version...
git pull origin main
if errorlevel 1 (
    echo.
    echo [!] Update failed. There may be file conflicts.
    echo     Please ask in the group chat for help.
    echo.
    pause
    exit /b 1
)
echo [OK] Code updated

:: Install packages
echo.
echo [4/4] Updating packages...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    pip install --user -r requirements.txt >nul 2>&1
)
echo [OK] Packages updated

echo.
echo ========================================
echo   [OK] Update Complete!
echo ========================================
echo.
echo Your data (docs/, output/) is preserved.
echo.
echo New features available - check CLAUDE.md for details.
echo.
pause
