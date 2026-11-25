@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0" || goto :fail
set "MINICRAFT_HOME=%~dp0"
set "CACHE=%~dp0.MiniCraft-cache"
set "MINICRAFT_TARGET_FILE=%CACHE%\target.txt"
set "SOURCE=%CACHE%\source.git"
set "STAGED=%CACHE%\Build-MiniCraft.next.py"
set "BUILDER=%CACHE%\Build-MiniCraft.py"
set "REPO=https://github.com/URZ-Studio/CS2-Mini.git"
echo ===========================================================
echo MiniCraft II - Permanent GitHub launcher
echo ===========================================================
where git >nul 2>&1 || goto :nogit
where py >nul 2>&1
if errorlevel 1 (
    where python >nul 2>&1 || goto :nopy
    set "PY_CMD=python"
) else (
    set "PY_CMD=py -3"
)
if not exist "%CACHE%\" mkdir "%CACHE%" || goto :fail
if not exist "%SOURCE%\HEAD" git init --bare "%SOURCE%" || goto :fail
echo [1/3] Fetching latest main from GitHub...
git --git-dir="%SOURCE%" fetch --no-tags --depth=1 "%REPO%" +refs/heads/main:refs/heads/main || goto :fetchfail
git --git-dir="%SOURCE%" rev-parse --short refs/heads/main || goto :fail
git --git-dir="%SOURCE%" show refs/heads/main:Build-MiniCraft.py > "%STAGED%" || goto :fail
echo [2/3] Validating downloaded builder...
%PY_CMD% "%STAGED%" --check || goto :fail
move /y "%STAGED%" "%BUILDER%" >nul || goto :fail
echo [3/3] Building or updating MiniCraft...
echo Close Galaxy Editor before proceeding.
if "%~1"=="" goto :defaulttarget
%PY_CMD% "%BUILDER%" "%~1" || goto :fail
goto :success
:defaulttarget
%PY_CMD% "%BUILDER%" || goto :fail
:success
echo.
echo Done. Open the target component folder in Galaxy Editor.
echo This launcher does not publish to Battle.net.
pause
exit /b 0
:nogit
echo Git for Windows is required. Install it and reopen this launcher.
goto :fail
:nopy
echo Python 3 is required.
goto :fail
:fetchfail
echo GitHub fetch failed. Check network and GitHub login for this private repository.
echo No local mod was updated. Run the launcher again after signing in.
goto :fail
:fail
echo.
echo Update failed. Read the error above.
pause
exit /b 1
