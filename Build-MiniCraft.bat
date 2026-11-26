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
if /i "%~1"=="--classic" goto classicarg
if not "%~1"=="" if /i "%~nx1"=="Mods" goto bothmods
if not "%~1"=="" goto bothclassic
:both
echo [1/2] Installing or updating Classic...
call "%BOOT%\worker.bat" classic || goto fail
echo [2/2] Installing or updating EVO...
call "%BOOT%\worker.bat" evo || goto fail
goto done
:bothmods
echo [1/2] Installing or updating Classic...
call "%BOOT%\worker.bat" classic || goto fail
echo [2/2] Installing or updating EVO...
call "%BOOT%\worker.bat" evo "%~1" || goto fail
goto done
:bothclassic
echo [1/2] Installing or updating Classic...
call "%BOOT%\worker.bat" classic "%~1" || goto fail
echo [2/2] Installing or updating EVO...
call "%BOOT%\worker.bat" evo || goto fail
goto done
:classicarg
call "%BOOT%\worker.bat" classic "%~2" || goto fail
goto done
:evoarg
call "%BOOT%\worker.bat" evo "%~2" || goto fail
goto done
:done
echo.
echo Installation and update completed.
pause
exit /b 0
:fail
echo.
echo Installation failed. Check the error above.
echo If installing both, an earlier successful update may already be applied.
pause
exit /b 1
