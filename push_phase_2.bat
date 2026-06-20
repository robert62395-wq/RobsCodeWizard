@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push Phase 2 (v0.4.2) to GitHub
echo ============================================================

set TAG=v0.4.2
set MSG=v0.4.2: Phase 2 - Translation Tab UI + review pane + Convert Line Connect Codes (numeric to alphabetic)

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
if errorlevel 1 (
    echo [WARN] Nothing to commit or commit failed. Continuing to tag...
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
echo  Done. GitHub Actions will now build EXE + Installer for v0.4.2.
echo  Watch: https://github.com/robert62395-wq/RobsCodeWizard/actions
echo ============================================================
pause
