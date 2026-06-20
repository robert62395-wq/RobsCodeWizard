@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 5 Overlay (v0.4.5)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/6] Backing up affected files...
if not exist "_backup_v0_4_5" mkdir "_backup_v0_4_5"
for %%F in (app\ui\main_window.py app\ui\convert_line_connect_dialog.py app\services\line_connect_translator.py app\services\odot_exporter.py app\ui\export_tab.py resources\version.txt CHANGELOG.md) do (
    if exist "%%F" copy /Y "%%F" "_backup_v0_4_5\" >nul
)

echo [2/6] Copying overlay files...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/6] Patching app\ui\main_window.py to add Export tab...
.venv\Scripts\python overlay\patch_main_window.py
if errorlevel 1 (
    echo [ERROR] main_window.py patch failed. Review output above.
    pause & exit /b 1
)

echo [4/6] Running Phase 5 tests (exporter + line-connect)...
.venv\Scripts\python -m pytest tests\test_odot_exporter.py tests\test_line_connect_translator.py -v
if errorlevel 1 (
    echo [ERROR] Phase 5 tests failed.
    pause & exit /b 1
)

echo [5/6] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q

echo [6/6] Done. Phase 5 applied. v0.4.5.
echo.
echo Launch the app - "Export" tab should appear after "Modified Data".
echo Tools > Convert Line Connect Codes... now supports BOTH directions.
echo.
echo Next: run push_phase_5.bat to commit, tag, and push.
pause
