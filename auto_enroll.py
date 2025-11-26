"""
Automated Employee Enrollment System
All-in-one script: Enroll → Encode → Train
"""
import tkinter as tk
from tkinter import ttk, messagebox
from project.utils import Conf
from tinydb import TinyDB, where
import face_recognition
import cv2
import os
import time
import threading
import pickle
import numpy as np
from imutils import paths
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

# Create necessary directories
if not os.path.exists("dataset"):
    os.mkdir("dataset")
if not os.path.exists("dataset/PROJECT"):
    os.mkdir("dataset/PROJECT")
if not os.path.exists("output"):
    os.mkdir("output")

# Global variables
stop_event = threading.Event()
conf = None
db = None
student_table = None

def initialize_config():
    """Initialize configuration and database"""
    global conf, db, student_table
    config_file = "config/config.json"
    conf = Conf(config_file)
    db = TinyDB(conf["db_path"])
    student_table = db.table("student")

def enroll_employee(employee_id, employee_name, progress_callback, status_callback):
    """Step 1: Enroll employee face images"""
    try:
        status_callback("Step 1/3: Enrolling employee face...")
        
        # Check if employee already exists
        found_employees = []
        for record in student_table.all():
            for sub_key, details in record.items():
                if employee_id == sub_key:
                    found_employees.append(employee_id)
        
        if found_employees:
            return False, f"Employee ID '{employee_id}' is already enrolled."
        
        # Start camera capture
        vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Create directory for storing face images
        employee_path = os.path.join(conf["dataset_path"], conf["class"], employee_id)
        os.makedirs(employee_path, exist_ok=True)
        
        total_saved = 0
        status_callback(f"Step 1/3: Capturing faces (0/{conf['face_count']})")
        
        while total_saved < conf["face_count"]:
            if stop_event.is_set():
                vs.release()
                cv2.destroyAllWindows()
                return False, "Enrollment cancelled by user"
            
            ret, frame = vs.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb_frame, model=conf["detection_method"])
            frame_copy = frame.copy()
            
            # Draw boxes and save face images
            for (top, right, bottom, left) in boxes:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                
                padding = 70
                top = max(0, top - padding)
                bottom = min(frame.shape[0], bottom + padding)
                left = max(0, left - padding)
                right = min(frame.shape[1], right + padding)
                face_image = frame_copy[top:bottom, left:right]
                
                if total_saved < conf["face_count"]:
                    save_path = os.path.join(employee_path, f"{str(total_saved).zfill(5)}.png")
                    cv2.imwrite(save_path, face_image)
                    total_saved += 1
                    progress = int((total_saved / conf["face_count"]) * 33)  # 33% of total
                    progress_callback(progress)
                    status_callback(f"Step 1/3: Capturing faces ({total_saved}/{conf['face_count']})")
            
            # Draw status on frame
            cv2.putText(frame, f"Captured: {total_saved}/{conf['face_count']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Enrollment - Look at camera", frame)
            cv2.waitKey(1)
        
        vs.release()
        cv2.destroyAllWindows()
        
        # Add employee to database
        student_table.insert({employee_id: [employee_name, "enrolled"]})
        status_callback(f"Step 1/3: ✓ Enrolled {total_saved} face images")
        time.sleep(1)
        
        return True, "Enrollment completed successfully"
    
    except Exception as e:
        return False, f"Enrollment error: {str(e)}"

def encode_faces(progress_callback, status_callback):
    """Step 2: Generate face encodings"""
    try:
        status_callback("Step 2/3: Generating face encodings...")
        progress_callback(33)
        
        dataset_path = os.path.join(conf["dataset_path"], conf["class"])
        encodings_path = conf["encodings_path"]
        
        # Grab image paths
        imagePaths = list(paths.list_images(dataset_path))
        total_images = len(imagePaths)
        
        if total_images == 0:
            return False, "No images found in dataset"
        
        knownEncodings = []
        knownNames = []
        
        for (i, imagePath) in enumerate(imagePaths):
            # Extract the person name
            name = imagePath.split(os.path.sep)[-2]
            
            # Load and process the image
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to grayscale and expand dimensions
            gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            gray_img = np.expand_dims(gray_image, axis=2).repeat(3, axis=2)
            encodings = face_recognition.face_encodings(gray_img)
            
            # Save encodings and names
            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)
            
            # Update progress (33% to 66%)
            progress = 33 + int((i + 1) / total_images * 33)
            progress_callback(progress)
            status_callback(f"Step 2/3: Encoding images ({i + 1}/{total_images})")
        
        # Serialize encodings
        data = {"encodings": knownEncodings, "names": knownNames}
        with open(encodings_path, "wb") as f:
            pickle.dump(data, f)
        
        status_callback(f"Step 2/3: ✓ Encoded {total_images} images")
        time.sleep(1)
        
        return True, f"Encoded {total_images} images successfully"
    
    except Exception as e:
        return False, f"Encoding error: {str(e)}"

def train_model(progress_callback, status_callback):
    """Step 3: Train recognition model"""
    try:
        status_callback("Step 3/3: Training recognition model...")
        progress_callback(66)
        
        encodings_path = conf["encodings_path"]
        recognizer_path = conf["recognizer_path"]
        le_path = conf["le_path"]
        
        # Load the face encodings
        with open(encodings_path, "rb") as f:
            data = pickle.load(f)
        
        progress_callback(70)
        status_callback("Step 3/3: Encoding labels...")
        
        # Encode the labels
        le = LabelEncoder()
        labels = le.fit_transform(data["names"])
        
        progress_callback(80)
        status_callback("Step 3/3: Training SVM model...")
        
        # Train the model
        recognizer = SVC(C=1.0, kernel="linear", probability=True)
        recognizer.fit(data["encodings"], labels)
        
        progress_callback(90)
        status_callback("Step 3/3: Saving model files...")
        
        # Write the model to disk
        with open(recognizer_path, "wb") as f:
            pickle.dump(recognizer, f)
        
        # Write the label encoder to disk
        with open(le_path, "wb") as f:
            pickle.dump(le, f)
        
        progress_callback(100)
        status_callback("Step 3/3: ✓ Model training completed")
        time.sleep(1)
        
        return True, "Model training completed successfully"
    
    except Exception as e:
        return False, f"Training error: {str(e)}"

def automated_enrollment_process(employee_id, employee_name, progress_callback, status_callback, completion_callback):
    """Main automated process: Enroll → Encode → Train"""
    try:
        # Step 1: Enroll
        success, message = enroll_employee(employee_id, employee_name, progress_callback, status_callback)
        if not success:
            completion_callback(False, message)
            return
        
        # Step 2: Encode
        success, message = encode_faces(progress_callback, status_callback)
        if not success:
            completion_callback(False, message)
            return
        
        # Step 3: Train
        success, message = train_model(progress_callback, status_callback)
        if not success:
            completion_callback(False, message)
            return
        
        # Success!
        status_callback("✓ All steps completed successfully!")
        completion_callback(True, f"Employee '{employee_name}' enrolled and system trained successfully!\n\nThe system is now ready for recognition.")
    
    except Exception as e:
        completion_callback(False, f"Process error: {str(e)}")
    finally:
        if db:
            db.close()

# ===== GUI Code =====

class AutomatedEnrollmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Employee Enrollment System")
        self.root.geometry("700x550")
        self.root.configure(bg="#f0f0f0")
        
        # Center window
        self.center_window(700, 550)
        
        # Initialize config
        initialize_config()
        
        # Header
        header_frame = tk.Frame(root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚀 Automated Employee Enrollment", 
                              font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=25)
        
        # Main content
        content_frame = tk.Frame(root, bg="#f0f0f0", padx=40, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Info label
        info_label = tk.Label(content_frame, 
                             text="Complete enrollment in one step!\n" +
                                  "System will automatically: Capture faces → Encode → Train model",
                             font=("Arial", 10), bg="#f0f0f0", fg="#555", justify="center")
        info_label.pack(pady=(0, 20))
        
        # Input fields
        tk.Label(content_frame, text="Employee ID:", font=("Arial", 11), 
                bg="#f0f0f0").pack(anchor="w")
        self.entry_id = tk.Entry(content_frame, font=("Arial", 12), width=30)
        self.entry_id.pack(pady=(5, 15), ipady=5)
        
        tk.Label(content_frame, text="Employee Name:", font=("Arial", 11), 
                bg="#f0f0f0").pack(anchor="w")
        self.entry_name = tk.Entry(content_frame, font=("Arial", 12), width=30)
        self.entry_name.pack(pady=(5, 20), ipady=5)
        
        # Progress section
        progress_frame = tk.Frame(content_frame, bg="#f0f0f0")
        progress_frame.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(progress_frame, text="Ready to enroll", 
                                     font=("Arial", 10), bg="#f0f0f0", fg="#555")
        self.status_label.pack(anchor="w", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=600, mode="determinate")
        self.progress_bar.pack(fill="x")
        
        self.percentage_label = tk.Label(progress_frame, text="0%", 
                                        font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.percentage_label.pack(pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Enrollment", 
                                      font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
                                      padx=20, pady=10, command=self.start_enrollment,
                                      cursor="hand2", relief="flat")
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = tk.Button(button_frame, text="⏹ Stop", 
                                     font=("Arial", 12, "bold"), bg="#e74c3c", fg="white",
                                     padx=20, pady=10, command=self.stop_enrollment,
                                     cursor="hand2", relief="flat", state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        self.reset_button = tk.Button(button_frame, text="🔄 Reset", 
                                      font=("Arial", 12, "bold"), bg="#95a5a6", fg="white",
                                      padx=20, pady=10, command=self.reset_form,
                                      cursor="hand2", relief="flat")
        self.reset_button.pack(side="left", padx=5)
        
        # Style progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=25, troughcolor='#ddd', 
                       background='#27ae60', bordercolor='#ddd', lightcolor='#27ae60', 
                       darkcolor='#27ae60')
    
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.percentage_label.config(text=f"{value}%")
        self.root.update_idletasks()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def on_completion(self, success, message):
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if success:
            messagebox.showinfo("✓ Success", message)
            self.reset_form()
        else:
            messagebox.showerror("✗ Error", message)
            self.update_status("Failed. Please try again.")
    
    def start_enrollment(self):
        employee_id = self.entry_id.get().strip()
        employee_name = self.entry_name.get().strip()
        
        # Validate inputs
        if not employee_id or not employee_name:
            messagebox.showerror("Input Error", "Please provide both Employee ID and Name.")
            return
        
        if not employee_id.isdigit():
            messagebox.showerror("Input Error", "Employee ID must be numeric.")
            return
        
        # Update UI
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar["value"] = 0
        self.percentage_label.config(text="0%")
        stop_event.clear()
        
        # Start enrollment process in background thread
        thread = threading.Thread(
            target=automated_enrollment_process,
            args=(employee_id, employee_name, self.update_progress, 
                  self.update_status, self.on_completion),
            daemon=True
        )
        thread.start()
    
    def stop_enrollment(self):
        stop_event.set()
        self.update_status("Stopping... Please wait.")
        self.stop_button.config(state="disabled")
    
    def reset_form(self):
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.progress_bar["value"] = 0
        self.percentage_label.config(text="0%")
        self.status_label.config(text="Ready to enroll")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomatedEnrollmentApp(root)
    root.mainloop()
