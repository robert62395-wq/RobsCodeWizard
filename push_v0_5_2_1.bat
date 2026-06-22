@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.5.2.1 to GitHub
echo ============================================================
echo.
echo This will commit, tag, and push v0.5.2.1.
echo Status bar foundation: help_icon, help_dialogs, status_bar_helper,
echo plus main_window.py patched with imports + statusBar init.
echo.

git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

set TAG=v0.5.2.1
set MSG=v0.5.2.1: Status bar foundation - HelpIcon + help_dialogs + status_bar_helper + main_window patched

echo.
echo [1/4] Staging changes...
git add -A

echo [2/4] Committing...
git commit -m "%MSG%"
if errorlevel 1 (
    echo [WARN] Nothing to commit or commit failed.
)

echo [3/4] Creating tag %TAG%...
git tag -a %TAG% -m "%MSG%"
if errorlevel 1 (
    echo [ERROR] Tag failed. May already exist. Aborting.
    pause & exit /b 1
)

echo [4/4] Pushing main and tag...
git push origin main
git push origin %TAG%

echo.
echo ============================================================
echo  Done. GitHub Actions will build EXE + Installer for v0.5.2.1.
echo  Watch: https://github.com/robert62395-wq/RobsCodeWizard/actions
echo ============================================================
pause
