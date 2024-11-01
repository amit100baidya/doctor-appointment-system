import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import hashlib

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

conn.commit()

# Main Application Class
class DoctorAppointmentApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Doctor Appointment System")
        self.geometry("800x500")
        self.user = None  # Currently logged in user
        self.login_screen()

    def login_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Login", font=("Arial", 24))
        label.pack(pady=20)

        # Username and password fields
        username_label = ttk.Label(self, text="Username:")
        username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        password_label = ttk.Label(self, text="Password:")
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.pack(pady=20)

        register_button = ttk.Button(self, text="Register", command=self.register_screen)
        register_button.pack(pady=10)

    def register_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Register", font=("Arial", 24))
        label.pack(pady=20)

        # Username and password fields
        username_label = ttk.Label(self, text="Username:")
        username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        password_label = ttk.Label(self, text="Password:")
        password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        role_label = ttk.Label(self, text="Role:")
        role_label.pack(pady=5)
        self.role_var = tk.StringVar(value="patient")
        role_menu = ttk.OptionMenu(self, self.role_var, "patient", "doctor")
        role_menu.pack(pady=5)

        speciality_label = ttk.Label(self, text="Speciality:")
        speciality_label.pack(pady=5)
        self.speciality_entry = ttk.Entry(self)
        self.speciality_entry.pack(pady=5)

        # Register button
        register_button = ttk.Button(self, text="Register", command=self.register)
        register_button.pack(pady=20)

        back_button = ttk.Button(self, text="Back to Login", command=self.login_screen)
        back_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = hash_password(self.password_entry.get())

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
        label = ttk.Label(self, text="Home", font=("Arial", 24))
        label.pack(pady=20)

        if self.user[3] == 'patient':
            book_button = ttk.Button(self, text="Book Appointment", command=self.book_appointment_screen)
            book_button.pack(pady=10)

            view_button = ttk.Button(self, text="View Appointments", command=self.view_appointments_screen)
            view_button.pack(pady=10)
        elif self.user[3] == 'doctor':
            view_button = ttk.Button(self, text="View Your Appointments", command=self.view_appointments_screen)
            view_button.pack(pady=10)

        logout_button = ttk.Button(self, text="Logout", command=self.logout)
        logout_button.pack(pady=20)

    def book_appointment_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Book an Appointment", font=("Arial", 20))
        label.pack(pady=20)

        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()

        if not doctors:
            messagebox.showerror("No Doctors Available", "There are no doctors available at the moment. Please try again later.")
            self.home_screen()
            return

        doctor_label = ttk.Label(self, text="Select Doctor:")
        doctor_label.pack(pady=5)
        self.doctor_var = tk.StringVar(value=f"{doctors[0][1]} - {doctors[0][2]}")
        doctor_menu = ttk.OptionMenu(self, self.doctor_var, *[f"{doctor[1]} - {doctor[2]}" for doctor in doctors])
        doctor_menu.pack(pady=5)

        date_label = ttk.Label(self, text="Select Date (YYYY-MM-DD):")
        date_label.pack(pady=5)
        self.date_entry = ttk.Entry(self)
        self.date_entry.pack(pady=5)

        time_label = ttk.Label(self, text="Select Time (HH:MM AM/PM):")
        time_label.pack(pady=5)
        self.time_entry = ttk.Entry(self)
        self.time_entry.pack(pady=5)

        submit_button = ttk.Button(self, text="Confirm Appointment", command=self.confirm_appointment)
        submit_button.pack(pady=20)

        back_button = ttk.Button(self, text="Back", command=self.home_screen)
        back_button.pack(pady=10)

    def confirm_appointment(self):
        doctor_name_speciality = self.doctor_var.get()
        doctor_name = doctor_name_speciality.split(" - ")[0]
        date = self.date_entry.get()
        time = self.time_entry.get()

        cursor.execute("SELECT id FROM doctors WHERE name=?", (doctor_name,))
        doctor_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)",
                       (self.user[0], doctor_id, date, time))
        conn.commit()

        messagebox.showinfo("Appointment Confirmed", f"Appointment with {doctor_name} on {date} at {time} confirmed.")
        self.home_screen()

    def view_appointments_screen(self):
        self.clear_frame()
        label = ttk.Label(self, text="Your Appointments", font=("Arial", 20))
        label.pack(pady=20)

        listbox = tk.Listbox(self, width=80, height=15)
        listbox.pack(pady=20)

        if self.user[3] == 'patient':
            # Patients see their own appointments
            cursor.execute(
                "SELECT d.name, a.date, a.time FROM appointments a "
                "JOIN doctors d ON a.doctor_id = d.id "
                "WHERE a.patient_id=?",
                (self.user[0],)
            )
        elif self.user[3] == 'doctor':
            # Doctors see appointments booked with them
            cursor.execute(
                "SELECT u.username, a.date, a.time FROM appointments a "
                "JOIN users u ON a.patient_id = u.id "
                "WHERE a.doctor_id=?",
                (self.user[0],)
            )

        appointments = cursor.fetchall()

        if not appointments:
            listbox.insert(tk.END, "No appointments found.")
        else:
            for appointment in appointments:
                listbox.insert(tk.END, f"{appointment[0]} - {appointment[1]} at {appointment[2]}")

        back_button = ttk.Button(self, text="Back", command=self.home_screen)
        back_button.pack(pady=10)

    def logout(self):
        self.user = None
        self.login_screen()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = DoctorAppointmentApp()
    app.mainloop()