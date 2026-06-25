@echo off
echo =========================================
echo  Push v0.5.5 - Translation Rewrite
echo =========================================

git status --short

set /p CONFIRM="Push v0.5.5? (Y/N): "
if /I not "%CONFIRM%"=="Y" exit /b

git add -A
git commit -m "v0.5.5: Translation tab QTableView rewrite + UX polish"
git tag v0.5.5

git push origin main
git push origin v0.5.5

echo Done.
pause
