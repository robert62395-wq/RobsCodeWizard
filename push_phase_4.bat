@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push Phase 4 (v0.4.4) to GitHub
echo ============================================================

set TAG=v0.4.4
set MSG=v0.4.4: Phase 4 - Hardened Point/Elevation offsets + IGLD85 helpers

git status --short

set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

git add -A
git commit -m "%MSG%"
git tag -a %TAG% -m "%MSG%"
if errorlevel 1 (
    echo [ERROR] Tag failed. May already exist.
    pause & exit /b 1
)
git push origin main
git push origin %TAG%

echo.
echo Done. GitHub Actions will build EXE + Installer for v0.4.4.
pause
