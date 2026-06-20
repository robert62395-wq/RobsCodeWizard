@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 3 Overlay (v0.4.3)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run this from the Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/5] Backing up affected files...
if not exist "_backup_v0_4_3" mkdir "_backup_v0_4_3"
if exist "app\ui\translation_tab.py" copy /Y "app\ui\translation_tab.py" "_backup_v0_4_3\" >nul
if exist "resources\version.txt" copy /Y "resources\version.txt" "_backup_v0_4_3\" >nul
if exist "CHANGELOG.md" copy /Y "CHANGELOG.md" "_backup_v0_4_3\" >nul

echo [2/5] Copying overlay files into source tree...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/5] Running Phase 3 grammar + code + description tests...
.venv\Scripts\python -m pytest tests\test_grammar_translator.py tests\test_code_translator.py tests\test_description_translator.py -v
if errorlevel 1 (
    echo [ERROR] Phase 3 tests failed.
    pause & exit /b 1
)

echo [4/5] Running full test suite (sanity check)...
.venv\Scripts\python -m pytest tests\ -q

echo [5/5] Done. Phase 3 applied. Version bumped to v0.4.3.
echo.
echo MANUAL STEP: NONE. main_window.py already wires TranslationTab from v0.4.2.1.
echo.
echo Next: run push_phase_3.bat to commit, tag v0.4.3, and push.
pause
