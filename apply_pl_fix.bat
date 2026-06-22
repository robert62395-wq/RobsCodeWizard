@echo off
setlocal
echo ============================================================
echo  Rob's Code Wizard - v0.4.4.1 hotfix (Add PL to ODOT)
echo ============================================================

if not exist "app\main.py" (
    echo [ERROR] Run from Robs_Code_Wizard project root.
    pause & exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found.
    pause & exit /b 1
)

if not exist "seed_translation_map_standalone.py" (
    echo [ERROR] seed_translation_map_standalone.py not found.
    echo         Run the seeder bundle first (you already have this from v0.4.4).
    pause & exit /b 1
)

echo [1/4] Backing up ODOT_CODES.xlsx and translation_map.json...
if not exist "_backup_v0_4_4_1" mkdir "_backup_v0_4_4_1"
if exist "resources\ODOT_CODES.xlsx" copy /Y "resources\ODOT_CODES.xlsx" "_backup_v0_4_4_1\" >nul
if exist "app\data\ODOT_CODES.xlsx" copy /Y "app\data\ODOT_CODES.xlsx" "_backup_v0_4_4_1\" >nul
if exist "app\data\translation_map.json" copy /Y "app\data\translation_map.json" "_backup_v0_4_4_1\" >nul

echo [2/4] Ensuring openpyxl is installed...
.venv\Scripts\python -m pip install openpyxl -q
if errorlevel 1 (
    echo [ERROR] pip install openpyxl failed.
    pause & exit /b 1
)

echo [3/4] Adding PL to ODOT_CODES.xlsx (idempotent)...
.venv\Scripts\python add_pl_to_odot_catalog.py
if errorlevel 1 (
    echo [ERROR] PL catalog patch failed.
    pause & exit /b 1
)

echo [4/4] Reseeding translation_map.json...
.venv\Scripts\python seed_translation_map_standalone.py
if errorlevel 1 (
    echo [ERROR] Reseeding failed.
    pause & exit /b 1
)

echo.
echo ============================================================
echo  Done. PL added to ODOT catalog and translation map reseeded.
echo  Restart Rob's Code Wizard to see PL in the Translation tab.
echo ============================================================
pause
