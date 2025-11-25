@echo off
REM Refraction Engine V1 - Parity Test Suite (Windows)
REM ===================================================
REM
REM Runs PL9 parity tests to verify accuracy against reference calculations.
REM
REM Usage:
REM   scripts\run_parity_suite.bat                  Run all parity tests
REM   scripts\run_parity_suite.bat -v               Verbose output
REM   scripts\run_parity_suite.bat --chart=arezoo   Run specific chart

setlocal enabledelayedexpansion

REM ============================================================================
REM CONFIGURATION
REM ============================================================================

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%\.."
set "TESTS_DIR=%ROOT_DIR%\tests\parity"

REM Default threshold: 90 arcseconds
if not defined PARITY_THRESHOLD set "PARITY_THRESHOLD=90"
set "THRESHOLD_ARCSEC=%PARITY_THRESHOLD%"

REM ============================================================================
REM HELPER FUNCTIONS
REM ============================================================================

:log_info
echo [INFO] %*
exit /b 0

:log_success
echo [PASS] %*
exit /b 0

:log_error
echo [FAIL] %*
exit /b 0

REM ============================================================================
REM MAIN EXECUTION
REM ============================================================================

:main
echo.
echo ================================================================
echo   Refraction Engine V1 - Parity Test Suite
echo ================================================================
echo   Root:      %ROOT_DIR%
echo   Tests:     %TESTS_DIR%
echo   Threshold: %THRESHOLD_ARCSEC% arcseconds
echo ================================================================
echo.

REM Check Python
call :log_info Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    call :log_error Python not found. Please install Python 3.8+
    exit /b 2
)

REM Check pytest
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    call :log_error pytest not found. Install with: pip install pytest
    exit /b 2
)

REM Check test directory
if not exist "%TESTS_DIR%" (
    call :log_error Parity tests directory not found: %TESTS_DIR%
    exit /b 2
)

call :log_success All dependencies OK

REM Change to root directory
cd /d "%ROOT_DIR%"

REM Parse arguments
set "PYTEST_ARGS="
set "CHART_FILTER="

:parse_args
if "%~1"=="" goto run_tests
if /i "%~1"=="-v" (
    set "PYTEST_ARGS=%PYTEST_ARGS% -v"
    shift
    goto parse_args
)
if /i "%~1"=="-vv" (
    set "PYTEST_ARGS=%PYTEST_ARGS% -vv"
    shift
    goto parse_args
)
if /i "%~1"=="--help" goto show_help
if /i "%~1"=="-h" goto show_help

REM Handle --chart=NAME argument
echo %~1 | findstr /C:"--chart=" >nul
if not errorlevel 1 (
    set "CHART_ARG=%~1"
    set "CHART_FILTER=!CHART_ARG:--chart=!"
    set "PYTEST_ARGS=%PYTEST_ARGS% -k !CHART_FILTER!"
    shift
    goto parse_args
)

REM Handle --threshold=VALUE argument
echo %~1 | findstr /C:"--threshold=" >nul
if not errorlevel 1 (
    set "THRESH_ARG=%~1"
    set "THRESHOLD_ARCSEC=!THRESH_ARG:--threshold=!"
    set "PARITY_THRESHOLD=!THRESHOLD_ARCSEC!"
    shift
    goto parse_args
)

REM Pass through other arguments
set "PYTEST_ARGS=%PYTEST_ARGS% %~1"
shift
goto parse_args

:run_tests
REM Run parity tests
echo.
call :log_info Running parity tests...
call :log_info Command: pytest %TESTS_DIR% %PYTEST_ARGS%
echo.

python -m pytest "%TESTS_DIR%" %PYTEST_ARGS% --tb=short
if errorlevel 1 (
    echo.
    call :log_error Parity tests failed!
    call :log_error Some calculations deviate ^> %THRESHOLD_ARCSEC% arcseconds from PL9 reference
    echo.
    exit /b 1
)

echo.
call :log_success All parity tests passed!
call :log_info Maximum deviation: ^< %THRESHOLD_ARCSEC% arcseconds
echo.
exit /b 0

:show_help
echo Refraction Engine V1 - Parity Test Suite
echo =========================================
echo.
echo Usage:
echo   %~nx0 [OPTIONS]
echo.
echo Options:
echo   -v, --verbose              Verbose output (show each test)
echo   -vv                        Very verbose output
echo   --chart=NAME               Run tests for specific chart only
echo   --threshold=ARCSEC         Set custom threshold (default: 90)
echo   -h, --help                 Show this help message
echo.
echo Examples:
echo   %~nx0                      Run all parity tests
echo   %~nx0 -v                   Run with verbose output
echo   %~nx0 --chart=arezoo       Run only Arezoo's chart
echo   %~nx0 --threshold=60       Use stricter threshold
echo.
exit /b 0
