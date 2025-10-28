"""
Unit tests for OllamaAPIManager class.
Tests interactions with locally running Ollama API.
"""

import json
import pytest
from unittest.mock import patch, Mock, MagicMock
import requests

from app.services.ollama_api_manager import OllamaAPIManager


class TestOllamaAPIManagerInit:
    """Test OllamaAPIManager initialization."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        manager = OllamaAPIManager()

        assert manager.base_url == "http://localhost:11434"
        assert manager.model == "llama3"
        assert manager.request_count == 0
        assert manager.max_requests_per_minute == 30

    @pytest.mark.unit
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        manager = OllamaAPIManager(
            base_url="http://custom:8080",
            model="mistral"
        )

        assert manager.base_url == "http://custom:8080"
        assert manager.model == "mistral"


class TestOllamaAPIManagerConfiguration:
    """Test configuration methods."""

    @pytest.mark.unit
    def test_set_base_url(self):
        """Test setting base URL."""
        manager = OllamaAPIManager()

        manager.set_base_url("http://newhost:9090")
        assert manager.base_url == "http://newhost:9090"

    @pytest.mark.unit
    def test_set_model(self):
        """Test setting model."""
        manager = OllamaAPIManager()

        manager.set_model("codellama")
        assert manager.model == "codellama"


class TestOllamaAPIManagerListModels:
    """Test listing available models."""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.get')
    def test_list_models_success(self, mock_get):
        """Test successfully listing models."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [
                {'name': 'llama3'},
                {'name': 'mistral'},
                {'name': 'codellama'}
            ]
        }
        mock_get.return_value = mock_response

        manager = OllamaAPIManager()
        success, models, error = manager.list_available_models()

        assert success is True
        assert models == ['llama3', 'mistral', 'codellama']
        assert error is None
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.get')
    def test_list_models_empty(self, mock_get):
        """Test listing models when no models are available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'models': []}
        mock_get.return_value = mock_response

        manager = OllamaAPIManager()
        success, models, error = manager.list_available_models()

        assert success is True
        assert models == []
        assert error is None

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.get')
    def test_list_models_http_error(self, mock_get):
        """Test listing models with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_get.return_value = mock_response

        manager = OllamaAPIManager()
        success, models, error = manager.list_available_models()

        assert success is False
        assert models is None
        assert "404" in error

    @pytest.mark.unit
    @pytest.mark.requires_ollama
    @patch('app.services.ollama_api_manager.requests.get')
    def test_list_models_connection_error(self, mock_get):
        """Test listing models with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        manager = OllamaAPIManager()
        success, models, error = manager.list_available_models()

        assert success is False
        assert models is None
        assert "Connection error" in error


class TestOllamaAPIManagerTestConnection:
    """Test connection testing."""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    @patch('app.services.ollama_api_manager.requests.get')
    def test_connection_success(self, mock_get, mock_post):
        """Test successful connection test."""
        # Mock models list
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'models': [{'name': 'llama3'}]
        }
        mock_get.return_value = mock_get_response

        # Mock generation
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        manager = OllamaAPIManager()
        success, message = manager.test_connection()

        assert success is True
        assert "successful" in message.lower()

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.get')
    def test_connection_models_list_fails(self, mock_get):
        """Test connection when models list fails."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        manager = OllamaAPIManager()
        success, message = manager.test_connection()

        assert success is False
        assert "Failed to connect" in message

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    @patch('app.services.ollama_api_manager.requests.get')
    def test_connection_generation_fails(self, mock_get, mock_post):
        """Test connection when generation fails."""
        # Models list succeeds
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'models': [{'name': 'llama3'}]
        }
        mock_get.return_value = mock_get_response

        # Generation fails
        mock_post_response = Mock()
        mock_post_response.status_code = 500
        mock_post_response.text = "Internal server error"
        mock_post.return_value = mock_post_response

        manager = OllamaAPIManager()
        success, message = manager.test_connection()

        assert success is False
        assert "500" in message

    @pytest.mark.unit
    @pytest.mark.requires_ollama
    @patch('app.services.ollama_api_manager.requests.post')
    @patch('app.services.ollama_api_manager.requests.get')
    def test_connection_timeout(self, mock_get, mock_post):
        """Test connection with network timeout."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {'models': [{'name': 'llama3'}]}
        mock_get.return_value = mock_get_response

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        manager = OllamaAPIManager()
        success, message = manager.test_connection()

        assert success is False
        assert "Could not connect" in message


class TestOllamaAPIManagerProcessCell:
    """Test cell processing functionality."""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_single_cell_success(self, mock_post):
        """Test successfully processing a single cell."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200

        # Simulate streaming chunks
        response_lines = [
            json.dumps({'response': 'JOHN', 'done': False}).encode(),
            json.dumps({'response': ' DOE', 'done': False}).encode(),
            json.dumps({'response': '', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="john doe",
            system_prompt="You are a helper",
            user_prompt="Convert to uppercase"
        )

        assert success is True
        assert result == "JOHN DOE"
        assert error is None

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_cell_with_context(self, mock_post):
        """Test processing cell with context data."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': 'result', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        context_data = {'Name': 'John', 'Age': 30}

        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt",
            context_data=context_data
        )

        assert success is True
        # Verify context was included in API call
        call_args = mock_post.call_args
        request_json = call_args[1]['json']
        assert 'Name' in request_json['prompt']
        assert 'Age' in request_json['prompt']

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_cell_api_error(self, mock_post):
        """Test processing cell with API error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is False
        assert result is None
        assert error is not None
        assert "500" in error

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_cell_with_temperature(self, mock_post):
        """Test processing with custom temperature."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': 'result', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt",
            temperature=0.8,
            max_tokens=500
        )

        # Verify temperature and max_tokens were passed
        call_args = mock_post.call_args
        request_json = call_args[1]['json']
        assert request_json['options']['temperature'] == 0.8
        assert request_json['options']['num_predict'] == 500

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_cell_strips_whitespace(self, mock_post):
        """Test that result is stripped of whitespace."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': '  result  ', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert result == "result"  # Whitespace stripped

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_cell_handles_json_decode_error(self, mock_post):
        """Test handling of malformed JSON in stream."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            b'not valid json',
            json.dumps({'response': 'valid', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        # Should still succeed with valid chunks
        assert success is True
        assert result == "valid"


class TestOllamaAPIManagerStreaming:
    """Test streaming functionality."""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_generate_streaming_success(self, mock_post):
        """Test streaming generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': 'chunk1', 'done': False}).encode(),
            json.dumps({'response': 'chunk2', 'done': False}).encode(),
            json.dumps({'response': 'chunk3', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        chunks = list(manager._generate_streaming("prompt", "system"))

        assert chunks == ['chunk1', 'chunk2', 'chunk3']

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_generate_streaming_stops_on_done(self, mock_post):
        """Test that streaming stops when done=True."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': 'chunk1', 'done': False}).encode(),
            json.dumps({'response': 'chunk2', 'done': True}).encode(),
            json.dumps({'response': 'chunk3', 'done': False}).encode()  # Should not reach this
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        chunks = list(manager._generate_streaming("prompt", "system"))

        assert chunks == ['chunk1', 'chunk2']

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_generate_streaming_error(self, mock_post):
        """Test streaming with error response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()

        with pytest.raises(Exception) as exc_info:
            list(manager._generate_streaming("prompt", "system"))

        assert "404" in str(exc_info.value)


class TestOllamaAPIManagerRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.unit
    def test_rate_limit_check_initial(self):
        """Test rate limit check initially passes."""
        manager = OllamaAPIManager()

        assert manager._check_rate_limit() is True

    @pytest.mark.unit
    def test_rate_limit_increment(self):
        """Test rate limit counter increments."""
        manager = OllamaAPIManager()

        initial_count = manager.request_count
        manager._increment_request_count()

        assert manager.request_count == initial_count + 1

    @pytest.mark.unit
    def test_rate_limit_blocks_when_exceeded(self):
        """Test rate limiting blocks when limit is exceeded."""
        manager = OllamaAPIManager()

        # Hit the rate limit
        manager.request_count = manager.max_requests_per_minute

        assert manager._check_rate_limit() is False

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.time.time')
    def test_rate_limit_resets_after_minute(self, mock_time):
        """Test rate limit resets after a minute."""
        manager = OllamaAPIManager()

        # Set initial time
        mock_time.return_value = 1000.0
        manager.request_start_time = 1000.0
        manager.request_count = 30

        # Advance time by more than 60 seconds
        mock_time.return_value = 1065.0

        # Check should reset counter
        result = manager._check_rate_limit()

        assert result is True
        assert manager.request_count == 0

    @pytest.mark.unit
    def test_process_blocked_by_rate_limit(self):
        """Test that processing is blocked when rate limit is hit."""
        manager = OllamaAPIManager()

        # Hit the rate limit
        manager.request_count = manager.max_requests_per_minute

        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is False
        assert "rate limit" in error.lower()

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_increments_rate_limit(self, mock_post):
        """Test that processing increments rate limit counter."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': 'result', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        initial_count = manager.request_count

        manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert manager.request_count == initial_count + 1


class TestOllamaAPIManagerEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_process_empty_content(self, mock_post):
        """Test processing empty cell content."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            json.dumps({'response': '', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is True
        assert result == ""

    @pytest.mark.unit
    @patch('app.services.ollama_api_manager.requests.post')
    def test_streaming_empty_lines(self, mock_post):
        """Test streaming handles empty lines."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_lines = [
            b'',  # Empty line
            json.dumps({'response': 'result', 'done': True}).encode(),
            b''  # Another empty line
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        manager = OllamaAPIManager()
        success, result, error = manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )

        assert success is True
        assert result == "result"
