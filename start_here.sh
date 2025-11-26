#!/bin/bash
# Employee Attendance System - Easy Launcher
# Works on Linux/Raspberry Pi/Mac

clear
echo "================================================"
echo "   Employee Attendance Management System"
echo "================================================"
echo ""
echo "Select an option:"
echo ""
echo "   1. Enroll New Employee (Automated - Recommended)"
echo "   2. Start Attendance Recognition"
echo "   3. View Today's Attendance Report"
echo "   4. View Incomplete Checkouts"
echo "   5. View Absent Employees"
echo "   6. Exit"
echo ""
echo "================================================"
echo ""

read -p "Enter your choice (1-6): " choice

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
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice! Please run the script again."
        read -p "Press Enter to continue..."
        ;;
esac
