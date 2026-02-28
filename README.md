# Claude Bar Tab

A macOS menu bar widget that displays your Claude API Gateway spend information.

## Features

- 💰 Shows current spend in the menu bar
- 📊 Displays detailed spend, budget, and usage percentage in dropdown menu
- 🔄 Auto-refresh at configurable intervals (5, 10, or 30 minutes)
- 🖱️ Manual refresh on demand
- 🎯 Native macOS menu bar integration

## Requirements

- macOS
- Python 3.7+
- Access to `~/.claude/settings.json` with API credentials

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x claude_bar_tab.py
```

## Usage

### Option 1: Run from Terminal
```bash
./run.sh
```
This will keep the terminal window open while the app runs. Close the terminal or press Ctrl+C to quit.

### Option 2: Run directly from Finder
Double-click `run.sh` in Finder to launch the app.

### Option 3: Manual run
```bash
source venv/bin/activate
python claude_bar_tab.py
```

The widget will appear in your menu bar showing your current spend. Click on it to see:
- Detailed spend information
- Budget limit
- Usage percentage
- Refresh options

## Auto-start on Login (Optional)

To make the app start automatically when you log in:

1. Open **System Settings** → **General** → **Login Items**
2. Click the **+** button
3. Navigate to and select the `claude_bar_tab.py` script
4. Or create a LaunchAgent (see below for advanced setup)

### Advanced: Create a LaunchAgent

Create `~/Library/LaunchAgents/com.claude.bartab.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.bartab</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/git/claude-bar-tab/claude_bar_tab.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Replace `YOUR_USERNAME` with your actual username, then:

```bash
launchctl load ~/Library/LaunchAgents/com.claude.bartab.plist
```

## Configuration

The app reads your API credentials from `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://your-api-gateway.com",
    "ANTHROPIC_AUTH_TOKEN": "your-token-here"
  }
}
```

## Troubleshooting

If the widget shows "Error":
- Check that `~/.claude/settings.json` exists and is properly formatted
- Verify your API credentials are correct
- Check your internet connection
- Look at console output for detailed error messages

## License

MIT
