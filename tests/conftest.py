"""
pytest configuration and shared fixtures.

This module mocks the rumps library before the main module is imported,
allowing tests to run on any platform without macOS dependencies.
"""

import sys
from unittest.mock import MagicMock, patch
import pytest


# Mock rumps module before any imports
class MockMenuItem:
    """Mock MenuItem class."""
    def __init__(self, title, callback=None):
        self.title = title
        self.callback = callback
        self.state = False


class MockTimer:
    """Mock Timer class."""
    def __init__(self, callback, interval):
        self.callback = callback
        self.interval = interval
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False


class MockMenu(dict):
    """Mock menu class that extends dict with insert_after method."""
    def insert_after(self, after_key, item):
        """Mock insert_after method for inserting menu items."""
        # For testing purposes, just add the item to the dict
        if isinstance(item, MockMenuItem):
            self[item.title] = item

    def pop(self, key, default=None):
        """Override pop to handle missing keys gracefully."""
        return super().pop(key, default)


class MockApp:
    """Mock App class."""
    def __init__(self, name, quit_button=None):
        self.title = name
        self._menu = MockMenu()
        self.quit_button = quit_button

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, items):
        """Set menu items, handling None (separators) and MenuItem objects."""
        self._menu.clear()
        for item in items:
            if item is None:
                continue
            if isinstance(item, str):
                self._menu[item] = MockMenuItem(item)
            elif isinstance(item, MockMenuItem):
                self._menu[item.title] = item


def mock_clicked(title):
    """Mock decorator for clicked menu items."""
    def decorator(func):
        func._clicked_title = title
        return func
    return decorator


def mock_quit_application():
    """Mock quit_application function."""
    pass


# Create mock rumps module
mock_rumps = MagicMock()
mock_rumps.App = MockApp
mock_rumps.MenuItem = MockMenuItem
mock_rumps.Timer = MockTimer
mock_rumps.clicked = mock_clicked
mock_rumps.quit_application = mock_quit_application

# Inject mock into sys.modules before import
sys.modules['rumps'] = mock_rumps


@pytest.fixture
def app():
    """
    Create a ClaudeSpendApp instance for testing.

    Patches update_spend during __init__ to prevent automatic API calls,
    then restores the real method.
    """
    from claude_bar_tab import ClaudeSpendApp

    # Patch update_spend to a no-op during initialization
    with patch.object(ClaudeSpendApp, 'update_spend', lambda self, _: None):
        app_instance = ClaudeSpendApp()

    return app_instance
