#!/bin/bash

# Run script: Executes the wallpaper watcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
SETUP_SCRIPT="$SCRIPT_DIR/setup.sh"
PYTHON_SCRIPT="$SCRIPT_DIR/lib/bg_watcher.py"

# Ensure setup is complete
if [ -f "$SETUP_SCRIPT" ]; then
    bash "$SETUP_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Error: Setup failed"
        exit 1
    fi
else
    echo "Error: setup.sh not found"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: lib/bg_watcher.py not found"
    exit 1
fi

# Run the Python script using the virtual environment
echo "Starting wallpaper watcher..."
"$VENV_DIR/bin/python" "$PYTHON_SCRIPT"
