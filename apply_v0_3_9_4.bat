@echo off
title Apply v0.3.9.4 Patch - Rob's Code Wizard

echo.
echo ============================================================
echo   Apply v0.3.9.4 Patch
echo   - Replaces app\ui\linework_fix_overlay.py with Qt version
echo   - Patches app\ui\main_window.py to use the overlay
echo   - Verifies app\__init__.py version is 0.3.9.4
echo ============================================================
echo.

echo [Step 0] Verifying project layout...
if not exist "app\ui\main_window.py" goto :no_mainwin
if not exist "app\services\linework_fix.py" goto :no_linework
if not exist "app\__init__.py" goto :no_init
if not exist "_apply_v0_3_9_4.py" goto :no_helper
echo   Project layout OK.

echo [Step 1] Locating Python...
set PYEXE=
if exist ".venv\Scripts\python.exe" set PYEXE=.venv\Scripts\python.exe
if not defined PYEXE goto :try_path
goto :py_found

:try_path
where python >nul 2>&1
if errorlevel 1 goto :no_python
set PYEXE=python

:py_found
echo   Using: %PYEXE%

echo.
echo [Step 2] Backing up files...
if not exist "app\ui\linework_fix_overlay.py" goto :skip_overlay_bak
copy /Y "app\ui\linework_fix_overlay.py" "app\ui\linework_fix_overlay.py.bak" >nul
echo   Backed up: app\ui\linework_fix_overlay.py.bak

:skip_overlay_bak
copy /Y "app\ui\main_window.py" "app\ui\main_window.py.bak" >nul
echo   Backed up: app\ui\main_window.py.bak

echo.
echo [Step 3] Running Python patch helper...
"%PYEXE%" "_apply_v0_3_9_4.py"
if errorlevel 1 goto :fail

echo.
echo [Step 4] Verifying patches...

findstr /C:"LineworkFixOverlay" "app\ui\main_window.py" >nul
if errorlevel 1 goto :no_overlay_ref
echo   OK: main_window.py references LineworkFixOverlay.

findstr /C:"LineworkFixDialog" "app\ui\main_window.py" >nul
if errorlevel 1 goto :dialog_gone
echo   [WARN] main_window.py still references LineworkFixDialog.
goto :after_dialog_check

:dialog_gone
echo   OK: main_window.py no longer references LineworkFixDialog.

:after_dialog_check
findstr /C:"class LineworkFixOverlay" "app\ui\linework_fix_overlay.py" >nul
if errorlevel 1 goto :no_overlay_class
echo   OK: linework_fix_overlay.py contains LineworkFixOverlay class.

findstr /C:"PySide6" "app\ui\linework_fix_overlay.py" >nul
if errorlevel 1 goto :no_pyside
echo   OK: linework_fix_overlay.py uses PySide6.

findstr /C:"0.3.9.4" "app\__init__.py" >nul
if errorlevel 1 goto :version_missing
echo   OK: app\__init__.py version is 0.3.9.4.
goto :success

:version_missing
echo   [WARN] app\__init__.py does not contain 0.3.9.4.
echo          Open it and ensure: __version__ = "0.3.9.4"

:success
echo.
echo ============================================================
echo   SUCCESS - v0.3.9.4 patch applied.
echo.
echo   Backups created:
echo     - app\ui\main_window.py.bak
echo     - app\ui\linework_fix_overlay.py.bak (if file existed)
echo.
echo   Next steps:
echo     1. .venv\Scripts\activate
echo     2. pyinstaller --noconfirm --onefile --windowed --name RobsCodeWizard --add-data "assets;assets" app\main.py
echo     3. dist\RobsCodeWizard.exe
echo     4. git add -A
echo     5. git commit -m "v0.3.9.4: Phase 4 overlay"
echo     6. tag_release.bat (enter v0.3.9.4)
echo ============================================================
goto :end_pause

:no_mainwin
echo [ERROR] app\ui\main_window.py not found.
echo         Run this from the project root folder.
goto :end_pause

:no_linework
echo [ERROR] app\services\linework_fix.py not found.
goto :end_pause

:no_init
echo [ERROR] app\__init__.py not found.
goto :end_pause

:no_helper
echo [ERROR] _apply_v0_3_9_4.py not found next to this .bat file.
echo         Extract BOTH files from the zip into the same folder.
goto :end_pause

:no_python
echo [ERROR] No Python found.
echo         No .venv folder and no python on PATH.
goto :end_pause

:no_overlay_ref
echo [ERROR] main_window.py was not patched.
goto :fail

:no_overlay_class
echo [ERROR] linework_fix_overlay.py is missing the class.
goto :fail

:no_pyside
echo [ERROR] linework_fix_overlay.py does not import PySide6.
goto :fail

:fail
echo.
echo ============================================================
echo   [ERROR] Patch failed. See messages above.
echo.
echo   To restore the originals:
echo     copy /Y app\ui\main_window.py.bak app\ui\main_window.py
echo     copy /Y app\ui\linework_fix_overlay.py.bak app\ui\linework_fix_overlay.py
echo ============================================================

:end_pause
echo.
echo Press any key to close this window...
pause >nul
exit /b
