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
import rumps


class ClaudeSpendApp(rumps.App):
    def __init__(self):
        super(ClaudeSpendApp, self).__init__("💰", quit_button=None)
        self.menu = [
            "Refresh Now",
            None,  # Separator
            rumps.MenuItem("Auto-refresh: 5 min", callback=self.set_interval_5),
            rumps.MenuItem("Auto-refresh: 10 min", callback=self.set_interval_10),
            rumps.MenuItem("Auto-refresh: 30 min", callback=self.set_interval_30),
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
                return data["info"]
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch spend info: {e}")

    @rumps.clicked("Refresh Now")
    def manual_refresh(self, _):
        """Manual refresh triggered by menu click."""
        self.update_spend(None)

    def update_spend(self, _):
        """Update the menu bar with current spend information."""
        try:
            info = self.fetch_spend_info()
            spend = info["spend"]
            max_budget = info["max_budget"]
            pct = (spend / max_budget * 100) if max_budget > 0 else 0

            # Update menu bar title
            self.title = f"💰 ${spend:.2f}"

            # Update menu items with detailed info
            if "Refresh Now" in self.menu:
                self.menu.pop("Refresh Now")

            self.menu.insert_before(
                "Auto-refresh: 5 min",
                [
                    rumps.MenuItem(f"Spend: ${spend:.2f}", callback=None),
                    rumps.MenuItem(f"Budget: ${max_budget:.2f}", callback=None),
                    rumps.MenuItem(f"Usage: {pct:.1f}%", callback=None),
                    None,
                    "Refresh Now",
                    None
                ]
            )

        except Exception as e:
            self.title = "💰 Error"
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
