@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 6 Overlay (v0.4.6)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/4] Backing up affected files...
if not exist "_backup_v0_4_6" mkdir "_backup_v0_4_6"
for %%F in (app\services\linework_parser.py app\services\validator.py app\services\suggester.py app\services\description_translator.py resources\version.txt CHANGELOG.md) do (
    if exist "%%F" copy /Y "%%F" "_backup_v0_4_6\" >nul
)

echo [2/4] Copying overlay files into source tree...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/4] Running Phase 6 tests...
.venv\Scripts\python -m pytest tests\test_size_bearing.py tests\test_linework_parser.py tests\test_validator.py tests\test_suggester.py -v
if errorlevel 1 (
    echo [WARN] Some Phase 6 tests failed. Review output above.
    pause
)

echo [4/4] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q

echo.
echo ============================================================
echo  Done. Phase 6 applied. v0.4.6.
echo ============================================================
echo.
echo Launch the app and verify:
echo   - VTD 12, PI1 6, GRBR 24 - no longer flagged invalid
echo   - "EP foobar" in D column - Suggestion shows "EP / FOOBAR"
echo   - Translation tab preserves size on VTD 12 ^<-^> ODOT round trip
echo.
echo Next: run push_phase_6.bat to commit, tag, and push.
pause
