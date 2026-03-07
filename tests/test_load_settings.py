"""
Tests for load_settings() function.

Tests verify settings file loading, JSON parsing, and required field validation.
"""

import json
import pytest
from unittest.mock import mock_open, patch
from pathlib import Path
from claude_bar_tab import ConfigError


def test_load_settings_success(app):
    """Valid JSON returns (url, key) tuple."""
    settings_data = {
        "env": {
            "ANTHROPIC_BASE_URL": "https://api.example.com",
            "ANTHROPIC_AUTH_TOKEN": "test-token-123"
        }
    }

    m = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", m):
        url, key = app.load_settings()

    assert url == "https://api.example.com"
    assert key == "test-token-123"


def test_load_settings_file_not_found(app):
    """Missing file raises ConfigError."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with pytest.raises(ConfigError) as exc_info:
            app.load_settings()

    assert "Settings not found" in str(exc_info.value)


def test_load_settings_malformed_json(app):
    """Invalid JSON raises ConfigError."""
    m = mock_open(read_data="{not valid json")

    with patch("builtins.open", m):
        with pytest.raises(ConfigError) as exc_info:
            app.load_settings()

    assert "invalid JSON" in str(exc_info.value)


def test_load_settings_missing_env_key(app):
    """No env key raises ConfigError."""
    settings_data = {
        "other_key": "value"
    }

    m = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", m):
        with pytest.raises(ConfigError) as exc_info:
            app.load_settings()

    assert "Missing key: env" in str(exc_info.value)


def test_load_settings_missing_base_url(app):
    """No ANTHROPIC_BASE_URL raises ConfigError."""
    settings_data = {
        "env": {
            "ANTHROPIC_AUTH_TOKEN": "test-token-123"
        }
    }

    m = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", m):
        with pytest.raises(ConfigError) as exc_info:
            app.load_settings()

    assert "Missing key: ANTHROPIC_BASE_URL" in str(exc_info.value)


def test_load_settings_missing_auth_token(app):
    """No ANTHROPIC_AUTH_TOKEN raises ConfigError."""
    settings_data = {
        "env": {
            "ANTHROPIC_BASE_URL": "https://api.example.com"
        }
    }

    m = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", m):
        with pytest.raises(ConfigError) as exc_info:
            app.load_settings()

    assert "Missing key: ANTHROPIC_AUTH_TOKEN" in str(exc_info.value)


def test_load_settings_uses_correct_path(app):
    """Opens ~/.claude/settings.json."""
    settings_data = {
        "env": {
            "ANTHROPIC_BASE_URL": "https://api.example.com",
            "ANTHROPIC_AUTH_TOKEN": "test-token-123"
        }
    }

    m = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", m) as mock_file:
        app.load_settings()

    expected_path = Path.home() / ".claude" / "settings.json"
    mock_file.assert_called_once_with(expected_path)
