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


class ClaudeSpendApp(rumps.App):
    def __init__(self):
        super(ClaudeSpendApp, self).__init__("❋", quit_button=None)

        # Create menu structure with placeholders for spend info
        self.spend_item = rumps.MenuItem("Spend: Loading...", callback=None)
        self.budget_item = rumps.MenuItem("Budget: Loading...", callback=None)
        self.usage_item = rumps.MenuItem("Usage: Loading...", callback=None)
        self.domain_item = rumps.MenuItem("Domain: Loading...", callback=None)
        self.expiry_item = rumps.MenuItem("Expires: Loading...", callback=None)

        # Metadata items - will be populated dynamically
        self.metadata_items = []

        self.menu = [
            self.spend_item,
            self.budget_item,
            self.usage_item,
            self.expiry_item,
            None,  # Separator
            self.domain_item,
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
        settings_path = Path.home() / ".claude" / "settings.json"
        try:
            with open(settings_path) as f:
                settings = json.load(f)
                url = settings["env"]["ANTHROPIC_BASE_URL"]
                key = settings["env"]["ANTHROPIC_AUTH_TOKEN"]
                return url, key
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to load settings from {settings_path}: {e}")

    def fetch_spend_info(self):
        """Fetch spend information from the API gateway."""
        url, key = self.load_settings()

        request = urllib.request.Request(
            f"{url}/key/info",
            headers={"Authorization": f"Bearer {key}"}
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.load(response)
                return data["info"], url
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch spend info: {e}")

    @rumps.clicked("Refresh Now")
    def manual_refresh(self, _):
        """Manual refresh triggered by menu click."""
        self.update_spend(None)

    def update_spend(self, _):
        """Update the menu bar with current spend information."""
        try:
            info, base_url = self.fetch_spend_info()
            spend = info["spend"]
            max_budget = info["max_budget"]
            pct = (spend / max_budget * 100) if max_budget > 0 else 0

            # Update menu bar title
            self.title = f"❋ ${spend:.2f}"

            # Update menu items with detailed info
            self.spend_item.title = f"Spend: ${spend:.2f}"
            self.budget_item.title = f"Budget: ${max_budget:.2f}"
            self.usage_item.title = f"Usage: {pct:.1f}%"

            # Update domain
            parsed_url = urlparse(base_url)
            self.domain_item.title = f"Domain: {parsed_url.netloc}"

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
                    item = rumps.MenuItem(f"{key}: {value}", callback=None)
                    self.metadata_items.append(item)
                    self.menu.insert_after("Metadata", item)

        except Exception as e:
            self.title = "❋ Error"
            self.spend_item.title = "Spend: Error"
            self.budget_item.title = "Budget: Error"
            self.usage_item.title = "Usage: Error"
            self.domain_item.title = "Domain: Error"
            self.expiry_item.title = "Expires: Error"
            print(f"Error updating spend: {e}")

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
