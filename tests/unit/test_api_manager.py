"""
Unit tests for APIManager class.
Tests API interactions with OpenAI and Ollama.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from openai import APIError, RateLimitError

from app.services.api_manager import APIManager, APIType


class TestAPIManagerInit:
    """Test APIManager initialization."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        manager = APIManager()

        assert manager.api_key == ""
        assert manager.model == "gpt-3.5-turbo"
        assert manager.api_type == APIType.OPENAI
        assert manager.client is None

    @pytest.mark.unit
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        manager = APIManager(api_key="test-key")

        assert manager.api_key == "test-key"
        assert manager.api_type == APIType.OPENAI

    @pytest.mark.unit
    def test_init_with_ollama(self):
        """Test initialization with Ollama API type."""
        manager = APIManager(api_type="ollama", ollama_url="http://localhost:11434")

        assert manager.api_type == APIType.OLLAMA
        assert manager.ollama_url == "http://localhost:11434"

    @pytest.mark.unit
    def test_rate_limiting_initialized(self):
        """Test that rate limiting is properly initialized."""
        manager = APIManager()

        assert manager.request_count == 0
        assert manager.max_requests_per_minute == 20


class TestAPIManagerInitialization:
    """Test API client initialization."""

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_initialize_openai(self, mock_openai):
        """Test initializing OpenAI client."""
        manager = APIManager(api_type="openai")

        success = manager.initialize(api_key="test-key")

        assert success is True
        assert manager.api_key == "test-key"
        mock_openai.assert_called_once_with(api_key="test-key")

    @pytest.mark.unit
    def test_initialize_without_key(self):
        """Test initialization fails without API key for OpenAI."""
        manager = APIManager(api_type="openai")

        success = manager.initialize()

        assert success is False
        assert manager.client is None

    @pytest.mark.unit
    def test_initialize_ollama(self):
        """Test initializing Ollama (no actual initialization needed)."""
        manager = APIManager(api_type="ollama")

        success = manager.initialize()

        assert success is True


class TestAPIManagerConfiguration:
    """Test API configuration methods."""

    @pytest.mark.unit
    def test_set_api_type(self):
        """Test setting API type."""
        manager = APIManager()

        manager.set_api_type("ollama")
        assert manager.api_type == APIType.OLLAMA

        manager.set_api_type("openai")
        assert manager.api_type == APIType.OPENAI

    @pytest.mark.unit
    def test_set_model(self):
        """Test setting model."""
        manager = APIManager()

        manager.set_model("gpt-4")
        assert manager.model == "gpt-4"

    @pytest.mark.unit
    def test_set_model_for_ollama(self):
        """Test setting model updates Ollama manager."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'set_model') as mock_set:
            manager.set_model("llama3")
            mock_set.assert_called_once_with("llama3")

    @pytest.mark.unit
    def test_set_ollama_url(self):
        """Test setting Ollama URL."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'set_base_url') as mock_set:
            manager.set_ollama_url("http://localhost:8080")
            assert manager.ollama_url == "http://localhost:8080"
            mock_set.assert_called_once_with("http://localhost:8080")


class TestAPIManagerModelList:
    """Test getting available models."""

    @pytest.mark.unit
    def test_get_openai_models(self):
        """Test getting list of OpenAI models."""
        manager = APIManager(api_type="openai")

        models = manager.get_available_models()

        assert len(models) > 0
        assert any(m['id'] == 'gpt-3.5-turbo' for m in models)
        assert any(m['id'] == 'gpt-4' for m in models)
        assert all(m['api'] == 'openai' for m in models)

    @pytest.mark.unit
    def test_get_ollama_models_success(self):
        """Test getting list of Ollama models successfully."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'list_available_models') as mock_list:
            mock_list.return_value = (True, ['llama3', 'mistral', 'codellama'], None)

            models = manager.get_available_models()

            assert len(models) == 3
            assert models[0]['id'] == 'llama3'
            assert all(m['api'] == 'ollama' for m in models)

    @pytest.mark.unit
    def test_get_ollama_models_failure(self):
        """Test getting Ollama models when server is unavailable."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'list_available_models') as mock_list:
            mock_list.return_value = (False, None, "Connection error")

            models = manager.get_available_models()

            assert models == []


class TestAPIManagerTestConnection:
    """Test connection testing."""

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_test_connection_success(self, mock_openai):
        """Test successful connection test."""
        manager = APIManager(api_key="test-key")

        # Mock the OpenAI client response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Test response"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        success, message = manager.test_connection()

        assert success is True
        assert "successful" in message.lower()

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_test_connection_rate_limit_error(self, mock_openai):
        """Test connection with rate limit error."""
        manager = APIManager(api_key="test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RateLimitError("Rate limited", response=MagicMock(), body=None)
        manager.client = mock_client

        success, message = manager.test_connection()

        assert success is False
        assert "rate limit" in message.lower()

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_test_connection_api_error(self, mock_openai):
        """Test connection with API error."""
        manager = APIManager(api_key="test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIError("API Error", request=MagicMock(), body=None)
        manager.client = mock_client

        success, message = manager.test_connection()

        assert success is False
        assert "error" in message.lower()

    @pytest.mark.unit
    def test_test_connection_ollama(self):
        """Test connection for Ollama."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'test_connection') as mock_test:
            mock_test.return_value = (True, "Connection successful")

            success, message = manager.test_connection()

            assert success is True
            mock_test.assert_called_once()


class TestAPIManagerProcessCell:
    """Test cell processing functionality."""

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_single_cell_openai_success(self, mock_openai):
        """Test processing a single cell with OpenAI."""
        manager = APIManager(api_key="test-key")

        # Mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "JOHN DOE"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        success, result, error = manager.process_single_cell(
            cell_content="john doe",
            system_prompt="You are a helper",
            user_prompt="Convert to uppercase",
            temperature=0.3,
            max_tokens=100
        )

        assert success is True
        assert result == "JOHN DOE"
        assert error is None

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_single_cell_with_context(self, mock_openai):
        """Test processing cell with context data."""
        manager = APIManager(api_key="test-key")

        # Mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "john.doe@company.com"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        context_data = {'Name': 'John Doe', 'Company': 'Acme Corp'}

        success, result, error = manager.process_single_cell(
            cell_content="john",
            system_prompt="You are a helper",
            user_prompt="Generate email",
            temperature=0.3,
            max_tokens=100,
            context_data=context_data
        )

        assert success is True
        # Verify context was included in the API call
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        assert 'Name' in user_message
        assert 'Company' in user_message

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_single_cell_api_error(self, mock_openai):
        """Test processing cell with API error."""
        manager = APIManager(api_key="test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIError("API Error", request=MagicMock(), body=None)
        manager.client = mock_client

        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is False
        assert result is None
        assert error is not None

    @pytest.mark.unit
    def test_process_single_cell_ollama(self):
        """Test processing cell with Ollama."""
        manager = APIManager(api_type="ollama")

        with patch.object(manager.ollama_manager, 'process_single_cell') as mock_process:
            mock_process.return_value = (True, "result", None)

            success, result, error = manager.process_single_cell(
                cell_content="test",
                system_prompt="system",
                user_prompt="prompt"
            )

            assert success is True
            assert result == "result"
            mock_process.assert_called_once()

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_without_initialized_client(self, mock_openai):
        """Test processing when client is not initialized."""
        manager = APIManager()  # No API key
        manager.client = None

        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is False
        assert result is None
        assert "not initialized" in error.lower()


class TestAPIManagerRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.unit
    def test_rate_limit_check_initial(self):
        """Test rate limit check initially passes."""
        manager = APIManager()

        assert manager._check_rate_limit() is True

    @pytest.mark.unit
    def test_rate_limit_increment(self):
        """Test rate limit counter increments."""
        manager = APIManager()

        initial_count = manager.request_count
        manager._increment_request_count()

        assert manager.request_count == initial_count + 1

    @pytest.mark.unit
    def test_rate_limit_blocks_when_exceeded(self):
        """Test rate limiting blocks when limit is exceeded."""
        manager = APIManager()

        # Simulate hitting the rate limit
        manager.request_count = manager.max_requests_per_minute

        assert manager._check_rate_limit() is False

    @pytest.mark.unit
    @patch('app.services.api_manager.time.time')
    def test_rate_limit_resets_after_minute(self, mock_time):
        """Test rate limit resets after a minute."""
        manager = APIManager()

        # Set initial time
        mock_time.return_value = 1000.0
        manager.request_start_time = 1000.0
        manager.request_count = 20

        # Advance time by more than 60 seconds
        mock_time.return_value = 1065.0

        # Check should reset counter
        result = manager._check_rate_limit()

        assert result is True
        assert manager.request_count == 0

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_increments_rate_limit(self, mock_openai):
        """Test that processing increments rate limit counter."""
        manager = APIManager(api_key="test-key")

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "result"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        initial_count = manager.request_count

        manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert manager.request_count == initial_count + 1

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_blocked_by_rate_limit(self, mock_openai):
        """Test that processing is blocked when rate limit is hit."""
        manager = APIManager(api_key="test-key")
        manager.client = MagicMock()

        # Hit the rate limit
        manager.request_count = manager.max_requests_per_minute

        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is False
        assert "rate limit" in error.lower()


class TestAPIManagerEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_empty_content(self, mock_openai):
        """Test processing empty cell content."""
        manager = APIManager(api_key="test-key")

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = ""
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        success, result, error = manager.process_single_cell(
            cell_content="",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is True
        assert result == ""

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_process_special_characters(self, mock_openai):
        """Test processing content with special characters."""
        manager = APIManager(api_key="test-key")

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "processed"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        special_content = "Test\n\tWith\r\nSpecial©️Characters™️"

        success, result, error = manager.process_single_cell(
            cell_content=special_content,
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is True

    @pytest.mark.unit
    @patch('app.services.api_manager.OpenAI')
    def test_initialize_with_invalid_key_format(self, mock_openai):
        """Test initialization with various API key formats."""
        manager = APIManager()

        # Should accept any string as API key
        success = manager.initialize(api_key="sk-test123")
        assert manager.api_key == "sk-test123"
