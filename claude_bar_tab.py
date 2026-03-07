#!/usr/bin/env python3
"""
Claude API Gateway Spend Tracker - macOS Menu Bar Widget
Displays your Claude API spend information in the macOS menu bar.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import rumps


# Custom exception hierarchy for error categorization
class AppError(Exception):
    """Base class for application-specific errors."""
    def __init__(self, user_message):
        self.user_message = user_message
        super().__init__(user_message)


class ConfigError(AppError):
    """Settings file issues (missing, malformed, missing keys)."""
    pass


class AuthError(AppError):
    """Authentication/authorization errors (401, 403)."""
    pass


class NetworkError(AppError):
    """Network connectivity issues (timeout, connection refused, DNS)."""
    pass


class ServerError(AppError):
    """Server-side errors (5xx responses)."""
    pass


class DataError(AppError):
    """Unexpected response format or missing data."""
    pass


class ClaudeSpendApp(rumps.App):
    def do_nothing(self, _):
        """Dummy callback to prevent menu items from being greyed out."""
        pass

    def __init__(self):
        super(ClaudeSpendApp, self).__init__("❋", quit_button=None)

        # Settings file path
        self.settings_path = Path.home() / ".claude" / "settings.json"

        # Create error display item (hidden by default)
        self.error_item = rumps.MenuItem("", callback=self.do_nothing)
        self.error_item.hide()

        # Create menu structure with placeholders for spend info
        self.spend_item = rumps.MenuItem("Spend: Loading...", callback=self.do_nothing)
        self.budget_item = rumps.MenuItem("Budget: Loading...", callback=self.do_nothing)
        self.usage_item = rumps.MenuItem("Usage: Loading...", callback=self.do_nothing)
        self.domain_item = rumps.MenuItem("Domain: Loading...", callback=self.do_nothing)
        self.expiry_item = rumps.MenuItem("Expires: Loading...", callback=self.do_nothing)
        self.settings_file_item = rumps.MenuItem("", callback=self.do_nothing)
        self.settings_file_item.hide()

        # Metadata items - will be populated dynamically
        self.metadata_items = []

        self.menu = [
            self.error_item,
            None,  # Separator
            self.spend_item,
            self.budget_item,
            self.usage_item,
            self.expiry_item,
            None,  # Separator
            self.domain_item,
            self.settings_file_item,
            None,  # Separator (metadata will be inserted here)
            "Metadata",
            None,  # Separator
            rumps.MenuItem("Auto-refresh: 5 min", callback=self.set_interval_5),
            rumps.MenuItem("Auto-refresh: 10 min", callback=self.set_interval_10),
            rumps.MenuItem("Auto-refresh: 30 min", callback=self.set_interval_30),
            None,  # Separator (metadata will be inserted here)
            "Refresh Now",
            None,
            "Quit"
        ]

        self.interval = 300  # Default 5 minutes
        self.menu["Auto-refresh: 5 min"].state = True

        # Initial update
        self.update_spend(None)

        # Set up timer for auto-refresh
        self.timer = rumps.Timer(self.update_spend, self.interval)
        self.timer.start()

    def load_settings(self):
        """Load settings from Claude settings file."""
        try:
            with open(self.settings_path) as f:
                settings = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Settings not found: {self.settings_path}")
        except json.JSONDecodeError:
            raise ConfigError("Settings file has invalid JSON")

        try:
            url = settings["env"]["ANTHROPIC_BASE_URL"]
        except KeyError:
            if "env" not in settings:
                raise ConfigError("Missing key: env")
            raise ConfigError("Missing key: ANTHROPIC_BASE_URL")

        try:
            key = settings["env"]["ANTHROPIC_AUTH_TOKEN"]
        except KeyError:
            raise ConfigError("Missing key: ANTHROPIC_AUTH_TOKEN")

        return url, key

    def fetch_spend_data(self, url, key):
        """Fetch spend data from the API gateway."""
        request = urllib.request.Request(
            f"{url}/key/info",
            headers={"Authorization": f"Bearer {key}"}
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.load(response)
                return data["info"]
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise AuthError(f"Unauthorized ({e.code})")
            elif e.code == 403:
                raise AuthError(f"Forbidden ({e.code})")
            elif 500 <= e.code < 600:
                raise ServerError(f"Server error ({e.code})")
            else:
                raise ServerError(f"HTTP error ({e.code})")
        except urllib.error.URLError as e:
            reason = str(e.reason)
            if "timed out" in reason.lower():
                raise NetworkError("Connection timed out")
            elif isinstance(e.reason, ConnectionRefusedError):
                raise NetworkError("Connection refused")
            else:
                raise NetworkError(reason)
        except (KeyError, json.JSONDecodeError):
            raise DataError("Unexpected response format")

    def fetch_spend_info(self):
        """Fetch spend information from the API gateway."""
        url, key = self.load_settings()
        info = self.fetch_spend_data(url, key)
        return info, url

    def _set_error_state(self, title_suffix, error_message, domain_text="Domain: Error"):
        """Set menu items to error state."""
        self.title = f"❋ {title_suffix}"
        self.error_item.title = f"⚠ {error_message}"
        self.error_item.show()
        self.spend_item.title = "Spend: Error"
        self.budget_item.title = "Budget: Error"
        self.usage_item.title = "Usage: Error"
        self.domain_item.title = domain_text
        self.expiry_item.title = "Expires: Error"
        self.settings_file_item.title = f"Settings: {self.settings_path}"
        self.settings_file_item.show()

    @rumps.clicked("Refresh Now")
    def manual_refresh(self, _):
        """Manual refresh triggered by menu click."""
        self.update_spend(None)

    def update_spend(self, _):
        """Update the menu bar with current spend information."""
        # Phase 1: Try to load settings
        try:
            url, key = self.load_settings()
        except ConfigError as e:
            # Settings failed to load - domain is unavailable
            self._set_error_state("Config", e.user_message, "Domain: Error")
            return

        # Phase 2: Settings loaded successfully, domain is known
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        try:
            info = self.fetch_spend_data(url, key)
            spend = info["spend"]
            max_budget = info["max_budget"]
            pct = (spend / max_budget * 100) if max_budget > 0 else 0

            # Update menu bar title
            self.title = f"❋ ${spend:.2f}"

            # Clear error display and settings file item
            self.error_item.hide()
            self.settings_file_item.hide()

            # Update menu items with detailed info
            self.spend_item.title = f"Spend: ${spend:.2f}"
            self.budget_item.title = f"Budget: ${max_budget:.2f}"
            self.usage_item.title = f"Usage: {pct:.1f}%"

            # Update domain
            self.domain_item.title = f"Domain: {domain}"

            # Update expiry - calculate days until expiration
            expires_str = info.get("expires", "")
            if expires_str:
                expires_dt = datetime.fromisoformat(expires_str.replace('+00:00', ''))
                days_until_expiry = (expires_dt - datetime.now()).days
                self.expiry_item.title = f"Expires: {days_until_expiry}d"
            else:
                self.expiry_item.title = "Expires: Unknown"

            # Update metadata - remove old metadata items first
            for item in self.metadata_items:
                if item in self.menu.values():
                    self.menu.pop(item.title)
            self.metadata_items.clear()

            # Add new metadata items
            metadata = info.get("metadata", {})
            if metadata:
                for key, value in metadata.items():
                    item = rumps.MenuItem(f"{key}: {value}", callback=self.do_nothing)
                    self.metadata_items.append(item)
                    self.menu.insert_after("Metadata", item)

        except AuthError as e:
            self._set_error_state("Auth", e.user_message, f"Domain: {domain}")
        except NetworkError as e:
            self._set_error_state("Offline", e.user_message, f"Domain: {domain}")
        except ServerError as e:
            self._set_error_state("Server", e.user_message, f"Domain: {domain}")
        except DataError as e:
            self._set_error_state("Data", e.user_message, f"Domain: {domain}")
        except Exception as e:
            self._set_error_state("Error", str(e), f"Domain: {domain}")

    def set_interval_5(self, sender):
        """Set refresh interval to 5 minutes."""
        self.set_interval(sender, 300, "5 min")

    def set_interval_10(self, sender):
        """Set refresh interval to 10 minutes."""
        self.set_interval(sender, 600, "10 min")

    def set_interval_30(self, sender):
        """Set refresh interval to 30 minutes."""
        self.set_interval(sender, 1800, "30 min")

    def set_interval(self, sender, seconds, label):
        """Update the refresh interval."""
        # Uncheck all interval options
        self.menu["Auto-refresh: 5 min"].state = False
        self.menu["Auto-refresh: 10 min"].state = False
        self.menu["Auto-refresh: 30 min"].state = False

        # Check the selected option
        sender.state = True

        # Update timer
        self.timer.stop()
        self.timer.interval = seconds
        self.timer.start()

    @rumps.clicked("Quit")
    def quit_app(self, _):
        """Quit the application."""
        rumps.quit_application()


if __name__ == "__main__":
    ClaudeSpendApp().run()
