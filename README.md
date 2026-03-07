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
- Access to `~/.claude/settings.json` with API credentials

## Installation

### Option 1: Standalone App (Recommended)

Build and install a standalone macOS application:

1. Clone this repository:
```bash
git clone https://github.com/pjh68/claude-bar-tab.git
cd claude-bar-tab
```

2. Run the installer:
```bash
./install.sh
```

3. Launch the app:
```bash
open "/Applications/Claude Bar Tab.app"
```

The app runs as a menu bar-only application (no dock icon) and includes all dependencies. The install.sh script automatically creates a virtual environment, installs dependencies, builds with py2app, and copies to /Applications.

### Option 2: Run from Python Script

For development or if you prefer running directly from Python:

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the app:
```bash
./run.sh
```

To stop the app, click "Quit" from the menu, or run:
```bash
pkill -f claude_bar_tab.py
```

## Usage

The widget will appear in your menu bar showing your current spend (e.g., "❋ $12.34"). Click on it to see:
- Detailed spend information
- Budget limit
- Usage percentage
- Domain information
- Expiration date
- Auto-refresh interval options (5, 10, or 30 minutes)
- Manual refresh option

## Auto-start on Login (Optional)

### For Standalone App (Recommended)

1. Open **System Settings** → **General** → **Login Items**
2. Click the **+** button
3. Navigate to `/Applications/` and select **Claude Bar Tab**
4. The app will now start automatically when you log in

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

### App Build Configuration

The standalone app is configured in `setup.py` with the following settings:
- **Bundle ID**: `com.github.pjh68.claude-bar-tab`
- **Version**: 1.0.0
- **Menu bar only**: No dock icon (`LSUIElement: True`)
- **Included packages**: rumps, urllib, json

## Troubleshooting

If the widget shows "Error":
- Check that `~/.claude/settings.json` exists and is properly formatted
- Verify your API credentials are correct
- Check your internet connection
- Look at console output for detailed error messages

## License

MIT
