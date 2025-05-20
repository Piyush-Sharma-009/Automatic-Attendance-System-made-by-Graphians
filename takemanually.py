import tkinter as tk
from tkinter import messagebox
import os
import pandas as pd
import datetime
import time
from typing import List, Dict

# Global variables
ts = time.time()
current_date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
current_time = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")

class AttendanceSystem:
    def __init__(self):
        self.attendance_records: List[Dict] = []
        self.existing_enrollments = set()

    def validate_student(self, enrollment: str, name: str) -> bool:
        """Comprehensive validation of student data"""
        errors = []
        if not enrollment:
            errors.append("Enrollment cannot be empty")
        if not name:
            errors.append("Name cannot be empty")
        elif len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        elif any(char.isdigit() for char in name):
            errors.append("Name cannot contain numbers")
        if not enrollment.isdigit():
            errors.append("Enrollment must be numeric")
        elif len(enrollment) < 3:
            errors.append("Enrollment too short (min 3 digits)")
        elif enrollment in self.existing_enrollments:
            errors.append("Enrollment already exists")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        return True

    def add_student(self, enrollment: str, name: str) -> None:
        """Add validated student to records"""
        if not self.validate_student(enrollment, name):
            return
            
        self.attendance_records.append({
            'Enrollment': enrollment,
            'Name': str(name).strip("[]'\" "),  # Force string and remove brackets
            'Date': current_date,
            'Status': 'Present'
        })
        self.existing_enrollments.add(enrollment)
        messagebox.showinfo("Success", f"Added {name.strip()} ({enrollment})")

    def backup_data(self) -> bool:
        """Create backup of current records"""
        if not self.attendance_records:
            return False
            
        backup_dir = os.path.join("Attendance", "Backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            backup_file = os.path.join(
                backup_dir,
                f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            pd.DataFrame(self.attendance_records).to_csv(backup_file, index=False)
            return True
        except Exception as e:
            print(f"Backup failed: {str(e)}")
            return False

    def save_attendance(self, subject: str) -> None:
        """Save attendance data with multiple safety checks"""
        if not self.attendance_records:
            messagebox.showerror("Error", "No attendance records to save")
            return

        # Validate subject name
        if not subject or not subject.replace("_", "").isalnum():
            messagebox.showerror("Error", "Invalid subject name")
            return

        # Create backup first
        if not self.backup_data():
            messagebox.showwarning("Warning", "Backup failed - proceeding anyway")

        # Prepare save directory
        attendance_dir = "Attendance"
        os.makedirs(attendance_dir, exist_ok=True)

        # Create safe filename
        safe_subject = "".join(
            c for c in subject if c.isalnum() or c in (' ', '_')
        ).rstrip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(attendance_dir, f"{safe_subject}_{timestamp}.csv")

        try:
            # Create DataFrame with proper types
            df = pd.DataFrame(
                self.attendance_records,
                columns=['Enrollment', 'Name', 'Date', 'Status'],
                dtype={'Enrollment': str, 'Name': str}
            )
            
            # Final validation
            if df.isnull().values.any() or df['Name'].str.strip().eq('').any():
                messagebox.showerror("Error", "Invalid data detected - not saving")
                return

            # Save to CSV
            df.to_csv(filename, index=False)
            messagebox.showinfo(
                "Success", 
                f"Saved {len(df)} records to:\n{filename}"
            )
            os.startfile(attendance_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")

def manually_fill():
    """Entry point for manual attendance filling"""
    sb = tk.Tk()
    sb.iconbitmap("AMS.ico")
    sb.title("Enter subject name")
    sb.geometry("580x320")
    sb.configure(background="snow")

    # Subject Entry
    tk.Label(
        sb,
        text="Enter Subject",
        width=15,
        height=2,
        fg="white",
        bg="blue2",
        font=("times", 15, "bold")
    ).place(x=30, y=100)

    subject_entry = tk.Entry(
        sb, 
        width=20, 
        bg="yellow", 
        fg="red", 
        font=("times", 23, "bold")
    )
    subject_entry.place(x=250, y=105)

    # Button
    tk.Button(
        sb,
        text="Fill Attendance",
        command=lambda: start_attendance(subject_entry.get().strip()),
        fg="white",
        bg="deep pink",
        width=20,
        height=2,
        activebackground="Red",
        font=("times", 15, "bold")
    ).place(x=250, y=160)

    sb.mainloop()

def start_attendance(subject):
    """Validate subject and start attendance recording"""
    if not subject:
        messagebox.showerror("Error", "Please enter subject name")
        return
    sb.destroy() if 'sb' in globals() else None
    fill_attendance(subject)

def fill_attendance(subject):
    """Main attendance interface"""
    MFW = tk.Tk()
    MFW.iconbitmap("AMS.ico")
    MFW.title(f"Manual attendance of {subject}")
    MFW.geometry("880x520")  # Slightly taller for status bar
    MFW.configure(background="snow")

    # Initialize attendance system
    attendance = AttendanceSystem()

    # Status bar
    status_var = tk.StringVar()
    status_bar = tk.Label(
        MFW,
        textvariable=status_var,
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.W,
        bg="lightgray",
        font=("times", 12)
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(message):
        status_var.set(message)
        MFW.update_idletasks()

    # GUI Components
    tk.Label(
        MFW,
        text="Enter Enrollment",
        width=15,
        height=2,
        fg="white",
        bg="blue2",
        font=("times", 15, "bold")
    ).place(x=30, y=100)

    enrollment_entry = tk.Entry(
        MFW,
        width=20,
        validate="key",
        bg="yellow",
        fg="red",
        font=("times", 23, "bold")
    )
    enrollment_entry['validatecommand'] = (
        MFW.register(lambda p: p.isdigit() or p == ""), 
        '%P'
    )
    enrollment_entry.place(x=290, y=105)

    tk.Label(
        MFW,
        text="Enter Student Name",
        width=15,
        height=2,
        fg="white",
        bg="blue2",
        font=("times", 15, "bold")
    ).place(x=30, y=200)

    name_entry = tk.Entry(
        MFW,
        width=20,
        bg="yellow",
        fg="red",
        font=("times", 23, "bold")
    )
    name_entry.place(x=290, y=205)

    # Buttons
    def add_student():
        update_status("Validating student data...")
        enrollment = enrollment_entry.get().strip()
        name = name_entry.get().strip()
        attendance.add_student(enrollment, name)
        if enrollment and name:  # If successfully added
            enrollment_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
        update_status(f"Total records: {len(attendance.attendance_records)}")

    def save_data():
        update_status("Saving attendance...")
        attendance.save_attendance(subject)
        update_status(f"Saved {len(attendance.attendance_records)} records")

    buttons = [
        ("Clear", 690, 100, lambda: [enrollment_entry.delete(0, tk.END), update_status("Fields cleared")]),
        ("Clear", 690, 200, lambda: [name_entry.delete(0, tk.END), update_status("Fields cleared")]),
        ("Add Student", 170, 300, add_student),
        ("Save Attendance", 570, 300, save_data),
        ("Open Folder", 730, 410, lambda: [os.startfile("Attendance"), update_status("Opened Attendance folder")])
    ]

    for text, x, y, cmd in buttons:
        bg_color = {
            "Clear": "deep pink",
            "Add Student": "lime green",
            "Save Attendance": "red",
            "Open Folder": "lawn green"
        }.get(text, "gray")
        
        tk.Button(
            MFW,
            text=text,
            command=cmd,
            width=10 if text == "Clear" else 12 if text == "Open Folder" else 20,
            height=1 if text in ("Clear", "Open Folder") else 2,
            font=("times", 15, "bold"),
            bg=bg_color
        ).place(x=x, y=y)

    update_status("Ready to record attendance")
    MFW.mainloop()

if __name__ == "__main__":
    manually_fill()