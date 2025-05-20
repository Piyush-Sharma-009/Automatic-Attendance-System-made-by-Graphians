import pandas as pd
from glob import glob
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from datetime import datetime

def subjectchoose(text_to_speech):
    def calculate_attendance():
        subject = tx.get().strip()  # Define subject here
        if not subject:
            text_to_speech("Please enter the subject name.")
            return
        
        try:
            # Get all attendance files for the subject
            filenames = glob(f"Attendance\\{subject}\\{subject}_*.csv")
            if not filenames:
                text_to_speech(f"No attendance files found for {subject}")
                return

            # Read and merge all CSV files
            dfs: List[pd.DataFrame] = []
            for f in filenames:
                try:
                    df = pd.read_csv(f)
                    # Clean name fields if they have brackets
                    if 'Name' in df.columns:
                        df['Name'] = df['Name'].str.replace(r'[\[\]\']', '', regex=True)
                    
                    # Extract date and time from filename
                    try:
                        timestamp_str = os.path.basename(f).split('_')[-1].split('.')[0]
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
                        df['Recorded_At'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        df['Recorded_At'] = "Unknown"
                        
                    dfs.append(df)
                except Exception as e:
                    print(f"Error reading {f}: {str(e)}")

            if not dfs:
                text_to_speech("No valid attendance data found")
                return

            # Merge all DataFrames
            merged_df = pd.concat(dfs, ignore_index=True)
            merged_df.fillna('', inplace=True)

            # Remove Attendance column if it exists
            if 'Attendance' in merged_df.columns:
                merged_df = merged_df.drop(columns=['Attendance'])

            # Reorder columns to show timing information first
            cols = ['Recorded_At'] + [col for col in merged_df.columns if col != 'Recorded_At']
            merged_df = merged_df[cols]

            # Save merged attendance
            output_path = f"Attendance\\{subject}\\attendance.csv"
            merged_df.to_csv(output_path, index=False)

            # Display in GUI
            display_attendance(merged_df, subject)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            text_to_speech(f"Error processing attendance: {str(e)}")

    def display_attendance(df, subject):  # subject parameter properly defined
        """Display attendance in a scrollable table with timing info"""
        root = tk.Tk()
        root.title(f"Attendance of {subject}")
        root.configure(background="black")
        root.geometry("1000x600")

        # Create frame for treeview and scrollbar
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        # Treeview widget
        tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configure column headings and widths
        col_widths = {
            'Recorded_At': 150,
            'Enrollment': 100,
            'Name': 150,
            'Date': 100,
            'Status': 80
        }
        
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, 
                       width=col_widths.get(col, 100), 
                       anchor='center' if col == 'Recorded_At' else 'w')

        # Add data to treeview
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        # Configure grid weights
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Add export button
        export_btn = tk.Button(
            root,
            text="Export to CSV",
            command=lambda: export_csv(df, subject),  # Pass subject here
            bd=3,
            font=("times new roman", 12),
            bg="black",
            fg="yellow",
            height=1,
            width=15,
            relief=tk.RIDGE
        )
        export_btn.pack(pady=10)

        root.mainloop()

    def export_csv(df, subject):  # Properly defined subject parameter
        """Export the displayed data to CSV"""
        try:
            export_path = f"Attendance\\{subject}\\attendance_with_timing.csv"  # Use lowercase subject
            df.to_csv(export_path, index=False)
            messagebox.showinfo("Success", f"Data exported to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def Attf():
        """Open attendance folder"""
        subject = tx.get().strip()  # Define subject here
        if not subject:
            text_to_speech("Please enter the subject name")
        else:
            folder_path = f"Attendance\\{subject}"
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                text_to_speech(f"Folder not found for {subject}")

    # Main GUI window
    subject_gui = tk.Tk()  # Renamed to avoid conflict
    subject_gui.title("Subject Selection")
    subject_gui.geometry("580x320")
    subject_gui.resizable(0, 0)
    subject_gui.configure(background="black")

    # Title label
    titl = tk.Label(
        subject_gui,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=100, y=12)

    # Subject entry
    sub_label = tk.Label(
        subject_gui,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=tk.RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    tx = tk.Entry(
        subject_gui,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=tk.RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    # Buttons
    fill_a = tk.Button(
        subject_gui,
        text="View Attendance",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=tk.RIDGE,
    )
    fill_a.place(x=195, y=170)

    attf = tk.Button(
        subject_gui,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=tk.RIDGE,
    )
    attf.place(x=360, y=170)

    subject_gui.mainloop()