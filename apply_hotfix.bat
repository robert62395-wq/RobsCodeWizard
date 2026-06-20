@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - v0.4.1 Hotfix (restore app.__version__)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run this from the Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/4] Backing up current app\__init__.py...
if not exist "_backup_v0_4_1_hotfix" mkdir "_backup_v0_4_1_hotfix"
if exist "app\__init__.py" copy /Y "app\__init__.py" "_backup_v0_4_1_hotfix\" >nul

echo [2/4] Restoring app\__init__.py with version-from-file loader...
copy /Y "overlay\app\__init__.py" "app\__init__.py" >nul

echo [3/4] Verifying test collection...
.venv\Scripts\python -m pytest tests\ --collect-only -q
if errorlevel 1 (
    echo [ERROR] Collection still failing. Review output above.
    pause & exit /b 1
)

echo [4/4] Running full test suite...
.venv\Scripts\python -m pytest tests\ -v
if errorlevel 1 (
    echo [WARN] Some tests failed. Review output above.
    pause & exit /b 1
)

echo.
echo ============================================================
echo  Hotfix applied. Next: run push_hotfix.bat
echo ============================================================
pause
