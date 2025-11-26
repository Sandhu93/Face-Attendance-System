"""
Camera Test Script for Raspberry Pi / Linux / Windows
Tests camera connection and displays video feed
"""
import cv2
import platform
import sys
import os

def find_camera():
    """Find available camera index and backend"""
    
    # For Raspberry Pi 5, try libcamera first
    if platform.system() == 'Linux' and os.path.exists('/usr/bin/libcamera-hello'):
        print("[INFO] Raspberry Pi detected, trying libcamera backend...")
        # Try CAP_V4L2 with different indices
        for idx in [0, 1, 2]:
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"[SUCCESS] Found camera at index {idx} with V4L2")
                    return cap, idx, 'V4L2'
                cap.release()
        
        # Try without backend specification
        for idx in [0, 1, 2]:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"[SUCCESS] Found camera at index {idx}")
                    return cap, idx, 'Default'
                cap.release()
    
    # Windows
    if platform.system() == 'Windows':
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            print("[INFO] Using DirectShow backend (Windows)")
            return cap, 0, 'DSHOW'
    
    # Generic Linux/Mac - try multiple indices
    else:
        print("[INFO] Scanning for cameras...")
        for idx in range(10):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"[SUCCESS] Found camera at index {idx}")
                    return cap, idx, 'Default'
                cap.release()
    
    return None, None, None

print("=" * 60)
print("Camera Test Script")
print("=" * 60)
print(f"Platform: {platform.system()}")
print(f"Python Version: {sys.version}")
print()

# Try to open camera
print("[INFO] Attempting to open camera...")

cap, camera_idx, backend = find_camera()

# Check if camera opened successfully
if cap is None or not cap.isOpened():
    print()
    print("[ERROR] Failed to open camera!")
    print()
    print("Troubleshooting steps:")
    print()
    
    if platform.system() == 'Linux':
        print("For Raspberry Pi / Linux:")
        print("  1. Check camera is detected:")
        print("     v4l2-ctl --list-devices")
        print("     libcamera-hello --list-cameras  (for Pi 5)")
        print()
        print("  2. For Pi Camera, enable it:")
        print("     sudo raspi-config")
        print("     Interface Options → Camera → Enable")
        print()
        print("  3. Check camera status:")
        print("     vcgencmd get_camera")
        print("     (Should show: supported=1 detected=1)")
        print()
        print("  4. Add user to video group:")
        print("     sudo usermod -a -G video $USER")
        print("     Then reboot")
        print()
        print("  5. Test with simple capture:")
        print("     raspistill -o test.jpg  (for Pi Camera)")
        print("     fswebcam test.jpg       (for USB Camera)")
        print()
        print("  6. Check camera permissions:")
        print("     ls -l /dev/video*")
        print()
        print("  7. Try different camera index:")
        print("     Try VideoCapture(1) or VideoCapture(2)")
    
    elif platform.system() == 'Windows':
        print("For Windows:")
        print("  1. Check camera in Device Manager")
        print("  2. Close other apps using camera (Zoom, Teams, etc.)")
        print("  3. Grant camera permissions in Windows Settings")
        print("  4. Try restarting your computer")
    
    else:
        print("For Mac:")
        print("  1. Grant camera permissions in System Preferences")
        print("  2. Close other apps using camera")
    
    cap.release()
    sys.exit(1)

print("[SUCCESS] Camera opened successfully!")
print(f"[INFO] Using camera index: {camera_idx}")
print(f"[INFO] Backend: {backend}")
print()

# Get camera properties
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Camera Properties:")
print(f"  Resolution: {int(width)} x {int(height)}")
print(f"  FPS: {int(fps)}")
print()

# Try to read a frame
print("[INFO] Reading test frame...")
ret, frame = cap.read()

if not ret:
    print("[ERROR] Failed to read frame from camera!")
    cap.release()
    sys.exit(1)

print(f"[SUCCESS] Frame captured successfully! Shape: {frame.shape}")
print()
print("[INFO] Press 'q' to quit, 's' to save snapshot")
print()

frame_count = 0
try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("[WARNING] Failed to read frame")
            break
        
        frame_count += 1
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Add info overlay
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' for snapshot", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"{int(width)}x{int(height)}", (10, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Display frame
        cv2.imshow("Camera Test - Face Attendance System", frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("[INFO] Quitting...")
            break
        elif key == ord('s'):
            filename = f"camera_test_snapshot_{frame_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[INFO] Snapshot saved: {filename}")

except KeyboardInterrupt:
    print("\n[INFO] Interrupted by user")

except Exception as e:
    print(f"\n[ERROR] An error occurred: {e}")

finally:
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print()
    print("[INFO] Camera released")
    print(f"[INFO] Total frames captured: {frame_count}")
    print()
    
    if frame_count > 0:
        print("✅ Camera is working correctly!")
        print("You can now use the enrollment and recognition systems.")
    else:
        print("❌ Camera test failed!")
        print("Please check the troubleshooting steps above.")
    
    print()
    print("=" * 60)
