#!/bin/bash

# Installation script for Claude Bar Tab
# This script builds the app and installs it to /Applications

set -e  # Exit on error

echo "======================================"
echo "Claude Bar Tab Installer"
echo "======================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the project root directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
pip install -q py2app

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build the app
echo "Building Claude Bar Tab.app..."
python setup.py py2app

# Check if build was successful
if [ ! -d "dist/Claude Bar Tab.app" ]; then
    echo "Error: Build failed. Claude Bar Tab.app not found in dist directory."
    exit 1
fi

echo "Build successful!"

# Install to Applications
APP_NAME="Claude Bar Tab.app"
DEST_PATH="/Applications/$APP_NAME"

echo ""
echo "Installing to /Applications..."

# Remove existing installation if present
if [ -d "$DEST_PATH" ]; then
    echo "Removing existing installation..."
    rm -rf "$DEST_PATH"
fi

# Copy to Applications
cp -R "dist/$APP_NAME" "/Applications/"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "Installation complete!"
    echo "======================================"
    echo ""
    echo "Claude Bar Tab has been installed to /Applications"
    echo "You can now launch it from Spotlight or your Applications folder."
else
    echo "Error: Failed to copy app to /Applications"
    echo "You may need to run this script with sudo:"
    echo "  sudo ./install.sh"
    exit 1
fi
