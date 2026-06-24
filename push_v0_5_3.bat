@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.5.3 to GitHub
echo ============================================================
echo.
echo This will commit, tag, and push v0.5.3 (Phase 1 of error
echo handling and resilience).
echo.

git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

set TAG=v0.5.3
set MSG=v0.5.3: Error handling Phase 1 - corruption recovery, safe handlers, diag log downgrade

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
echo  Done. GitHub Actions will build EXE + Installer for v0.5.3.
echo  Watch: https://github.com/robert62395-wq/RobsCodeWizard/actions
echo ============================================================
pause