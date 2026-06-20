@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - v0.4.2.1 main_window.py integration
echo ============================================================

if not exist "app\ui\main_window.py" (
    echo [ERROR] Run this from the Robs_Code_Wizard project root.
    echo         app\ui\main_window.py not found.
    pause & exit /b 1
)

echo [1/4] Backing up current app\ui\main_window.py...
if not exist "_backup_v0_4_2_main_window" mkdir "_backup_v0_4_2_main_window"
copy /Y "app\ui\main_window.py" "_backup_v0_4_2_main_window\" >nul

echo [2/4] Copying edited main_window.py...
copy /Y "overlay\app\ui\main_window.py" "app\ui\main_window.py" >nul

echo [3/4] Verifying full test suite collects and runs...
.venv\Scripts\python -m pytest tests\ -q
if errorlevel 1 (
    echo [WARN] Some tests failed. Review output above before pushing.
    pause
) else (
    echo [OK] All tests pass.
)

echo [4/4] Done. Launch the app to verify:
echo   - "Translation" tab appears between Raw Data and Modified Data
echo   - Tools menu has "Convert Line Connect Codes..." (enabled after Open)
echo.
echo Next: run push_hotfix.bat to tag v0.4.2.1 and push.
pause
