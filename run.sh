#!/bin/bash
# Launcher script for Claude Bar Tab

cd "$(dirname "$0")"
source venv/bin/activate
python claude_bar_tab.py
