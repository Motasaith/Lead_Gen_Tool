@echo off
REM ============================================================
REM Quick start: just run this to use LeadBot
REM (Requires venv set up via setup.bat or manually)
REM ============================================================

setlocal
cd /d "%~dp0"

if not exist venv (
    echo ERROR: Virtual environment not found.
    echo Run setup.bat first, or create a venv at ..\venv
    pause
    exit /b 1
)

call ..\venv\Scripts\activate.bat || (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)

REM Run the system tray app (or dashboard if pystray not installed)
python launcher.py 2>nul || python dashboard.py

endlocal
