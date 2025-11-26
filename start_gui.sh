#!/bin/bash
# GUI Launcher for Employee Attendance System
# For touchscreen displays on Raspberry Pi

# Project directory - Change this if your project is in a different location
PROJECT_DIR="$HOME/smartAttendance"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "Error: Project directory not found at $PROJECT_DIR"
    echo "Please update PROJECT_DIR in this script."
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
