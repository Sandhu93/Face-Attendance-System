# Employee Attendance Management System with SQLite

## Overview
This system now uses **SQLite database** for storing attendance records instead of JSON files. This provides:

✅ **Persistent Data** - Never lose historical attendance data  
✅ **Fast Performance** - Indexed queries for instant lookups  
✅ **Scalable** - Can handle thousands of records without slowing down  
✅ **Queryable** - Easy to generate reports and analytics  
✅ **No FPS Impact** - Smart caching keeps recognition speed at 15-25 FPS  

---

## Database Schema

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    date TEXT NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT,
    working_hours REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, date)
)
```

**Features:**
- One record per employee per day
- Automatic timestamp tracking
- Indexed for fast queries
- UPSERT operations for updates

---

## Performance Optimizations

### 1. **In-Memory Caching**
- Loads today's attendance into RAM on startup
- All lookups happen in memory (microseconds)
- Database writes only when attendance changes

### 2. **Indexed Queries**
- `employee_id + date` composite index
- O(log n) lookup time instead of O(n)

### 3. **Connection Pooling**
- Single persistent connection (no reconnection overhead)
- `check_same_thread=False` for thread safety

### 4. **Smart Cache Refresh**
- Auto-detects date change at midnight
- Reloads cache for new day
- No manual intervention needed

---

## How to Use

### Run Recognition System
```powershell
python recognition.py
```

---

## 📊 Attendance Viewing & Reports

### Basic Viewing Commands

**View Today's Attendance**
```powershell
python view_attendance.py today
```

**View This Week's Attendance**
```powershell
python view_attendance.py week
```

**View This Month's Attendance**
```powershell
python view_attendance.py month
```

**View Custom Date Range**
```powershell
python view_attendance.py range 2025-11-01 2025-11-30
```

**View Employee History**
```powershell
python view_attendance.py employee 601
```

**View Summary Report**
```powershell
python view_attendance.py summary 2025-11-01 2025-11-30
```

---

### 🆕 Advanced Monitoring Commands

**⚠️ View Incomplete Checkouts** (Employees who forgot to check out)
```powershell
# View all incomplete checkouts
python view_attendance.py incomplete

# View incomplete checkouts for specific date
python view_attendance.py incomplete 2025-11-26
```

**Output Example:**
```
================================================================================
⚠️  INCOMPLETE CHECKOUTS - Employees Who Forgot to Check Out
================================================================================
Date         ID         Name                      Check-IN        Status         
--------------------------------------------------------------------------------
2025-11-26   601        SandeepBKadam            09:00:00        Missing OUT    
2025-11-25   603        JohnDoe                  08:45:00        Missing OUT    
--------------------------------------------------------------------------------
Total: 2 incomplete checkout(s)
```

---

**❌ View Absent Employees** (Enrolled but didn't check in)
```powershell
# View today's absent employees
python view_attendance.py absent

# View absent for specific date
python view_attendance.py absent 2025-11-26
```

**Output Example:**
```
======================================================================
❌ ABSENT EMPLOYEES - 2025-11-26
======================================================================
ID         Name                           Status              
----------------------------------------------------------------------
602        AliceSmith                     ABSENT              
604        BobJohnson                     ABSENT              
----------------------------------------------------------------------
Total Absent: 2 employee(s)
Total Present: 3 employee(s)
Total Enrolled: 5 employee(s)
```

---

**📋 Comprehensive Daily Report** (All-in-one view)
```powershell
# Today's full report
python view_attendance.py report

# Specific date report
python view_attendance.py report 2025-11-26
```

**Output Example:**
```
##########################################################################################
                              DAILY ATTENDANCE REPORT                                    
                                   2025-11-26                                            
##########################################################################################

==========================================================================================
✓ PRESENT EMPLOYEES (3)
==========================================================================================
ID         Name                      Check-IN     Check-OUT    Hours      Status         
------------------------------------------------------------------------------------------
601        SandeepBKadam            09:00:00     17:30:00     8.50       Complete ✓     
603        JohnDoe                  08:45:00     18:00:00     9.25       Complete ✓     
605        MaryJane                 09:15:00     N/A          0.00       ⚠️ Missing OUT  
==========================================================================================

==========================================================================================
⚠️  INCOMPLETE CHECKOUTS (1)
==========================================================================================
ID         Name                      Check-IN        Action Required               
------------------------------------------------------------------------------------------
605        MaryJane                 09:15:00        Remind to check out           
==========================================================================================

==========================================================================================
❌ ABSENT EMPLOYEES (2)
==========================================================================================
ID         Name                           Status                        
------------------------------------------------------------------------------------------
602        AliceSmith                     ABSENT - No check-in          
604        BobJohnson                     ABSENT - No check-in          
==========================================================================================

==========================================================================================
📊 SUMMARY STATISTICS
==========================================================================================
Total Enrolled Employees:     5
Present:                      3 (60.0%)
Absent:                       2
Complete Checkouts:           2
Incomplete Checkouts:         1
==========================================================================================
```

---

### 📤 Export Commands

**Export to CSV**
```powershell
python view_attendance.py export 2025-11-01 2025-11-30
```
Creates `attendance_report.csv` with all attendance records for the date range.

---

## 🔄 Continuous Multi-Day Operation

### How the System Handles Days Automatically

The system is designed for **24/7/365 continuous operation** without manual intervention.

#### Automatic Date Detection

Every face recognition triggers a date check:
```python
if current_date != current_cache_date:
    load_today_attendance()  # Automatically refresh for new day
```

#### Multi-Day Scenario Example

**Day 1 - November 26, 2025:**
- 9:00 AM: Employee 601 arrives → **CHECK-IN recorded**
- 5:30 PM: Employee 601 leaves → **CHECK-OUT updated** (8.5 hours)
- Database: `{date: "2025-11-26", check_in: "09:00:00", check_out: "17:30:00", hours: 8.5}`

**Midnight (12:00:01 AM) - Date Changes:**
- System continues running (no restart needed)
- Cache still contains yesterday's data

**Day 2 - November 27, 2025:**
- 9:00 AM: Employee 601 arrives → **Date mismatch detected!**
- System automatically:
  1. Calls `load_today_attendance()`
  2. Queries database for today's records (empty)
  3. Clears cache
  4. Updates `current_cache_date = "2025-11-27"`
- Employee 601 not in cache → **NEW CHECK-IN recorded** (fresh day)
- 6:00 PM: Employee 601 leaves → **CHECK-OUT updated** (9.0 hours)
- Database: `{date: "2025-11-27", check_in: "09:00:00", check_out: "18:00:00", hours: 9.0}`

**Result After Multiple Days:**
```sql
SELECT * FROM attendance WHERE employee_id = '601' ORDER BY date;
```
| date | check_in | check_out | working_hours |
|------|----------|-----------|---------------|
| 2025-11-26 | 09:00:00 | 17:30:00 | 8.5 |
| 2025-11-27 | 09:00:00 | 18:00:00 | 9.0 |
| 2025-11-28 | 08:45:00 | 17:15:00 | 8.5 |

Each day gets its own separate record automatically!

---

### Handling Forgotten Checkouts

**Scenario:** Employee checks in but forgets to check out

**Day 1 (Nov 26):**
- 9:00 AM: CHECK-IN recorded
- Leaves without checking out
- Database: `{date: "2025-11-26", check_in: "09:00:00", check_out: NULL, hours: 0}`

**Day 2 (Nov 27):**
- 9:00 AM: Shows face again
- System detects new date → Cache refreshed
- **Result: NEW CHECK-IN (not checkout!)** ✓ Correct behavior
- Database now has TWO records:
  - `2025-11-26` → Incomplete (NULL checkout, 0 hours)
  - `2025-11-27` → New check-in

**Detection & Correction:**
```powershell
# Find all incomplete checkouts
python view_attendance.py incomplete

# View comprehensive daily report
python view_attendance.py report
```

The system preserves incomplete records, allowing you to:
- Identify who forgot to check out
- Manually correct if needed
- Generate reports on attendance patterns

---

## 🎯 Key Features

### 1. **Complete Attendance Visibility**
- ✅ **Present Employees** - Who checked in today
- ⚠️ **Incomplete Checkouts** - Who forgot to check out
- ❌ **Absent Employees** - Who didn't show up
- 📊 **Attendance Rate** - Daily percentage calculation

### 2. **Automatic Day Transitions**
- No manual resets required
- Works seamlessly across midnight
- Each day is a separate database record
- Historical data preserved forever

### 3. **Performance Optimized**
- In-memory caching for today's data
- Database writes only on changes
- Indexed queries for fast lookups
- Maintains 15-25 FPS recognition speed

### 4. **Flexible Checkout Updates**
- First detection = CHECK-IN
- Second, third, fourth... = CHECK-OUT updates
- Final checkout time = last detection of the day
- Accurate working hours calculation

---

## 📈 Reporting & Analytics

### Quick Daily Checks

**Morning:** Check who's present/absent
```powershell
python view_attendance.py report
```

**Throughout Day:** Monitor incomplete checkouts
```powershell
python view_attendance.py incomplete
```

**End of Day:** Export for HR/payroll
```powershell
python view_attendance.py export 2025-11-26 2025-11-26
```

### Weekly/Monthly Analysis
```powershell
# Last 7 days summary
python view_attendance.py summary 2025-11-20 2025-11-26

# Export month for payroll
python view_attendance.py export 2025-11-01 2025-11-30
```

---

## ⚙️ Administrative Tasks

### Find Problem Cases

**Who consistently forgets to check out?**
```powershell
python view_attendance.py incomplete
```

**Who has poor attendance?**
```powershell
python view_attendance.py employee 601
```

**Today's attendance rate?**
```powershell
python view_attendance.py report
```

### Manual Corrections

**Update forgotten checkout:**
```python
import sqlite3
conn = sqlite3.connect('database/attendance.db')
cursor = conn.cursor()

cursor.execute('''
    UPDATE attendance
    SET check_out = ?, working_hours = ?
    WHERE employee_id = ? AND date = ?
''', ("2025-11-26 18:00:00", 9.0, "601", "2025-11-26"))

conn.commit()
conn.close()
```

**Delete incorrect record:**
```python
cursor.execute('''
    DELETE FROM attendance
    WHERE employee_id = ? AND date = ?
''', ("601", "2025-11-26"))
```

---

## Migration from JSON

If you have existing `attendance.json`, the system will:
1. Use SQLite database going forward
2. Old JSON file is no longer updated
3. Historical data is preserved in `attendance.json` (can manually import if needed)

### Manual Import (Optional)
To import old JSON data into SQLite:
```python
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('database/attendance.db')
cursor = conn.cursor()

# Read old JSON
with open('attendance.json', 'r') as f:
    data = json.load(f)

# Import each record
for emp_id, record in data.get('attendance', {}).items():
    # Parse the old format
    if 'check_in' in record:
        date = record['check_in'].split(' ')[0]
        cursor.execute('''
            INSERT OR IGNORE INTO attendance 
            (employee_id, employee_name, date, check_in, check_out, working_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (emp_id, record['name'], date, record['check_in'], 
              record.get('check_out'), record.get('working_hours', 0)))

conn.commit()
conn.close()
print("Migration complete!")
```

---

## Database Location

**File:** `database/attendance.db`

You can:
- ✅ Back it up regularly
- ✅ Copy it to another machine
- ✅ Open with any SQLite viewer (DB Browser for SQLite)
- ✅ Query directly with SQL tools

---

## Advantages Over JSON

| Feature | JSON | SQLite |
|---------|------|--------|
| Speed | Slow for large data | Fast (indexed) |
| Scalability | Poor (reads entire file) | Excellent |
| Data Integrity | No constraints | UNIQUE constraints |
| Concurrent Access | File locking issues | Built-in support |
| Query Support | No | Full SQL |
| Historical Data | Lost on reset | Preserved forever |
| Backup | Manual copy | Automated tools |

---

## Sample Queries

### Get Total Working Hours Per Employee
```sql
SELECT 
    employee_name,
    SUM(working_hours) as total_hours
FROM attendance
WHERE date BETWEEN '2025-11-01' AND '2025-11-30'
GROUP BY employee_id, employee_name;
```

### Find Late Arrivals (after 9:30 AM)
```sql
SELECT 
    date,
    employee_name,
    check_in
FROM attendance
WHERE time(check_in) > '09:30:00'
ORDER BY date DESC;
```

### Average Working Hours Per Day
```sql
SELECT 
    employee_name,
    AVG(working_hours) as avg_hours
FROM attendance
GROUP BY employee_id, employee_name;
```

---

## FPS Performance

**Before SQLite:** 15-25 FPS  
**After SQLite:** 15-25 FPS (no change!)  

The caching strategy ensures zero impact on recognition performance.

---

## Troubleshooting

### Database Locked Error
- Close other applications accessing the database
- Restart the recognition system

### Cache Not Updating
- System auto-detects date changes
- If issue persists, restart the application

### Viewing Database
Download **DB Browser for SQLite**:
- https://sqlitebrowser.org/
- Open `database/attendance.db`
- Browse/edit/export data visually

---

## System Requirements

- Python 3.8+
- SQLite3 (included with Python)
- All existing dependencies (no new installations needed)

---

## Backup Strategy

### Automatic Backup Script (Optional)
```powershell
# backup_attendance.ps1
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
Copy-Item "database/attendance.db" "backups/attendance_$date.db"
```

Run daily via Windows Task Scheduler for automatic backups.
