"""
Attendance Viewer - View and export attendance records from SQLite database
"""
import sqlite3
from datetime import datetime, timedelta
import json
import csv

def connect_db():
    """Connect to the attendance database"""
    return sqlite3.connect('database/attendance.db')

def view_today_attendance():
    """View today's attendance"""
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT employee_id, employee_name, check_in, check_out, working_hours
        FROM attendance
        WHERE date = ?
        ORDER BY check_in DESC
    ''', (today,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"TODAY'S ATTENDANCE - {today}")
    print(f"{'='*80}")
    print(f"{'ID':<10} {'Name':<20} {'Check-IN':<20} {'Check-OUT':<20} {'Hours':<10}")
    print(f"{'-'*80}")
    
    for row in rows:
        emp_id, name, check_in, check_out, hours = row
        check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
        check_out_time = check_out.split(' ')[1] if check_out else 'N/A'
        print(f"{emp_id:<10} {name:<20} {check_in_time:<20} {check_out_time:<20} {hours:<10.2f}")
    
    print(f"{'='*80}\n")
    return rows

def view_date_range_attendance(start_date, end_date):
    """View attendance for a date range"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, employee_id, employee_name, check_in, check_out, working_hours
        FROM attendance
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC, check_in DESC
    ''', (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*90}")
    print(f"ATTENDANCE REPORT - {start_date} to {end_date}")
    print(f"{'='*90}")
    print(f"{'Date':<12} {'ID':<10} {'Name':<20} {'Check-IN':<10} {'Check-OUT':<10} {'Hours':<10}")
    print(f"{'-'*90}")
    
    for row in rows:
        date, emp_id, name, check_in, check_out, hours = row
        check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
        check_out_time = check_out.split(' ')[1] if check_out else 'N/A'
        print(f"{date:<12} {emp_id:<10} {name:<20} {check_in_time:<10} {check_out_time:<10} {hours:<10.2f}")
    
    print(f"{'='*90}\n")
    return rows

def view_employee_attendance(employee_id, days=30):
    """View attendance history for a specific employee"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, check_in, check_out, working_hours
        FROM attendance
        WHERE employee_id = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (employee_id, days))
    
    rows = cursor.fetchall()
    
    # Get employee name
    cursor.execute('''
        SELECT employee_name FROM attendance
        WHERE employee_id = ?
        LIMIT 1
    ''', (employee_id,))
    
    result = cursor.fetchone()
    emp_name = result[0] if result else "Unknown"
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"EMPLOYEE ATTENDANCE - {emp_name} (ID: {employee_id})")
    print(f"{'='*80}")
    print(f"{'Date':<12} {'Check-IN':<20} {'Check-OUT':<20} {'Hours':<10}")
    print(f"{'-'*80}")
    
    total_hours = 0
    for row in rows:
        date, check_in, check_out, hours = row
        check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
        check_out_time = check_out.split(' ')[1] if check_out else 'N/A'
        print(f"{date:<12} {check_in_time:<20} {check_out_time:<20} {hours:<10.2f}")
        total_hours += hours if hours else 0
    
    print(f"{'-'*80}")
    print(f"Total working hours: {total_hours:.2f}")
    print(f"{'='*80}\n")
    return rows

def export_to_csv(start_date, end_date, filename="attendance_report.csv"):
    """Export attendance to CSV file"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, employee_id, employee_name, check_in, check_out, working_hours
        FROM attendance
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC, employee_id
    ''', (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Employee ID', 'Employee Name', 'Check-IN', 'Check-OUT', 'Working Hours'])
        writer.writerows(rows)
    
    print(f"Exported {len(rows)} records to {filename}")
    return filename

def get_attendance_summary(start_date, end_date):
    """Get summary statistics for attendance"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            employee_id,
            employee_name,
            COUNT(*) as days_present,
            SUM(working_hours) as total_hours,
            AVG(working_hours) as avg_hours
        FROM attendance
        WHERE date BETWEEN ? AND ?
        GROUP BY employee_id, employee_name
        ORDER BY employee_name
    ''', (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*90}")
    print(f"ATTENDANCE SUMMARY - {start_date} to {end_date}")
    print(f"{'='*90}")
    print(f"{'ID':<10} {'Name':<25} {'Days':<10} {'Total Hours':<15} {'Avg Hours/Day':<15}")
    print(f"{'-'*90}")
    
    for row in rows:
        emp_id, name, days, total_hours, avg_hours = row
        print(f"{emp_id:<10} {name:<25} {days:<10} {total_hours:<15.2f} {avg_hours:<15.2f}")
    
    print(f"{'='*90}\n")
    return rows

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nAttendance Viewer Usage:")
        print("  python view_attendance.py today                    - View today's attendance")
        print("  python view_attendance.py week                     - View this week's attendance")
        print("  python view_attendance.py month                    - View this month's attendance")
        print("  python view_attendance.py range YYYY-MM-DD YYYY-MM-DD - View date range")
        print("  python view_attendance.py employee <ID>            - View employee attendance")
        print("  python view_attendance.py export YYYY-MM-DD YYYY-MM-DD - Export to CSV")
        print("  python view_attendance.py summary YYYY-MM-DD YYYY-MM-DD - View summary report")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "today":
        view_today_attendance()
    
    elif command == "week":
        today = datetime.now()
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        view_date_range_attendance(start, end)
    
    elif command == "month":
        today = datetime.now()
        start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        view_date_range_attendance(start, end)
    
    elif command == "range" and len(sys.argv) == 4:
        view_date_range_attendance(sys.argv[2], sys.argv[3])
    
    elif command == "employee" and len(sys.argv) == 3:
        view_employee_attendance(sys.argv[2])
    
    elif command == "export" and len(sys.argv) == 4:
        export_to_csv(sys.argv[2], sys.argv[3])
    
    elif command == "summary" and len(sys.argv) == 4:
        get_attendance_summary(sys.argv[2], sys.argv[3])
    
    else:
        print("Invalid command or missing arguments. Run without arguments to see usage.")
