@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push Phase 5 (v0.4.5) to GitHub
echo ============================================================

set TAG=v0.4.5
set MSG=v0.4.5: Phase 5 - ODOT export (Civil3D + OpenRoads) + Export tab + reverse line-connect conversion

git status --short
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" exit /b 0

git add -A
git commit -m "%MSG%"
git tag -a %TAG% -m "%MSG%"
if errorlevel 1 (
    echo [ERROR] Tag failed.
    pause & exit /b 1
)
git push origin main
git push origin %TAG%

echo.
echo Done. GitHub Actions will build EXE + Installer for v0.4.5.
pause
