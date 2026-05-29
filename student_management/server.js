const express = require('express');
const { MongoClient, ReturnDocument } = require('mongodb');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Configure body parsers
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// MongoDB connection settings
const MONGO_URI = process.env.MONGO_URI || "mongodb+srv://bishwaprakashrout2007_db_user:qh6b6J7qR8wLWnRw@student-management.qrzvdcw.mongodb.net/?appName=student-management";
let db, studentsCol, adminCol, countersCol;

// Setup profile uploads folder
const uploadDir = path.join(__dirname, 'public', 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname);
    cb(null, 'profile-' + uniqueSuffix + ext);
  }
});
const upload = multer({ storage: storage });

// Connect to MongoDB Atlas
async function initDB() {
  try {
    const client = new MongoClient(MONGO_URI);
    await client.connect();
    console.log("Connected successfully to MongoDB Atlas");
    db = client.db("student_management");
    
    studentsCol = db.collection("students");
    adminCol = db.collection("admin");
    countersCol = db.collection("counters");
    
    // Seed default admin if missing
    const adminCount = await adminCol.countDocuments({ username: "bishwa" });
    if (adminCount === 0) {
      await adminCol.insertOne({ username: "bishwa", password: "admin" });
      console.log("Seeded default admin user: bishwa");
    }
    
    // Seed counters sequence if missing
    const counterDoc = await countersCol.findOne({ _id: "student_id" });
    if (!counterDoc) {
      await countersCol.insertOne({ _id: "student_id", sequence_value: 0 });
      console.log("Seeded student_id sequence counter");
    }
  } catch (err) {
    console.error("MongoDB Connection Failure:", err);
    process.exit(1);
  }
}

// Helper to increment auto-increment ID
async function getNextSequenceValue(sequenceName) {
  const sequenceDoc = await countersCol.findOneAndUpdate(
    { _id: sequenceName },
    { $inc: { sequence_value: 1 } },
    { upsert: true, returnDocument: ReturnDocument.AFTER }
  );
  return sequenceDoc.sequence_value;
}

// Serve static web app assets
app.use(express.static(path.join(__dirname, 'public')));

// AUTHENTICATION API
app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ success: false, message: "Username and password required" });
    }
    const admin = await adminCol.findOne({ username, password });
    if (admin) {
      return res.json({ success: true, username: admin.username });
    } else {
      return res.status(401).json({ success: false, message: "Invalid credentials" });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// GET STUDENTS / SEARCH STUDENTS API
app.get('/api/students', async (req, res) => {
  try {
    const { search_by, search_term } = req.query;
    let query = {};
    
    if (search_by && search_term) {
      const dbColumnMap = {
        "Name": "full_name",
        "Class": "class_name",
        "Mobile": "mobile",
        "ID": "id"
      };
      
      const dbCol = dbColumnMap[search_by] || "full_name";
      if (dbCol === "id") {
        const idInt = parseInt(search_term, 10);
        query = { id: isNaN(idInt) ? -1 : idInt };
      } else {
        query = { [dbCol]: { $regex: search_term, $options: 'i' } };
      }
    }
    
    const students = await studentsCol.find(query).toArray();
    res.json({ success: true, students });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// ADD STUDENT API
app.post('/api/students', upload.single('profile_image'), async (req, res) => {
  try {
    const { full_name, class_name, email, mobile, address, gender, dob } = req.body;
    if (!full_name || !class_name || !email || !mobile || !gender || !dob) {
      return res.status(400).json({ success: false, message: "Required fields are missing!" });
    }
    
    const studentId = await getNextSequenceValue("student_id");
    const imagePath = req.file ? `/uploads/${req.file.filename}` : '';
    
    const newStudent = {
      id: studentId,
      full_name,
      class_name,
      email,
      mobile,
      address: address || '',
      gender,
      dob,
      profile_image: imagePath
    };
    
    await studentsCol.insertOne(newStudent);
    res.status(201).json({ success: true, student: newStudent });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// UPDATE STUDENT API
app.put('/api/students/:id', upload.single('profile_image'), async (req, res) => {
  try {
    const studentId = parseInt(req.params.id, 10);
    if (isNaN(studentId)) {
      return res.status(400).json({ success: false, message: "Invalid Student ID" });
    }
    
    const { full_name, class_name, email, mobile, address, gender, dob } = req.body;
    const updateData = {
      full_name,
      class_name,
      email,
      mobile,
      address,
      gender,
      dob
    };
    
    if (req.file) {
      updateData.profile_image = `/uploads/${req.file.filename}`;
    }
    
    const result = await studentsCol.updateOne({ id: studentId }, { $set: updateData });
    if (result.matchedCount === 0) {
      return res.status(404).json({ success: false, message: "Student record not found" });
    }
    
    res.json({ success: true, message: "Student record updated" });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// DELETE STUDENT API
app.delete('/api/students/:id', async (req, res) => {
  try {
    const studentId = parseInt(req.params.id, 10);
    if (isNaN(studentId)) {
      return res.status(400).json({ success: false, message: "Invalid Student ID" });
    }
    
    const result = await studentsCol.deleteOne({ id: studentId });
    if (result.deletedCount === 0) {
      return res.status(404).json({ success: false, message: "Student record not found" });
    }
    
    res.json({ success: true, message: "Student record deleted successfully" });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// STATS API
app.get('/api/stats', async (req, res) => {
  try {
    const totalStudents = await studentsCol.countDocuments({});
    
    const distinctClasses = await studentsCol.distinct("class_name");
    const totalClasses = distinctClasses.length;
    
    const recentStudents = await studentsCol.find().sort({ id: -1 }).limit(5).toArray();
    
    const classDistribution = await studentsCol.aggregate([
      { $group: { _id: "$class_name", count: { $sum: 1 } } }
    ]).toArray();
    
    res.json({
      success: true,
      stats: {
        total_students: totalStudents,
        total_classes: totalClasses,
        recent_students: recentStudents,
        class_distribution: classDistribution.map(item => ({ class_name: item._id, count: item.count }))
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Start application after connecting database
initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
  });
});
