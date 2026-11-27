@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if "%~1"=="" goto usage
if not exist "%~1\ComponentList.SC2Components" goto usage
set "TEMPLATE=%~f1"
set "OUTPUT=%~dp0MiniCraft-FastestAI.SC2Map"
if not "%~2"=="" set "OUTPUT=%~f2"
set "CACHE=%~dp0.MiniCraft-FastestAI-cache"
set "REPO=https://github.com/URZ-Studio/CS2-Mini.git"
where git >nul 2>&1 || goto fail
where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1 || goto fail
  set "PY=python"
) else (
  set "PY=py -3"
)
if not exist "%CACHE%\" mkdir "%CACHE%" || goto fail
if not exist "%CACHE%\source.git\HEAD" git init --bare "%CACHE%\source.git" || goto fail
git --git-dir="%CACHE%\source.git" fetch --no-tags --depth=1 "%REPO%" +refs/heads/main:refs/heads/main || goto fail
git --git-dir="%CACHE%\source.git" show refs/heads/main:FastestAI/Build-FastestAI.py > "%CACHE%\Build-FastestAI.py" || goto fail
git --git-dir="%CACHE%\source.git" show refs/heads/main:FastestAI/FastestAI.galaxy > "%CACHE%\FastestAI.galaxy" || goto fail
%PY% "%CACHE%\Build-FastestAI.py" "%TEMPLATE%" --output "%OUTPUT%" || goto fail
echo.
echo Open the generated ComponentList.SC2Components in Galaxy Editor.
echo Save As and Test Document. This launcher cannot compile or publish the map.
pause
exit /b 0
:usage
echo Drag an EMPTY flat Galaxy Editor map component folder onto this BAT.
echo See FastestAI/README.md for the four player slots and start locations.
pause
exit /b 2
:fail
echo Test map generation failed. Read the error above.
pause
exit /b 1
