@echo off
REM Non-interactive run used by the Scheduled Task. Logs instead of prompting,
REM and never opens a browser window in your face at 08:00.
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set NO_COLOR=1

if not exist "logs" mkdir "logs"
for /f "tokens=1-3 delims=/- " %%a in ("%DATE%") do set STAMP=%%c-%%b-%%a

python argus.py run --no-open >> "logs\argus-%STAMP%.log" 2>&1
endlocal
