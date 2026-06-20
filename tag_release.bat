@echo off
setlocal EnableDelayedExpansion
title Rob's Code Wizard - Tag and Push Release (v0.3.9.5.1.4)

echo.
echo ============================================================
echo   Rob's Code Wizard - Tag and Push Release
echo ============================================================
echo.

set "ABORT=0"

echo [Step 0] Checking for git...
where git >nul 2>&1
if errorlevel 1 ( echo [ERROR] git was not found on PATH. & goto :end_pause )

echo [Step 1] Verifying this is a git repo...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 ( echo [ERROR] Not a git repo. & goto :end_pause )

echo [Step 2] Verifying remote 'origin'...
git remote get-url origin >nul 2>&1
if errorlevel 1 ( echo [ERROR] No remote 'origin' configured. & goto :end_pause )

echo [Step 3] Checking for uncommitted changes...
set "DIRTY=0"
git diff --quiet
if errorlevel 1 set "DIRTY=1"
git diff --cached --quiet
if errorlevel 1 set "DIRTY=1"
if "!DIRTY!"=="1" call :prompt_dirty
if "!ABORT!"=="1" goto :end_pause

echo.
echo [Step 4] Collecting tag info...
set "TAG_NAME=%~1"
if "!TAG_NAME!"=="" (
    set /p TAG_NAME="Tag name (e.g. v0.3.9.5.1) "
)
if "!TAG_NAME!"=="" ( echo [ERROR] Tag name is required. & goto :end_pause )

REM Validate tag pattern via PowerShell. Accept vMAJOR.MINOR.PATCH with up to 2 extra .N
set "VALID=0"
for /f "usebackq delims=" %%V in (`powershell -NoProfile -Command "if ('!TAG_NAME!' -match '^v[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+){0,2}$') {'1'} else {'0'}"`) do set "VALID=%%V"
if not "!VALID!"=="1" (
    call :prompt_invalid_tag
    if "!ABORT!"=="1" goto :end_pause
)

set "TAG_MSG=%~2"
if "!TAG_MSG!"=="" (
    set /p TAG_MSG="Tag message [default Release !TAG_NAME!] "
)
if "!TAG_MSG!"=="" set "TAG_MSG=Release !TAG_NAME!"

echo.
echo ------------------------------------------------------------
echo  Tag      : !TAG_NAME!
echo  Message  : !TAG_MSG!
echo ------------------------------------------------------------
pause

echo.
echo [Step 5] Checking if tag already exists...
git rev-parse "!TAG_NAME!" >nul 2>&1
if not errorlevel 1 call :prompt_replace_tag
if "!ABORT!"=="1" goto :end_pause

echo.
echo [Step 6] Creating annotated tag...
git tag -a !TAG_NAME! -m "!TAG_MSG!"
if errorlevel 1 goto :fail

echo.
echo [Step 7] Pushing tag !TAG_NAME! to origin...
git push origin !TAG_NAME!
if errorlevel 1 goto :fail

for /f "tokens=*" %%U in ('git remote get-url origin') do set "REMOTE_URL=%%U"
set "REMOTE_URL=!REMOTE_URL:.git=!"
echo.
echo ============================================================
echo   SUCCESS - Tag !TAG_NAME! pushed.
echo   Actions: !REMOTE_URL!/actions
echo   Release: !REMOTE_URL!/releases/tag/!TAG_NAME!
echo ============================================================
goto :end_pause

:prompt_dirty
echo [WARN] You have uncommitted or staged changes.
echo        The tag will point at your LAST COMMIT only.
set "ANS="
set /p ANS="Continue anyway (Y/N) "
if /I "!ANS!"=="Y" ( set "ABORT=0" & exit /b 0 )
echo Aborted.
set "ABORT=1"
exit /b 0

:prompt_replace_tag
echo [WARN] Tag !TAG_NAME! already exists locally.
set "ANS="
set /p ANS="Delete and recreate (Y/N) "
if /I "!ANS!"=="Y" (
    git tag -d !TAG_NAME!
    git push origin :refs/tags/!TAG_NAME! >nul 2>&1
    set "ABORT=0"
    exit /b 0
)
echo Aborted.
set "ABORT=1"
exit /b 0

:prompt_invalid_tag
echo [WARN] Tag !TAG_NAME! does not match recommended pattern.
echo        Expected: vMAJOR.MINOR.PATCH[.W[.X]]  e.g. v0.3.9.5.1
set "ANS="
set /p ANS="Use it anyway (Y/N) "
if /I "!ANS!"=="Y" ( set "ABORT=0" & exit /b 0 )
echo Aborted.
set "ABORT=1"
exit /b 0

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
