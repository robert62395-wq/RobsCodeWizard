@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.5.5
echo ============================================================

git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

set TAG=v0.5.5
set MSG=v0.5.5: First-launch UX polish and Translation tab model-view cleanup

git add -A
git commit -m "%MSG%"
git tag -a %TAG% -m "%MSG%"

if errorlevel 1 (
    echo [ERROR] Tag failed. It may already exist.
    pause & exit /b 1
)

git push origin main
git push origin %TAG%

echo.
echo v0.5.5 pushed. Check GitHub Actions for build.
pause
``