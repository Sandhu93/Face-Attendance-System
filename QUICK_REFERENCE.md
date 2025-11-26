# 📋 Quick Reference Card

## 🚀 First Time Setup on Raspberry Pi

```bash
# 1. Enable camera
sudo raspi-config
# Navigate: Interface Options → Camera → Enable → Reboot

# 2. Add user to video group
sudo usermod -a -G video $USER
sudo reboot

# 3. Navigate to project
cd ~/smartAttendance

# 4. Activate virtual environment
source .venv/bin/activate

# 5. Run diagnostic
chmod +x camera_diagnostic.sh
./camera_diagnostic.sh

# 6. Test camera
python3 test_camera.py

# 7. Start using system
chmod +x start_here.sh
./start_here.sh
```

---

## 🚀 Daily Usage

```bash
cd ~/smartAttendance
./start_here.sh
```

**Individual Commands:**
```bash
# Enroll new employee
python3 auto_enroll.py

# Start attendance recognition
python3 recognition.py

# View reports
python3 view_attendance.py report
python3 view_attendance.py incomplete
python3 view_attendance.py absent

# Manage employees (delete enrollments)
python3 manage_employees.py

# Test camera
python3 test_camera.py
```

Or create desktop shortcut:
```bash
ln -s ~/smartAttendance/start_here.sh ~/Desktop/Attendance
```

---

## 🔧 Quick Fixes

### Camera Not Working
```bash
# Run diagnostic
cd ~/smartAttendance
./camera_diagnostic.sh

# Quick test
python3 test_camera.py

# Enable Pi Camera
sudo raspi-config nonint do_camera 0
sudo reboot

# Load camera module
sudo modprobe bcm2835-v4l2

# Kill process using camera
sudo fuser -k /dev/video0
```

### Empty Directories in dataset/PROJECT
```bash
# Delete empty directories
cd ~/smartAttendance
find dataset/PROJECT -type d -empty -delete

# Test camera first
python3 test_camera.py

# Then re-enroll
./start_here.sh
# Choose: 1. Enroll New Employee
```

### Virtual Environment Not Active
```bash
cd ~/smartAttendance
source .venv/bin/activate
```

### Permission Denied on Scripts
```bash
chmod +x start_here.sh
chmod +x camera_diagnostic.sh
```

---

## 📸 Camera Commands

```bash
# Check camera detected
v4l2-ctl --list-devices

# Check Pi Camera status
vcgencmd get_camera

# List video devices
ls -l /dev/video*

# Test Pi Camera capture
libcamera-still -o test.jpg

# Test USB camera capture
fswebcam test.jpg

# Check camera module loaded
lsmod | grep -E "bcm2835|uvcvideo"

# Load Pi Camera module
sudo modprobe bcm2835-v4l2

# Scan for available cameras
python3 -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```

---

## 🗂️ File Locations

```
~/smartAttendance/
├── start_here.sh          # Main launcher
├── test_camera.py         # Camera test tool
├── camera_diagnostic.sh   # Diagnostic tool
├── auto_enroll.py         # Automated enrollment
├── enroll.py              # Manual enrollment
├── recognition.py         # Attendance system
├── view_attendance.py     # Reports
├── database/
│   ├── enroll.json       # Employee registry
│   └── attendance.db     # Attendance records
├── dataset/
│   └── PROJECT/
│       └── <employee_id>/ # Face images (20+ files)
└── output/
    ├── encodings.pickle   # Face encodings
    ├── recognizer.pickle  # Trained model
    └── le.pickle          # Label encoder
```

---

## 📊 Menu Options

```
./start_here.sh  (Linux/Pi)  or  START_HERE.bat  (Windows)

1. Enroll New Employee     → Use for new employees
2. Start Recognition       → Daily attendance system
3. View Today's Report     → See today's attendance
4. Incomplete Checkouts    → Find forgotten checkouts
5. View Absent Employees   → Who's not present
6. Manage Employees        → Delete enrollments & re-train
7. Test Camera             → Troubleshoot camera (Linux/Pi)
8. Exit                    → Close menu
```

---

## ✅ Verification Checklist

Before enrollment:
- [ ] Camera detected: `v4l2-ctl --list-devices`
- [ ] Camera enabled: `vcgencmd get_camera` shows `supported=1 detected=1`
- [ ] User in video group: `groups | grep video`
- [ ] Virtual env active: Check prompt shows `(.venv)`
- [ ] Camera test passes: `python3 test_camera.py` shows video
- [ ] Scripts executable: `ls -l start_here.sh` shows `-rwxr-xr-x`

After enrollment:
- [ ] Images captured: `ls dataset/PROJECT/<id>/` shows 20+ files
- [ ] Model trained: `output/recognizer.pickle` exists
- [ ] Employee in DB: Check `database/enroll.json`

---

## 🆘 Common Errors

| Error | Solution |
|-------|----------|
| `Failed to open camera` | Run `camera_diagnostic.sh` |
| `Permission denied` | `chmod +x script_name.sh` |
| `No module named cv2` | `pip3 install opencv-python` |
| `Camera is not available` | Enable in `raspi-config` |
| `VIDIOC_REQBUFS error` | Wrong camera index, try index 1 |
| Empty directories created | Camera failed, test first |
| `bash: command not found` | Check you're in correct directory |
| `source: not found` | Use `bash` not `sh` |

---

## 🎓 Tips & Tricks

### Auto-start on Boot
```bash
crontab -e
# Add: @reboot sleep 30 && cd ~/smartAttendance && ./start_here.sh
```

### Run in Background
```bash
nohup python3 recognition.py > attendance.log 2>&1 &
```

### View Logs
```bash
tail -f attendance.log
```

### Backup Database
```bash
cp database/attendance.db database/attendance_backup_$(date +%Y%m%d).db
```

### Reset System
```bash
# Clear all data (WARNING: Deletes everything!)
rm -rf dataset/PROJECT/*
rm -rf output/*
rm database/attendance.db
# Keep enroll.json to preserve employee registry
```

---

## 📞 Need Help?

1. **Camera issues:** See `CAMERA_TROUBLESHOOTING.md`
2. **Setup help:** See `RASPBERRY_PI_SETUP.md`
3. **Usage guide:** See `USER_GUIDE.md`
4. **Run diagnostic:** `./camera_diagnostic.sh`
5. **Test camera:** `python3 test_camera.py`

---

## 🔄 Update System

```bash
cd ~/smartAttendance
git pull  # If using git
source .venv/bin/activate
pip3 install -r requirements.txt --upgrade
```

---

## 💡 Pro Tips

1. **Use automated enrollment** - It's faster than 3-step manual process
2. **Test camera before enrolling** - Save time by catching issues early
3. **Run recognition full screen** - Press F11 for better visibility
4. **Check reports daily** - Monitor incomplete checkouts
5. **Backup database weekly** - Prevent data loss
6. **Clean lens regularly** - Better recognition accuracy
7. **Good lighting helps** - Face detection works best with even lighting
8. **Stand 2-3 feet away** - Optimal distance for face capture

---

## 🌟 Performance Tips for Raspberry Pi

### In config/config.json:
```json
{
  "detection_method": "hog",  // Faster than "cnn" on Pi
  "face_count": 20            // Reduce from 30 for faster enrollment
}
```

### In recognition.py:
- Lower resolution: 320x240 instead of 640x480
- Skip more frames: `process_every_n_frames = 5`
- Close other apps while running

---

**Quick Start:** `cd ~/smartAttendance && ./start_here.sh` 🚀
