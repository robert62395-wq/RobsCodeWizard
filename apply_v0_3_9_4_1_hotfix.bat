@echo off
title Apply v0.3.9.4.1 Hotfix - Rob's Code Wizard

echo.
echo ============================================================
echo   Apply v0.3.9.4.1 Hotfix
echo   - Fixes _populate_table freeze on large files
echo   - Defers codeset-switch revalidation
echo   - Bumps version to 0.3.9.4.1
echo ============================================================
echo.

echo [Step 0] Verifying project layout...
if not exist "app\ui\main_window.py" goto :no_mainwin
if not exist "app\__init__.py" goto :no_init
if not exist "_apply_hotfix1.py" goto :no_helper
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
copy /Y "app\ui\main_window.py" "app\ui\main_window.py.hotfix1.bak" >nul
echo   Backed up: app\ui\main_window.py.hotfix1.bak
copy /Y "app\__init__.py" "app\__init__.py.hotfix1.bak" >nul
echo   Backed up: app\__init__.py.hotfix1.bak

echo.
echo [Step 3] Running Python patch helper...
"%PYEXE%" "_apply_hotfix1.py"
if errorlevel 1 goto :fail

echo.
echo [Step 4] Verifying patches...

findstr /C:"setUpdatesEnabled(False)" "app\ui\main_window.py" >nul
if errorlevel 1 goto :no_updates_guard
echo   OK: _populate_table has setUpdatesEnabled guard.

findstr /C:"_revalidate_and_repopulate" "app\ui\main_window.py" >nul
if errorlevel 1 goto :no_defer
echo   OK: _revalidate_and_repopulate exists.

findstr /C:"QTimer.singleShot" "app\ui\main_window.py" >nul
if errorlevel 1 goto :no_timer
echo   OK: codeset switch uses QTimer.singleShot.

findstr /C:"0.3.9.4.1" "app\__init__.py" >nul
if errorlevel 1 goto :no_version
echo   OK: version is 0.3.9.4.1.

goto :success

:no_updates_guard
echo [ERROR] _populate_table was not patched.
goto :fail

:no_defer
echo [ERROR] _revalidate_and_repopulate method missing.
goto :fail

:no_timer
echo [ERROR] QTimer.singleShot not found in main_window.py.
goto :fail

:no_version
echo [ERROR] app\__init__.py version not bumped.
goto :fail

:success
echo.
echo ============================================================
echo   SUCCESS - v0.3.9.4.1 hotfix applied.
echo.
echo   Backups created:
echo     - app\ui\main_window.py.hotfix1.bak
echo     - app\__init__.py.hotfix1.bak
echo.
echo   Next steps:
echo     1. Test from source:
echo          python launcher.py
echo        Open VDT file, switch ODOT to VDT - should NOT freeze.
echo     2. Rebuild EXE:
echo          pyinstaller --noconfirm --onefile --windowed --name RobsCodeWizard --add-data "resources;resources" app\main.py
echo     3. Test: dist\RobsCodeWizard.exe
echo     4. Commit: git add -A and git commit -m "v0.3.9.4.1: populate_table + codeset hotfix"
echo     5. Tag:    tag_release.bat (use v0.3.9.4.1)
echo ============================================================
goto :end_pause

:no_mainwin
echo [ERROR] app\ui\main_window.py not found. Run from project root.
goto :end_pause

:no_init
echo [ERROR] app\__init__.py not found.
goto :end_pause

:no_helper
echo [ERROR] _apply_hotfix1.py not found next to this .bat.
goto :end_pause

:no_python
echo [ERROR] No Python found (no .venv and no python on PATH).
goto :end_pause

:fail
echo.
echo ============================================================
echo   [ERROR] Patch failed. See messages above.
echo.
echo   To restore:
echo     copy /Y app\ui\main_window.py.hotfix1.bak app\ui\main_window.py
echo     copy /Y app\__init__.py.hotfix1.bak app\__init__.py
echo ============================================================

:end_pause
echo.
echo Press any key to close this window...
pause >nul
exit /b
