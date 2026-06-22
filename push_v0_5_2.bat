@echo off
setlocal
set TAG=v0.5.2
set MSG=v0.5.2: Status bar + help icon foundation (Phase 2 of 7 toward v1.0)

git status --short
set /p CONFIRM="Proceed with commit, tag, and push? (Y/N): "
if /I not "%CONFIRM%"=="Y" exit /b 0

git add -A
git commit -m "%MSG%"
git tag -a %TAG% -m "%MSG%"
if errorlevel 1 (
    echo Tag failed.
    pause & exit /b 1
)
git push origin main
git push origin %TAG%
pause