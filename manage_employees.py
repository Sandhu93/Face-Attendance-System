"""
Employee Management System
Delete enrollments and re-train model
"""
import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar
from project.utils import Conf
from tinydb import TinyDB
import os
import shutil
import pickle
import numpy as np
from imutils import paths
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import face_recognition

class EmployeeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management - Delete Enrollments")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        self.config_file = "config/config.json"
        self.conf = Conf(self.config_file)
        self.db = TinyDB(self.conf["db_path"])
        self.employee_table = self.db.table("student")
        
        self.create_widgets()
        self.refresh_employee_list()
    
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="Employee Management System",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Select employee(s) to delete and click 'Delete Selected'",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        instructions.pack(pady=5)
        
        # Frame for listbox and scrollbar
        list_frame = tk.Frame(self.root, bg="#f0f0f0")
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.employee_listbox = Listbox(
            list_frame,
            font=("Arial", 11),
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            height=15,
            bg="white",
            fg="#333",
            selectbackground="#4CAF50",
            selectforeground="white"
        )
        self.employee_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.employee_listbox.yview)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh List",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10,
            command=self.refresh_employee_list,
            cursor="hand2"
        )
        refresh_btn.grid(row=0, column=0, padx=10)
        
        # Delete button
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            command=self.delete_selected,
            cursor="hand2"
        )
        delete_btn.grid(row=0, column=1, padx=10)
        
        # View Details button
        view_btn = tk.Button(
            button_frame,
            text="👁️ View Details",
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=10,
            command=self.view_details,
            cursor="hand2"
        )
        view_btn.grid(row=0, column=2, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        self.status_label.pack(pady=10)
        
        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="❌ Close",
            font=("Arial", 11),
            bg="#757575",
            fg="white",
            padx=30,
            pady=8,
            command=self.root.quit,
            cursor="hand2"
        )
        exit_btn.pack(pady=10)
    
    def refresh_employee_list(self):
        """Refresh the employee list"""
        self.employee_listbox.delete(0, tk.END)
        self.employees = []
        
        for record in self.employee_table.all():
            for emp_id, details in record.items():
                emp_name = details[0] if isinstance(details, list) else details
                self.employees.append((emp_id, emp_name))
                
                # Check if dataset exists
                dataset_path = os.path.join(
                    self.conf["dataset_path"],
                    self.conf["class"],
                    emp_id
                )
                image_count = 0
                if os.path.exists(dataset_path):
                    image_count = len([f for f in os.listdir(dataset_path) 
                                     if f.endswith(('.png', '.jpg', '.jpeg'))])
                
                display_text = f"ID: {emp_id:6s} | Name: {emp_name:20s} | Images: {image_count}"
                self.employee_listbox.insert(tk.END, display_text)
        
        total = len(self.employees)
        self.status_label.config(text=f"Total Employees: {total}")
    
    def view_details(self):
        """View details of selected employee"""
        selection = self.employee_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an employee to view details.")
            return
        
        details_text = ""
        for idx in selection:
            emp_id, emp_name = self.employees[idx]
            
            dataset_path = os.path.join(
                self.conf["dataset_path"],
                self.conf["class"],
                emp_id
            )
            
            image_count = 0
            dataset_size = 0
            if os.path.exists(dataset_path):
                images = [f for f in os.listdir(dataset_path) 
                         if f.endswith(('.png', '.jpg', '.jpeg'))]
                image_count = len(images)
                dataset_size = sum(os.path.getsize(os.path.join(dataset_path, f)) 
                                 for f in images) / 1024  # KB
            
            details_text += f"Employee ID: {emp_id}\n"
            details_text += f"Name: {emp_name}\n"
            details_text += f"Face Images: {image_count}\n"
            details_text += f"Dataset Size: {dataset_size:.2f} KB\n"
            details_text += f"Dataset Path: {dataset_path}\n"
            details_text += "-" * 50 + "\n\n"
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Employee Details")
        details_window.geometry("500x400")
        
        text_widget = tk.Text(details_window, font=("Courier", 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, details_text)
        text_widget.config(state=tk.DISABLED)
    
    def delete_selected(self):
        """Delete selected employees"""
        selection = self.employee_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select employee(s) to delete.")
            return
        
        # Confirm deletion
        selected_names = [self.employees[idx] for idx in selection]
        confirm_msg = "Are you sure you want to delete these employees?\n\n"
        confirm_msg += "\n".join([f"ID: {emp_id}, Name: {name}" 
                                  for emp_id, name in selected_names])
        confirm_msg += "\n\nThis will:\n"
        confirm_msg += "✗ Delete employee from database\n"
        confirm_msg += "✗ Delete all face images\n"
        confirm_msg += "✗ Re-train the recognition model\n"
        confirm_msg += "\nThis action cannot be undone!"
        
        if not messagebox.askyesno("Confirm Deletion", confirm_msg):
            return
        
        self.status_label.config(text="Deleting employees...")
        self.root.update()
        
        deleted_count = 0
        errors = []
        
        for idx in selection:
            emp_id, emp_name = self.employees[idx]
            
            try:
                # Delete from database
                self.employee_table.remove(lambda x: emp_id in x)
                
                # Delete dataset folder
                dataset_path = os.path.join(
                    self.conf["dataset_path"],
                    self.conf["class"],
                    emp_id
                )
                if os.path.exists(dataset_path):
                    shutil.rmtree(dataset_path)
                
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"{emp_name} (ID: {emp_id}): {str(e)}")
        
        # Re-train model if any employees deleted
        if deleted_count > 0:
            self.status_label.config(text="Re-training model...")
            self.root.update()
            
            try:
                self.retrain_model()
                messagebox.showinfo(
                    "Success",
                    f"Successfully deleted {deleted_count} employee(s).\n"
                    f"Model re-trained successfully!"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Employees deleted but model re-training failed:\n{str(e)}\n\n"
                    f"Please run: python encode_faces.py && python train_model.py"
                )
        
        if errors:
            error_msg = "Some errors occurred:\n\n" + "\n".join(errors)
            messagebox.showwarning("Partial Success", error_msg)
        
        # Refresh the list
        self.refresh_employee_list()
        self.status_label.config(text=f"Deleted {deleted_count} employee(s)")
    
    def retrain_model(self):
        """Re-encode faces and re-train model"""
        # Step 1: Encode faces
        self.status_label.config(text="Step 1/2: Encoding faces...")
        self.root.update()
        
        image_paths = list(paths.list_images(self.conf["dataset_path"]))
        known_encodings = []
        known_names = []
        
        for (i, image_path) in enumerate(image_paths):
            name = image_path.split(os.path.sep)[-2]
            
            image = face_recognition.load_image_file(image_path)
            boxes = face_recognition.face_locations(
                image,
                model=self.conf["detection_method"]
            )
            encodings = face_recognition.face_encodings(image, boxes)
            
            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(name)
        
        # Save encodings
        data = {"encodings": known_encodings, "names": known_names}
        with open(self.conf["encodings_path"], "wb") as f:
            f.write(pickle.dumps(data))
        
        # Step 2: Train model
        self.status_label.config(text="Step 2/2: Training model...")
        self.root.update()
        
        le = LabelEncoder()
        labels = le.fit_transform(known_names)
        
        recognizer = SVC(C=1.0, kernel="linear", probability=True)
        recognizer.fit(known_encodings, labels)
        
        # Save model
        with open(self.conf["recognizer_path"], "wb") as f:
            f.write(pickle.dumps(recognizer))
        
        with open(self.conf["le_path"], "wb") as f:
            f.write(pickle.dumps(le))
        
        self.status_label.config(text="Model re-trained successfully!")

def main():
    root = tk.Tk()
    app = EmployeeManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
