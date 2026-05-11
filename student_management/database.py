import sqlite3
import os

class Database:
    def __init__(self, db_path='student_management.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Admin table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # Check if admin exists, if not create default
        self.cursor.execute('SELECT * FROM admin WHERE username="bishwa"')
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO admin (username, password) VALUES ("bishwa", "admin")')

        # Students table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                email TEXT NOT NULL,
                mobile TEXT NOT NULL,
                address TEXT NOT NULL,
                gender TEXT NOT NULL,
                dob TEXT NOT NULL,
                profile_image TEXT
            )
        ''')
        self.conn.commit()

    def check_login(self, username, password):
        self.cursor.execute('SELECT * FROM admin WHERE username=? AND password=?', (username, password))
        return self.cursor.fetchone() is not None

    def insert_student(self, full_name, class_name, email, mobile, address, gender, dob, profile_image=""):
        try:
            self.cursor.execute('''
                INSERT INTO students (full_name, class_name, email, mobile, address, gender, dob, profile_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, class_name, email, mobile, address, gender, dob, profile_image))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting student: {e}")
            return False

    def fetch_all_students(self):
        self.cursor.execute('SELECT * FROM students')
        return self.cursor.fetchall()

    def update_student(self, id, full_name, class_name, email, mobile, address, gender, dob, profile_image=""):
        try:
            self.cursor.execute('''
                UPDATE students 
                SET full_name=?, class_name=?, email=?, mobile=?, address=?, gender=?, dob=?, profile_image=?
                WHERE id=?
            ''', (full_name, class_name, email, mobile, address, gender, dob, profile_image, id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating student: {e}")
            return False

    def delete_student(self, id):
        try:
            self.cursor.execute('DELETE FROM students WHERE id=?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting student: {e}")
            return False

    def search_student(self, search_by, search_term):
        try:
            # Map user friendly search fields to db columns
            column_map = {
                "Name": "full_name",
                "Class": "class_name",
                "Mobile": "mobile",
                "ID": "id"
            }
            db_column = column_map.get(search_by, "full_name")
            query = f"SELECT * FROM students WHERE {db_column} LIKE ?"
            self.cursor.execute(query, ('%' + search_term + '%',))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching student: {e}")
            return []

    def get_stats(self):
        stats = {}
        # Total students
        self.cursor.execute('SELECT COUNT(*) FROM students')
        stats['total_students'] = self.cursor.fetchone()[0]
        
        # Total classes
        self.cursor.execute('SELECT COUNT(DISTINCT class_name) FROM students')
        stats['total_classes'] = self.cursor.fetchone()[0]
        
        # Recent additions (last 5)
        self.cursor.execute('SELECT * FROM students ORDER BY id DESC LIMIT 5')
        stats['recent_students'] = self.cursor.fetchall()
        
        # Class distribution for charts
        self.cursor.execute('SELECT class_name, COUNT(*) FROM students GROUP BY class_name')
        stats['class_distribution'] = self.cursor.fetchall()

        return stats

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
