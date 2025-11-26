@echo off
REM Employee Attendance System - Easy Launcher
REM No coding knowledge required!

echo ================================================
echo   Employee Attendance Management System
echo ================================================
echo.
echo Select an option:
echo.
echo   1. Enroll New Employee (Automated - Recommended)
echo   2. Start Attendance Recognition
echo   3. View Today's Attendance Report
echo   4. View Incomplete Checkouts
echo   5. View Absent Employees
echo   6. Exit
echo.
echo ================================================
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting Automated Enrollment...
    echo This will: Capture faces, Encode, and Train model automatically
    echo.
    python auto_enroll.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Starting Attendance Recognition System...
    echo.
    python recognition.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Generating Today's Report...
    echo.
    python view_attendance.py report
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Checking Incomplete Checkouts...
    echo.
    python view_attendance.py incomplete
    pause
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Checking Absent Employees...
    echo.
    python view_attendance.py absent
    pause
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Goodbye!
    goto end
)

echo.
echo Invalid choice! Please run the script again.
pause

:end
