# Testing Guide for Excel AI Assistant

This document provides comprehensive information about the testing infrastructure for Excel AI Assistant.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing Tests](#writing-tests)
6. [Coverage Reports](#coverage-reports)
7. [Continuous Integration](#continuous-integration)
8. [Best Practices](#best-practices)

## Overview

The Excel AI Assistant uses pytest as its testing framework, with comprehensive unit and integration tests to ensure code quality and reliability.

### Test Statistics

- **Test Coverage Target**: 80%+
- **Total Test Files**: 6
- **Test Categories**:
  - Unit tests for service classes
  - Integration tests for workflows
  - Fixtures for test data

## Installation

### Install Development Dependencies

Install all testing dependencies using uv:

```bash
# Using uv (recommended)
uv pip install -r requirements-dev.txt

# Or using pip
pip install -r requirements-dev.txt
```

### Required Packages

- `pytest>=8.0.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-mock>=3.12.0` - Mocking utilities
- `pytest-timeout>=2.2.0` - Test timeout management
- `pytest-xdist>=3.5.0` - Parallel test execution

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_data_manager.py

# Run specific test class
pytest tests/unit/test_data_manager.py::TestDataManagerInit

# Run specific test method
pytest tests/unit/test_data_manager.py::TestDataManagerInit::test_init
```

### Running Tests by Marker

Tests are organized using markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests that don't require external services
pytest -m "not requires_ollama and not requires_openai"

# Run slow tests
pytest -m slow
```

### Parallel Test Execution

For faster test execution, run tests in parallel:

```bash
# Auto-detect CPU count and run in parallel
pytest -n auto

# Run on 4 cores
pytest -n 4
```

### Test with Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html

# Run tests with terminal coverage report
pytest --cov=app --cov-report=term-missing

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml
```

## Test Structure

```
tests/
├── __init__.py                  # Test package initialization
├── conftest.py                  # Shared fixtures and configuration
├── unit/                        # Unit tests
│   ├── __init__.py
│   ├── test_api_manager.py      # APIManager tests
│   ├── test_data_manager.py     # DataManager tests
│   ├── test_ollama_api_manager.py # OllamaAPIManager tests
│   └── test_config.py           # AppConfig tests
├── integration/                 # Integration tests
│   ├── __init__.py
│   └── test_batch_processing.py # End-to-end workflow tests
├── fixtures/                    # Test data fixtures
└── data/                        # Sample test data files
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Unit Test

```python
import pytest
from app.services.data_manager import DataManager


class TestDataManager:
    """Test DataManager functionality."""

    @pytest.mark.unit
    def test_load_csv_file(self, sample_csv_file):
        """Test loading a CSV file."""
        dm = DataManager()
        success, error = dm.load_file(str(sample_csv_file))

        assert success is True
        assert error == ""
        assert dm.df is not None
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py` and can be used in any test:

```python
def test_with_sample_data(sample_dataframe):
    """Test using the sample dataframe fixture."""
    assert len(sample_dataframe) > 0
```

### Available Fixtures

- `temp_dir` - Temporary directory for file operations
- `sample_csv_file` - Sample CSV file
- `sample_excel_file` - Sample Excel file
- `sample_dataframe` - Sample pandas DataFrame
- `large_dataframe` - Large DataFrame for performance tests
- `sample_cells_batch` - Batch of cells for processing tests
- `sample_cells_with_context` - Cells with context data
- `mock_tkinter_root` - Mocked Tkinter root window

### Mocking API Calls

```python
from unittest.mock import patch, MagicMock

@patch('app.services.api_manager.OpenAI')
def test_api_call(mock_openai):
    """Test with mocked OpenAI."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "result"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    # Your test code here
```

### Async Tests

Use `pytest-asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    result = await some_async_function()
    assert result is not None
```

## Coverage Reports

### Generating Coverage Reports

After running tests with coverage, reports are generated in multiple formats:

#### HTML Report (Human-readable)

```bash
pytest --cov=app --cov-report=html
```

View the report by opening `htmlcov/index.html` in your browser.

#### Terminal Report

```bash
pytest --cov=app --cov-report=term-missing
```

Shows coverage directly in the terminal with line numbers of missing coverage.

#### XML Report (For CI/CD)

```bash
pytest --cov=app --cov-report=xml
```

Generates `coverage.xml` for CI/CD integration.

### Coverage Configuration

Coverage settings are configured in `.coveragerc`:

- **Source**: `app/` directory
- **Omit**: Test files, cache, virtual environments
- **Target**: 80% minimum coverage

### Excluded from Coverage

The following are excluded from coverage requirements:
- `__repr__` methods
- Abstract methods
- Type checking blocks
- Debug-only code
- `if __name__ == '__main__':` blocks

## Continuous Integration

### GitHub Actions Workflow

A GitHub Actions workflow is provided for automated testing:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -r requirements.txt
          uv pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Running Tests Locally (CI Simulation)

To simulate CI environment locally:

```bash
# Run full test suite with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run with strict markers (fail on unknown markers)
pytest --strict-markers

# Run with all warnings as errors
pytest -W error
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fixtures to set up test data
- Clean up resources after tests

### 2. Descriptive Test Names

```python
# Good
def test_load_csv_file_with_missing_values():
    pass

# Bad
def test_load_file():
    pass
```

### 3. Test One Thing at a Time

```python
# Good - Single assertion per test
def test_data_manager_initializes_with_no_data():
    dm = DataManager()
    assert dm.df is None

# Avoid - Multiple unrelated assertions
def test_data_manager():
    dm = DataManager()
    assert dm.df is None
    assert dm.file_type is None
    # ... many more assertions
```

### 4. Use Appropriate Markers

```python
@pytest.mark.unit
def test_unit_functionality():
    """Fast, isolated test."""
    pass

@pytest.mark.integration
def test_workflow():
    """Test component interactions."""
    pass

@pytest.mark.slow
def test_performance():
    """Long-running test."""
    pass

@pytest.mark.requires_ollama
def test_ollama_integration():
    """Requires Ollama to be running."""
    pass
```

### 5. Mock External Dependencies

- Always mock external API calls
- Use fixtures for common mocks
- Mock at the appropriate level

### 6. Test Edge Cases

```python
def test_empty_input():
    """Test with empty input."""
    pass

def test_invalid_input():
    """Test with invalid input."""
    pass

def test_boundary_conditions():
    """Test with boundary values."""
    pass
```

### 7. Maintain Test Performance

- Keep unit tests fast (< 100ms each)
- Use markers for slow tests
- Run quick tests during development
- Run full suite before commits

## Test Markers Reference

| Marker | Description | Usage |
|--------|-------------|-------|
| `@pytest.mark.unit` | Fast, isolated unit tests | `pytest -m unit` |
| `@pytest.mark.integration` | Component interaction tests | `pytest -m integration` |
| `@pytest.mark.slow` | Long-running tests | `pytest -m "not slow"` |
| `@pytest.mark.api` | Tests requiring API access | `pytest -m api` |
| `@pytest.mark.requires_ollama` | Requires Ollama running | `pytest -m "not requires_ollama"` |
| `@pytest.mark.requires_openai` | Requires OpenAI API key | `pytest -m "not requires_openai"` |

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Ensure you're in the project root
cd /path/to/excel-ai-assistant

# Install in development mode
uv pip install -e .
```

### Coverage Too Low

```bash
# See which files need more tests
pytest --cov=app --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Async Tests Fail

```bash
# Ensure pytest-asyncio is installed
uv pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### Tests Hang or Timeout

```bash
# Run with timeout
pytest --timeout=30

# Run specific test with verbose output
pytest -vv tests/path/to/test.py::test_name
```

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov=app`
4. Add docstrings to test functions
5. Use appropriate markers
6. Update this guide if adding new patterns

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
