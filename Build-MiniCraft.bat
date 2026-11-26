@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0" || goto fail
set "MINICRAFT_LAUNCHER_HOME=%~dp0"
set "BOOT=%~dp0.MiniCraft-launcher"
set "REPO=https://github.com/URZ-Studio/CS2-Mini.git"
where git >nul 2>&1 || goto fail
if not exist "%BOOT%" mkdir "%BOOT%" || goto fail
if not exist "%BOOT%\source.git\HEAD" git init --bare "%BOOT%\source.git" || goto fail
git --git-dir="%BOOT%\source.git" fetch --no-tags --depth=1 "%REPO%" +refs/heads/main:refs/heads/main || goto fail
git --git-dir="%BOOT%\source.git" show refs/heads/main:Installer-Worker.bat > "%BOOT%\worker.next.bat" || goto fail
move /y "%BOOT%\worker.next.bat" "%BOOT%\worker.bat" >nul || goto fail
if /i "%~1"=="--evo" goto evoarg
if not "%~1"=="" goto classicarg
:menu
echo.
echo ========================================
echo MiniCraft II - Universal Installer
echo ========================================
echo [1] Classic - Install / Update
echo [2] EVO - Install / Update
echo [3] Both - Install / Update
echo [0] Exit
choice /c 1230 /n /m "Select: "
if errorlevel 255 goto fail
if errorlevel 4 exit /b 0
if errorlevel 3 goto both
if errorlevel 2 goto evo
if errorlevel 1 goto classic
goto fail
:classic
call "%BOOT%\worker.bat" classic || goto fail
goto done
:evo
call "%BOOT%\worker.bat" evo || goto fail
goto done
:both
call "%BOOT%\worker.bat" classic || goto fail
call "%BOOT%\worker.bat" evo || goto fail
goto done
:classicarg
call "%BOOT%\worker.bat" classic "%~1" || goto fail
goto done
:evoarg
call "%BOOT%\worker.bat" evo "%~2" || goto fail
goto done
:done
echo.
echo Selected installation completed.
pause
exit /b 0
:fail
echo.
echo Installation failed. Check the error above.
echo If installing both, an earlier successful update may already be applied.
pause
exit /b 1
