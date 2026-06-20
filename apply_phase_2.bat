@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 2 Overlay (v0.4.2)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run this from the Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/6] Backing up affected files...
if not exist "_backup_v0_4_2" mkdir "_backup_v0_4_2"
for %%F in (app\main_window.py resources\version.txt CHANGELOG.md) do (
    if exist "%%F" copy /Y "%%F" "_backup_v0_4_2\" >nul
)

echo [2/6] Copying overlay files into source tree...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/6] Ensuring rapidfuzz is installed...
.venv\Scripts\python -m pip install "rapidfuzz>=3.0" -q

echo [4/6] Running Phase 2 parser + translator tests...
.venv\Scripts\python -m pytest tests\test_linework_parser.py tests\test_line_connect_translator.py -v
if errorlevel 1 (
    echo [ERROR] Tests failed. Review output above.
    pause & exit /b 1
)

echo [5/6] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q
if errorlevel 1 (
    echo [WARN] Full suite has failures - review before pushing.
    pause
)

echo [6/6] Done. Phase 2 applied. Version bumped to v0.4.2.
echo.
echo MANUAL STEP: integrate translation_tab + tools menu into app\main_window.py
echo See app\ui\main_window_patch.py for the exact snippets.
echo.
echo Next: run push_phase_2.bat after main_window.py integration is in place.
pause
