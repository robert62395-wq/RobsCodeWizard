@echo off
title Rob's Code Wizard - v0.3.9.4 run.bat
setlocal
cd /d %~dp0

echo ============================================================
echo   Rob's Code Wizard - v0.3.9.4
echo   One-click setup / test / launch
echo ============================================================
echo.

if not exist .venv (
    echo [1/4] Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: failed to create venv. Is Python on PATH?
        pause
        exit /b 1
    )
    set FIRST_RUN=1
) else (
    echo [1/4] Reusing existing virtual environment .venv
    set FIRST_RUN=0
)

echo [2/4] Activating venv ...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: failed to activate venv.
    pause
    exit /b 1
)

if "%FIRST_RUN%"=="1" (
    echo [3/4] Installing requirements ^(first run only^) ...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: pip install failed.
        pause
        exit /b 1
    )
) else (
    echo [3/4] Skipping pip install ^(venv already set up^)
)

echo.
echo [4/4] Running test suite ...
python -m pytest -q tests
if errorlevel 1 (
    echo.
    echo WARNING: some tests failed. Review the output above.
) else (
    echo.
    echo All tests passed.
)

echo.
set /p LAUNCH="Launch Rob's Code Wizard now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    echo.
    echo Launching app ...
    python launcher.py
) else (
    echo.
    echo Skipped launch. You can run "python launcher.py" any time after activating the venv.
)

echo.
pause
endlocal