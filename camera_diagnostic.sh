#!/bin/bash
# Quick Camera Diagnostic for Raspberry Pi
# Run this to check camera setup

echo "=============================================="
echo "  Raspberry Pi Camera Diagnostic Tool"
echo "=============================================="
echo ""

# Check OS
echo "1. System Information:"
echo "   Platform: $(uname -s)"
echo "   Architecture: $(uname -m)"
echo "   Kernel: $(uname -r)"
echo ""

# Check Python
echo "2. Python Version:"
python3 --version
echo ""

# Check camera detection
echo "3. Camera Detection:"
if command -v v4l2-ctl &> /dev/null; then
    echo "   Video Devices:"
    v4l2-ctl --list-devices 2>/dev/null || echo "   No devices found"
else
    echo "   v4l2-ctl not installed. Install: sudo apt install v4l-utils"
fi
echo ""

# Check Pi Camera
echo "4. Pi Camera Status:"
if command -v vcgencmd &> /dev/null; then
    vcgencmd get_camera
else
    echo "   Not a Raspberry Pi (vcgencmd not found)"
fi
echo ""

# Check video devices
echo "5. Video Device Files:"
ls -l /dev/video* 2>/dev/null || echo "   No video devices found"
echo ""

# Check user groups
echo "6. User Groups:"
groups | grep -q video && echo "   ✅ User is in 'video' group" || echo "   ❌ User NOT in 'video' group - Run: sudo usermod -a -G video \$USER"
echo ""

# Check camera modules
echo "7. Camera Modules Loaded:"
lsmod | grep -E "bcm2835|uvcvideo" || echo "   No camera modules loaded"
echo ""

# Check OpenCV
echo "8. OpenCV Installation:"
python3 -c "import cv2; print(f'   OpenCV version: {cv2.__version__}')" 2>/dev/null || echo "   ❌ OpenCV not installed"
echo ""

# Test camera opening
echo "9. Camera Test:"
python3 -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print('   ✅ Camera opened and frame captured successfully!')
        print(f'   Frame shape: {frame.shape}')
    else:
        print('   ⚠️  Camera opened but failed to read frame')
    cap.release()
else:
    print('   ❌ Failed to open camera')
" 2>/dev/null || echo "   ❌ Python test failed"
echo ""

# Check virtual environment
echo "10. Virtual Environment:"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "    ✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "    ⚠️  No virtual environment active"
    echo "    Run: source ~/smartAttendance/.venv/bin/activate"
fi
echo ""

echo "=============================================="
echo "  Recommendations:"
echo "=============================================="

# Generate recommendations
ISSUES_FOUND=0

# Check if user in video group
if ! groups | grep -q video; then
    echo "❌ Add user to video group:"
    echo "   sudo usermod -a -G video \$USER"
    echo "   sudo reboot"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check if camera module loaded for Pi Camera
if command -v vcgencmd &> /dev/null; then
    if ! lsmod | grep -q bcm2835; then
        echo "❌ Pi Camera module not loaded:"
        echo "   sudo modprobe bcm2835-v4l2"
        echo "   echo 'bcm2835-v4l2' | sudo tee -a /etc/modules"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

# Check if video devices exist
if ! ls /dev/video* &> /dev/null; then
    echo "❌ No video devices found:"
    echo "   - Enable camera in: sudo raspi-config"
    echo "   - Check camera connection"
    echo "   - For Pi Camera: Interface Options → Camera → Enable"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check if OpenCV installed
if ! python3 -c "import cv2" 2>/dev/null; then
    echo "❌ OpenCV not installed:"
    echo "   pip3 install opencv-python"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No issues found! Camera should work."
    echo ""
    echo "Next steps:"
    echo "  1. Run: python3 test_camera.py"
    echo "  2. If successful, run: ./start_here.sh"
else
    echo ""
    echo "Found $ISSUES_FOUND issue(s) - Fix them and run this script again"
fi

echo ""
echo "=============================================="
echo ""
echo "For detailed troubleshooting, see:"
echo "  CAMERA_TROUBLESHOOTING.md"
echo ""
