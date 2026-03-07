"""
Tests for fetch_spend_info() function.

Tests verify API request construction, response parsing, and HTTP error handling.
"""

import json
import urllib.error
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO


@pytest.fixture
def mock_settings():
    """Fixture to mock load_settings."""
    with patch("claude_bar_tab.ClaudeSpendApp.load_settings") as mock:
        mock.return_value = ("https://api.example.com", "test-token-123")
        yield mock


def test_fetch_spend_info_success(app, mock_settings):
    """Valid response returns (info_dict, url)."""
    response_data = {
        "info": {
            "spend": 10.50,
            "max_budget": 100.00
        }
    }

    mock_response = MagicMock()
    mock_response.__enter__ = MagicMock(return_value=BytesIO(json.dumps(response_data).encode()))
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        info, url = app.fetch_spend_info()

    assert info == {"spend": 10.50, "max_budget": 100.00}
    assert url == "https://api.example.com"


def test_fetch_spend_info_constructs_correct_request(app, mock_settings):
    """URL is {base}/key/info, header is Bearer {token}."""
    response_data = {"info": {"spend": 10.50, "max_budget": 100.00}}

    mock_response = MagicMock()
    mock_response.__enter__ = MagicMock(return_value=BytesIO(json.dumps(response_data).encode()))
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        app.fetch_spend_info()

    # Verify the request was made with correct URL and headers
    call_args = mock_urlopen.call_args
    request = call_args[0][0]

    assert request.full_url == "https://api.example.com/key/info"
    assert request.headers["Authorization"] == "Bearer test-token-123"


def test_fetch_spend_info_timeout_is_10(app, mock_settings):
    """urlopen called with timeout=10."""
    response_data = {"info": {"spend": 10.50, "max_budget": 100.00}}

    mock_response = MagicMock()
    mock_response.__enter__ = MagicMock(return_value=BytesIO(json.dumps(response_data).encode()))
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        app.fetch_spend_info()

    # Verify timeout parameter
    call_args = mock_urlopen.call_args
    assert call_args[1]["timeout"] == 10


def test_fetch_spend_info_http_401(app, mock_settings):
    """401 Unauthorized raises Exception."""
    error = urllib.error.HTTPError(
        "https://api.example.com/key/info",
        401,
        "Unauthorized",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_http_403(app, mock_settings):
    """403 Forbidden raises Exception."""
    error = urllib.error.HTTPError(
        "https://api.example.com/key/info",
        403,
        "Forbidden",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_http_404(app, mock_settings):
    """404 Not Found raises Exception."""
    error = urllib.error.HTTPError(
        "https://api.example.com/key/info",
        404,
        "Not Found",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_http_500(app, mock_settings):
    """500 Internal Server Error raises Exception."""
    error = urllib.error.HTTPError(
        "https://api.example.com/key/info",
        500,
        "Internal Server Error",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_network_timeout(app, mock_settings):
    """URLError("timed out") raises Exception."""
    error = urllib.error.URLError("timed out")

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_connection_refused(app, mock_settings):
    """URLError(ConnectionRefusedError) raises Exception."""
    error = urllib.error.URLError(ConnectionRefusedError())

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Failed to fetch spend info" in str(exc_info.value)


def test_fetch_spend_info_settings_failure_propagates(app):
    """Exception from load_settings propagates."""
    with patch.object(app, "load_settings", side_effect=Exception("Settings error")):
        with pytest.raises(Exception) as exc_info:
            app.fetch_spend_info()

    assert "Settings error" in str(exc_info.value)
