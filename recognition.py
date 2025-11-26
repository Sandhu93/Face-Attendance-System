import tkinter as tk
from tkinter import messagebox
import cv2
import time
import platform
import os
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
import pickle
import json
import sqlite3
from tinydb import TinyDB, where
import face_recognition
from project.utils import Conf

# Initialize the configuration and recognizer
conf = Conf("config/config.json")
recognizer = pickle.loads(open(conf["recognizer_path"], "rb").read())
le = pickle.loads(open(conf["le_path"], "rb").read())

# Initialize the TinyDB for attendance and students
db = TinyDB(conf["db_path"])
studentTable = db.table("student")
json_file_path_enroll = 'database/enroll.json'

def open_camera():
    """Open camera with best available method for the platform"""
    if platform.system() == 'Windows':
        return cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # For Raspberry Pi 5 and other Linux systems
    # Try V4L2 backend with multiple indices
    for idx in [0, 1, 2]:
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                cap.release()
                return cv2.VideoCapture(idx, cv2.CAP_V4L2)
            cap.release()
    
    # Fallback to default backend
    for idx in [0, 1, 2]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                return cap
            cap.release()
    
    return cv2.VideoCapture(0)

# Initialize SQLite database for attendance
attendance_db_path = 'database/attendance.db'
conn = sqlite3.connect(attendance_db_path, check_same_thread=False)
cursor = conn.cursor()

# Create attendance table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
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
''')
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_employee_date 
    ON attendance(employee_id, date)
''')
conn.commit()

# Initialize the video capture (cross-platform compatible)
print("[INFO] Opening camera...")
vs = open_camera()

# Verify camera opened successfully
if not vs.isOpened():
    print("[ERROR] Failed to open camera!")
    print("Please check:")
    print("  1. Camera is connected properly")
    print("  2. Camera permissions are granted")
    print("  3. No other application is using the camera")
    print("  4. Run diagnostic: python3 test_camera.py")
    print("  5. On Raspberry Pi 5: Camera might be at different index")
    exit(1)

print("[SUCCESS] Camera opened successfully!")

vs.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
vs.set(cv2.CAP_PROP_FPS, 30)

# Cache for student names to avoid repeated database queries
student_name_cache = {}
for record in studentTable.all():
    for student_id, details in record.items():
        student_name_cache[student_id] = details[0]

# Cache for today's attendance to reduce database queries
attendance_cache = {}
current_cache_date = datetime.now().strftime("%Y-%m-%d")

# Cooldown tracking: employee_id -> last_checkout_timestamp
checkout_cooldown = {}  # 10-minute cooldown after checkout
COOLDOWN_MINUTES = 10

def load_today_attendance():
    """Load today's attendance into cache on startup"""
    global attendance_cache, current_cache_date
    today = datetime.now().strftime("%Y-%m-%d")
    current_cache_date = today
    
    cursor.execute('''
        SELECT employee_id, employee_name, check_in, check_out, working_hours
        FROM attendance
        WHERE date = ?
    ''', (today,))
    
    rows = cursor.fetchall()
    attendance_cache = {}
    for row in rows:
        emp_id, emp_name, check_in, check_out, working_hours = row
        attendance_cache[emp_id] = {
            'name': emp_name,
            'check_in': check_in,
            'check_out': check_out,
            'working_hours': working_hours
        }

# Load today's attendance on startup
load_today_attendance()

# Frame processing counter - process every Nth frame for face detection
frame_counter = 0
process_every_n_frames = 3  # Process every 3rd frame for better FPS
# Function to store attendance with IN/OUT tracking (optimized with SQLite and caching)
def store_attendance(name, id):
    global attendance_cache, current_cache_date, checkout_cooldown
    
    if not name or name.lower() == "unknown":
        print("Face not recognized, attendance not stored.")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_timestamp = datetime.now()
    
    # Check if employee is in cooldown period (10 minutes after last checkout)
    if id in checkout_cooldown:
        time_since_checkout = (current_timestamp - checkout_cooldown[id]).total_seconds() / 60
        if time_since_checkout < COOLDOWN_MINUTES:
            remaining = COOLDOWN_MINUTES - int(time_since_checkout)
            print(f"Employee {name} (ID: {id}) is in cooldown. {remaining} minutes remaining.")
            return None  # Ignore detection during cooldown
    
    # Check if date changed (new day) - reload cache
    if current_date != current_cache_date:
        load_today_attendance()

    # Check if employee has any record today in cache
    if id in attendance_cache:
        employee_record = attendance_cache[id]
        
        # Same day - update check_out time (allows multiple updates)
        attendance_cache[id]['check_out'] = current_time
        print(f"Check-OUT updated for {name} (ID: {id}) at {current_time}")
        
        # Calculate working hours
        check_in_dt = datetime.strptime(employee_record['check_in'], "%Y-%m-%d %H:%M:%S")
        check_out_dt = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        duration = check_out_dt - check_in_dt
        hours = duration.total_seconds() / 3600
        attendance_cache[id]['working_hours'] = round(hours, 2)
        
        # Update database using UPSERT
        cursor.execute('''
            INSERT INTO attendance (employee_id, employee_name, date, check_in, check_out, working_hours, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(employee_id, date) 
            DO UPDATE SET 
                check_out = excluded.check_out,
                working_hours = excluded.working_hours,
                updated_at = datetime('now')
        ''', (id, name, current_date, employee_record['check_in'], current_time, round(hours, 2)))
        conn.commit()
        
        # Set cooldown timer (10 minutes from now)
        checkout_cooldown[id] = current_timestamp
        print(f"Cooldown activated for {name} (ID: {id}) - 10 minutes")
        
        return f"Check-OUT Updated: {name} | Total hours: {round(hours, 2)}h", "checkout", id, current_time, round(hours, 2)
    else:
        # First check-in of the day
        attendance_cache[id] = {
            "name": name,
            "check_in": current_time,
            "check_out": None,
            "working_hours": 0
        }
        
        # Clear cooldown on new check-in (new day)
        if id in checkout_cooldown:
            del checkout_cooldown[id]
        
        print(f"Check-IN recorded for {name} (ID: {id}) at {current_time}")
        
        # Insert into database
        cursor.execute('''
            INSERT INTO attendance (employee_id, employee_name, date, check_in, check_out, working_hours)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, date) 
            DO UPDATE SET 
                check_in = excluded.check_in,
                updated_at = datetime('now')
        ''', (id, name, current_date, current_time, None, 0))
        conn.commit()
        
        return f"Check-IN: {name} marked present at {current_time.split(' ')[1]}", "checkin", id, current_time, 0

# Tkinter window setup
root = tk.Tk()
root.title("Employee Attendance Management System - Press 'S' to Start, 'Q' to Quit, 'F' for Fullscreen")

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate video display size (maintain aspect ratio)
video_width = min(1280, int(screen_width * 0.9))
video_height = int(video_width * 3 / 4)  # 4:3 aspect ratio

# Set window size
window_height = video_height + 150  # Extra space for status labels
root.geometry(f"{video_width}x{window_height}+{(screen_width-video_width)//2}+20")
root.configure(bg="#1a1a1a")

# Fullscreen toggle variable
is_fullscreen = False

# Label to show keyboard shortcuts
shortcut_label = tk.Label(root, 
                          text="⌨️  Keyboard: [S] Start | [Q] Quit | [F] Fullscreen | [R] Reset", 
                          font=("Arial", 12, "bold"), 
                          fg="#00ff00",
                          bg="#1a1a1a")
shortcut_label.pack(pady=5)

# Label to show attendance status
attendance_label = tk.Label(root, 
                           text="Status: Press 'S' to START recognition", 
                           font=("Arial", 16, "bold"), 
                           fg="#ffcc00",
                           bg="#1a1a1a")
attendance_label.pack(pady=5)

# Info label for instructions
info_label = tk.Label(root, 
                     text="First detection = CHECK-IN | Every subsequent detection = CHECK-OUT (updates)", 
                     font=("Arial", 11), 
                     fg="#888888",
                     bg="#1a1a1a")
info_label.pack(pady=3)

# Canvas to display video feed (larger size)
canvas = tk.Canvas(root, width=video_width-40, height=video_height-40, bg="#000000", highlightthickness=0)
canvas.pack(pady=10)

# Notification panel for check-in/check-out (initially hidden)
notification_frame = tk.Frame(root, bg="#ffffff", relief="raised", borderwidth=3)
notification_label = tk.Label(notification_frame, text="", font=("Arial", 20, "bold"), bg="#ffffff", fg="#000000")
notification_label.pack(pady=10)

notification_details = tk.Label(notification_frame, text="", font=("Arial", 14), bg="#ffffff", fg="#333333")
notification_details.pack(pady=5)

notification_photo_label = tk.Label(notification_frame, bg="#ffffff")
notification_photo_label.pack(pady=10)

# Function to show notification
def show_notification(name, emp_id, action_type, time_str, hours=0):
    """Show check-in/check-out notification for 3 seconds"""
    # Position notification in center of canvas
    x = (video_width - 400) // 2
    y = (video_height - 200) // 2
    
    # Set colors based on action
    if action_type == "checkin":
        bg_color = "#00ff00"  # Green
        fg_color = "#000000"
        title_text = f"✓ CHECK-IN SUCCESSFUL"
        detail_text = f"{name} (ID: {emp_id})\n{time_str.split(' ')[1]}"
    else:  # checkout
        bg_color = "#ff3333"  # Red
        fg_color = "#ffffff"
        title_text = f"✓ CHECK-OUT SUCCESSFUL"
        detail_text = f"{name} (ID: {emp_id})\n{time_str.split(' ')[1]}\nWorking Hours: {hours}h"
    
    # Update notification appearance
    notification_frame.config(bg=bg_color, highlightbackground=bg_color, highlightthickness=5)
    notification_label.config(text=title_text, bg=bg_color, fg=fg_color)
    notification_details.config(text=detail_text, bg=bg_color, fg=fg_color)
    
    # Load employee photo if exists
    photo_path = os.path.join(conf["dataset_path"], conf["class"], emp_id)
    if os.path.exists(photo_path):
        images = [f for f in os.listdir(photo_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            img_path = os.path.join(photo_path, images[0])
            try:
                photo = Image.open(img_path)
                photo = photo.resize((100, 100), Image.LANCZOS)
                photo_tk = ImageTk.PhotoImage(photo)
                notification_photo_label.config(image=photo_tk, bg=bg_color)
                notification_photo_label.image = photo_tk
            except:
                notification_photo_label.config(image="", bg=bg_color)
        else:
            notification_photo_label.config(image="", bg=bg_color)
    else:
        notification_photo_label.config(image="", bg=bg_color)
    
    # Show notification
    notification_frame.place(x=x, y=y, width=400, height=250)
    
    # Hide after 3 seconds
    root.after(3000, lambda: notification_frame.place_forget())

# Initialize variables
prevPerson = None
curPerson = None
consecCount = 0
video_running = False  # Flag to check if the video feed is running
last_boxes = []  # Store last detected boxes
last_person_name = ""  # Store last recognized person name

# Function to update the GUI with the video feed and attendance status
def update_frame():
    global prevPerson, curPerson, consecCount, video_running, frame_counter, last_boxes, last_person_name

    if not video_running:
        return  # Stop updating frames if video is not running

    ret, frame = vs.read()
    if not ret:
        print("Failed to grab frame")
        return

    frame_counter += 1
    
    # Resize frame for faster processing (scale down by 0.5)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    
    # Only process face detection/recognition every N frames
    if frame_counter % process_every_n_frames == 0:
        # Convert to RGB for face_recognition (no grayscale needed)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces on smaller frame
        boxes = face_recognition.face_locations(rgb_small, model=conf["detection_method"])
        
        # Scale boxes back to original frame size
        last_boxes = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in boxes]

        if len(boxes) > 0:
            # Get encodings from smaller frame
            encodings = face_recognition.face_encodings(rgb_small, boxes)
            preds = recognizer.predict_proba(encodings)[0]
            j = np.argmax(preds)
            curPerson = le.classes_[j]

            if prevPerson == curPerson:
                consecCount += 1
            else:
                consecCount = 0

            prevPerson = curPerson

            # Use cached student names instead of database query
            name = student_name_cache.get(curPerson, "Unknown")
            last_person_name = name
            
            # Only store attendance every 10 consecutive frames (reduce writes)
            if consecCount == 10:
                result = store_attendance(name, curPerson)
                if result:
                    attn_info, action_type, emp_id, time_str, hours = result
                    attendance_label.config(text=f"{attn_info}")
                    # Show notification
                    show_notification(name, emp_id, action_type, time_str, hours)
                # Reset counter to allow next check-out after some time
                consecCount = 0
        else:
            last_person_name = ""
    
    # Draw rectangles on every frame using last detected boxes
    for (top, right, bottom, left) in last_boxes:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        if last_person_name:
            cv2.putText(frame, last_person_name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Add status text
    cv2.putText(frame, "Status: Detecting", (10, 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Convert the frame to an ImageTk object and update the canvas
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Resize frame to fit canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if canvas_width > 1 and canvas_height > 1:
        img = Image.fromarray(frame_rgb)
        img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk

    # Repeat the frame update every 10 milliseconds
    root.after(10, update_frame)

# Start video function
def start_video():
    global video_running
    if not video_running:
        video_running = True
        attendance_label.config(text="Status: RUNNING - Show face to CHECK-IN/CHECK-OUT", fg="#00ff00")
        update_frame()

# Stop video function
def stop_video():
    global video_running
    video_running = False
    attendance_label.config(text="Status: STOPPED - Press 'S' to restart", fg="#ff6600")

# Reset function
def reset_status():
    global consecCount, prevPerson, curPerson
    consecCount = 0
    prevPerson = None
    curPerson = None
    attendance_label.config(text="Status: RESET - Recognition cleared", fg="#ffcc00")

# Toggle fullscreen
def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    if is_fullscreen:
        shortcut_label.config(text="⌨️  FULLSCREEN MODE | Press 'F' or ESC to exit fullscreen")
    else:
        shortcut_label.config(text="⌨️  Keyboard: [S] Start | [Q] Quit | [F] Fullscreen | [R] Reset")

# Exit program function
def exit_program(event=None):
    global video_running
    video_running = False
    vs.release()
    cv2.destroyAllWindows()
    conn.close()
    root.quit()

# Keyboard event handler
def on_key_press(event):
    key = event.char.lower()
    
    if key == 's':
        start_video()
    elif key == 'q':
        exit_program()
    elif key == 'f':
        toggle_fullscreen()
    elif key == 'r':
        reset_status()
    elif key == 'p':  # Pause
        stop_video()

# Bind keyboard events
root.bind('<KeyPress>', on_key_press)
root.bind('<Escape>', toggle_fullscreen)  # ESC to exit fullscreen
root.bind('<F11>', toggle_fullscreen)     # F11 for fullscreen (standard)

# Auto-start video on launch
root.after(1000, start_video)  # Start after 1 second

# Start the Tkinter main loop
root.mainloop()

# Clean up after exiting the Tkinter window
vs.release()
cv2.destroyAllWindows()
conn.close()
