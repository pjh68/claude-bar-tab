"""
Tests for update_spend() function.

Tests verify response parsing, menu item updates, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from claude_bar_tab import ConfigError, AuthError, NetworkError, ServerError, DataError


@pytest.fixture
def mock_fetch():
    """Fixture to mock fetch_spend_info."""
    with patch("claude_bar_tab.ClaudeSpendApp.fetch_spend_info") as mock:
        yield mock


def test_update_spend_typical_data(app, mock_fetch):
    """Correct title, spend, budget, usage, domain."""
    info = {
        "spend": 25.50,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.title == "❋ $25.50"
    assert app.spend_item.title == "Spend: $25.50"
    assert app.budget_item.title == "Budget: $100.00"
    assert app.usage_item.title == "Usage: 25.5%"
    assert app.domain_item.title == "Domain: api.example.com"


def test_update_spend_zero_budget(app, mock_fetch):
    """No ZeroDivisionError; usage shows 0.0%."""
    info = {
        "spend": 10.00,
        "max_budget": 0.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.usage_item.title == "Usage: 0.0%"


def test_update_spend_zero_spend_zero_budget(app, mock_fetch):
    """Both zero handled correctly."""
    info = {
        "spend": 0.00,
        "max_budget": 0.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.title == "❋ $0.00"
    assert app.spend_item.title == "Spend: $0.00"
    assert app.budget_item.title == "Budget: $0.00"
    assert app.usage_item.title == "Usage: 0.0%"


def test_update_spend_full_budget(app, mock_fetch):
    """100% usage displayed."""
    info = {
        "spend": 100.00,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.usage_item.title == "Usage: 100.0%"


def test_update_spend_over_budget(app, mock_fetch):
    """>100% usage displayed."""
    info = {
        "spend": 150.00,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.usage_item.title == "Usage: 150.0%"


def test_update_spend_domain_parsing(app, mock_fetch):
    """Domain extracted from URL."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://my-gateway.example.com")

    app.update_spend(None)

    assert app.domain_item.title == "Domain: my-gateway.example.com"


def test_update_spend_domain_with_port(app, mock_fetch):
    """Port included in domain display."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://localhost:8080")

    app.update_spend(None)

    assert app.domain_item.title == "Domain: localhost:8080"


def test_update_spend_expiry_future(app, mock_fetch):
    """Days until expiry calculated."""
    # Set expiry to 30 days from now
    future_date = datetime.now() + timedelta(days=30)
    expires_str = future_date.isoformat()

    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "expires": expires_str
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    # Should be approximately 30 days (might be 29 or 30 depending on timing)
    assert "29d" in app.expiry_item.title or "30d" in app.expiry_item.title


def test_update_spend_expiry_past(app, mock_fetch):
    """Negative days shown for past expiry."""
    # Set expiry to 10 days ago
    past_date = datetime.now() - timedelta(days=10)
    expires_str = past_date.isoformat()

    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "expires": expires_str
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    # Should be approximately -10 days (allow for timing variations)
    assert "-11d" in app.expiry_item.title or "-10d" in app.expiry_item.title or "-9d" in app.expiry_item.title


def test_update_spend_expiry_missing(app, mock_fetch):
    """Shows 'Unknown' when no expires field."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.expiry_item.title == "Expires: Unknown"


def test_update_spend_expiry_empty_string(app, mock_fetch):
    """Shows 'Unknown' for empty string."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "expires": ""
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.expiry_item.title == "Expires: Unknown"


def test_update_spend_metadata_single_entry(app, mock_fetch):
    """Single metadata item created."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "metadata": {
            "key_name": "my-key"
        }
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert len(app.metadata_items) == 1
    assert app.metadata_items[0].title == "key_name: my-key"


def test_update_spend_metadata_multiple_entries(app, mock_fetch):
    """Multiple metadata items created."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "metadata": {
            "key_name": "my-key",
            "workspace": "personal",
            "tier": "pro"
        }
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert len(app.metadata_items) == 3
    titles = [item.title for item in app.metadata_items]
    assert "key_name: my-key" in titles
    assert "workspace: personal" in titles
    assert "tier: pro" in titles


def test_update_spend_metadata_empty_dict(app, mock_fetch):
    """No metadata items for empty dict."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00,
        "metadata": {}
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert len(app.metadata_items) == 0


def test_update_spend_metadata_missing(app, mock_fetch):
    """No metadata items when key absent."""
    info = {
        "spend": 10.00,
        "max_budget": 100.00
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert len(app.metadata_items) == 0


def test_update_spend_config_error(app, mock_fetch):
    """ConfigError shows '❋ Config' title and error detail."""
    mock_fetch.side_effect = ConfigError("Settings not found: ~/.claude/settings.json")

    app.update_spend(None)

    assert app.title == "❋ Config"
    assert app.error_item.title == "⚠ Settings not found: ~/.claude/settings.json"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_auth_error(app, mock_fetch):
    """AuthError shows '❋ Auth' title and error detail."""
    mock_fetch.side_effect = AuthError("Unauthorized (401)")

    app.update_spend(None)

    assert app.title == "❋ Auth"
    assert app.error_item.title == "⚠ Unauthorized (401)"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_network_error(app, mock_fetch):
    """NetworkError shows '❋ Offline' title and error detail."""
    mock_fetch.side_effect = NetworkError("Connection timed out")

    app.update_spend(None)

    assert app.title == "❋ Offline"
    assert app.error_item.title == "⚠ Connection timed out"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_server_error(app, mock_fetch):
    """ServerError shows '❋ Server' title and error detail."""
    mock_fetch.side_effect = ServerError("Server error (500)")

    app.update_spend(None)

    assert app.title == "❋ Server"
    assert app.error_item.title == "⚠ Server error (500)"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_data_error(app, mock_fetch):
    """DataError shows '❋ Data' title and error detail."""
    mock_fetch.side_effect = DataError("Unexpected response format")

    app.update_spend(None)

    assert app.title == "❋ Data"
    assert app.error_item.title == "⚠ Unexpected response format"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_generic_error(app, mock_fetch):
    """Unexpected exception shows '❋ Error' title and error detail."""
    mock_fetch.side_effect = Exception("Unexpected error")

    app.update_spend(None)

    assert app.title == "❋ Error"
    assert app.error_item.title == "⚠ Unexpected error"
    assert app.spend_item.title == "Spend: Error"
    assert app.budget_item.title == "Budget: Error"
    assert app.usage_item.title == "Usage: Error"
    assert app.domain_item.title == "Domain: Error"
    assert app.expiry_item.title == "Expires: Error"


def test_update_spend_success_clears_error(app, mock_fetch):
    """Successful update clears error_item."""
    info = {
        "spend": 25.50,
        "max_budget": 100.00,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.error_item.title == ""
    assert app.title == "❋ $25.50"


def test_update_spend_large_spend_formatting(app, mock_fetch):
    """Large numbers formatted to 2 decimal places."""
    info = {
        "spend": 12345.678,
        "max_budget": 50000.999,
        "expires": "2026-12-31T23:59:59"
    }
    mock_fetch.return_value = (info, "https://api.example.com")

    app.update_spend(None)

    assert app.title == "❋ $12345.68"
    assert app.spend_item.title == "Spend: $12345.68"
    assert app.budget_item.title == "Budget: $50001.00"
