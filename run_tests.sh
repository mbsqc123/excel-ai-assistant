#!/bin/bash
# Test runner script for Excel AI Assistant
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default options
COVERAGE=true
VERBOSE=false
PARALLEL=false
MARKERS=""
HTML_REPORT=false

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Excel AI Assistant Test Runner"
            echo ""
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -h, --help           Show this help message"
            echo "  -v, --verbose        Run tests with verbose output"
            echo "  -p, --parallel       Run tests in parallel"
            echo "  -m, --markers MARKS  Run only tests with specific markers (e.g., 'unit')"
            echo "  --no-coverage        Skip coverage reporting"
            echo "  --html               Generate HTML coverage report"
            echo "  --unit               Run only unit tests"
            echo "  --integration        Run only integration tests"
            echo "  --quick              Run quick tests (exclude slow tests)"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                  # Run all tests with coverage"
            echo "  ./run_tests.sh --unit           # Run only unit tests"
            echo "  ./run_tests.sh -v --html        # Verbose output with HTML report"
            echo "  ./run_tests.sh --parallel       # Run tests in parallel"
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        --unit)
            MARKERS="unit"
            shift
            ;;
        --integration)
            MARKERS="integration"
            shift
            ;;
        --quick)
            MARKERS="not slow"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed"
    print_info "Install with: pip install -r requirements-dev.txt"
    exit 1
fi

print_info "Starting Excel AI Assistant Test Suite"
echo ""

# Build pytest command
PYTEST_CMD="pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
    print_info "Running tests in parallel mode"
fi

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKERS\""
    print_info "Running tests with markers: $MARKERS"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing"

    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
        print_info "HTML coverage report will be generated"
    fi
fi

# Run tests
echo ""
print_info "Executing: $PYTEST_CMD"
echo ""

eval $PYTEST_CMD
TEST_EXIT_CODE=$?

echo ""

# Print results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

# Open HTML report if generated
if [ "$HTML_REPORT" = true ] && [ -d "htmlcov" ]; then
    echo ""
    print_info "Opening HTML coverage report..."

    if command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    elif command -v open &> /dev/null; then
        open htmlcov/index.html
    else
        print_info "HTML report generated at: htmlcov/index.html"
    fi
fi

exit $TEST_EXIT_CODE
