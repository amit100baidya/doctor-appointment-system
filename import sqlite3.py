import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import hashlib
from datetime import datetime
import tkinter.simpledialog as simpledialog  # Import simpledialog here

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection
conn = sqlite3.connect('doctor_appointment_system.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    speciality TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
)
''')
# Create notifications table to store cancellation notifications
cursor.execute('''
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
)
''')

conn.commit()


conn.commit()

# Main Application Class
class DoctorAppointmentApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Doctor Appointment System")
        self.geometry("1600x1000")
        self.user = None
        self.configure(background="#007BFF")
        self.login_screen()


    def login_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Login", font=("Verdana", 24, "bold"), foreground="#1a73e8")
        label.pack(pady=20)

        username_label = ttk.Label(self, text="Username:", font=("Verdana", 12), foreground="#001F3F")
        username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self, font=("Verdana", 10))
        self.username_entry.pack(pady=5)

        password_label = ttk.Label(self, text="Password:", font=("Verdana", 12), foreground="#001F3F")
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*", font=("Verdana", 10))
        self.password_entry.pack(pady=5)

        login_button = tb.Button(self, text="Login", style="dark.TButton", bootstyle="rounded", command=self.login)
        login_button.pack(pady=20)

        register_button = tb.Button(self, text="Register", style="warning.TButton", bootstyle="rounded", command=self.register_screen)
        register_button.pack(pady=10)

    def register_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Register", font=("Verdana", 24, "bold"), foreground="#1a73e8")
        label.pack(pady=20)

        username_label = ttk.Label(self, text="Username:", font=("Arial", 12), foreground="#001F3F")
        username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self, font=("Arial", 10))
        self.username_entry.pack(pady=5)

        password_label = ttk.Label(self, text="Password:", font=("Arial", 12), foreground="#001F3F")
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*", font=("Arial", 10))
        self.password_entry.pack(pady=5)

        role_label = ttk.Label(self, text="Role:", font=("Arial", 12), foreground="#001F3F")
        role_label.pack(pady=5)
        self.role_var = tk.StringVar(value="patient")
        role_menu = ttk.OptionMenu(self, self.role_var, "patient", "doctor")
        role_menu.pack(pady=5)

        speciality_label = ttk.Label(self, text="Speciality:", font=("Arial", 12), foreground="#001F3F")
        speciality_label.pack(pady=5)
        self.speciality_entry = ttk.Entry(self, font=("Arial", 10))
        self.speciality_entry.pack(pady=5)

        register_button = tb.Button(self, text="Register", style="info.TButton", bootstyle="rounded", command=self.register)
        register_button.pack(pady=20)

        back_button = tb.Button(self, text="Back to Login", style="secondary.TButton", bootstyle="rounded", command=self.login_screen)
        back_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = hash_password(self.password_entry.get())

        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            self.user = user
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.home_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = hash_password(self.password_entry.get())
        role = self.role_var.get()
        speciality = self.speciality_entry.get() if role == 'doctor' else None

        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return
        if role == 'doctor' and not speciality:
            messagebox.showerror("Input Error", "Please enter a speciality for the doctor.")
            return

        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            user_id = cursor.lastrowid
            if role == 'doctor':
                cursor.execute("INSERT INTO doctors (id, name, speciality) VALUES (?, ?, ?)", (user_id, username, speciality))
            conn.commit()
            messagebox.showinfo("Registration Successful", "You can now log in.")
            self.login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists.")

    def home_screen(self):
        self.clear_frame()
        notebook = ttk.Notebook(self)
    
        book_tab = ttk.Frame(notebook)
        view_tab = ttk.Frame(notebook)
        notification_tab = ttk.Frame(notebook)  # New tab for notifications
    
        notebook.add(book_tab, text="Book Appointment")
        notebook.add(view_tab, text="View Appointments")
        notebook.add(notification_tab, text="Notifications")  # Add the tab
        notebook.pack(expand=True, fill='both')

        if self.user[3] == 'patient':
            self.book_appointment_screen(parent=book_tab)
            self.view_appointments_screen(parent=view_tab)
        elif self.user[3] == 'doctor':
            self.view_appointments_screen(parent=view_tab)
            self.view_notifications(parent=notification_tab)  # Show notifications for the doctor

        logout_button = tb.Button(self, text="Logout", style="danger.TButton", bootstyle="rounded", command=self.logout)
        logout_button.pack(pady=20)

    def book_appointment_screen(self, parent):
        label = ttk.Label(parent, text="Book an Appointment", font=("Arial", 20), foreground="#1a73e8")
        label.pack(pady=20)

        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()

        if not doctors:
            messagebox.showerror("No Doctors Available", "There are no doctors available at the moment. Please try again later.")
            self.home_screen()
            return

        doctor_label = ttk.Label(parent, text="Select Doctor:", font=("Arial", 12), foreground="#001F3F")
        doctor_label.pack(pady=5)
        self.doctor_var = tk.StringVar(value=f"{doctors[0][1]} - {doctors[0][2]}")
        doctor_menu = ttk.OptionMenu(parent, self.doctor_var, *[f"{doctor[1]} - {doctor[2]}" for doctor in doctors])
        doctor_menu.pack(pady=5)

        date_label = ttk.Label(parent, text="Select Date (YYYY-MM-DD):", font=("Arial", 12), foreground="#001F3F")
        date_label.pack(pady=5)
        self.date_entry = ttk.Entry(parent, font=("Arial", 10))
        self.date_entry.pack(pady=5)

        time_label = ttk.Label(parent, text="Select Time (HH:MM AM/PM):", font=("Arial", 12), foreground="#001F3F")
        time_label.pack(pady=5)
        self.time_entry = ttk.Entry(parent, font=("Arial", 10))
        self.time_entry.pack(pady=5)

        submit_button = tb.Button(parent, text="Confirm Appointment", style="success.TButton", bootstyle="rounded", command=self.confirm_appointment)
        submit_button.pack(pady=20)

    def confirm_appointment(self):
        doctor_name_speciality = self.doctor_var.get()
        doctor_name = doctor_name_speciality.split(" - ")[0]
        date = self.date_entry.get()
        time = self.time_entry.get()

        if not date or not time:
            messagebox.showerror("Input Error", "Please enter both date and time.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        try:
            datetime.strptime(time, "%I:%M %p")
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter the time in HH:MM AM/PM format.")
            return

        cursor.execute("SELECT id FROM doctors WHERE name=?", (doctor_name,))
        doctor = cursor.fetchone()
        if not doctor:
            messagebox.showerror("Doctor Not Found", "The selected doctor could not be found.")
            return

        patient_id = self.user[0]
        doctor_id = doctor[0]

        # Insert the appointment into the database
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)", (patient_id, doctor_id, date, time))
        conn.commit()
        messagebox.showinfo("Appointment Confirmed", f"Your appointment with {doctor_name} on {date} at {time} is confirmed.")
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def view_appointments_screen(self, parent):
        label = ttk.Label(parent, text="Your Appointments", font=("Arial", 20), foreground="#1a73e8")
        label.pack(pady=20)

        # Fetch user's appointments
        if self.user[3] == 'patient':
            cursor.execute('''
                SELECT a.id, d.name, a.date, a.time
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.patient_id = ?
            ''', (self.user[0],))
        elif self.user[3] == 'doctor':
            cursor.execute('''
                SELECT a.id, u.username, a.date, a.time
                FROM appointments a
                JOIN users u ON a.patient_id = u.id
                WHERE a.doctor_id = ?
            ''', (self.user[0],))

        appointments = cursor.fetchall()

        # Create a Treeview widget to display the appointments
        columns = ("ID", "Doctor/Patient", "Date", "Time")
        self.appointments_tree = ttk.Treeview(parent, columns=columns, show="headings")
        self.appointments_tree.heading("ID", text="ID")
        self.appointments_tree.heading("Doctor/Patient", text="Doctor/Patient")
        self.appointments_tree.heading("Date", text="Date")
        self.appointments_tree.heading("Time", text="Time")

        self.appointments_tree.pack(fill="both", expand=True)

        for appointment in appointments:
            self.appointments_tree.insert("", tk.END, values=appointment)

        # Button to cancel appointment (for patients only)
        if self.user[3] == 'patient':
            cancel_button = tb.Button(parent, text="Cancel Appointment", style="danger.TButton", bootstyle="rounded", command=self.cancel_appointment)
            cancel_button.pack(pady=20)

    def cancel_appointment(self):
        selected_item = self.appointments_tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an appointment to cancel.")
            return

        appointment_id = self.appointments_tree.item(selected_item, 'values')[0]
        confirm = messagebox.askyesno("Cancel Confirmation", "Are you sure you want to cancel this appointment?")
        if confirm:
        # Ask for the cancellation reason
            reason = simpledialog.askstring("Cancellation Reason", "Please enter the reason for cancellation:")
            if not reason:
                messagebox.showerror("Input Error", "You must provide a reason for canceling the appointment.")
                return

        # Fetch appointment details
            cursor.execute('''
                SELECT a.date, a.time, d.name, d.id, u.username
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                JOIN users u ON a.patient_id = u.id
                WHERE a.id = ?
            ''', (appointment_id,))
            appointment_details = cursor.fetchone()
            if not appointment_details:
                messagebox.showerror("Error", "Could not retrieve appointment details.")
                return
        
            appointment_date, appointment_time, doctor_name, doctor_id, patient_name = appointment_details

        # Delete the appointment
            cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            conn.commit()
            self.appointments_tree.delete(selected_item)
            messagebox.showinfo("Appointment Cancelled", "Your appointment has been cancelled.")

        # Create notification message
            notification_message = (
                f"Patient {patient_name} has cancelled the appointment on {appointment_date} at {appointment_time}.\n"
                f"Reason: {reason}"
            )
        
        # Insert notification into the database for the doctor
            cursor.execute(
                "INSERT INTO notifications (doctor_id, message, date, time) VALUES (?, ?, ?, ?)",
                (doctor_id, notification_message, appointment_date, appointment_time)
            )
            conn.commit()

        # Inform the patient that the doctor will be notified
            messagebox.showinfo("Notification Sent", f"A cancellation notification has been sent to Dr. {doctor_name}.")


    def send_cancellation_notification(self, doctor_name, patient_name, appointment_date, appointment_time, reason):
        # Simulating sending a notification
        if self.user[3] == 'patient':
            messagebox.showinfo(
                "Notification Sent",
                f"Notification sent to Dr. {doctor_name}:\n"
                f"Patient {patient_name} has cancelled the appointment on {appointment_date} at {appointment_time}.\n"
                f"Reason: {reason}"
            )
        elif self.user[3] == 'doctor':
            messagebox.showinfo(
                "Notification Sent",
                f"Notification sent to Patient {patient_name}:\n"
                f"Dr. {doctor_name} has cancelled the appointment on {appointment_date} at {appointment_time}.\n"
                f"Reason: {reason}"
            )
    def view_notifications(self, parent):
        label = ttk.Label(parent, text="Your Notifications", font=("Arial", 20), foreground="#1a73e8")
        label.pack(pady=20)

        cursor.execute("SELECT message, date, time FROM notifications WHERE doctor_id=?", (self.user[0],))
        notifications = cursor.fetchall()

        if not notifications:
            label = ttk.Label(parent, text="No Notifications Found", font=("Arial", 12), foreground="#001F3F")
            label.pack(pady=5)
            return

        for notification in notifications:
            notification_message = f"On {notification[1]} at {notification[2]}: {notification[0]}"
            notification_label = ttk.Label(parent, text=notification_message, font=("Arial", 12), foreground="#001F3F")
            notification_label.pack(pady=5)



    def logout(self):
        self.user = None
        self.login_screen()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

# Run the application
if __name__ == "__main__":
    app = DoctorAppointmentApp()
    app.mainloop()

