@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.5.3.2 to GitHub (hotfix)
echo ============================================================
echo.

git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

set TAG=v0.5.3.2
set MSG=v0.5.3.2 hotfix: update legacy test_odot_exporter.py to unpack 3-tuple returns

echo.
echo [1/4] Staging changes...
git add -A

echo [2/4] Committing...
git commit -m "%MSG%"

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
echo  Done. CI should now build cleanly.
echo  Watch: https://github.com/robert62395-wq/RobsCodeWizard/actions
echo ============================================================
pause