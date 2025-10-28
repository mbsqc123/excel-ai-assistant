"""
Pytest configuration and shared fixtures for Excel AI Assistant tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator
import pandas as pd
import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_csv_file(temp_dir: Path) -> Path:
    """Create a sample CSV file for testing."""
    df = pd.DataFrame({
        'Name': ['John Doe', 'jane smith', 'BOB JOHNSON', 'Alice Brown'],
        'Email': ['john@example.com', 'JANE@EXAMPLE.COM', 'bob@test.com', 'alice@demo.com'],
        'Age': [30, 25, 35, 28],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
        'Salary': [50000, 60000, 55000, 65000]
    })

    file_path = temp_dir / "sample.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_excel_file(temp_dir: Path) -> Path:
    """Create a sample Excel file for testing."""
    df = pd.DataFrame({
        'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
        'Price': [999.99, 29.99, 79.99, 299.99],
        'Quantity': [5, 50, 25, 10],
        'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics']
    })

    file_path = temp_dir / "sample.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'Text': ['hello world', 'TESTING', 'Mixed Case Text', '  spaces  '],
        'Numbers': [10, 20, 30, 40],
        'Dates': pd.to_datetime(['2024-01-01', '2024-02-15', '2024-03-30', '2024-04-20']),
        'Floats': [1.5, 2.7, 3.9, 4.2]
    })


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Create an empty DataFrame for testing edge cases."""
    return pd.DataFrame()


@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """Create a large DataFrame for performance testing."""
    import numpy as np

    size = 1000
    return pd.DataFrame({
        'ID': range(size),
        'Name': [f'User_{i}' for i in range(size)],
        'Value': np.random.rand(size),
        'Category': np.random.choice(['A', 'B', 'C', 'D'], size),
        'Text': [f'Sample text content {i}' for i in range(size)]
    })


@pytest.fixture
def mock_openai_response():
    """Mock response from OpenAI API."""
    class MockChoice:
        def __init__(self, content: str):
            self.message = type('Message', (), {'content': content})()

    class MockResponse:
        def __init__(self, content: str):
            self.choices = [MockChoice(content)]

    return MockResponse


@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        'model': 'llama3',
        'created_at': '2024-01-01T00:00:00Z',
        'response': 'Mocked response',
        'done': True
    }


@pytest.fixture
def sample_api_config():
    """Sample API configuration for testing."""
    return {
        'api_type': 'openai',
        'api_key': 'test-api-key-12345',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.3,
        'max_tokens': 150,
        'ollama_url': 'http://localhost:11434',
        'ollama_model': 'llama3'
    }


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        'api_type': 'openai',
        'api_key': '',
        'model': 'gpt-3.5-turbo',
        'theme': 'light',
        'recent_files': [],
        'temperature': 0.3,
        'max_tokens': 150,
        'batch_size': 10,
        'prompts': {
            'Test Prompt': 'This is a test prompt.'
        }
    }


@pytest.fixture
def mock_config_file(temp_dir: Path, sample_config_data):
    """Create a mock configuration file."""
    import json

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(sample_config_data, f)

    return config_file


@pytest.fixture
def sample_cells_batch():
    """Sample batch of cells for processing."""
    return [
        {'row': 0, 'col': 'Name', 'content': 'john doe'},
        {'row': 1, 'col': 'Name', 'content': 'JANE SMITH'},
        {'row': 2, 'col': 'Name', 'content': 'bob johnson'},
        {'row': 3, 'col': 'Name', 'content': 'alice brown'}
    ]


@pytest.fixture
def sample_cells_with_context():
    """Sample batch of cells with context data."""
    return [
        {
            'row': 0,
            'col': 'Email',
            'content': 'john@example.com',
            'context_data': {'Name': 'John Doe', 'Age': 30}
        },
        {
            'row': 1,
            'col': 'Email',
            'content': 'jane@example.com',
            'context_data': {'Name': 'Jane Smith', 'Age': 25}
        }
    ]


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    # Store original environment
    original_env = os.environ.copy()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_tkinter_root(mocker):
    """Mock Tkinter root window for UI tests."""
    mock_root = mocker.MagicMock()
    mock_root.winfo_exists.return_value = True
    return mock_root
