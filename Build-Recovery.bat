@echo off
setlocal
cd /d "%~dp0" || exit /b 1
where py >nul 2>&1
if errorlevel 1 (python "%~dp0Build-Recovery.py") else (py -3 "%~dp0Build-Recovery.py")
set "RC=%ERRORLEVEL%"
echo Exit code: %RC%
pause
exit /b %RC%
