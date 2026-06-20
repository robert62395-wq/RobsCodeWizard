@echo off
setlocal enabledelayedexpansion
title Rob's Code Wizard v0.3.9.5.1 (hotfix .1)

:menu
cls
echo ============================================================
echo   Rob's Code Wizard  -  v0.3.9.5.1  (hotfix .1)
echo   Build / Test / Launch Menu
echo ------------------------------------------------------------
echo            __
echo       (___()'`;     Woof.
echo       /,    /`
echo       \\"--\\"
echo ============================================================
echo.
echo   [1] Setup + Test + Launch
echo   [2] Build EXE          (PyInstaller onefile windowed)
echo   [3] Build Installer    (Inno Setup -^> dist\RobsCodeWizard_Setup.exe)
echo   [4] Build All          (EXE then Installer)
echo   [Q] Quit
echo.
set "choice="
set /p choice=Select an option: 

if /i "%choice%"=="1" goto setup_test_launch
if /i "%choice%"=="2" goto build_exe
if /i "%choice%"=="3" goto build_installer
if /i "%choice%"=="4" goto build_all
if /i "%choice%"=="Q" goto end
echo.
echo Invalid choice: "%choice%"
pause
goto menu

:setup_test_launch
echo.
echo --- [1] Setup + Test + Launch ---
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 ( echo ERROR: venv create failed. & pause & goto menu )
) else (
    echo Found existing .venv
)
call .venv\Scripts\activate.bat
if errorlevel 1 ( echo ERROR: venv activate failed. & pause & goto menu )

if exist requirements.txt (
    echo Installing requirements...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 ( echo ERROR: pip install failed. & pause & goto menu )
)

echo.
echo Running pytest (non-blocking)...
python -m pytest -q
echo (pytest exit code: %errorlevel% - continuing)

echo.
echo Launching Rob's Code Wizard...
set "PYTHONPATH=%CD%"
python -u -m app
if errorlevel 1 (
    echo Module launch failed, trying app\main.py with PYTHONPATH...
    python -u app\main.py
)
set "PYTHONPATH="
echo.
echo App exited.
pause
goto menu

:build_exe
echo.
echo --- [2] Build EXE ---
if not exist ".venv\Scripts\python.exe" ( echo .venv missing - run [1] first. & pause & goto menu )
call .venv\Scripts\activate.bat
where pyinstaller >nul 2>&1
if errorlevel 1 ( echo Installing PyInstaller... & python -m pip install pyinstaller )

echo Cleaning previous build artifacts...
if exist build\RobsCodeWizard rmdir /s /q build\RobsCodeWizard
if exist dist\RobsCodeWizard.exe del /q dist\RobsCodeWizard.exe

call :assemble_pyi_args
echo.
echo Running PyInstaller with args:
echo   !PYI_ARGS!
echo.
pyinstaller !PYI_ARGS!
if errorlevel 1 ( echo ERROR: PyInstaller failed. & pause & goto menu )

if exist dist\RobsCodeWizard.exe (
    echo.
    echo Built: dist\RobsCodeWizard.exe
) else (
    echo ERROR: dist\RobsCodeWizard.exe not produced.
)
pause
goto menu

:build_installer
echo.
echo --- [3] Build Installer ---
if not exist dist\RobsCodeWizard.exe (
    echo dist\RobsCodeWizard.exe missing - building EXE first...
    call :build_exe_inline
    if errorlevel 1 ( echo ERROR: EXE build failed. & pause & goto menu )
)
if not exist build\installer.iss ( echo ERROR: build\installer.iss missing. & pause & goto menu )

call :find_iscc
if "!ISCC_EXE!"=="" (
    echo ERROR: Inno Setup compiler not found.
    echo Install from https://jrsoftware.org/isdl.php
    pause & goto menu
)

echo Using compiler: !ISCC_EXE!
"!ISCC_EXE!" build\installer.iss
if errorlevel 1 ( echo ERROR: Inno Setup compile failed. & pause & goto menu )

if exist dist\RobsCodeWizard_Setup.exe (
    echo.
    echo Built: dist\RobsCodeWizard_Setup.exe
)
pause
goto menu

:build_all
echo.
echo --- [4] Build All ---
call :build_exe_inline
if errorlevel 1 ( echo ERROR: EXE build failed. & pause & goto menu )
call :build_installer_inline
pause
goto menu

:assemble_pyi_args
set "PYI_ARGS=--noconfirm --clean --onefile --windowed --name RobsCodeWizard"

if exist "resources\icon.ico" (
    echo Found: resources\icon.ico   -- using as app icon
    set "PYI_ARGS=!PYI_ARGS! --icon "resources\icon.ico""
) else (
    if exist "app\assets\icon.ico" (
        echo Found: app\assets\icon.ico   -- using as app icon
        set "PYI_ARGS=!PYI_ARGS! --icon "app\assets\icon.ico""
    ) else (
        echo Skipping: icon              ^(not found^)
    )
)

if exist "app\assets\" (
    echo Found: app\assets\          -- bundling
    set "PYI_ARGS=!PYI_ARGS! --add-data "app\assets;app\assets""
)
if exist "app\data\" (
    echo Found: app\data\            -- bundling
    set "PYI_ARGS=!PYI_ARGS! --add-data "app\data;app\data""
)
if exist "resources\" (
    echo Found: resources\           -- bundling
    set "PYI_ARGS=!PYI_ARGS! --add-data "resources;resources""
)

set "PYI_ARGS=!PYI_ARGS! app\main.py"
exit /b 0

:build_exe_inline
if not exist ".venv\Scripts\python.exe" ( python -m venv .venv )
call .venv\Scripts\activate.bat
where pyinstaller >nul 2>&1
if errorlevel 1 ( python -m pip install pyinstaller )
call :assemble_pyi_args
pyinstaller !PYI_ARGS!
exit /b %errorlevel%

:find_iscc
set "ISCC_EXE="
where iscc.exe >nul 2>&1
if not errorlevel 1 ( set "ISCC_EXE=iscc.exe" )
if "!ISCC_EXE!"=="" if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if "!ISCC_EXE!"=="" if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if "!ISCC_EXE!"=="" if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
if "!ISCC_EXE!"=="" if exist "%LOCALAPPDATA%\Programs\Inno Setup 5\ISCC.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 5\ISCC.exe"
if "!ISCC_EXE!"=="" if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
exit /b 0

:build_installer_inline
call :find_iscc
if "!ISCC_EXE!"=="" ( echo ERROR: ISCC.exe not found. & exit /b 1 )
echo Using compiler: !ISCC_EXE!
"!ISCC_EXE!" build\installer.iss
exit /b %errorlevel%

:end
echo Bye.
endlocal
exit /b 0
