@echo off
REM Test runner script for Excel AI Assistant (Windows)
REM Usage: run_tests.bat [options]

setlocal enabledelayedexpansion

set COVERAGE=true
set VERBOSE=false
set PARALLEL=false
set MARKERS=
set HTML_REPORT=false

:parse_args
if "%~1"=="" goto run_tests
if /i "%~1"=="-h" goto show_help
if /i "%~1"=="--help" goto show_help
if /i "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if /i "%~1"=="-p" (
    set PARALLEL=true
    shift
    goto parse_args
)
if /i "%~1"=="--parallel" (
    set PARALLEL=true
    shift
    goto parse_args
)
if /i "%~1"=="--no-coverage" (
    set COVERAGE=false
    shift
    goto parse_args
)
if /i "%~1"=="--html" (
    set HTML_REPORT=true
    shift
    goto parse_args
)
if /i "%~1"=="--unit" (
    set MARKERS=unit
    shift
    goto parse_args
)
if /i "%~1"=="--integration" (
    set MARKERS=integration
    shift
    goto parse_args
)
if /i "%~1"=="--quick" (
    set MARKERS=not slow
    shift
    goto parse_args
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:show_help
echo Excel AI Assistant Test Runner (Windows)
echo.
echo Usage: run_tests.bat [options]
echo.
echo Options:
echo   -h, --help           Show this help message
echo   -v, --verbose        Run tests with verbose output
echo   -p, --parallel       Run tests in parallel
echo   --no-coverage        Skip coverage reporting
echo   --html               Generate HTML coverage report
echo   --unit               Run only unit tests
echo   --integration        Run only integration tests
echo   --quick              Run quick tests (exclude slow tests)
echo.
echo Examples:
echo   run_tests.bat                  # Run all tests with coverage
echo   run_tests.bat --unit           # Run only unit tests
echo   run_tests.bat -v --html        # Verbose output with HTML report
echo   run_tests.bat --parallel       # Run tests in parallel
exit /b 0

:run_tests
echo Starting Excel AI Assistant Test Suite
echo.

REM Check if pytest is installed
pytest --version >nul 2>&1
if errorlevel 1 (
    echo Error: pytest is not installed
    echo Install with: pip install -r requirements-dev.txt
    exit /b 1
)

REM Build pytest command
set PYTEST_CMD=pytest

if "%VERBOSE%"=="true" (
    set PYTEST_CMD=!PYTEST_CMD! -v
)

if "%PARALLEL%"=="true" (
    set PYTEST_CMD=!PYTEST_CMD! -n auto
    echo Running tests in parallel mode
)

if not "%MARKERS%"=="" (
    set PYTEST_CMD=!PYTEST_CMD! -m "!MARKERS!"
    echo Running tests with markers: !MARKERS!
)

if "%COVERAGE%"=="true" (
    set PYTEST_CMD=!PYTEST_CMD! --cov=app --cov-report=term-missing

    if "%HTML_REPORT%"=="true" (
        set PYTEST_CMD=!PYTEST_CMD! --cov-report=html
        echo HTML coverage report will be generated
    )
)

echo.
echo Executing: !PYTEST_CMD!
echo.

REM Run tests
call !PYTEST_CMD!
set TEST_EXIT_CODE=!errorlevel!

echo.

REM Print results
if !TEST_EXIT_CODE! equ 0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILED] Some tests failed (exit code: !TEST_EXIT_CODE!)
)

REM Open HTML report if generated
if "%HTML_REPORT%"=="true" (
    if exist "htmlcov\index.html" (
        echo.
        echo Opening HTML coverage report...
        start htmlcov\index.html
    )
)

exit /b !TEST_EXIT_CODE!
