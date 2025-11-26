#!/bin/bash
# Employee Attendance System - Easy Launcher
# Works on Linux/Raspberry Pi/Mac

# Project directory - Change this if your project is in a different location
PROJECT_DIR="$HOME/smartAttendance"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "Error: Project directory not found at $PROJECT_DIR"
    echo "Please update PROJECT_DIR in this script to match your installation path."
    read -p "Press Enter to exit..."
    exit 1
}

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated ✓"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated ✓"
else
    echo "Warning: Virtual environment not found!"
    echo "Looking for .venv or venv in $PROJECT_DIR"
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

clear
echo "================================================"
echo "   Employee Attendance Management System"
echo "================================================"
echo "Working Directory: $PROJECT_DIR"
echo ""
echo "Select an option:"
echo ""
echo "   1. Enroll New Employee (Automated - Recommended)"
echo "   2. Start Attendance Recognition"
echo "   3. View Today's Attendance Report"
echo "   4. View Incomplete Checkouts"
echo "   5. View Absent Employees"
echo "   6. Manage Employees (Delete Enrollments)"
echo "   7. Test Camera (Troubleshooting)"
echo "   8. Exit"
echo ""
echo "================================================"
echo ""

read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo ""
        echo "Starting Automated Enrollment..."
        echo "This will: Capture faces, Encode, and Train model automatically"
        echo ""
        python3 auto_enroll.py
        ;;
    2)
        echo ""
        echo "Starting Attendance Recognition System..."
        echo ""
        python3 recognition.py
        ;;
    3)
        echo ""
        echo "Generating Today's Report..."
        echo ""
        python3 view_attendance.py report
        read -p "Press Enter to continue..."
        ;;
    4)
        echo ""
        echo "Checking Incomplete Checkouts..."
        echo ""
        python3 view_attendance.py incomplete
        read -p "Press Enter to continue..."
        ;;
    5)
        echo ""
        echo "Checking Absent Employees..."
        echo ""
        python3 view_attendance.py absent
        read -p "Press Enter to continue..."
        ;;
    6)
        echo ""
        echo "Opening Employee Management..."
        echo ""
        python3 manage_employees.py
        ;;
    7)
        echo ""
        echo "Testing Camera..."
        echo ""
        python3 test_camera.py
        ;;
    8)
        echo ""
        echo "Goodbye!"
        # Deactivate virtual environment if it was activated
        if [ -n "$VIRTUAL_ENV" ]; then
            deactivate
        fi
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice! Please run the script again."
        read -p "Press Enter to continue..."
        ;;
esac

# Deactivate virtual environment after execution
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
