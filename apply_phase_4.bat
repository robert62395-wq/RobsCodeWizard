@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 4 Overlay (v0.4.4)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/5] Backing up affected files...
if not exist "_backup_v0_4_4" mkdir "_backup_v0_4_4"
if exist "app\services\offsets.py" copy /Y "app\services\offsets.py" "_backup_v0_4_4\" >nul
if exist "resources\version.txt" copy /Y "resources\version.txt" "_backup_v0_4_4\" >nul
if exist "CHANGELOG.md" copy /Y "CHANGELOG.md" "_backup_v0_4_4\" >nul

echo [2/5] Copying overlay files into source tree...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/5] Running Phase 4 offset tests...
.venv\Scripts\python -m pytest tests\test_offsets.py -v
if errorlevel 1 (
    echo [ERROR] Phase 4 tests failed.
    pause & exit /b 1
)

echo [4/5] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q

echo [5/5] Done. Phase 4 applied. v0.4.4.
echo Next: run push_phase_4.bat to commit, tag, and push.
pause
