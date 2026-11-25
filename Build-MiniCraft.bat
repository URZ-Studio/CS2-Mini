@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0Build-MiniCraft.py" %*
) else (
  python "%~dp0Build-MiniCraft.py" %*
)
if errorlevel 1 (
  echo Build failed. See error above.
  pause
  exit /b 1
)
if "%~1"=="" explorer "%~dp0MiniCraft-II-v0.1.4.SC2Mod"
pause
