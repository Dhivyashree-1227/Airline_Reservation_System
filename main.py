import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

def query_db(query, params=(), fetchone=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def execute_db(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airline Reservation System - Login")
        self.root.geometry("400x300")

        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.login).pack(pady=10)
        tk.Button(root, text="Sign Up", command=self.open_signup).pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        user = query_db(
            "SELECT username, role FROM users WHERE username=:1 AND password=:2",
            (username, password),
            fetchone=True,
        )
        if user:
            role = user[1]
            messagebox.showinfo("Success", f"Welcome {username}! Role: {role}")
            self.root.destroy()
            if role == "admin":
                AdminDashboard(username)
            else:
                UserDashboard(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_signup(self):
        self.root.destroy()
        SignUpApp(tk.Tk())

class SignUpApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airline Reservation System - Sign Up")
        self.root.geometry("400x350")

        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Label(root, text="Confirm Password:").pack(pady=5)
        self.confirm_password_entry = tk.Entry(root, show="*")
        self.confirm_password_entry.pack()

        tk.Label(root, text="Role (admin/user):").pack(pady=5)
        self.role_entry = tk.Entry(root)
        self.role_entry.pack()

        tk.Button(root, text="Register", command=self.register).pack(pady=10)
        tk.Button(root, text="Back to Login", command=self.back_to_login).pack()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        role = self.role_entry.get().strip().lower()

        if not (username and password and confirm_password and role):
            messagebox.showerror("Error", "All fields are required")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if role not in ("admin", "user"):
            messagebox.showerror("Error", "Role must be 'admin' or 'user'")
            return

        exists = query_db("SELECT username FROM users WHERE username=:1", (username,), True)
        if exists:
            messagebox.showerror("Error", "Username already exists")
            return

        execute_db(
            "INSERT INTO users (user_id, username, password, role) VALUES (users_seq.NEXTVAL, :1, :2, :3)",
            (username, password, role),
        )
        messagebox.showinfo("Success", "User registered successfully!")
        self.root.destroy()
        LoginApp(tk.Tk())

    def back_to_login(self):
        self.root.destroy()
        LoginApp(tk.Tk())

class AdminDashboard:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Admin Dashboard")
        self.root.geometry("900x600")

        tk.Label(self.root, text=f"Welcome Admin: {username}", font=("Arial", 16)).pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Manage Flights", width=15, command=self.show_manage_flights).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Manage Routes", width=15, command=self.show_manage_routes).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Manage Users", width=15, command=self.show_manage_users).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Manage Bookings", width=15, command=self.show_manage_bookings).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Logout", width=15, command=self.root.destroy).grid(row=0, column=4, padx=5)

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.show_manage_flights()
        self.root.mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_manage_flights(self):
        self.clear_content()
        columns = ("Flight ID", "Origin", "Destination", "Departure", "Arrival", "Price")
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_flights()

        form_frame = tk.Frame(self.content_frame)
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Origin:").grid(row=0, column=0, padx=5, pady=5)
        self.origin_entry = tk.Entry(form_frame)
        self.origin_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Destination:").grid(row=1, column=0, padx=5, pady=5)
        self.destination_entry = tk.Entry(form_frame)
        self.destination_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Departure (YYYY-MM-DD HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        self.departure_entry = tk.Entry(form_frame)
        self.departure_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Arrival (YYYY-MM-DD HH:MM):").grid(row=3, column=0, padx=5, pady=5)
        self.arrival_entry = tk.Entry(form_frame)
        self.arrival_entry.grid(row=3, column=1)

        tk.Label(form_frame, text="Price:").grid(row=4, column=0, padx=5, pady=5)
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=4, column=1)

        tk.Button(form_frame, text="Add Flight", command=self.add_flight).grid(row=5, column=0, columnspan=2, pady=10)

    def load_flights(self):
        flights = query_db("""
            SELECT flight_id, origin, destination, TO_CHAR(departure_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(arrival_time, 'YYYY-MM-DD HH24:MI'), price
            FROM flights
            ORDER BY departure_time
        """)
        self.tree.delete(*self.tree.get_children())
        for flight in flights:
            self.tree.insert("", "end", values=flight)

    def add_flight(self):
        origin = self.origin_entry.get().strip()
        destination = self.destination_entry.get().strip()
        departure = self.departure_entry.get().strip()
        arrival = self.arrival_entry.get().strip()
        price = self.price_entry.get().strip()

        if not (origin and destination and departure and arrival and price):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            price_val = float(price)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return

        try:
            execute_db(
                "INSERT INTO flights (flight_id, origin, destination, departure_time, arrival_time, price) VALUES (flight_seq.NEXTVAL, :1, :2, TO_TIMESTAMP(:3, 'YYYY-MM-DD HH24:MI'), TO_TIMESTAMP(:4, 'YYYY-MM-DD HH24:MI'), :5)",
                (origin, destination, departure, arrival, price_val),
            )
            messagebox.showinfo("Success", "Flight added successfully!")
            self.load_flights()
            self.origin_entry.delete(0, tk.END)
            self.destination_entry.delete(0, tk.END)
            self.departure_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add flight: {e}")

    def show_manage_routes(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Manage Routes - Coming Soon", font=("Arial", 14)).pack(pady=50)

    def show_manage_users(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Manage Users", font=("Arial", 14)).pack(pady=10)

        columns = ("User ID", "Username", "Role")
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_users()

        tk.Button(self.content_frame, text="Delete Selected User", command=self.delete_user).pack(pady=10)

    def load_users(self):
        users = query_db("SELECT user_id, username, role FROM users ORDER BY user_id")
        self.tree.delete(*self.tree.get_children())
        for user in users:
            self.tree.insert("", "end", values=user)

    def delete_user(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No user selected")
            return
        user = self.tree.item(selected, "values")
        user_id = user[0]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete user ID {user_id}?"):
            try:
                execute_db("DELETE FROM users WHERE user_id = :1", (user_id,))
                messagebox.showinfo("Success", "User deleted")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

    def show_manage_bookings(self):
        self.clear_content()
        tk.Label(self.content_frame, text="All Bookings", font=("Arial", 14)).pack(pady=10)

        columns = ("Booking ID", "Username", "Origin", "Destination", "Departure", "Arrival", "Price")
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        bookings = query_db("""
            SELECT b.booking_id, u.username, f.origin, f.destination,
                   TO_CHAR(f.departure_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(f.arrival_time, 'YYYY-MM-DD HH24:MI'), f.price
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN flights f ON b.flight_id = f.flight_id
            ORDER BY f.departure_time
        """)
        self.tree.delete(*self.tree.get_children())
        for booking in bookings:
            self.tree.insert("", "end", values=booking)

        tk.Button(self.content_frame, text="Cancel Selected Booking", command=self.cancel_booking).pack(pady=10)

    def cancel_booking(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No booking selected")
            return
        booking = self.tree.item(selected, 'values')
        booking_id = booking[0]

        if messagebox.askyesno("Confirm", f"Cancel booking ID {booking_id}?"):
            try:
                execute_db("DELETE FROM bookings WHERE booking_id = :1", (booking_id,))
                messagebox.showinfo("Success", "Booking cancelled successfully")
                self.show_manage_bookings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel booking: {e}")

class UserDashboard:
    def __init__(self, username):
        self.username = username
        self.user_id = self.get_user_id(username)

        self.root = tk.Tk()
        self.root.title("User Dashboard")
        self.root.geometry("800x600")

        self.create_main_screen()

        self.root.mainloop()

    def create_main_screen(self):
        # Clear previous contents
        self.clear_window()

        tk.Label(self.root, text=f"Welcome User: {self.username}", font=("Arial", 16)).pack(pady=10)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Origin:").grid(row=0, column=0, padx=5)
        self.origin_entry = tk.Entry(search_frame)
        self.origin_entry.grid(row=0, column=1)

        tk.Label(search_frame, text="Destination:").grid(row=0, column=2, padx=5)
        self.destination_entry = tk.Entry(search_frame)
        self.destination_entry.grid(row=0, column=3)

        tk.Label(search_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=4, padx=5)
        self.date_entry = tk.Entry(search_frame)
        self.date_entry.grid(row=0, column=5)

        tk.Button(search_frame, text="Search Flights", command=self.search_flights).grid(row=0, column=6, padx=10)

        columns = ("Flight ID", "Origin", "Destination", "Departure", "Arrival", "Price")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=20)

        tk.Button(self.root, text="Book Selected Flight", command=self.book_flight).pack(pady=10)
        tk.Button(self.root, text="View My Bookings", command=self.view_bookings).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.destroy).pack(pady=10)

    def get_user_id(self, username):
        user = query_db("SELECT user_id FROM users WHERE username=:1", (username,), fetchone=True)
        return user[0] if user else None

    def search_flights(self):
        origin = self.origin_entry.get().strip() or None
        destination = self.destination_entry.get().strip() or None
        date = self.date_entry.get().strip() or None

        query = """
            SELECT flight_id, origin, destination, TO_CHAR(departure_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(arrival_time, 'YYYY-MM-DD HH24:MI'), price
            FROM flights
            WHERE (:origin1 IS NULL OR origin = :origin2)
              AND (:destination1 IS NULL OR destination = :destination2)
              AND (:date1 IS NULL OR TRUNC(departure_time) = TO_DATE(:date2, 'YYYY-MM-DD'))
            ORDER BY departure_time
        """
        flights = query_db(query, {'origin1': origin, 'origin2': origin, 'destination1': destination, 
                                    'destination2': destination, 'date1': date, 'date2': date})
        self.tree.delete(*self.tree.get_children())
        for flight in flights:
            self.tree.insert("", "end", values=flight)

    def book_flight(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No flight selected")
            return
        flight = self.tree.item(selected, 'values')
        flight_id = flight[0]

        try:
            execute_db(
                "INSERT INTO bookings (booking_id, user_id, flight_id) VALUES (bookings_seq.NEXTVAL, :1, :2)",
                (self.user_id, flight_id),
            )
            messagebox.showinfo("Success", "Flight booked successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to book flight: {e}")

    def view_bookings(self):
        self.clear_window()
        tk.Label(self.root, text="My Bookings", font=("Arial", 14)).pack(pady=5)

        # Add Back Button
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=5)

        columns = ("Booking ID", "Origin", "Destination", "Departure", "Arrival", "Price")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(pady=10)

        bookings = query_db(
            """
            SELECT b.booking_id, f.origin, f.destination,
                   TO_CHAR(f.departure_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(f.arrival_time, 'YYYY-MM-DD HH24:MI'),
                   f.price
            FROM bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE b.user_id = :user_id
            ORDER BY f.departure_time
            """,
            {'user_id': self.user_id},
        )

        for booking in bookings:
            self.tree.insert("", "end", values=booking)

        tk.Button(self.root, text="Cancel Selected Booking", command=self.cancel_booking).pack(pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def cancel_booking(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No booking selected")
            return
        booking = self.tree.item(selected, 'values')
        booking_id = booking[0]

        if messagebox.askyesno("Confirm", f"Cancel booking ID {booking_id}?"):
            try:
                execute_db("DELETE FROM bookings WHERE booking_id = :1", (booking_id,))
                messagebox.showinfo("Success", "Booking cancelled successfully")
                self.view_bookings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel booking: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
