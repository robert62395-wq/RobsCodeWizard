@echo off
setlocal
echo ============================================================
echo  FORCED RESEED of translation_map.json
echo ============================================================
echo This will OVERWRITE app\data\translation_map.json
echo and DISCARD all manual overrides.
echo.
set /p CONFIRM="Type YES to continue: "
if /I not "%CONFIRM%"=="YES" (
    echo Aborted.
    pause & exit /b 0
)

if not exist "_backup_reseed" mkdir "_backup_reseed"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set TS=%DT:~0,8%_%DT:~8,6%
if exist "app\data\translation_map.json" copy /Y "app\data\translation_map.json" "_backup_reseed\translation_map_%TS%.json" >nul

.venv\Scripts\python -m app.services.seed_translation_map --force
echo Backup saved to _backup_reseed\translation_map_%TS%.json
pause
