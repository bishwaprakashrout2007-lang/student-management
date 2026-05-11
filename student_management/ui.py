import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import csv
import os
import shutil
from database import Database

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        self.db = Database()
        self.current_theme = "superhero" # dark theme default
        self.style = tb.Style(theme=self.current_theme)

        self.current_user = None
        
        self.show_login_screen()

    def show_login_screen(self):
        # Clear existing
        for widget in self.root.winfo_children():
            widget.destroy()

        self.login_frame = tb.Frame(self.root, padding=40)
        self.login_frame.pack(expand=True)

        title = tb.Label(self.login_frame, text="Admin Login", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        tb.Label(self.login_frame, text="Username").pack(anchor="w")
        self.username_var = tk.StringVar()
        tb.Entry(self.login_frame, textvariable=self.username_var, width=30).pack(pady=5)

        tb.Label(self.login_frame, text="Password").pack(anchor="w", pady=(10, 0))
        self.password_var = tk.StringVar()
        tb.Entry(self.login_frame, textvariable=self.password_var, show="*", width=30).pack(pady=5)

        tb.Button(self.login_frame, text="Login", command=self.login, bootstyle=SUCCESS, width=28).pack(pady=20)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if self.db.check_login(username, password):
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials", parent=self.root)

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Layout: Sidebar (left), Content (right)
        self.sidebar = tb.Frame(self.root, width=200, style="dark")
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content_frame = tb.Frame(self.root, padding=10)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self.setup_sidebar()
        self.show_overview()

    def setup_sidebar(self):
        tb.Label(self.sidebar, text="SMS", font=("Helvetica", 20, "bold"), style="inverse-dark").pack(pady=20)
        
        tb.Button(self.sidebar, text="Overview", command=self.show_overview, bootstyle="link-inverse").pack(fill=X, pady=5, padx=10)
        tb.Button(self.sidebar, text="Manage Students", command=self.show_manage_students, bootstyle="link-inverse").pack(fill=X, pady=5, padx=10)
        tb.Button(self.sidebar, text="Toggle Theme", command=self.toggle_theme, bootstyle="link-inverse").pack(fill=X, pady=5, padx=10)
        tb.Button(self.sidebar, text="Logout", command=self.logout, bootstyle="danger-outline").pack(side=BOTTOM, fill=X, pady=20, padx=10)

    def toggle_theme(self):
        self.current_theme = "lumen" if self.current_theme == "superhero" else "superhero"
        self.style.theme_use(self.current_theme)

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_overview(self):
        self.clear_content()

        header = tb.Label(self.content_frame, text="Dashboard Overview", font=("Helvetica", 18, "bold"))
        header.pack(anchor="w", pady=10)

        stats = self.db.get_stats()

        # Cards Frame
        cards_frame = tb.Frame(self.content_frame)
        cards_frame.pack(fill=X, pady=10)

        self.create_card(cards_frame, "Total Students", str(stats['total_students']), INFO, 0)
        self.create_card(cards_frame, "Total Classes", str(stats['total_classes']), SUCCESS, 1)

        # Charts and Recent Activity
        lower_frame = tb.Frame(self.content_frame)
        lower_frame.pack(fill=BOTH, expand=True, pady=10)

        # Chart
        chart_frame = tb.Labelframe(lower_frame, text="Class Distribution", padding=10)
        chart_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

        if stats['class_distribution']:
            fig = Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)
            classes = [x[0] for x in stats['class_distribution']]
            counts = [x[1] for x in stats['class_distribution']]
            ax.pie(counts, labels=classes, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Set background transparent to match theme better
            fig.patch.set_alpha(0.0)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            tb.Label(chart_frame, text="No data available.").pack(pady=20)

        # Recent Students
        recent_frame = tb.Labelframe(lower_frame, text="Recent Students", padding=10)
        recent_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        for student in stats['recent_students']:
            tb.Label(recent_frame, text=f"• {student[1]} (Class {student[2]})").pack(anchor="w", pady=2)

    def create_card(self, parent, title, value, style_color, column):
        card = tb.Frame(parent, bootstyle=style_color, padding=20)
        card.grid(row=0, column=column, padx=10, sticky="nsew")
        parent.columnconfigure(column, weight=1)
        
        tb.Label(card, text=title, font=("Helvetica", 12), bootstyle=f"inverse-{style_color}").pack()
        tb.Label(card, text=value, font=("Helvetica", 24, "bold"), bootstyle=f"inverse-{style_color}").pack()

    def show_manage_students(self):
        self.clear_content()

        header_frame = tb.Frame(self.content_frame)
        header_frame.pack(fill=X, pady=10)

        tb.Label(header_frame, text="Manage Students", font=("Helvetica", 18, "bold")).pack(side=LEFT)
        
        tb.Button(header_frame, text="Export to CSV", command=self.export_csv, bootstyle="info-outline").pack(side=RIGHT, padx=5)

        # Form Area
        self.form_frame = tb.Labelframe(self.content_frame, text="Student Details", padding=10)
        self.form_frame.pack(fill=X, pady=10)

        # Variables
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_class = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_mobile = tk.StringVar()
        self.var_address = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_dob = tk.StringVar()
        self.var_image_path = tk.StringVar()

        # Row 1
        tb.Label(self.form_frame, text="Full Name*").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tb.Entry(self.form_frame, textvariable=self.var_name).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(self.form_frame, text="Class*").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tb.Combobox(self.form_frame, textvariable=self.var_class, values=["12th", "B.Sc", "B.Tech", "BCA", "BBA", "MCA", "MBA"]).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Row 2
        tb.Label(self.form_frame, text="Email*").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tb.Entry(self.form_frame, textvariable=self.var_email).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(self.form_frame, text="Mobile*").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        tb.Entry(self.form_frame, textvariable=self.var_mobile).grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Row 3
        tb.Label(self.form_frame, text="Gender*").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tb.Combobox(self.form_frame, textvariable=self.var_gender, values=["Male", "Female", "Other"]).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(self.form_frame, text="DOB (YYYY-MM-DD)*").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        tb.Entry(self.form_frame, textvariable=self.var_dob).grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Row 4
        tb.Label(self.form_frame, text="Address").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        tb.Entry(self.form_frame, textvariable=self.var_address).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(self.form_frame, text="Profile Image").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        img_frame = tb.Frame(self.form_frame)
        img_frame.grid(row=3, column=3, sticky="ew")
        tb.Entry(img_frame, textvariable=self.var_image_path, state="readonly", width=15).pack(side=LEFT, fill=X, expand=True)
        tb.Button(img_frame, text="Browse", command=self.browse_image).pack(side=RIGHT, padx=2)

        for i in range(4):
            self.form_frame.columnconfigure(i, weight=1)

        # Action Buttons
        action_frame = tb.Frame(self.form_frame)
        action_frame.grid(row=4, column=0, columnspan=4, pady=10)

        tb.Button(action_frame, text="Add", command=self.add_student, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        tb.Button(action_frame, text="Update", command=self.update_student, bootstyle=WARNING).pack(side=LEFT, padx=5)
        tb.Button(action_frame, text="Delete", command=self.delete_student, bootstyle=DANGER).pack(side=LEFT, padx=5)
        tb.Button(action_frame, text="Clear", command=self.clear_form, bootstyle=SECONDARY).pack(side=LEFT, padx=5)

        # Search Area
        search_frame = tb.Frame(self.content_frame)
        search_frame.pack(fill=X, pady=5)
        
        self.var_search_by = tk.StringVar(value="Name")
        tb.Combobox(search_frame, textvariable=self.var_search_by, values=["Name", "Class", "Mobile", "ID"], width=15, state="readonly").pack(side=LEFT, padx=5)
        
        self.var_search_term = tk.StringVar()
        tb.Entry(search_frame, textvariable=self.var_search_term).pack(side=LEFT, fill=X, expand=True, padx=5)
        
        tb.Button(search_frame, text="Search", command=self.search_data, bootstyle=INFO).pack(side=LEFT, padx=5)
        tb.Button(search_frame, text="Show All", command=self.load_data, bootstyle=SECONDARY).pack(side=LEFT, padx=5)

        # Data Grid
        columns = ("ID", "Name", "Class", "Email", "Mobile", "Gender", "DOB")
        self.tree = tb.Treeview(self.content_frame, columns=columns, show="headings", bootstyle=INFO)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=150)

        self.tree.pack(fill=BOTH, expand=True, pady=5)
        self.tree.bind("<ButtonRelease-1>", self.get_cursor_row)

        self.load_data()

    def browse_image(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select Image", filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("all files", "*.*")))
        if filename:
            self.var_image_path.set(filename)

    def validate_form(self):
        if not self.var_name.get() or not self.var_class.get() or not self.var_email.get() or not self.var_mobile.get() or not self.var_gender.get() or not self.var_dob.get():
            messagebox.showerror("Error", "All fields marked with * are required!")
            return False
            
        # Email validation
        email_regex = r'^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(email_regex, self.var_email.get()):
            messagebox.showerror("Error", "Invalid Email Address!")
            return False

        # Mobile validation (10 digits)
        if not self.var_mobile.get().isdigit() or len(self.var_mobile.get()) < 10:
            messagebox.showerror("Error", "Mobile number must be at least 10 digits long!")
            return False

        return True

    def process_image(self):
        src_path = self.var_image_path.get()
        if src_path and os.path.exists(src_path):
            # If it's already in our assets folder, just return the relative path
            if "assets/profiles" in src_path:
                return src_path

            ext = src_path.split('.')[-1]
            dest_dir = "assets/profiles"
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            # Simple unique name based on time
            import time
            dest_name = f"profile_{int(time.time())}.{ext}"
            dest_path = os.path.join(dest_dir, dest_name)
            
            try:
                shutil.copy(src_path, dest_path)
                return dest_path
            except Exception as e:
                print(f"Failed to copy image: {e}")
                return ""
        return ""

    def add_student(self):
        if self.validate_form():
            img_path = self.process_image()
            res = self.db.insert_student(
                self.var_name.get(), self.var_class.get(), self.var_email.get(),
                self.var_mobile.get(), self.var_address.get(), self.var_gender.get(),
                self.var_dob.get(), img_path
            )
            if res:
                messagebox.showinfo("Success", "Student Record Added!")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to add record.")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.fetch_all_students()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[6], row[7]))

    def clear_form(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_class.set("")
        self.var_email.set("")
        self.var_mobile.set("")
        self.var_address.set("")
        self.var_gender.set("")
        self.var_dob.set("")
        self.var_image_path.set("")

    def get_cursor_row(self, ev):
        cursor_row = self.tree.focus()
        contents = self.tree.item(cursor_row)
        row = contents['values']
        if row:
            self.var_id.set(row[0])
            self.var_name.set(row[1])
            self.var_class.set(row[2])
            self.var_email.set(row[3])
            self.var_mobile.set(row[4])
            self.var_gender.set(row[5])
            self.var_dob.set(row[6])
            
            # Need to fetch the full record to get address and image path
            all_data = self.db.search_student("ID", str(row[0]))
            if all_data:
                self.var_address.set(all_data[0][5])
                self.var_image_path.set(all_data[0][8])

    def update_student(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Please select a student from the list to update")
            return

        if self.validate_form():
            img_path = self.process_image()
            res = self.db.update_student(
                self.var_id.get(), self.var_name.get(), self.var_class.get(),
                self.var_email.get(), self.var_mobile.get(), self.var_address.get(),
                self.var_gender.get(), self.var_dob.get(), img_path
            )
            if res:
                messagebox.showinfo("Success", "Student Record Updated!")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to update record.")

    def delete_student(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Please select a student from the list to delete")
            return
            
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this student?")
        if confirm:
            res = self.db.delete_student(self.var_id.get())
            if res:
                messagebox.showinfo("Success", "Student Record Deleted!")
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete record.")

    def search_data(self):
        term = self.var_search_term.get()
        by = self.var_search_by.get()
        
        if not term:
            messagebox.showerror("Error", "Please enter a search term")
            return
            
        rows = self.db.search_student(by, term)
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[6], row[7]))

    def export_csv(self):
        rows = []
        for child in self.tree.get_children():
            rows.append(self.tree.item(child)["values"])
            
        if not rows:
            messagebox.showinfo("Info", "No data to export")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Class", "Email", "Mobile", "Gender", "DOB"])
                    writer.writerows(rows)
                messagebox.showinfo("Success", f"Data exported successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
