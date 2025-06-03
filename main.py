import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Database Setup
def create_db():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no INTEGER NOT NULL UNIQUE,
            class TEXT NOT NULL
        )
    ''')
    
    # Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Main Application
class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("800x600")
        
        create_db()  # Initialize database
        
        # GUI Components
        self.setup_ui()
    
    def setup_ui(self):
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tabs
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab1, text="Add Student")
        self.notebook.add(self.tab2, text="Mark Attendance")
        self.notebook.add(self.tab3, text="View Attendance")
        
        # Tab 1: Add Student
        tk.Label(self.tab1, text="Name:").grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self.tab1, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.tab1, text="Roll No:").grid(row=1, column=0, padx=10, pady=10)
        self.roll_entry = tk.Entry(self.tab1, width=30)
        self.roll_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self.tab1, text="Class:").grid(row=2, column=0, padx=10, pady=10)
        self.class_entry = tk.Entry(self.tab1, width=30)
        self.class_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Button(self.tab1, text="Add Student", command=self.add_student).grid(row=3, column=1, pady=10)
        
        # Tab 2: Mark Attendance
        self.date_label = tk.Label(self.tab2, text=f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        self.date_label.pack(pady=10)
        
        self.student_listbox = tk.Listbox(self.tab2, selectmode=tk.MULTIPLE, height=15)
        self.student_listbox.pack(pady=10)
        self.load_students()
        
        tk.Button(self.tab2, text="Mark Present", command=lambda: self.mark_attendance("Present")).pack(side=tk.LEFT, padx=20)
        tk.Button(self.tab2, text="Mark Absent", command=lambda: self.mark_attendance("Absent")).pack(side=tk.RIGHT, padx=20)
        
        # Tab 3: View Attendance
        tk.Label(self.tab3, text="Select Date:").pack(pady=10)
        self.date_combobox = ttk.Combobox(self.tab3, values=self.get_dates())
        self.date_combobox.pack(pady=10)
        
        self.attendance_tree = ttk.Treeview(self.tab3, columns=("Name", "Roll No", "Status"))
        self.attendance_tree.heading("#0", text="ID")
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Roll No", text="Roll No")
        self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.pack(pady=10)
        
        tk.Button(self.tab3, text="Load Attendance", command=self.load_attendance).pack(pady=10)
    
    def add_student(self):
        name = self.name_entry.get()
        roll_no = self.roll_entry.get()
        class_name = self.class_entry.get()
        
        if not name or not roll_no or not class_name:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, roll_no, class) VALUES (?, ?, ?)", (name, roll_no, class_name))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.name_entry.delete(0, tk.END)
            self.roll_entry.delete(0, tk.END)
            self.class_entry.delete(0, tk.END)
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll No already exists!")
        finally:
            conn.close()
    
    def load_students(self):
        self.student_listbox.delete(0, tk.END)
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, roll_no FROM students")
        students = cursor.fetchall()
        for student in students:
            self.student_listbox.insert(tk.END, f"{student[0]} (Roll: {student[1]})")
        conn.close()
    
    def mark_attendance(self, status):
        selected_indices = self.student_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No student selected!")
            return
        
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for index in selected_indices:
            student_info = self.student_listbox.get(index)
            roll_no = student_info.split("Roll: ")[1].strip(")")
            cursor.execute("SELECT student_id FROM students WHERE roll_no=?", (roll_no,))
            student_id = cursor.fetchone()[0]
            
            # Check if attendance already marked for today
            cursor.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, current_date))
            if cursor.fetchone():
                cursor.execute("UPDATE attendance SET status=? WHERE student_id=? AND date=?", (status, student_id, current_date))
            else:
                cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, current_date, status))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Attendance marked as {status}!")
    
    def get_dates(self):
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM attendance")
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
    
    def load_attendance(self):
        selected_date = self.date_combobox.get()
        if not selected_date:
            messagebox.showerror("Error", "Please select a date!")
            return
        
        self.attendance_tree.delete(*self.attendance_tree.get_children())
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.name, s.roll_no, a.status 
            FROM students s 
            JOIN attendance a ON s.student_id = a.student_id 
            WHERE a.date=?
        ''', (selected_date,))
        
        for row in cursor.fetchall():
            self.attendance_tree.insert("", tk.END, values=(row[0], row[1], row[2]))
        
        conn.close()

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop()