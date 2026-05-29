import os
import pymongo
from pymongo import MongoClient

class Database:
    def __init__(self, uri=None):
        if uri is None:
            # MongoDB Atlas connection string
            uri = "mongodb+srv://bishwaprakashrout2007_db_user:qh6b6J7qR8wLWnRw@student-management.qrzvdcw.mongodb.net/?appName=student-management"
        
        self.client = MongoClient(uri)
        self.db = self.client["student_management"]
        
        # Collections
        self.admin_col = self.db["admin"]
        self.students_col = self.db["students"]
        self.counters_col = self.db["counters"]
        
        self.create_tables()
        self.migrate_from_sqlite()

    def create_tables(self):
        # Create default admin if not exists
        if self.admin_col.count_documents({"username": "bishwa"}) == 0:
            self.admin_col.insert_one({"username": "bishwa", "password": "admin"})
            
        # Ensure sequence counter document exists
        if self.counters_col.count_documents({"_id": "student_id"}) == 0:
            self.counters_col.insert_one({"_id": "student_id", "sequence_value": 0})

    def get_next_sequence_value(self, sequence_name):
        sequence_document = self.counters_col.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {'sequence_value': 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        return sequence_document['sequence_value']

    def migrate_from_sqlite(self):
        sqlite_path = 'student_management.db'
        if not os.path.exists(sqlite_path):
            sqlite_path = os.path.join('student_management', 'student_management.db')
            if not os.path.exists(sqlite_path):
                return
        
        try:
            import sqlite3
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            
            # Check if students table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
            if not cursor.fetchone():
                conn.close()
                return
            
            # Fetch all students
            cursor.execute('SELECT * FROM students')
            sqlite_students = cursor.fetchall()
            
            # Fetch all admins
            cursor.execute('SELECT * FROM admin')
            sqlite_admins = cursor.fetchall()
            
            print(f"Starting migration from SQLite to MongoDB...")
            
            # Migrate admins
            for admin in sqlite_admins:
                username = admin[1]
                password = admin[2]
                if self.admin_col.count_documents({"username": username}) == 0:
                    self.admin_col.insert_one({"username": username, "password": password})
            
            # Migrate students
            max_id = 0
            for student in sqlite_students:
                s_id = student[0]
                full_name = student[1]
                class_name = student[2]
                email = student[3]
                mobile = student[4]
                address = student[5]
                gender = student[6]
                dob = student[7]
                profile_image = student[8]
                
                if self.students_col.count_documents({"id": s_id}) == 0:
                    self.students_col.insert_one({
                        "id": s_id,
                        "full_name": full_name,
                        "class_name": class_name,
                        "email": email,
                        "mobile": mobile,
                        "address": address,
                        "gender": gender,
                        "dob": dob,
                        "profile_image": profile_image
                    })
                if s_id > max_id:
                    max_id = s_id
            
            # Update counter to max_id
            if max_id > 0:
                self.counters_col.update_one(
                    {"_id": "student_id"},
                    {"$set": {"sequence_value": max_id}},
                    upsert=True
                )
            
            cursor.close()
            conn.close()
            del cursor
            del conn
            import gc
            gc.collect()
            # Backup SQLite file so we don't migrate again
            backup_path = sqlite_path + ".bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(sqlite_path, backup_path)
            print(f"Successfully migrated {len(sqlite_students)} students and {len(sqlite_admins)} admins from SQLite to MongoDB.")
        except Exception as e:
            print(f"Error during migration from SQLite: {e}")

    def check_login(self, username, password):
        try:
            user = self.admin_col.find_one({"username": username, "password": password})
            return user is not None
        except Exception as e:
            print(f"Error checking login: {e}")
            return False

    def insert_student(self, full_name, class_name, email, mobile, address, gender, dob, profile_image=""):
        try:
            student_id = self.get_next_sequence_value("student_id")
            student_doc = {
                "id": student_id,
                "full_name": full_name,
                "class_name": class_name,
                "email": email,
                "mobile": mobile,
                "address": address,
                "gender": gender,
                "dob": dob,
                "profile_image": profile_image
            }
            self.students_col.insert_one(student_doc)
            return True
        except Exception as e:
            print(f"Error inserting student: {e}")
            return False

    def fetch_all_students(self):
        try:
            students = self.students_col.find()
            rows = []
            for s in students:
                rows.append((
                    s.get("id"),
                    s.get("full_name"),
                    s.get("class_name"),
                    s.get("email"),
                    s.get("mobile"),
                    s.get("address"),
                    s.get("gender"),
                    s.get("dob"),
                    s.get("profile_image")
                ))
            return rows
        except Exception as e:
            print(f"Error fetching students: {e}")
            return []

    def update_student(self, id, full_name, class_name, email, mobile, address, gender, dob, profile_image=""):
        try:
            id_int = int(id)
            self.students_col.update_one(
                {"id": id_int},
                {"$set": {
                    "full_name": full_name,
                    "class_name": class_name,
                    "email": email,
                    "mobile": mobile,
                    "address": address,
                    "gender": gender,
                    "dob": dob,
                    "profile_image": profile_image
                }}
            )
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False

    def delete_student(self, id):
        try:
            id_int = int(id)
            self.students_col.delete_one({"id": id_int})
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False

    def search_student(self, search_by, search_term):
        try:
            column_map = {
                "Name": "full_name",
                "Class": "class_name",
                "Mobile": "mobile",
                "ID": "id"
            }
            db_column = column_map.get(search_by, "full_name")
            
            if db_column == "id":
                try:
                    val = int(search_term)
                    query = {"id": val}
                except ValueError:
                    query = {"id": -1}
            else:
                # Regex search for substring (case-insensitive)
                query = {db_column: {"$regex": search_term, "$options": "i"}}
                
            students = self.students_col.find(query)
            rows = []
            for s in students:
                rows.append((
                    s.get("id"),
                    s.get("full_name"),
                    s.get("class_name"),
                    s.get("email"),
                    s.get("mobile"),
                    s.get("address"),
                    s.get("gender"),
                    s.get("dob"),
                    s.get("profile_image")
                ))
            return rows
        except Exception as e:
            print(f"Error searching student: {e}")
            return []

    def get_stats(self):
        stats = {}
        try:
            stats['total_students'] = self.students_col.count_documents({})
            
            distinct_classes = self.students_col.distinct("class_name")
            stats['total_classes'] = len(distinct_classes)
            
            recent = self.students_col.find().sort("id", pymongo.DESCENDING).limit(5)
            recent_rows = []
            for s in recent:
                recent_rows.append((
                    s.get("id"),
                    s.get("full_name"),
                    s.get("class_name"),
                    s.get("email"),
                    s.get("mobile"),
                    s.get("address"),
                    s.get("gender"),
                    s.get("dob"),
                    s.get("profile_image")
                ))
            stats['recent_students'] = recent_rows
            
            pipeline = [
                {"$group": {"_id": "$class_name", "count": {"$sum": 1}}}
            ]
            class_dist = self.students_col.aggregate(pipeline)
            stats['class_distribution'] = [(item["_id"], item["count"]) for item in class_dist]
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            stats['total_students'] = 0
            stats['total_classes'] = 0
            stats['recent_students'] = []
            stats['class_distribution'] = []
            
        return stats
