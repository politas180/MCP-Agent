@echo off
REM Run tests for the MCP Agent
echo Running MCP Agent tests...

REM Activate conda environment
call conda activate mcp

REM Parse arguments
set TYPE=
set COMPONENT=
set HTML=

:parse
if "%~1"=="" goto :endparse
if "%~1"=="--unit" set TYPE=--type unit
if "%~1"=="--integration" set TYPE=--type integration
if "%~1"=="--frontend" set COMPONENT=--component frontend
if "%~1"=="--backend" set COMPONENT=--component backend
if "%~1"=="--tools" set COMPONENT=--component tools
if "%~1"=="--html" set HTML=--html
shift
goto :parse
:endparse

REM Run the tests
python tests/run_tests.py %TYPE% %COMPONENT% %HTML%

REM Check the exit code
if %ERRORLEVEL% NEQ 0 (
    echo Tests failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
) else (
    echo All tests passed!
)
