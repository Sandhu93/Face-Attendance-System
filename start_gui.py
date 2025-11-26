#!/usr/bin/env python3
"""
Employee Attendance System - GUI Launcher
For touchscreen displays without keyboard on Raspberry Pi
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class AttendanceSystemLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Attendance System")
        
        # Get screen dimensions and set window to fullscreen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg="#2c3e50")
        
        # Fullscreen mode
        self.is_fullscreen = True
        self.root.attributes('-fullscreen', True)
        
        # Header
        header_frame = tk.Frame(root, bg="#34495e", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Employee Attendance Management System", 
                              font=("Arial", 24, "bold"), bg="#34495e", fg="white")
        title_label.pack(pady=30)
        
        # Main content frame
        content_frame = tk.Frame(root, bg="#2c3e50")
        content_frame.pack(fill="both", expand=True, pady=20)
        
        # Button container
        button_container = tk.Frame(content_frame, bg="#2c3e50")
        button_container.pack(expand=True)
        
        # Define buttons with commands
        buttons = [
            ("🚀 Enroll New Employee", self.launch_auto_enroll, "#27ae60"),
            ("✅ Start Attendance Recognition", self.launch_recognition, "#3498db"),
            ("📊 View Today's Report", self.view_report, "#e67e22"),
            ("⚠️ View Incomplete Checkouts", self.view_incomplete, "#e74c3c"),
            ("👤 View Absent Employees", self.view_absent, "#95a5a6"),
            ("🗑️ Manage Employees", self.manage_employees, "#9b59b6"),
            ("📷 Test Camera", self.test_camera, "#f39c12"),
        ]
        
        # Create buttons in grid layout (2 columns for large buttons)
        for idx, (text, command, color) in enumerate(buttons):
            row = idx // 2
            col = idx % 2
            
            btn = tk.Button(button_container, text=text, 
                          font=("Arial", 18, "bold"), bg=color, fg="white",
                          padx=40, pady=30, command=command,
                          cursor="hand2", relief="flat", 
                          activebackground=color, activeforeground="white")
            btn.grid(row=row, column=col, padx=20, pady=15, sticky="ew")
        
        # Configure grid columns to expand evenly
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)
        
        # Exit button at bottom
        exit_frame = tk.Frame(root, bg="#2c3e50")
        exit_frame.pack(side="bottom", pady=20)
        
        exit_btn = tk.Button(exit_frame, text="❌ Exit", 
                           font=("Arial", 16, "bold"), bg="#c0392b", fg="white",
                           padx=60, pady=20, command=self.exit_app,
                           cursor="hand2", relief="flat")
        exit_btn.pack()
    
    def launch_auto_enroll(self):
        """Launch automated enrollment"""
        self.run_python_script("auto_enroll.py")
    
    def launch_recognition(self):
        """Launch attendance recognition"""
        self.run_python_script("recognition.py")
    
    def view_report(self):
        """View today's attendance report"""
        self.run_python_script("view_attendance.py", ["report"])
    
    def view_incomplete(self):
        """View incomplete checkouts"""
        self.run_python_script("view_attendance.py", ["incomplete"])
    
    def view_absent(self):
        """View absent employees"""
        self.run_python_script("view_attendance.py", ["absent"])
    
    def manage_employees(self):
        """Open employee management"""
        self.run_python_script("manage_employees.py")
    
    def test_camera(self):
        """Test camera functionality"""
        self.run_python_script("test_camera.py")
    
    def run_python_script(self, script_name, args=None):
        """Run a Python script in the same environment"""
        try:
            cmd = [sys.executable, script_name]
            if args:
                cmd.extend(args)
            
            # Run the script
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Script execution failed:\n{str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Script not found: {script_name}\n\nPlease ensure you're in the correct directory.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            self.root.destroy()

def main():
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    root = tk.Tk()
    app = AttendanceSystemLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
