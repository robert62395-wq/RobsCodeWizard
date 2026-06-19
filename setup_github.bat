@echo off
setlocal EnableDelayedExpansion
title Rob's Code Wizard - GitHub Initial Push (v0.3.9.3.0)

echo.
echo ============================================================
echo   Rob's Code Wizard - GitHub Initial Repo Setup
echo   Baseline version: v0.3.9.3.0
echo ============================================================
echo.

REM --- 0. Verify git is available ------------------------------
echo [Step 0] Checking for git...
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git was not found on PATH.
    goto :end_pause
)
echo   git found.
echo.

REM --- 1. Collect inputs ---------------------------------------
echo [Step 1] Collecting inputs...
echo.

set "GH_USER="
set /p GH_USER=GitHub username: 
if "!GH_USER!"=="" (
    echo [ERROR] Username is required.
    goto :end_pause
)

set "REPO_NAME="
set /p REPO_NAME=Repository name [RobsCodeWizard]: 
if "!REPO_NAME!"=="" set "REPO_NAME=RobsCodeWizard"

set "BRANCH="
set /p BRANCH=Default branch [main]: 
if "!BRANCH!"=="" set "BRANCH=main"

set "COMMIT_MSG="
set /p COMMIT_MSG=Initial commit message [Initial commit v0.3.9.3.0]: 
if "!COMMIT_MSG!"=="" set "COMMIT_MSG=Initial commit v0.3.9.3.0"

set "TAG_NAME="
set /p TAG_NAME=Tag name to apply [v0.3.9.3.0]: 
if "!TAG_NAME!"=="" set "TAG_NAME=v0.3.9.3.0"

set "TAG_MSG="
set /p TAG_MSG=Tag message [Baseline v0.3.9.3.0 last downloaded build]: 
if "!TAG_MSG!"=="" set "TAG_MSG=Baseline v0.3.9.3.0 last downloaded build"

set "GIT_EMAIL="
set /p GIT_EMAIL=Git email (for commit author): 

set "GIT_NAME="
set /p GIT_NAME=Git display name (for commit author): 

echo.
echo ------------------------------------------------------------
echo  Username   : !GH_USER!
echo  Repo       : !REPO_NAME!
echo  Branch     : !BRANCH!
echo  Commit msg : !COMMIT_MSG!
echo  Tag        : !TAG_NAME!
echo  Tag msg    : !TAG_MSG!
echo  Author name: !GIT_NAME!
echo  Author mail: !GIT_EMAIL!
echo ------------------------------------------------------------
echo.
echo Make sure the EMPTY repo already exists at:
echo   https://github.com/!GH_USER!/!REPO_NAME!
echo (no README / no .gitignore / no license)
echo.
pause

REM --- 2. Configure git identity (local) -----------------------
echo.
echo [Step 2] Configuring git identity...
if not "!GIT_NAME!"==""  git config user.name  "!GIT_NAME!"
if not "!GIT_EMAIL!"=="" git config user.email "!GIT_EMAIL!"

REM --- 3. Credential helper ------------------------------------
echo.
echo [Step 3] Setting credential helper to Windows Credential Manager...
git config --local credential.helper manager

REM --- 4. Create .gitignore if missing -------------------------
echo.
echo [Step 4] Ensuring .gitignore exists...
if not exist ".gitignore" (
    echo   Creating default .gitignore...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *.pyo
        echo .venv/
        echo venv/
        echo env/
        echo.
        echo # Build artifacts
        echo build/
        echo dist/
        echo *.spec
        echo *.egg-info/
        echo.
        echo # Inno Setup
        echo Output/
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo.
        echo # OS
        echo Thumbs.db
        echo Desktop.ini
        echo .DS_Store
        echo.
        echo # Logs / temp
        echo *.log
        echo *.tmp
        echo.
        echo # Local config / secrets
        echo .env
        echo *.local
    ) > .gitignore
) else (
    echo   .gitignore already present.
)

REM --- 5. Init repo if needed ----------------------------------
echo.
echo [Step 5] Initializing git repo...
if not exist ".git" (
    git init
    if errorlevel 1 goto :fail
) else (
    echo   Existing .git folder detected - skipping init.
)

REM --- 6. Stage + commit ---------------------------------------
echo.
echo [Step 6] Staging files...
git add .
if errorlevel 1 goto :fail

echo   Checking if there is anything to commit...
git diff --cached --quiet
if errorlevel 1 (
    echo   Creating commit...
    git commit -m "!COMMIT_MSG!"
    if errorlevel 1 goto :fail
) else (
    echo   Nothing to commit - working tree already clean.
)

REM --- 7. Set branch -------------------------------------------
echo.
echo [Step 7] Setting branch to !BRANCH!...
git branch -M !BRANCH!

REM --- 8. Configure remote -------------------------------------
echo.
echo [Step 8] Configuring remote 'origin'...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/!GH_USER!/!REPO_NAME!.git
if errorlevel 1 goto :fail

REM --- 9. Push -------------------------------------------------
echo.
echo ------------------------------------------------------------
echo  Pushing to https://github.com/!GH_USER!/!REPO_NAME!.git
echo.
echo  If a popup appears, choose Token and paste your PAT.
echo  If the terminal asks for a password, paste your PAT
echo  (characters will be hidden - that's normal).
echo ------------------------------------------------------------
echo.
pause

git push -u origin !BRANCH!
if errorlevel 1 goto :fail

REM --- 10. Auto-tag --------------------------------------------
echo.
echo [Step 10] Tagging baseline as !TAG_NAME!...
git tag -d !TAG_NAME! >nul 2>&1
git tag -a !TAG_NAME! -m "!TAG_MSG!"
if errorlevel 1 goto :fail

git push origin !TAG_NAME!
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   SUCCESS - Initial push + tag complete.
echo.
echo   Repo : https://github.com/!GH_USER!/!REPO_NAME!
echo   Tag  : https://github.com/!GH_USER!/!REPO_NAME!/releases/tag/!TAG_NAME!
echo ============================================================
echo.
goto :end_pause

:fail
echo.
echo ============================================================
echo   [ERROR] Step failed. See messages above this line.
echo ============================================================

:end_pause
echo.
echo Press any key to close this window...
pause >nul
endlocal
exit /b