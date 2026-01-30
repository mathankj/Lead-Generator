@echo off
REM Techjays Full Workflow Automation Script for Windows
REM Usage: fullworkflow.bat <feature-slug>

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: fullworkflow.bat ^<feature-slug^>
    echo Example: fullworkflow.bat user-authentication
    exit /b 1
)

set FEATURE_SLUG=%~1
set LOG_FILE=workflow_%FEATURE_SLUG%_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log

echo ============================================
echo Techjays Full Workflow Automation
echo Feature: %FEATURE_SLUG%
echo Started: %date% %time%
echo ============================================
echo.

REM Step 1: Onboard
echo [Step 1/9] Running Onboard...
echo ----------------------------------------
call claude -p "/onboard" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Onboard had issues, check %LOG_FILE%
) else (
    echo [OK] Onboard complete
)
echo.

REM Step 2: Feature New
echo [Step 2/9] Creating Feature: %FEATURE_SLUG%...
echo ----------------------------------------
call claude -p "/feature-new %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Feature creation failed, check %LOG_FILE%
    exit /b 1
)
echo [OK] Feature created
echo.

REM Step 3: Planner
echo [Step 3/9] Planning Feature...
echo ----------------------------------------
call claude -p "/planner %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Planning had issues, check %LOG_FILE%
)
echo [OK] Planning complete
echo.

REM Step 4: Execute
echo [Step 4/9] Executing Implementation...
echo ----------------------------------------
call claude -p "/execute %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Execution had issues, check %LOG_FILE%
)
echo [OK] Implementation complete
echo.

REM Step 5: Tests
echo [Step 5/9] Generating Tests...
echo ----------------------------------------
call claude -p "/tests %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Tests had issues, check %LOG_FILE%
)
echo [OK] Tests complete
echo.

REM Step 6: Refactor
echo [Step 6/9] Refactoring (if needed)...
echo ----------------------------------------
call claude -p "/refactor %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Refactor had issues, check %LOG_FILE%
)
echo [OK] Refactor complete
echo.

REM Step 7: PR
echo [Step 7/9] Creating Pull Request...
echo ----------------------------------------
call claude -p "/pr %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PR creation failed, check %LOG_FILE%
    exit /b 1
)
echo [OK] PR created
echo.

REM Step 8: PR Comments
echo [Step 8/9] Handling PR Comments...
echo ----------------------------------------
call claude -p "/pr-comments %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PR comments handling had issues, check %LOG_FILE%
)
echo [OK] PR comments handled
echo.

REM Step 9: Submit
echo [Step 9/9] Finalizing Submission...
echo ----------------------------------------
call claude -p "/submit %FEATURE_SLUG%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Submit had issues, check %LOG_FILE%
)
echo [OK] Submit complete
echo.

echo ============================================
echo Workflow Complete!
echo Feature: %FEATURE_SLUG%
echo Log: %LOG_FILE%
echo Finished: %date% %time%
echo ============================================

endlocal
