"""
Unit tests for AppConfig class.
Tests configuration loading, saving, and management.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.config import AppConfig


class TestAppConfigInit:
    """Test AppConfig initialization."""

    @pytest.mark.unit
    def test_init_creates_default_config(self, temp_dir, monkeypatch):
        """Test that initialization creates default configuration."""
        # Override config path to use temp directory
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()

        assert config.get('api_type') == 'openai'
        assert config.get('model') == 'gpt-3.5-turbo'
        assert config.get('theme') == 'system'
        assert isinstance(config.get('prompts'), dict)

    @pytest.mark.unit
    def test_init_loads_existing_config(self, temp_dir, monkeypatch):
        """Test that initialization loads existing configuration file."""
        # Create a config file
        config_file = temp_dir / "config.json"
        config_data = {
            'api_type': 'ollama',
            'model': 'llama3',
            'theme': 'dark',
            'temperature': 0.5
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        def mock_get_config_path(self):
            return config_file

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()

        assert config.get('api_type') == 'ollama'
        assert config.get('model') == 'llama3'
        assert config.get('theme') == 'dark'
        assert config.get('temperature') == 0.5


class TestAppConfigPathGeneration:
    """Test configuration file path generation."""

    @pytest.mark.unit
    @patch('app.config.platform.system')
    @patch('app.config.Path.home')
    def test_get_config_path_windows(self, mock_home, mock_system):
        """Test config path generation on Windows."""
        mock_system.return_value = 'Windows'
        mock_home.return_value = Path('C:/Users/TestUser')

        config = AppConfig()
        config_path = config._get_config_path()

        assert 'AppData' in str(config_path)
        assert 'Roaming' in str(config_path)
        assert 'ExcelAIAssistant' in str(config_path)

    @pytest.mark.unit
    @patch('app.config.platform.system')
    @patch('app.config.Path.home')
    def test_get_config_path_macos(self, mock_home, mock_system):
        """Test config path generation on macOS."""
        mock_system.return_value = 'Darwin'
        mock_home.return_value = Path('/Users/TestUser')

        config = AppConfig()
        config_path = config._get_config_path()

        assert 'Library' in str(config_path)
        assert 'Application Support' in str(config_path)
        assert 'ExcelAIAssistant' in str(config_path)

    @pytest.mark.unit
    @patch('app.config.platform.system')
    @patch('app.config.Path.home')
    def test_get_config_path_linux(self, mock_home, mock_system):
        """Test config path generation on Linux."""
        mock_system.return_value = 'Linux'
        mock_home.return_value = Path('/home/testuser')

        config = AppConfig()
        config_path = config._get_config_path()

        assert '.config' in str(config_path)
        assert 'excel-ai-assistant' in str(config_path)


class TestAppConfigGetSet:
    """Test getting and setting configuration values."""

    @pytest.mark.unit
    def test_get_existing_value(self, temp_dir, monkeypatch):
        """Test getting an existing configuration value."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        value = config.get('model')

        assert value == 'gpt-3.5-turbo'

    @pytest.mark.unit
    def test_get_with_default(self, temp_dir, monkeypatch):
        """Test getting a non-existent value with default."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        value = config.get('nonexistent_key', 'default_value')

        assert value == 'default_value'

    @pytest.mark.unit
    def test_set_value(self, temp_dir, monkeypatch):
        """Test setting a configuration value."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('new_key', 'new_value')

        assert config.get('new_key') == 'new_value'

    @pytest.mark.unit
    def test_get_all(self, temp_dir, monkeypatch):
        """Test getting all configuration values."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        all_config = config.get_all()

        assert isinstance(all_config, dict)
        assert 'api_type' in all_config
        assert 'model' in all_config


class TestAppConfigSave:
    """Test configuration saving."""

    @pytest.mark.unit
    def test_save_config(self, temp_dir, monkeypatch):
        """Test saving configuration to file."""
        config_file = temp_dir / "config.json"

        def mock_get_config_path(self):
            return config_file

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('test_key', 'test_value')
        config.save()

        # Verify file was created
        assert config_file.exists()

        # Verify content
        with open(config_file, 'r') as f:
            saved_data = json.load(f)

        assert saved_data['test_key'] == 'test_value'


class TestAppConfigModelManagement:
    """Test model management methods."""

    @pytest.mark.unit
    def test_get_active_model_openai(self, temp_dir, monkeypatch):
        """Test getting active OpenAI model."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('api_type', 'openai')
        config.set('model', 'gpt-4')

        active_model = config.get_active_model()

        assert active_model['api_type'] == 'openai'
        assert active_model['model'] == 'gpt-4'

    @pytest.mark.unit
    def test_get_active_model_ollama(self, temp_dir, monkeypatch):
        """Test getting active Ollama model."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('api_type', 'ollama')
        config.set('ollama_model', 'mistral')

        active_model = config.get_active_model()

        assert active_model['api_type'] == 'ollama'
        assert active_model['model'] == 'mistral'

    @pytest.mark.unit
    def test_set_active_model_openai(self, temp_dir, monkeypatch):
        """Test setting active OpenAI model."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set_active_model('openai', 'gpt-4-turbo')

        assert config.get('api_type') == 'openai'
        assert config.get('model') == 'gpt-4-turbo'

    @pytest.mark.unit
    def test_set_active_model_ollama(self, temp_dir, monkeypatch):
        """Test setting active Ollama model."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set_active_model('ollama', 'codellama')

        assert config.get('api_type') == 'ollama'
        assert config.get('ollama_model') == 'codellama'


class TestAppConfigRecentFiles:
    """Test recent files management."""

    @pytest.mark.unit
    def test_add_recent_file(self, temp_dir, monkeypatch):
        """Test adding a file to recent files."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_recent_file('/path/to/file.xlsx')

        recent = config.get('recent_files')
        assert '/path/to/file.xlsx' in recent
        assert recent[0] == '/path/to/file.xlsx'

    @pytest.mark.unit
    def test_add_recent_file_moves_to_top(self, temp_dir, monkeypatch):
        """Test that adding existing file moves it to top."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_recent_file('/path/to/file1.xlsx')
        config.add_recent_file('/path/to/file2.xlsx')
        config.add_recent_file('/path/to/file1.xlsx')  # Add again

        recent = config.get('recent_files')
        assert recent[0] == '/path/to/file1.xlsx'
        assert len(recent) == 2  # Should not duplicate

    @pytest.mark.unit
    def test_recent_files_max_limit(self, temp_dir, monkeypatch):
        """Test that recent files respects max limit."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('max_recent_files', 3)

        # Add more than max
        for i in range(5):
            config.add_recent_file(f'/path/to/file{i}.xlsx')

        recent = config.get('recent_files')
        assert len(recent) == 3

    @pytest.mark.unit
    def test_clear_recent_files(self, temp_dir, monkeypatch):
        """Test clearing recent files."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_recent_file('/path/to/file.xlsx')
        config.clear_recent_files()

        recent = config.get('recent_files')
        assert len(recent) == 0


class TestAppConfigPromptTemplates:
    """Test prompt template management."""

    @pytest.mark.unit
    def test_get_prompt_templates(self, temp_dir, monkeypatch):
        """Test getting prompt templates."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        templates = config.get_prompt_templates()

        assert isinstance(templates, dict)
        assert 'Capitalize' in templates

    @pytest.mark.unit
    def test_add_prompt_template(self, temp_dir, monkeypatch):
        """Test adding a prompt template."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_prompt_template('Custom Prompt', 'Do something custom')

        templates = config.get_prompt_templates()
        assert 'Custom Prompt' in templates
        assert templates['Custom Prompt'] == 'Do something custom'

    @pytest.mark.unit
    def test_update_existing_template(self, temp_dir, monkeypatch):
        """Test updating an existing template."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_prompt_template('Capitalize', 'New capitalize prompt')

        templates = config.get_prompt_templates()
        assert templates['Capitalize'] == 'New capitalize prompt'

    @pytest.mark.unit
    def test_remove_prompt_template(self, temp_dir, monkeypatch):
        """Test removing a prompt template."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_prompt_template('To Remove', 'This will be removed')
        config.remove_prompt_template('To Remove')

        templates = config.get_prompt_templates()
        assert 'To Remove' not in templates

    @pytest.mark.unit
    def test_remove_nonexistent_template(self, temp_dir, monkeypatch):
        """Test removing a template that doesn't exist."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        # Should not raise an error
        config.remove_prompt_template('NonExistent')


class TestAppConfigRestoreDefaults:
    """Test restoring default configuration."""

    @pytest.mark.unit
    def test_restore_defaults_basic(self, temp_dir, monkeypatch):
        """Test restoring basic defaults."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.set('temperature', 0.9)
        config.set('model', 'gpt-4')

        config.restore_defaults()

        assert config.get('temperature') == 0.3
        assert config.get('model') == 'gpt-3.5-turbo'

    @pytest.mark.unit
    def test_restore_defaults_keeps_recent_files(self, temp_dir, monkeypatch):
        """Test that restore keeps recent files by default."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_recent_file('/path/to/file.xlsx')

        config.restore_defaults()

        recent = config.get('recent_files')
        assert '/path/to/file.xlsx' in recent

    @pytest.mark.unit
    def test_restore_defaults_including_prompts(self, temp_dir, monkeypatch):
        """Test restoring defaults including prompts."""
        def mock_get_config_path(self):
            return temp_dir / "config.json"

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        config.add_prompt_template('Custom', 'Custom prompt')
        config.add_recent_file('/path/to/file.xlsx')

        config.restore_defaults(include_prompts=True)

        templates = config.get_prompt_templates()
        assert 'Custom' not in templates
        assert 'Capitalize' in templates  # Default should be present

        # Recent files should be cleared
        recent = config.get('recent_files')
        assert len(recent) == 0


class TestAppConfigErrorHandling:
    """Test error handling in configuration."""

    @pytest.mark.unit
    def test_load_corrupted_config(self, temp_dir, monkeypatch):
        """Test loading a corrupted configuration file."""
        config_file = temp_dir / "config.json"
        config_file.write_text("not valid json {]")

        def mock_get_config_path(self):
            return config_file

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        # Should not raise error, should use defaults
        config = AppConfig()
        assert config.get('api_type') == 'openai'

    @pytest.mark.unit
    def test_prompt_merge_on_load(self, temp_dir, monkeypatch):
        """Test that prompts are properly merged on load."""
        config_file = temp_dir / "config.json"

        # Save config with only one custom prompt
        config_data = {
            'api_type': 'openai',
            'prompts': {
                'Custom Only': 'Custom prompt'
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        def mock_get_config_path(self):
            return config_file

        monkeypatch.setattr(AppConfig, '_get_config_path', mock_get_config_path)

        config = AppConfig()
        templates = config.get_prompt_templates()

        # Should have both custom and default prompts
        assert 'Custom Only' in templates
        assert 'Capitalize' in templates
