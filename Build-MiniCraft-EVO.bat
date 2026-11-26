@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0" || goto fail
set "CACHE=%~dp0.MiniCraft-EVO-cache"
set "REPO=https://github.com/URZ-Studio/CS2-Mini.git"
set "UPSTREAM=https://github.com/TeamKoprulu/SCEvoComplete.git"
set "REV=773c8e8ae8828121e8f37bb74ab82ceb761a45bc"
where git >nul 2>&1 || goto fail
where py >nul 2>&1
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
if not exist "%CACHE%" mkdir "%CACHE%" || goto fail
if not exist "%CACHE%\mini.git\HEAD" git init --bare "%CACHE%\mini.git" || goto fail
git --git-dir="%CACHE%\mini.git" fetch --depth=1 "%REPO%" +refs/heads/main:refs/heads/main || goto fail
if not exist "%CACHE%\EVO" mkdir "%CACHE%\EVO" || goto fail
git --git-dir="%CACHE%\mini.git" show refs/heads/main:EVO/Build-MiniCraft-EVO.py > "%CACHE%\EVO\Build-MiniCraft-EVO.py" || goto fail
git --git-dir="%CACHE%\mini.git" show refs/heads/main:Build-MiniCraft.py > "%CACHE%\Build-MiniCraft.py" || goto fail
%PY% "%CACHE%\EVO\Build-MiniCraft-EVO.py" --check || goto fail
%PY% "%CACHE%\Build-MiniCraft.py" --check || goto fail
if not exist "%CACHE%\upstream\.git" (
  git init "%CACHE%\upstream" || goto fail
  git -C "%CACHE%\upstream" remote add origin "%UPSTREAM%" || goto fail
)
git -C "%CACHE%\upstream" config core.longpaths true || goto fail
git -C "%CACHE%\upstream" rev-parse --verify "%REV%^{commit}" >nul 2>&1
if errorlevel 1 git -C "%CACHE%\upstream" fetch --depth=1 origin "%REV%" || goto fail
git -C "%CACHE%\upstream" checkout --detach "%REV%" || goto fail
set "MODS=%~1"
if not defined MODS if exist "%CACHE%\mods.txt" set /p MODS=<"%CACHE%\mods.txt"
if not defined MODS set /p "MODS=Enter installed StarCraft II Mods folder: "
if not defined MODS goto fail
set "MODS=%MODS:"=%"
%PY% "%CACHE%\EVO\Build-MiniCraft-EVO.py" --source "%CACHE%\upstream" --mods "%MODS%" --mini "%CACHE%\Build-MiniCraft.py" || goto fail
> "%CACHE%\mods.txt" echo(%MODS%
echo Done. Open the generated SCEvo_Multi component folder in Galaxy Editor.
pause
exit /b 0
:fail
echo Build failed. Existing MiniCraft is not modified.
pause
exit /b 1
