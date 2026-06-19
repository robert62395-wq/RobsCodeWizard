@echo off
setlocal EnableDelayedExpansion
title Rob's Code Wizard - Tag and Push Release

echo.
echo ============================================================
echo   Rob's Code Wizard - Tag and Push Release
echo ============================================================
echo.

REM --- 0. Verify git -------------------------------------------
echo [Step 0] Checking for git...
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git was not found on PATH.
    goto :end_pause
)

REM --- 1. Verify inside a repo ---------------------------------
echo [Step 1] Verifying this is a git repo...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This folder is not a git repository.
    echo         Run setup_github.bat first.
    goto :end_pause
)

REM --- 2. Verify remote ----------------------------------------
echo [Step 2] Verifying remote 'origin'...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No remote named 'origin' is configured.
    goto :end_pause
)

REM --- 3. Warn on dirty tree -----------------------------------
echo [Step 3] Checking for uncommitted changes...
set "DIRTY=0"
git diff --quiet
if errorlevel 1 set "DIRTY=1"
git diff --cached --quiet
if errorlevel 1 set "DIRTY=1"
if "!DIRTY!"=="1" (
    echo [WARN] You have uncommitted or staged changes.
    echo        The tag will point at your LAST COMMIT only.
    set "CONTINUE="
    set /p CONTINUE=Continue anyway? (Y/N): 
    if /I not "!CONTINUE!"=="Y" (
        echo Aborted.
        goto :end_pause
    )
)

REM --- 4. Collect tag info -------------------------------------
echo.
echo [Step 4] Collecting tag info...
set "TAG_NAME="
set /p TAG_NAME=Tag name (e.g. v0.3.9.4): 
if "!TAG_NAME!"=="" (
    echo [ERROR] Tag name is required.
    goto :end_pause
)

set "TAG_MSG="
set /p TAG_MSG=Tag message [Release !TAG_NAME!]: 
if "!TAG_MSG!"=="" set "TAG_MSG=Release !TAG_NAME!"

echo.
echo ------------------------------------------------------------
echo  Tag      : !TAG_NAME!
echo  Message  : !TAG_MSG!
echo ------------------------------------------------------------
echo.
pause

REM --- 5. Check existing tag -----------------------------------
echo.
echo [Step 5] Checking if tag already exists...
git rev-parse "!TAG_NAME!" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Tag !TAG_NAME! already exists locally.
    set "REPLACE="
    set /p REPLACE=Delete and recreate it? (Y/N): 
    if /I "!REPLACE!"=="Y" (
        git tag -d !TAG_NAME!
        git push origin :refs/tags/!TAG_NAME! >nul 2>&1
    ) else (
        echo Aborted.
        goto :end_pause
    )
)

REM --- 6. Create annotated tag ---------------------------------
echo.
echo [Step 6] Creating annotated tag...
git tag -a !TAG_NAME! -m "!TAG_MSG!"
if errorlevel 1 goto :fail

REM --- 7. Push tag ---------------------------------------------
echo.
echo [Step 7] Pushing tag !TAG_NAME! to origin...
git push origin !TAG_NAME!
if errorlevel 1 goto :fail

REM --- 8. Summary ----------------------------------------------
for /f "tokens=*" %%U in ('git remote get-url origin') do set "REMOTE_URL=%%U"
set "REMOTE_URL=!REMOTE_URL:.git=!"

echo.
echo ============================================================
echo   SUCCESS - Tag !TAG_NAME! pushed.
echo.
echo   GitHub Actions will build and publish the release.
echo   Watch progress at:
echo     !REMOTE_URL!/actions
echo.
echo   Release page (once workflow completes):
echo     !REMOTE_URL!/releases/tag/!TAG_NAME!
echo ============================================================
goto :end_pause

:fail
echo.
echo ============================================================
echo   [ERROR] Tag/push failed. See messages above.
echo ============================================================

:end_pause
echo.
echo Press any key to close this window...
pause >nul
endlocal
exit /b