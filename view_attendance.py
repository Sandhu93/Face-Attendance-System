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

def view_incomplete_checkouts(date=None):
    """View employees who forgot to checkout"""
    conn = connect_db()
    cursor = conn.cursor()
    
    if date:
        cursor.execute('''
            SELECT date, employee_id, employee_name, check_in
            FROM attendance
            WHERE check_out IS NULL AND date = ?
            ORDER BY date DESC, check_in DESC
        ''', (date,))
    else:
        cursor.execute('''
            SELECT date, employee_id, employee_name, check_in
            FROM attendance
            WHERE check_out IS NULL
            ORDER BY date DESC, check_in DESC
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*80}")
    print("⚠️  INCOMPLETE CHECKOUTS - Employees Who Forgot to Check Out")
    print(f"{'='*80}")
    print(f"{'Date':<12} {'ID':<10} {'Name':<25} {'Check-IN':<15} {'Status':<15}")
    print(f"{'-'*80}")
    
    if rows:
        for row in rows:
            date, emp_id, name, check_in = row
            check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
            print(f"{date:<12} {emp_id:<10} {name:<25} {check_in_time:<15} {'Missing OUT':<15}")
        print(f"{'-'*80}")
        print(f"Total: {len(rows)} incomplete checkout(s)")
    else:
        print("No incomplete checkouts found. All employees checked out properly! ✓")
    
    print(f"{'='*80}\n")
    return rows

def get_all_enrolled_employees():
    """Get all enrolled employees from the enrollment database"""
    try:
        from tinydb import TinyDB
        db = TinyDB('database/enroll.json')
        student_table = db.table("student")
        
        employees = {}
        for record in student_table.all():
            for emp_id, details in record.items():
                if emp_id != 'unknown':  # Skip unknown entries
                    employees[emp_id] = details[0] if isinstance(details, list) else details
        
        db.close()
        return employees
    except Exception as e:
        print(f"Warning: Could not load enrolled employees: {e}")
        return {}

def view_absent_employees(date=None):
    """View employees who are absent (enrolled but no attendance record)"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Get all enrolled employees
    all_employees = get_all_enrolled_employees()
    
    if not all_employees:
        print("\n⚠️  No enrolled employees found in database/enroll.json")
        return []
    
    # Get employees who attended on the given date
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT employee_id
        FROM attendance
        WHERE date = ?
    ''', (date,))
    
    present_employees = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Find absent employees
    absent_employees = []
    for emp_id, emp_name in all_employees.items():
        if emp_id not in present_employees:
            absent_employees.append((emp_id, emp_name))
    
    # Display results
    print(f"\n{'='*70}")
    print(f"❌ ABSENT EMPLOYEES - {date}")
    print(f"{'='*70}")
    print(f"{'ID':<10} {'Name':<30} {'Status':<20}")
    print(f"{'-'*70}")
    
    if absent_employees:
        for emp_id, emp_name in sorted(absent_employees):
            print(f"{emp_id:<10} {emp_name:<30} {'ABSENT':<20}")
        print(f"{'-'*70}")
        print(f"Total Absent: {len(absent_employees)} employee(s)")
        print(f"Total Present: {len(present_employees)} employee(s)")
        print(f"Total Enrolled: {len(all_employees)} employee(s)")
    else:
        print("All enrolled employees are present today! ✓")
    
    print(f"{'='*70}\n")
    return absent_employees

def view_daily_report(date=None):
    """Comprehensive daily report with attendance, incomplete checkouts, and absences"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n{'#'*90}")
    print(f"{'DAILY ATTENDANCE REPORT':^90}")
    print(f"{date:^90}")
    print(f"{'#'*90}\n")
    
    # 1. Present Employees
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT employee_id, employee_name, check_in, check_out, working_hours
        FROM attendance
        WHERE date = ?
        ORDER BY check_in
    ''', (date,))
    
    present_rows = cursor.fetchall()
    
    print(f"{'='*90}")
    print(f"✓ PRESENT EMPLOYEES ({len(present_rows)})")
    print(f"{'='*90}")
    print(f"{'ID':<10} {'Name':<25} {'Check-IN':<12} {'Check-OUT':<12} {'Hours':<10} {'Status':<15}")
    print(f"{'-'*90}")
    
    complete_checkouts = 0
    incomplete_checkouts = 0
    
    for row in present_rows:
        emp_id, name, check_in, check_out, hours = row
        check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
        check_out_time = check_out.split(' ')[1] if check_out else 'N/A'
        status = 'Complete ✓' if check_out else '⚠️ Missing OUT'
        
        if check_out:
            complete_checkouts += 1
        else:
            incomplete_checkouts += 1
            
        print(f"{emp_id:<10} {name:<25} {check_in_time:<12} {check_out_time:<12} {hours:<10.2f} {status:<15}")
    
    print(f"{'='*90}\n")
    
    # 2. Incomplete Checkouts
    if incomplete_checkouts > 0:
        print(f"{'='*90}")
        print(f"⚠️  INCOMPLETE CHECKOUTS ({incomplete_checkouts})")
        print(f"{'='*90}")
        
        cursor.execute('''
            SELECT employee_id, employee_name, check_in
            FROM attendance
            WHERE date = ? AND check_out IS NULL
            ORDER BY check_in
        ''', (date,))
        
        incomplete_rows = cursor.fetchall()
        print(f"{'ID':<10} {'Name':<25} {'Check-IN':<15} {'Action Required':<30}")
        print(f"{'-'*90}")
        
        for row in incomplete_rows:
            emp_id, name, check_in = row
            check_in_time = check_in.split(' ')[1] if check_in else 'N/A'
            print(f"{emp_id:<10} {name:<25} {check_in_time:<15} {'Remind to check out':<30}")
        
        print(f"{'='*90}\n")
    
    conn.close()
    
    # 3. Absent Employees
    all_employees = get_all_enrolled_employees()
    present_ids = {row[0] for row in present_rows}
    absent_employees = [(emp_id, emp_name) for emp_id, emp_name in all_employees.items() 
                       if emp_id not in present_ids]
    
    if absent_employees:
        print(f"{'='*90}")
        print(f"❌ ABSENT EMPLOYEES ({len(absent_employees)})")
        print(f"{'='*90}")
        print(f"{'ID':<10} {'Name':<30} {'Status':<30}")
        print(f"{'-'*90}")
        
        for emp_id, emp_name in sorted(absent_employees):
            print(f"{emp_id:<10} {emp_name:<30} {'ABSENT - No check-in':<30}")
        
        print(f"{'='*90}\n")
    
    # Summary Statistics
    total_enrolled = len(all_employees)
    total_present = len(present_rows)
    total_absent = len(absent_employees)
    attendance_rate = (total_present / total_enrolled * 100) if total_enrolled > 0 else 0
    
    print(f"{'='*90}")
    print(f"📊 SUMMARY STATISTICS")
    print(f"{'='*90}")
    print(f"Total Enrolled Employees:     {total_enrolled}")
    print(f"Present:                      {total_present} ({attendance_rate:.1f}%)")
    print(f"Absent:                       {total_absent}")
    print(f"Complete Checkouts:           {complete_checkouts}")
    print(f"Incomplete Checkouts:         {incomplete_checkouts}")
    print(f"{'='*90}\n")
    
    return {
        'present': present_rows,
        'absent': absent_employees,
        'incomplete': incomplete_checkouts,
        'attendance_rate': attendance_rate
    }

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
        print("\n  NEW COMMANDS:")
        print("  python view_attendance.py incomplete [YYYY-MM-DD]  - View incomplete checkouts")
        print("  python view_attendance.py absent [YYYY-MM-DD]      - View absent employees")
        print("  python view_attendance.py report [YYYY-MM-DD]      - Comprehensive daily report")
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
    
    elif command == "incomplete":
        date = sys.argv[2] if len(sys.argv) == 3 else None
        view_incomplete_checkouts(date)
    
    elif command == "absent":
        date = sys.argv[2] if len(sys.argv) == 3 else datetime.now().strftime("%Y-%m-%d")
        view_absent_employees(date)
    
    elif command == "report":
        date = sys.argv[2] if len(sys.argv) == 3 else None
        view_daily_report(date)
    
    else:
        print("Invalid command or missing arguments. Run without arguments to see usage.")
