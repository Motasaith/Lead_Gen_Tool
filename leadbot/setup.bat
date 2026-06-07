@echo off
REM ============================================================
REM LeadBot setup - creates venv and installs all dependencies
REM Run this once after extracting LeadBot to a new machine
REM ============================================================

setlocal
cd /d "%~dp0"

echo.
echo ============================================================
echo  LeadBot - First-time Setup
echo ============================================================
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required.
    echo Download from https://www.python.org/downloads/
    echo During install, CHECK "Add Python to PATH"!
    pause
    exit /b 1
)

for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYVER=%%V
echo Python version: %PYVER%

REM Create venv at ..\venv
if exist ..\venv (
    echo Virtual environment already exists at ..\venv
) else (
    echo [1/5] Creating virtual environment...
    python -m venv ..\venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv
        pause
        exit /b 1
    )
)

call ..\venv\Scripts\activate.bat

echo [2/5] Upgrading pip...
python -m pip install --quiet --upgrade pip

echo [3/5] Installing core dependencies...
python -m pip install --quiet crawl4ai fastapi "uvicorn[standard]" pystray Pillow apscheduler jinja2 python-dotenv pydantic

echo [4/5] Installing Playwright browsers (200MB download, may take 1-2 min)...
python -m playwright install chromium

echo [5/5] Copying .env.example to .env...
if not exist .env (
    copy .env.example .env >nul
    echo Created .env - edit it to add your Discord/Telegram webhooks
) else (
    echo .env already exists, skipping
)

echo.
echo ============================================================
echo  SETUP COMPLETE!
echo ============================================================
echo.
echo  Next steps:
echo    1. Edit .env to add your LLM key or webhook URLs
echo    2. Run: start.bat
echo    3. Or run the dashboard: python dashboard.py
echo    4. Or build a standalone .exe: build.bat
echo.
echo  See README.md for full documentation.
echo.

pause
endlocal
