@echo off
setlocal
set TAG=v0.4.6.1
set MSG=v0.4.6.1 hotfix: validator/suggester check full token before stripped suffix (fixes PI1 not matching itself)

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
