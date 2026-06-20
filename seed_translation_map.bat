@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - Seed Translation Map (Auto)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found. Run setup first to create it.
    pause & exit /b 1
)

echo [1/3] Installing dependencies (rapidfuzz, openpyxl)...
.venv\Scripts\python -m pip install rapidfuzz openpyxl -q
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause & exit /b 1
)

echo [2/3] Running standalone seeder...
.venv\Scripts\python seed_translation_map_standalone.py
if errorlevel 1 (
    echo [ERROR] Seeder failed. See output above.
    pause & exit /b 1
)

echo [3/3] Done.
echo.
echo NEXT: Restart Rob's Code Wizard. The Translation tab should show entries.
pause
