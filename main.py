import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------------- DATABASE ----------------

def connect_db():
    return sqlite3.connect("labguard.db")


def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            quantity INTEGER,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            equipment_name TEXT,
            booking_date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_name TEXT,
            description TEXT,
            service_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("LabGuard - Laboratory Management System")
root.geometry("1150x700")
root.minsize(950, 600)
BROWN = "#604735"
CREAM = "#F5EEDC"
BABY_BLUE = "#B9DDF2"
WHITE = "#FFFFFF"
TEXT = "#3D3028"
root.configure(bg=CREAM)

# Table and dropdown styling
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    background=WHITE,
    foreground=TEXT,
    fieldbackground=WHITE,
    rowheight=30,
    font=("Arial", 10)
)
style.configure(
    "Treeview.Heading",
    background=BROWN,
    foreground=CREAM,
    font=("Arial", 10, "bold"),
    padding=8
)
style.map(
    "Treeview",
    background=[("selected", BABY_BLUE)],
    foreground=[("selected", BROWN)]
)
style.configure("TCombobox", padding=5)

sidebar = tk.Frame(root, bg=BROWN, width=200)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main_area = tk.Frame(root, bg=CREAM)
main_area.pack(side="right", fill="both", expand=True)


def clear_page():
    for widget in main_area.winfo_children():
        widget.destroy()


def heading(title):
    tk.Label(
        main_area,
        text=title,
        font=("Arial", 25, "bold"),
        bg=CREAM,
        fg=BROWN
    ).pack(anchor="w", padx=30, pady=(25, 15))

    tk.Frame(
        main_area,
        bg=BABY_BLUE,
        height=4,
        width=75
    ).pack(anchor="w", padx=30, pady=(0, 15))


def create_table(columns):
    tree = ttk.Treeview(
        main_area,
        columns=columns,
        show="headings",
        height=15
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    return tree


# ---------------- DASHBOARD ----------------

def show_dashboard():
    clear_page()
    heading("Dashboard")

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM equipment")
    equipment = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings")
    bookings = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM maintenance")
    maintenance = cur.fetchone()[0]

    cur.execute(
        "SELECT SUM(quantity) FROM equipment WHERE status='Available'"
    )
    available = cur.fetchone()[0] or 0

    conn.close()

    stats = [
        ("Total Equipment", equipment),
        ("Available Units", available),
        ("Total Bookings", bookings),
        ("Maintenance Records", maintenance)
    ]

    for name, value in stats:
        card = tk.Frame(main_area, bg=WHITE, padx=25, pady=20)
        card.pack(fill="x", padx=30, pady=8)

        tk.Label(
            card,
            text=name,
            font=("Arial", 12),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            card,
            text=str(value),
            font=("Arial", 20, "bold"),
            fg=BROWN,
            bg=WHITE
        ).pack(anchor="w")


# ---------------- EQUIPMENT MANAGEMENT ----------------

def show_equipment():
    clear_page()
    heading("Equipment Management")

    columns = ("ID", "Name", "Category", "Quantity", "Status")
    tree = create_table(columns)

    def load_data():
        tree.delete(*tree.get_children())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM equipment")

        for row in cur.fetchall():
            tree.insert("", "end", values=row)

        conn.close()

    def add_equipment():
        window = tk.Toplevel(root)
        window.title("Add Equipment")
        window.geometry("350x350")

        tk.Label(window, text="Equipment Name").pack(pady=5)
        name = tk.Entry(window, width=30)
        name.pack()

        tk.Label(window, text="Category").pack(pady=5)
        category = tk.Entry(window, width=30)
        category.pack()

        tk.Label(window, text="Quantity").pack(pady=5)
        quantity = tk.Entry(window, width=30)
        quantity.pack()

        tk.Label(window, text="Status").pack(pady=5)
        status = ttk.Combobox(
            window,
            values=["Available", "Under Maintenance", "Unavailable"],
            state="readonly"
        )
        status.set("Available")
        status.pack()

        def save():
            try:
                n = name.get().strip()
                c = category.get().strip()
                q = int(quantity.get())

                if not n or not c or q <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Enter valid equipment details and quantity."
                )
                return

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO equipment
                (name, category, quantity, status)
                VALUES (?, ?, ?, ?)
            """, (n, c, q, status.get()))

            conn.commit()
            conn.close()

            window.destroy()
            load_data()
            messagebox.showinfo("Success", "Equipment added!")

        tk.Button(
            window,
            text="Save Equipment",
            command=save,
            bg=BABY_BLUE,
            fg=BROWN,
            activebackground="#A4CDE8",
            activeforeground=BROWN,
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)


    def delete_equipment():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select equipment first.")
            return

        equipment_id = tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm", "Delete this equipment?"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM equipment WHERE id=?", (equipment_id,))
            conn.commit()
            conn.close()
            load_data()

    buttons = tk.Frame(main_area, bg=CREAM)
    buttons.pack(pady=10)

    tk.Button(
        buttons, text="Add Equipment",
        command=add_equipment, bg=BABY_BLUE, fg=BROWN, activebackground="#A4CDE8", activeforeground=BROWN, width=18
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="Delete Equipment",
        command=delete_equipment, bg=BROWN, fg=CREAM, width=18
    ).pack(side="left", padx=5)

    load_data()


# ---------------- BOOKING MANAGEMENT ----------------

def show_bookings():
    clear_page()
    heading("Booking Management")

    columns = ("ID", "Student", "Equipment", "Booking Date")
    tree = create_table(columns)

    def load_data():
        tree.delete(*tree.get_children())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings")

        for row in cur.fetchall():
            tree.insert("", "end", values=row)

        conn.close()

    def add_booking():
        window = tk.Toplevel(root)
        window.title("New Booking")
        window.geometry("350x300")

        tk.Label(window, text="Student Name").pack(pady=5)
        student = tk.Entry(window, width=30)
        student.pack()

        tk.Label(window, text="Select Equipment").pack(pady=5)
        equipment = ttk.Combobox(window, state="readonly", width=27)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM equipment WHERE status='Available'"
        )
        equipment["values"] = [row[0] for row in cur.fetchall()]
        conn.close()

        equipment.pack()

        tk.Label(window, text="Booking Date (YYYY-MM-DD)").pack(pady=5)
        date = tk.Entry(window, width=30)
        date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date.pack()

        def save():
            s = student.get().strip()
            e = equipment.get()
            d = date.get().strip()

            if not s or not e or not d:
                messagebox.showwarning("Warning", "Fill all fields.")
                return

            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Enter date as YYYY-MM-DD."
                )
                return

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO bookings
                (student_name, equipment_name, booking_date)
                VALUES (?, ?, ?)
            """, (s, e, d))

            conn.commit()
            conn.close()

            window.destroy()
            load_data()
            messagebox.showinfo("Success", "Booking added!")

        tk.Button(
            window, text="Save Booking",
            command=save, bg=BABY_BLUE, fg=BROWN,
            activebackground="#A4CDE8", activeforeground=BROWN
        ).pack(pady=20)

    def delete_booking():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a booking first.")
            return

        booking_id = tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm", "Delete this booking?"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
            conn.commit()
            conn.close()
            load_data()

    buttons = tk.Frame(main_area, bg=CREAM)
    buttons.pack(pady=10)

    tk.Button(
        buttons, text="New Booking",
        command=add_booking, bg=BABY_BLUE, fg=BROWN, activebackground="#A4CDE8", activeforeground=BROWN, width=18
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="Delete Booking",
        command=delete_booking, bg=BROWN, fg=CREAM, width=18
    ).pack(side="left", padx=5)

    load_data()


# ---------------- MAINTENANCE MANAGEMENT ----------------

def show_maintenance():
    clear_page()
    heading("Maintenance Management")

    columns = ("ID", "Equipment", "Description", "Date", "Status")
    tree = create_table(columns)

    def load_data():
        tree.delete(*tree.get_children())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM maintenance")

        for row in cur.fetchall():
            tree.insert("", "end", values=row)

        conn.close()

    def add_record():
        window = tk.Toplevel(root)
        window.title("Add Maintenance")
        window.geometry("350x350")

        tk.Label(window, text="Equipment").pack(pady=5)
        equipment = ttk.Combobox(window, state="readonly", width=27)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM equipment")
        equipment["values"] = [row[0] for row in cur.fetchall()]
        conn.close()

        equipment.pack()

        tk.Label(window, text="Description").pack(pady=5)
        description = tk.Entry(window, width=30)
        description.pack()

        tk.Label(window, text="Service Date (YYYY-MM-DD)").pack(pady=5)
        date = tk.Entry(window, width=30)
        date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date.pack()

        tk.Label(window, text="Status").pack(pady=5)
        status = ttk.Combobox(
            window,
            values=["Pending", "In Progress", "Completed"],
            state="readonly"
        )
        status.set("Pending")
        status.pack()

        def save():
            e = equipment.get()
            d = description.get().strip()
            dt = date.get().strip()

            if not e or not d or not dt:
                messagebox.showwarning("Warning", "Fill all fields.")
                return

            try:
                datetime.strptime(dt, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Enter date as YYYY-MM-DD."
                )
                return

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO maintenance
                (equipment_name, description, service_date, status)
                VALUES (?, ?, ?, ?)
            """, (e, d, dt, status.get()))

            conn.commit()
            conn.close()

            window.destroy()
            load_data()
            messagebox.showinfo("Success", "Record added!")

        tk.Button(
            window, text="Save Record",
            command=save, bg=BABY_BLUE, fg=BROWN,
            activebackground="#A4CDE8", activeforeground=BROWN
        ).pack(pady=20)

    def update_status():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a record first.")
            return

        record = tree.item(selected[0])["values"]
        record_id = record[0]

        window = tk.Toplevel(root)
        window.title("Update Status")
        window.geometry("300x180")

        tk.Label(window, text="Select New Status").pack(pady=10)

        status = ttk.Combobox(
            window,
            values=["Pending", "In Progress", "Completed"],
            state="readonly"
        )
        status.set(record[4])
        status.pack(pady=10)

        def save():
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE maintenance SET status=? WHERE id=?",
                (status.get(), record_id)
            )
            conn.commit()
            conn.close()

            window.destroy()
            load_data()

        tk.Button(
            window, text="Update",
            command=save, bg=BABY_BLUE, fg=BROWN,
            activebackground="#A4CDE8", activeforeground=BROWN
        ).pack(pady=10)

    def delete_record():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a record first.")
            return

        record_id = tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm", "Delete this record?"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM maintenance WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            load_data()

    buttons = tk.Frame(main_area, bg=CREAM)
    buttons.pack(pady=10)

    tk.Button(
        buttons, text="Add Record",
        command=add_record, bg=BABY_BLUE, fg=BROWN, activebackground="#A4CDE8", activeforeground=BROWN, width=15
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="Update Status",
        command=update_status, bg=BROWN, fg=CREAM, width=15
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="Delete Record",
        command=delete_record, bg=BROWN, fg=CREAM, width=15
    ).pack(side="left", padx=5)

    load_data()


# ---------------- REPORTS ----------------

def show_reports():
    clear_page()
    heading("Laboratory Reports")

    conn = connect_db()
    cur = conn.cursor()

    queries = [
        ("Total Equipment Records", "SELECT COUNT(*) FROM equipment"),
        ("Total Bookings", "SELECT COUNT(*) FROM bookings"),
        ("Total Maintenance Records", "SELECT COUNT(*) FROM maintenance"),
        ("Available Equipment Units",
         "SELECT SUM(quantity) FROM equipment WHERE status='Available'"),
        ("Pending Maintenance",
         "SELECT COUNT(*) FROM maintenance WHERE status='Pending'"),
        ("Completed Maintenance",
         "SELECT COUNT(*) FROM maintenance WHERE status='Completed'")
    ]

    for title, query in queries:
        cur.execute(query)
        result = cur.fetchone()[0] or 0

        tk.Label(
            main_area,
            text=title + " : " + str(result),
            font=("Arial", 13),
            bg=WHITE,
            fg=TEXT,
            padx=15,
            pady=12
        ).pack(fill="x", padx=30, pady=7)

    conn.close()


# ---------------- NAVIGATION ----------------

tk.Label(
    sidebar,
    text="LABGUARD",
    font=("Arial", 20, "bold"),
    bg=BROWN,
    fg=CREAM
).pack(pady=30)

buttons = [
    ("Dashboard", show_dashboard),
    ("Equipment", show_equipment),
    ("Bookings", show_bookings),
    ("Maintenance", show_maintenance),
    ("Reports", show_reports)
]


for name, command in buttons:
    tk.Button(
        sidebar,
        text="   " + name,
        command=command,
        font=("Arial", 11, "bold"),
        bg=BROWN,
        fg=CREAM,
        activebackground=BABY_BLUE,
        activeforeground=BROWN,
        relief="flat",
        anchor="w",
        width=22,
        pady=14,
        cursor="hand2"
    ).pack(pady=4, padx=10)


# ---------------- START APPLICATION ----------------

create_tables()
show_dashboard()
root.mainloop()
