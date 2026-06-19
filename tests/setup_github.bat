@echo off
setlocal EnableDelayedExpansion
title Rob's Code Wizard - GitHub Initial Push (v0.3.9.3.0)

REM ============================================================
REM  setup_github.bat
REM  One-shot initial repo init + first push to GitHub
REM  Baseline: v0.3.9.3.0  (last downloaded build)
REM  Avoids gh CLI / AppData writes. Uses PAT + Windows Cred Mgr.
REM  Auto-tags the initial commit on success.
REM ============================================================

echo.
echo ============================================================
echo   Rob's Code Wizard - GitHub Initial Repo Setup
echo   Baseline version: v0.3.9.3.0
echo ============================================================
echo.

REM --- 0. Verify git is available ------------------------------
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git was not found on PATH.
    echo         Install Git for Windows or PortableGit and re-run.
    pause
    exit /b 1
)

REM --- 1. Collect inputs ---------------------------------------
set /p GH_USER=GitHub username: 
if "%GH_USER%"=="" (
    echo [ERROR] Username is required.
    pause
    exit /b 1
)

set /p REPO_NAME=Repository name if "%REPO_NAME%"=="" set REPO_NAME=RobsCodeWizard

set /p BRANCH=Default branch if "%BRANCH%"=="" set BRANCH=main

set /p COMMIT_MSG=Initial commit message [Initial commit v0.3.9.3.0]: 
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit v0.3.9.3.0

set /p TAG_NAME=Tag name to apply [v0.3.9.3.0]: 
if "%TAG_NAME%"=="" set TAG_NAME=v0.3.9.3.0

set /p TAG_MSG=Tag message [Baseline: v0.3.9.3.0 (last downloaded build)]: 
if "%TAG_MSG%"=="" set TAG_MSG=Baseline: v0.3.9.3.0 (last downloaded build)

set /p GIT_EMAIL=Git email (for commit author): 
set /p GIT_NAME=Git display name (for commit author): 

echo.
echo ------------------------------------------------------------
echo  Username   : %GH_USER%
echo  Repo       : %REPO_NAME%
echo  Branch     : %BRANCH%
echo  Commit msg : %COMMIT_MSG%
echo  Tag        : %TAG_NAME%
echo  Tag msg    : %TAG_MSG%
echo ------------------------------------------------------------
echo.
echo NOTE: Create the empty repo on github.com FIRST:
echo       https://github.com/new
echo       (no README, no .gitignore, no license - keep it empty)
echo.
pause

REM --- 2. Configure git identity (local to this repo) ----------
if not "%GIT_NAME%"=="" git config user.name "%GIT_NAME%"
