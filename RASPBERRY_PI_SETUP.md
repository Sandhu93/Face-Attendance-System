# 🍓 Raspberry Pi Setup Guide

## For Raspberry Pi / Linux / Ubuntu

---

## 📋 Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (2GB+ RAM recommended)
- USB Webcam or Pi Camera Module
- 16GB+ microSD card
- Power supply (5V 3A recommended)

### Software Requirements
- Raspberry Pi OS (64-bit recommended)
- Python 3.8+

---

## 🚀 Installation Steps

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install System Dependencies
```bash
# Install required system packages
sudo apt install -y python3-pip python3-venv
sudo apt install -y cmake build-essential
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libjasper-dev
sudo apt install -y libqtgui4 libqt4-test
sudo apt install -y libhdf5-dev libhdf5-serial-dev
sudo apt install -y libharfbuzz0b libwebp6 libtiff5 libopenexr24

# For camera support
sudo apt install -y libcamera-dev libcamera-tools
sudo apt install -y v4l-utils
```

### 3. Enable Camera (if using Pi Camera)
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot after enabling
sudo reboot
```

### 4. Clone/Copy Project Files
```bash
cd ~
# Copy your project folder here
# Or use: git clone <repository-url>
cd Face-Attendance-System
```

### 5. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 6. Install Python Dependencies

**Important:** For Raspberry Pi, install dlib from source:
```bash
# Install dlib (this takes 30-60 minutes on Pi!)
pip3 install --upgrade pip
pip3 install wheel
pip3 install dlib --no-cache-dir

# Install other requirements
pip3 install opencv-python
pip3 install face-recognition
pip3 install imutils
pip3 install scikit-learn
pip3 install tinydb
pip3 install json-minify
pip3 install python-datauri
pip3 install numpy==1.26.3
```

**Alternative (Faster):** Use pre-compiled wheel if available
```bash
# Download pre-compiled dlib for ARM
wget https://github.com/ageitgey/face_recognition_models/releases/download/v1.0/dlib-19.24.0-cp39-cp39-linux_aarch64.whl
pip3 install dlib-19.24.0-cp39-cp39-linux_aarch64.whl
```

---

## 🎯 Running the System

### Make Scripts Executable
```bash
chmod +x start_here.sh
```

### Launch Menu
```bash
./start_here.sh
```

Or activate environment and run directly:
```bash
source .venv/bin/activate
python3 auto_enroll.py
```

---

## 📸 Camera Configuration

### ⚠️ Camera Issues? 
**See [CAMERA_TROUBLESHOOTING.md](CAMERA_TROUBLESHOOTING.md) for detailed solutions**

### Test Camera First

```bash
cd ~/smartAttendance
source .venv/bin/activate
python3 test_camera.py
```

This will verify your camera works before trying enrollment.

### Test Camera
```bash
# For USB camera
v4l2-ctl --list-devices
python3 -c "import cv2; print(cv2.VideoCapture(0).read()[0])"

# For Pi Camera
libcamera-hello --list-cameras
```

### Camera Already Fixed! ✅

The latest code automatically detects your platform (Windows/Linux) and uses the correct camera backend. No manual changes needed!

---

## ⚡ Performance Optimization for Raspberry Pi

### 1. Reduce Image Resolution
Edit `config/config.json`:
```json
{
    "detection_method": "hog",  // Use "hog" instead of "cnn" for Pi
    "face_count": 20            // Reduce from 30 to 20 for faster enrollment
}
```

### 2. Optimize Recognition Speed
Update `recognition.py`:
```python
# Increase frame skip for better performance
process_every_n_frames = 5  # Change from 3 to 5
```

### 3. Lower Camera Resolution
```python
vs.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Lower from 640
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Lower from 480
```

### 4. Use Swap Memory (if RAM < 4GB)
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🔧 Raspberry Pi Specific Issues

### Issue: "ImportError: libcblas.so.3"
```bash
sudo apt install -y libatlas-base-dev
```

### Issue: "Cannot open camera"
```bash
# Check camera permissions
sudo usermod -a -G video $USER
# Reboot
sudo reboot
```

### Issue: "Illegal instruction" (dlib)
```bash
# Rebuild dlib without NEON optimizations
pip3 uninstall dlib
pip3 install dlib --no-cache-dir --install-option=--no DLIB_USE_CUDA
```

### Issue: Low FPS (< 5 FPS)
- Use "hog" detection method (not "cnn")
- Reduce camera resolution to 320x240
- Increase `process_every_n_frames` to 5 or 7
- Close unnecessary processes

---

## 🚀 Auto-Start on Boot (Optional)

### Method 1: systemd Service

Create service file:
```bash
sudo nano /etc/systemd/system/attendance.service
```

Add content:
```ini
[Unit]
Description=Employee Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Face-Attendance-System
Environment="DISPLAY=:0"
ExecStart=/home/pi/Face-Attendance-System/.venv/bin/python3 recognition.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable attendance.service
sudo systemctl start attendance.service
sudo systemctl status attendance.service
```

### Method 2: Crontab

```bash
crontab -e

# Add this line:
@reboot sleep 30 && cd /home/pi/Face-Attendance-System && .venv/bin/python3 recognition.py &
```

---

## 📊 Expected Performance on Raspberry Pi

| Model | RAM | FPS (HOG) | FPS (CNN) | Enrollment Time |
|-------|-----|-----------|-----------|-----------------|
| Pi 3B+ | 1GB | 2-4 FPS | N/A | 5-8 min |
| Pi 4 (2GB) | 2GB | 5-8 FPS | 1-2 FPS | 3-5 min |
| Pi 4 (4GB) | 4GB | 8-12 FPS | 2-3 FPS | 2-4 min |
| Pi 4 (8GB) | 8GB | 10-15 FPS | 3-5 FPS | 2-3 min |

**Recommendation:** Pi 4 with 4GB+ RAM for best experience

---

## 💡 Best Practices for Raspberry Pi

### Power Management
- Use official power supply (5V 3A)
- Consider UPS/battery backup for continuous operation
- Monitor CPU temperature: `vcgencmd measure_temp`

### Storage
- Use Class 10 microSD card (minimum)
- Consider SSD boot for better performance
- Backup database regularly

### Cooling
- Add heatsinks to CPU/RAM
- Use fan for 24/7 operation
- Monitor temperature during recognition

### Network
- Use Ethernet for stability (if available)
- Configure static IP for remote access

---

## 🌐 Remote Access Setup

### VNC (GUI Access)
```bash
sudo raspi-config
# Interface Options → VNC → Enable

# Install RealVNC Viewer on your computer
# Connect to: <raspberry-pi-ip>:5900
```

### SSH (Terminal Access)
```bash
sudo raspi-config
# Interface Options → SSH → Enable

# From another computer:
ssh pi@<raspberry-pi-ip>
```

### Web Dashboard (Optional - Future Feature)
```bash
# Install Flask for web interface
pip3 install flask

# Create simple dashboard
# Access via: http://<raspberry-pi-ip>:5000
```

---

## 🔐 Security Recommendations

### Change Default Password
```bash
passwd
# Change from default 'raspberry'
```

### Enable Firewall
```bash
sudo apt install ufw
sudo ufw allow 22  # SSH
sudo ufw allow 5900  # VNC
sudo ufw enable
```

### Regular Updates
```bash
# Create update script
nano ~/update_system.sh
```

Add:
```bash
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo reboot
```

Run weekly via cron:
```bash
crontab -e
# Add: 0 2 * * 0 /home/pi/update_system.sh
```

---

## 📦 Backup Strategy

### Database Backup
```bash
# Create backup script
nano ~/backup_attendance.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/Face-Attendance-System/database/attendance.db ~/backups/attendance_$DATE.db
# Keep only last 30 days
find ~/backups -name "attendance_*.db" -mtime +30 -delete
```

Schedule daily:
```bash
crontab -e
# Add: 0 1 * * * /home/pi/backup_attendance.sh
```

---

## 🆘 Troubleshooting Commands

```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list

# Check camera
raspistill -o test.jpg  # Pi Camera
fswebcam test.jpg       # USB Camera

# Check system resources
htop
free -h
df -h

# Check logs
journalctl -u attendance.service -f

# Test face recognition
python3 -c "import face_recognition; print('OK')"
```

---

## 🎯 Quick Start Checklist for Raspberry Pi

- [ ] System updated (`apt update && apt upgrade`)
- [ ] Dependencies installed (dlib, opencv, etc.)
- [ ] Camera enabled and tested
- [ ] Virtual environment created
- [ ] Python packages installed
- [ ] Scripts made executable (`chmod +x start_here.sh`)
- [ ] Camera works with OpenCV
- [ ] First employee enrolled successfully
- [ ] Recognition tested and working
- [ ] Auto-start configured (optional)
- [ ] Backup script created
- [ ] Remote access enabled (SSH/VNC)

---

## 📞 Common Raspberry Pi Questions

**Q: Which Pi model should I use?**  
A: Raspberry Pi 4 with 4GB+ RAM for best performance

**Q: Can I use Pi Camera Module?**  
A: Yes, just remove `cv2.CAP_DSHOW` from VideoCapture calls

**Q: Why is it slow?**  
A: Use "hog" detection, reduce resolution, increase frame skip

**Q: Can it run 24/7?**  
A: Yes, but ensure proper cooling and power supply

**Q: How to access remotely?**  
A: Enable SSH/VNC via raspi-config

**Q: How much storage needed?**  
A: 16GB minimum, 32GB+ recommended

---

## 🌟 Optimized Configuration for Pi

Create `config/config_pi.json`:
```json
{
    "language": "english-us",
    "dataset_path": "dataset",
    "class": "PROJECT",
    "n_face_detection": 20,
    "face_count": 20,
    "db_path": "database/enroll.json",
    "encodings_path": "output/encodings.pickle",
    "recognizer_path": "output/recognizer.pickle",
    "le_path": "output/le.pickle",
    "detection_method": "hog"
}
```

Use this config on Pi for better performance!

---

**Remember:** Raspberry Pi is less powerful than desktop, but with proper optimization, it works great for attendance systems! 🍓🚀
