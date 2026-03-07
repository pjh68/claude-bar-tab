"""
Setup script for building Claude Bar Tab macOS app with py2app
"""

from setuptools import setup

APP = ['claude_bar_tab.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'Claude Bar Tab',
        'CFBundleDisplayName': 'Claude Bar Tab',
        'CFBundleGetInfoString': 'Claude API Gateway Spend Tracker',
        'CFBundleIdentifier': 'com.github.pjh68.claude-bar-tab',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # This makes it a menu bar only app (no dock icon)
    },
    'packages': ['rumps', 'urllib', 'json'],
    'includes': ['urllib.request', 'urllib.error', 'urllib.parse'],
}

setup(
    name='ClaudeBarTab',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    py_modules=['claude_bar_tab'],
)
