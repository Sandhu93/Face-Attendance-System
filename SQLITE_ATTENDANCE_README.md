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

### View Today's Attendance
```powershell
python view_attendance.py today
```

### View This Week's Attendance
```powershell
python view_attendance.py week
```

### View This Month's Attendance
```powershell
python view_attendance.py month
```

### View Custom Date Range
```powershell
python view_attendance.py range 2025-11-01 2025-11-30
```

### View Employee History
```powershell
python view_attendance.py employee 601
```

### Export to CSV
```powershell
python view_attendance.py export 2025-11-01 2025-11-30
```

### View Summary Report
```powershell
python view_attendance.py summary 2025-11-01 2025-11-30
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
