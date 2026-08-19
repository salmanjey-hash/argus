@echo off
REM Registers a Windows Scheduled Task to run Argus FinCrime every weekday.
setlocal
cd /d "%~dp0"

echo.
echo  This will create a Windows Scheduled Task called "ArgusFinCrime"
echo  that runs the daily fetch every weekday at 08:00.
echo.
echo  Folder: %~dp0
echo.
set /p CONFIRM="  Create it? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo  Cancelled. Nothing was changed.
    pause
    exit /b 0
)

schtasks /create ^
    /tn "ArgusFinCrime" ^
    /tr "\"%~dp0run-quiet.cmd\"" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 08:00 ^
    /f

if errorlevel 1 (
    echo.
    echo  Could not create the task. You may need to run this as Administrator.
    pause
    exit /b 1
)

echo.
echo  Done. The task runs every weekday at 08:00.
echo.
echo  Check it:   schtasks /query /tn ArgusFinCrime
echo  Remove it:  schtasks /delete /tn ArgusFinCrime /f
echo.
pause
endlocal
