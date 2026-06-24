@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Push v0.5.4
echo ============================================================

git status --short

echo.
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo Aborted.
    pause & exit /b 0
)

set TAG=v0.5.4
set MSG=v0.5.4: Performance rewrite - QTableView + model eliminates 41s populate bottleneck

git add -A
git commit -m "%MSG%"
git tag -a %TAG% -m "%MSG%"

git push origin main
git push origin %TAG%

echo.
echo v0.5.4 pushed. Check GitHub Actions for build.
pause
