#!/bin/bash
# Launcher script for Claude Bar Tab

cd "$(dirname "$0")"
source venv/bin/activate
nohup python claude_bar_tab.py > /dev/null 2>&1 &
echo "Claude Bar Tab started (PID: $!)"
