@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push Phase 3 (v0.4.3) to GitHub
echo ============================================================

set TAG=v0.4.3
set MSG=v0.4.3: Phase 3 - VDT^<-^>ODOT grammar translator + Apply Translation

echo [1/5] Checking git status...
git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

echo [2/5] Staging all changes...
git add -A

echo [3/5] Committing...
git commit -m "%MSG%"

echo [4/5] Tagging %TAG%...
git tag -a %TAG% -m "%MSG%"
if errorlevel 1 (
    echo [ERROR] Tag failed. May already exist. Aborting.
    pause & exit /b 1
)

echo [5/5] Pushing main + tag...
git push origin main
git push origin %TAG%

echo.
echo ============================================================
echo  Done. GitHub Actions will build EXE + Installer for v0.4.3.
echo ============================================================
pause
