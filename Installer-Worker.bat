@echo off
if /i "%~1"=="classic" goto classic
if /i "%~1"=="evo" goto evo
exit /b 2
:classic
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%MINICRAFT_LAUNCHER_HOME%" || goto :fail
set "MINICRAFT_HOME=%MINICRAFT_LAUNCHER_HOME%"
set "CACHE=%MINICRAFT_LAUNCHER_HOME%.MiniCraft-cache"
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
if "%~2"=="" goto :defaulttarget
%PY_CMD% "%BUILDER%" "%~2" || goto :fail
goto :success
:defaulttarget
%PY_CMD% "%BUILDER%" || goto :fail
:success
echo.
echo Done. Open the target component folder in Galaxy Editor.
echo This launcher does not publish to Battle.net.

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

exit /b 1

:evo
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%MINICRAFT_LAUNCHER_HOME%" || goto evofail
set "CACHE=%MINICRAFT_LAUNCHER_HOME%.MiniCraft-EVO-cache"
set "REPO=https://github.com/URZ-Studio/CS2-Mini.git"
set "UPSTREAM=https://github.com/TeamKoprulu/SCEvoComplete.git"
set "REV=773c8e8ae8828121e8f37bb74ab82ceb761a45bc"
where git >nul 2>&1 || goto evofail
where py >nul 2>&1
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
if not exist "%CACHE%" mkdir "%CACHE%" || goto evofail
if not exist "%CACHE%\mini.git\HEAD" git init --bare "%CACHE%\mini.git" || goto evofail
git --git-dir="%CACHE%\mini.git" fetch --depth=1 "%REPO%" +refs/heads/main:refs/heads/main || goto evofail
if not exist "%CACHE%\EVO" mkdir "%CACHE%\EVO" || goto evofail
git --git-dir="%CACHE%\mini.git" show refs/heads/main:EVO/Build-MiniCraft-EVO.py > "%CACHE%\EVO\Build-MiniCraft-EVO.py" || goto evofail
git --git-dir="%CACHE%\mini.git" show refs/heads/main:Build-MiniCraft.py > "%CACHE%\Build-MiniCraft.py" || goto evofail
%PY% "%CACHE%\EVO\Build-MiniCraft-EVO.py" --check || goto evofail
%PY% "%CACHE%\Build-MiniCraft.py" --check || goto evofail
if not exist "%CACHE%\upstream\.git" (
  git init "%CACHE%\upstream" || goto evofail
  git -C "%CACHE%\upstream" remote add origin "%UPSTREAM%" || goto evofail
)
git -C "%CACHE%\upstream" config core.longpaths true || goto evofail
git -C "%CACHE%\upstream" rev-parse --verify "%REV%^{commit}" >nul 2>&1
if errorlevel 1 git -C "%CACHE%\upstream" fetch --depth=1 origin "%REV%" || goto evofail
git -C "%CACHE%\upstream" checkout --detach "%REV%" || goto evofail
set "MODS=%~2"
if not defined MODS if exist "%CACHE%\mods.txt" set /p MODS=<"%CACHE%\mods.txt"
if defined MODS goto modsready
if exist "%ProgramFiles(x86)%\StarCraft II\Mods\" set "MODS=%ProgramFiles(x86)%\StarCraft II\Mods"
if not defined MODS if exist "%ProgramFiles%\StarCraft II\Mods\" set "MODS=%ProgramFiles%\StarCraft II\Mods"
if not defined MODS set /p "MODS=Enter installed StarCraft II Mods folder (first setup only): "
:modsready
if not defined MODS goto evofail
set "MODS=%MODS:"=%"
%PY% "%CACHE%\EVO\Build-MiniCraft-EVO.py" --source "%CACHE%\upstream" --mods "%MODS%" --mini "%CACHE%\Build-MiniCraft.py" || goto evofail
> "%CACHE%\mods.txt" echo(%MODS%
echo Done. Open the generated SCEvo_Multi component folder in Galaxy Editor.

exit /b 0
:evofail
echo Build failed. Existing MiniCraft is not modified.

exit /b 1
