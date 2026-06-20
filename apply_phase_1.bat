@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Phase 1 Overlay (v0.4.1)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run this from the Robs_Code_Wizard project root.
    pause & exit /b 1
)

echo [1/6] Backing up affected files...
if not exist "_backup_v0_4_1" mkdir "_backup_v0_4_1"
for %%F in (app\catalogs\vdt_codes.py app\catalogs\odot_codes.py resources\version.txt CHANGELOG.md) do (
    if exist "%%F" copy /Y "%%F" "_backup_v0_4_1\" >nul
)

echo [2/6] Copying overlay files...
xcopy /Y /E /I overlay\app app\ >nul
xcopy /Y /E /I overlay\tests tests\ >nul
xcopy /Y /E /I overlay\resources resources\ >nul
copy /Y overlay\CHANGELOG.md . >nul

echo [3/6] Installing rapidfuzz...
.venv\Scripts\python -m pip install "rapidfuzz>=3.0" -q

echo [4/6] Seeding translation map (generate-if-missing)...
.venv\Scripts\python -m app.services.seed_translation_map

echo [5/6] Running Phase 1 tests...
.venv\Scripts\python -m pytest tests\test_translation_map.py -v
if errorlevel 1 (
    echo [ERROR] Tests failed. Review output above.
    pause & exit /b 1
)

echo [6/6] Done. Phase 1 applied. Version bumped to v0.4.1.
echo Next: run push_phase_1.bat to commit, tag, and push.
pause
