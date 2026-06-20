@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.4.1.1 Hotfix to GitHub
echo ============================================================

set TAG=v0.4.1.1
set MSG=v0.4.1.1 hotfix: restore app.__version__ clobbered by Phase 1 overlay

echo [1/5] Checking git status...
git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

echo [2/5] Staging changes...
git add -A

echo [3/5] Committing...
git commit -m "%MSG%"
if errorlevel 1 (
    echo [WARN] Nothing to commit. Continuing to tag...
)

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
echo  Done. GitHub Actions will rebuild EXE + Installer.
echo  Watch: https://github.com/robert62395-wq/RobsCodeWizard/actions
echo ============================================================
pause
