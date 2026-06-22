@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 7 Overlay (v0.4.7)
echo  Dialect-aware export grammar dispatch
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/4] Backing up affected files...
if not exist "_backup_v0_4_7" mkdir "_backup_v0_4_7"
for %%F in (app\services\odot_exporter.py app\ui\export_tab.py resources\version.txt CHANGELOG.md) do (
    if exist "%%F" copy /Y "%%F" "_backup_v0_4_7\" >nul
)

echo [2/4] Copying overlay files into source tree...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/4] Running Phase 7 tests (normalizer + exporter)...
.venv\Scripts\python -m pytest tests\test_grammar_normalizer.py tests\test_odot_exporter.py -v
if errorlevel 1 (
    echo [ERROR] Phase 7 tests failed.
    pause & exit /b 1
)

echo [4/4] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q

echo.
echo ============================================================
echo  Done. Phase 7 applied. v0.4.7.
echo ============================================================
echo.
echo Launch the app and check the Export tab:
echo   - VDT code set: Civil3D button uses VDT grammar, OpenRoads disabled
echo   - ODOT code set: both buttons enabled, grammars dispatch correctly
echo.
echo Next: run push_phase_7.bat to commit, tag, and push.
pause
