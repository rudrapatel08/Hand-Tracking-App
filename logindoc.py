import sqlite3
from tkinter import *
import tkinter as tk
import re
import hashlib
from tkinter import messagebox

class DatabaseManager:
    def __init__(self):
        # Establish connection to the SQLite database
        self.connection = sqlite3.connect("user_details.db")  # Create a cursor
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (username TEXT PRIMARY KEY, password TEXT)''')
        self.connection.commit()

    def __del__(self):
        # Close the database connection when the object is deleted
        self.connection.close()

    def register_user(self, username, password):
        hashed_password = self.hash_password(password)  # Hash the password before storing it
        try:
            # Insert the username and hashed password into the 'users' table
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            # If the username already exists, return False
            return False

    def verify_login(self, username, password):
        hashed_password = self.hash_password(password)  # Hash the provided password
        # Retrieve a row from the 'users' table where the username and password match
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        return self.cursor.fetchone() is not None  # Check if any matching row exists

    def hash_password(self, password):
        # Hash the password using SHA-256 algorithm
        return hashlib.sha256(password.encode()).hexdigest()

class Login(DatabaseManager):
    def __init__(self, master):
        # Initialise the parent class
        super().__init__()
        self.master = master
        self.master.title("Hand Tracking App")

        # Welcome screen
        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.screenSize = self.master.geometry("300x200") # Window size
        # Create a label for the welcome message
        self.welcome_txt = Label(text="Welcome!", bg="grey", width=300, height=2, font=("Calibre", 13))
        self.welcome_txt.pack()
        # Create a login button
        self.login_btn = Button(text="Login", width=30, height=2, command=self.login)
        self.login_btn.pack()
        # Create a sign-up button
        self.sign_up_btn = Button(text="Sign Up", width=30, height=2, command=self.sign_up)
        self.sign_up_btn.pack()

    def sign_up(self):
        # Sign Up screen
        self.sign_up_screen = Toplevel(self.master)
        self.sign_up_screen.title("Sign Up")
        self.SUS_size = self.sign_up_screen.geometry("300x200")  #
        self.SSU_text = Label(self.sign_up_screen, text="Sign Up", bg="grey", width=30, height=2, font=("Calibre", 13))
        self.SSU_text.pack()
        self.username = StringVar()
        self.password = StringVar()
        self.create_sign_up_widgets()

    def create_sign_up_widgets(self):
        Label(self.sign_up_screen, text="Please enter details below").pack()
        Label(self.sign_up_screen, text="").pack()

        # Username entry
        Label(self.sign_up_screen, text="Username * ").pack()
        self.username_entry = Entry(self.sign_up_screen, textvariable=self.username)
        self.username_entry.pack()

        # Password entry
        Label(self.sign_up_screen, text="Password * ").pack()
        self.password_entry = Entry(self.sign_up_screen, textvariable=self.password, show="*")
        self.password_entry.pack()

        # Clear button
        self.clear_btn = Button(self.sign_up_screen, text="Clear", command=self.clear_entries)
        self.clear_btn.pack()

        # Register button
        Label(self.sign_up_screen, text="").pack()
        Button(self.sign_up_screen, text="Register", width=10, height=1, command=self.register_user_action).pack()
        Label(self.sign_up_screen, text="").pack()

    def validate_username(self, username):
        # Validate the username so it only has alphabetic characters.
        return bool(re.match("^[a-zA-Z]+$", username))

    def validate_password(self, password):
        # Validate the password, so it has at least one letter and one digit.
        return bool(re.match("(?=.*[a-zA-Z])(?=.*\\d).+", password))

    def register_user_action(self):
        # Get username and password from entry fields
        self.usernameInfo = self.username.get()
        self.passwordInfo = self.password.get()

        # Validate username format
        if not self.validate_username(self.usernameInfo):
            messagebox.showerror("Error", "Username must contain only letters")
            return

        # Validate password format
        if not self.validate_password(self.passwordInfo):
            messagebox.showerror("Error", "Password must contain at least one letter and one number")
            return

        # Register the user
        if self.register_user(self.usernameInfo, self.passwordInfo):
            Label(self.sign_up_screen, text="Registration Success", fg="green", font=("calibri", 11)).pack()
        else:
            Label(self.sign_up_screen, text="Username already exists", fg="red", font=("calibri", 11)).pack()

        # Clear entry fields
        self.clear_entries()

    def clear_entries(self):
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)

    def login(self):
        # Login screen
        self.login_screen = Toplevel(self.master)
        self.login_screen.title("Login")

        self.LSSize = self.login_screen.geometry("300x250")
        self.LStext = Label(self.login_screen, text="Login", bg="grey", width=30, height=2, font=("Calibre", 13))
        self.LStext.pack()

        self.username_login = StringVar()
        self.password_login = StringVar()
        # Usernam-Password Boxes with inputs
        Label(self.login_screen, text="Username").pack()
        self.username_login_entry = Entry(self.login_screen, textvariable=self.username_login)
        self.username_login_entry.pack()

        Label(self.login_screen, text="Password").pack()
        self.password_login_entry = Entry(self.login_screen, textvariable=self.password_login, show="*")
        self.password_login_entry.pack()

        # login button
        Button(self.login_screen, text="Login", width=10, height=1, command=self.verify_login_action).pack()

    def verify_login_action(self):
        username = self.username_login.get()
        password = self.password_login.get()

        if self.verify_login(username, password):
            self.show_login_success()
        else:
            self.show_login_failure()

    def show_login_success(self):
        self.login_screen.destroy()
        messagebox.showinfo("Login", "Login successful")
        # Go to next page

    def show_login_failure(self):
        messagebox.showerror("Login", "Invalid username or password")

if __name__ == '__main__':
    root = tk.Tk()
    root.iconbitmap("robot_1.ico")
    mainApp = Login(root)
    root.mainloop()