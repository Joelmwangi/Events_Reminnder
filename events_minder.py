import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime
import time
import threading

# Database Setup
def init_db():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, date TEXT, description TEXT, email TEXT)''')
    conn.commit()
    conn.close()

# Functions
def show_frame(frame):
    frame.tkraise()

def register_user():
    name = entry_name.get()
    email = entry_email.get()
    password = entry_password.get()
    if name and email and password:
        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully!")
        entry_name.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_password.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please fill all fields")

def login_user():
    email = entry_login_email.get()
    password = entry_login_password.get()
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        messagebox.showinfo("Success", "Login successful!")
        global logged_in_user
        logged_in_user = email
        show_frame(event_frame)
        view_events()
    else:
        messagebox.showerror("Error", "Invalid credentials")

def add_event():
    title = entry_event.get()
    date = entry_date.get()
    description = entry_description.get("1.0", tk.END).strip()
    if title and date and description and logged_in_user:
        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, date, description, email) VALUES (?, ?, ?, ?)", (title, date, description, logged_in_user))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Event added successfully!")
        entry_event.delete(0, tk.END)
        entry_date.delete(0, tk.END)
        entry_description.delete("1.0", tk.END)
        view_events()
    else:
        messagebox.showerror("Error", "Please fill all fields or log in first")

def delete_event():
    selected_item = listbox_events.selection()
    if selected_item:
        item = listbox_events.item(selected_item, 'values')
        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE title=? AND date=? AND email=?", (item[0], item[1], logged_in_user))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Event deleted successfully!")
        view_events()

def edit_event():
    selected_item = listbox_events.selection()
    if selected_item:
        item = listbox_events.item(selected_item, 'values')
        new_title = entry_event.get()
        new_date = entry_date.get()
        new_description = entry_description.get("1.0", tk.END).strip()
        if new_title and new_date and new_description:
            conn = sqlite3.connect("events.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE events SET title=?, date=?, description=? WHERE title=? AND date=? AND email=?", 
                           (new_title, new_date, new_description, item[0], item[1], logged_in_user))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Event updated successfully!")
            view_events()
        else:
            messagebox.showerror("Error", "Please fill all fields")

def view_events():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY date")
    records = cursor.fetchall()
    conn.close()
    listbox_events.delete(*listbox_events.get_children())
    for row in records:
        listbox_events.insert("", tk.END, values=(row[1], row[2], row[3], row[4]))



def notify_user():
    while True:
        time.sleep(30) 
        if logged_in_user:
            conn = sqlite3.connect("events.db")
            cursor = conn.cursor()
                      
            today = datetime.datetime.now().strftime("%Y-%m-%d")
               
            cursor.execute("SELECT title, date, description FROM events WHERE date >= ? ORDER BY date LIMIT 1", (today,))
            event = cursor.fetchone()
            
            conn.close()

            if event:
                title, date, description = event
                messagebox.showinfo("Upcoming Event", f"Title: {title}\nDate: {date}\nDetails: {description}")


def logout():
    global logged_in_user
    logged_in_user = None
    show_frame(login_frame)

# Start Notification Thread
notification_thread = threading.Thread(target=notify_user, daemon=True)
notification_thread.start()

# GUI Setup
root = tk.Tk()
root.title("Event Minder")
root.geometry("600x750")
root.configure(bg="#e6f2ff")

# Frames for different pages
login_frame = tk.Frame(root, bg="#e6f2ff")
signup_frame = tk.Frame(root, bg="#e6f2ff")
event_frame = tk.Frame(root, bg="#e6f2ff")
for frame in (login_frame, signup_frame, event_frame):
    frame.grid(row=0, column=0, sticky='news')

# Signup Page
tk.Label(signup_frame, text="Sign Up", font=("Arial", 16, "bold"), bg="#e6f2ff").pack(pady=10)
tk.Label(signup_frame, text="Name:", bg="#e6f2ff").pack()
entry_name = tk.Entry(signup_frame)
entry_name.pack()

tk.Label(signup_frame, text="Email:", bg="#e6f2ff").pack()
entry_email = tk.Entry(signup_frame)
entry_email.pack()

tk.Label(signup_frame, text="Password:", bg="#e6f2ff").pack()
entry_password = tk.Entry(signup_frame, show="*")
entry_password.pack()

tk.Button(signup_frame, text="Register", command=register_user, bg="#4CAF50", fg="white").pack(pady=5)
tk.Button(signup_frame, text="Go to Login", command=lambda: show_frame(login_frame)).pack()

# Login Page
tk.Label(login_frame, text="Login", font=("Arial", 16, "bold"), bg="#e6f2ff").pack(pady=10)
tk.Label(login_frame, text="Email:", bg="#e6f2ff").pack()
entry_login_email = tk.Entry(login_frame)
entry_login_email.pack()

tk.Label(login_frame, text="Password:", bg="#e6f2ff").pack()
entry_login_password = tk.Entry(login_frame, show="*")
entry_login_password.pack()

tk.Button(login_frame, text="Login", command=login_user, bg="#2196F3", fg="white").pack(pady=5)
tk.Button(login_frame, text="Go to Signup", command=lambda: show_frame(signup_frame)).pack()

# Event Management Page
tk.Label(event_frame, text="Event Management", font=("Arial", 16, "bold"), bg="#e6f2ff").pack(pady=10)
tk.Label(event_frame, text="Event Title:", bg="#e6f2ff").pack()
entry_event = tk.Entry(event_frame)
entry_event.pack()

tk.Label(event_frame, text="Event Date (YYYY-MM-DD):", bg="#e6f2ff").pack()
entry_date = tk.Entry(event_frame)
entry_date.pack()

tk.Label(event_frame, text="Event Description:", bg="#e6f2ff").pack()
entry_description = tk.Text(event_frame, height=4, width=50)
entry_description.pack()

tk.Button(event_frame, text="Add Event", command=add_event, bg="#4CAF50", fg="white").pack(pady=5)
tk.Button(event_frame, text="Edit Event", command=edit_event, bg="#FFC107", fg="black").pack(pady=5)
tk.Button(event_frame, text="Delete Event", command=delete_event, bg="#f44336", fg="white").pack(pady=5)
tk.Button(event_frame, text="Logout", command=logout, bg="#FF5722", fg="white").pack(pady=5)

columns = ("Title", "Date", "Description", "Posted By")
listbox_events = ttk.Treeview(event_frame, columns=columns, show="headings")
for col in columns:
    listbox_events.heading(col, text=col)
listbox_events.pack()

# Initialize Database
init_db()
show_frame(login_frame)
logged_in_user = None

# Run Application
root.mainloop()
