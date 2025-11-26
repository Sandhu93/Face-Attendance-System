#!/bin/bash
# GUI Launcher for Employee Attendance System
# For touchscreen displays on Raspberry Pi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project directory - use script location or fallback to default
if [ -f "$SCRIPT_DIR/start_gui.py" ]; then
    PROJECT_DIR="$SCRIPT_DIR"
else
    PROJECT_DIR="$HOME/smartAttendance"
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "Error: Project directory not found at $PROJECT_DIR"
    echo "Please ensure start_gui.py exists in the same directory as this script."
    exit 1
}

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Launch GUI
python3 start_gui.py

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
