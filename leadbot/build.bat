@echo off
REM ============================================================
REM LeadBot .exe build script
REM Run this from the leadbot folder to build LeadBotDashboard.exe
REM ============================================================

setlocal

echo.
echo ============================================================
echo  Building LeadBot Dashboard .exe
echo ============================================================
echo.

REM Move to script's directory
cd /d "%~dp0"

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ and try again.
    pause
    exit /b 1
)

echo [1/4] Installing PyInstaller...
python -m pip install --quiet pyinstaller

echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building .exe (this takes 1-2 minutes)...
python -m PyInstaller --clean --noconfirm leadbot.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo [4/4] Verifying...
if not exist dist\LeadBotDashboard.exe (
    echo ERROR: LeadBotDashboard.exe was not created.
    pause
    exit /b 1
)

for %%I in (dist\LeadBotDashboard.exe) do set SIZE=%%~zI
set /a SIZEMB=%SIZE% / 1048576

echo.
echo ============================================================
echo  SUCCESS!
echo ============================================================
echo.
echo  Output: dist\LeadBotDashboard.exe
echo  Size:   %SIZEMB% MB
echo.
echo  How to use:
echo    1. Copy dist\LeadBotDashboard.exe anywhere
echo    2. Run it - browser opens to http://localhost:7860
echo    3. To view leads from your existing data folder, run:
echo       LeadBotDashboard.exe --data-dir "D:\try\Lead_Generator\leadbot\data"
echo.
echo  Optional: bundle your data folder with the .exe
echo    - Copy the .exe into your leadbot folder
echo    - Then just double-click it
echo.

pause
endlocal
