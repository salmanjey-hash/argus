@echo off
REM Argus FinCrime - daily run. Safe to double-click.
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo.
echo  Argus FinCrime - daily run
echo  ==========================
echo.

python argus.py run --no-open
if errorlevel 1 (
    echo.
    echo  Something went wrong. Run "python argus.py health" for detail.
    pause
    exit /b 1
)

echo.
echo  Done. Opening the dashboard...
start "" "%~dp0dashboard.html"
endlocal
