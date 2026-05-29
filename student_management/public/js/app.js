// App State Variables
let currentAdmin = null;
let currentView = 'overview';
let classChartInstance = null;

// Initialize app when DOM loads
document.addEventListener('DOMContentLoaded', () => {
  // Check if admin is saved in localStorage (persistent session)
  const savedAdmin = localStorage.getItem('sms_admin');
  if (savedAdmin) {
    loginSuccess(savedAdmin);
  }

  // Setup event listeners
  document.getElementById('login-form').addEventListener('submit', handleLogin);
  document.getElementById('student-form').addEventListener('submit', handleStudentSubmit);
});

// TOAST NOTIFICATIONS
function showToast(message, isError = false) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show ${isError ? 'toast-error' : 'toast-success'}`;
  
  setTimeout(() => {
    toast.className = 'toast';
  }, 3000);
}

// AUTHENTICATION
async function handleLogin(e) {
  e.preventDefault();
  const usernameInput = document.getElementById('login-username').value;
  const passwordInput = document.getElementById('login-password').value;

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: usernameInput, password: passwordInput })
    });

    const data = await response.json();
    if (data.success) {
      loginSuccess(data.username);
      showToast("Signed in successfully!");
    } else {
      showToast(data.message || "Invalid login credentials", true);
    }
  } catch (error) {
    showToast("Network error. Please try again.", true);
  }
}

function loginSuccess(username) {
  currentAdmin = username;
  localStorage.setItem('sms_admin', username);
  document.getElementById('admin-name').textContent = username;
  
  // Toggle screens
  document.getElementById('login-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');
  
  // Load dashboard overview data
  switchView('overview');
}

function logout() {
  currentAdmin = null;
  localStorage.removeItem('sms_admin');
  document.getElementById('login-screen').classList.add('active');
  document.getElementById('app-screen').classList.remove('active');
  
  // Clear forms
  document.getElementById('login-form').reset();
  showToast("Logged out successfully");
}

// NAVIGATION
function switchView(viewName) {
  currentView = viewName;
  
  // Toggle navigation links active classes
  document.getElementById('nav-overview').classList.toggle('active', viewName === 'overview');
  document.getElementById('nav-manage').classList.toggle('active', viewName === 'manage');
  
  // Toggle panels
  document.getElementById('view-overview').classList.toggle('active', viewName === 'overview');
  document.getElementById('view-manage').classList.toggle('active', viewName === 'manage');
  
  // Update titles
  const title = document.getElementById('view-title');
  const subtitle = document.getElementById('view-subtitle');
  
  if (viewName === 'overview') {
    title.textContent = "Dashboard Overview";
    subtitle.textContent = "Live summary of student enrollment and statistics";
    loadDashboardStats();
  } else {
    title.textContent = "Manage Students";
    subtitle.textContent = "Add, update, search, or remove student profiles";
    loadAllStudents();
  }
}

// DASHBOARD OVERVIEW DATA
async function loadDashboardStats() {
  try {
    const response = await fetch('/api/stats');
    const data = await response.json();
    
    if (data.success) {
      const stats = data.stats;
      
      // Update numbers
      document.getElementById('stat-students-count').textContent = stats.total_students;
      document.getElementById('stat-classes-count').textContent = stats.total_classes;
      
      // Render recent activity list
      const recentList = document.getElementById('recent-list');
      recentList.innerHTML = '';
      
      if (stats.recent_students.length === 0) {
        recentList.innerHTML = `<li class="recent-item">No students added yet.</li>`;
      } else {
        stats.recent_students.forEach(student => {
          const initials = student.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
          const avatarHTML = student.profile_image 
            ? `<img src="${student.profile_image}" class="recent-avatar" alt="${student.full_name}">`
            : `<div class="recent-avatar-placeholder">${initials}</div>`;
            
          const li = document.createElement('li');
          li.className = 'recent-item';
          li.innerHTML = `
            ${avatarHTML}
            <div class="recent-details">
              <h4>${student.full_name}</h4>
              <p>Class ${student.class_name} • ID: ${student.id}</p>
            </div>
          `;
          recentList.appendChild(li);
        });
      }
      
      // Render Chart
      renderChart(stats.class_distribution);
    }
  } catch (error) {
    showToast("Failed to load dashboard metrics", true);
  }
}

function renderChart(distribution) {
  const ctx = document.getElementById('classChart').getContext('2d');
  
  // Destroy existing chart instance to avoid rendering overlaps
  if (classChartInstance) {
    classChartInstance.destroy();
  }
  
  if (!distribution || distribution.length === 0) {
    // Show empty message
    return;
  }
  
  const labels = distribution.map(item => item.class_name);
  const data = distribution.map(item => item.count);
  
  classChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          '#6366f1', // Indigo
          '#10b981', // Emerald
          '#0ea5e9', // Sky
          '#f59e0b', // Amber
          '#ec4899', // Pink
          '#8b5cf6', // Violet
          '#3b82f6'  // Blue
        ],
        borderWidth: 2,
        borderColor: '#1e293b'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#9ca3af',
            font: {
              family: 'Outfit',
              size: 13
            }
          }
        }
      }
    }
  });
}

// MANAGE STUDENTS TABLE & CRUD
async function loadAllStudents() {
  try {
    const response = await fetch('/api/students');
    const data = await response.json();
    if (data.success) {
      populateStudentsTable(data.students);
    }
  } catch (error) {
    showToast("Failed to fetch students list", true);
  }
}

async function searchStudents() {
  const searchBy = document.getElementById('search-by').value;
  const searchTerm = document.getElementById('search-term').value.trim();
  
  if (!searchTerm) {
    showToast("Please enter a search term", true);
    return;
  }
  
  try {
    const response = await fetch(`/api/students?search_by=${searchBy}&search_term=${encodeURIComponent(searchTerm)}`);
    const data = await response.json();
    if (data.success) {
      populateStudentsTable(data.students);
    }
  } catch (error) {
    showToast("Search failed", true);
  }
}

function populateStudentsTable(students) {
  const tbody = document.getElementById('students-table-body');
  tbody.innerHTML = '';
  
  if (students.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 30px;">
          No student records found.
        </td>
      </tr>
    `;
    return;
  }
  
  students.forEach(student => {
    const initials = student.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    const photoHTML = student.profile_image
      ? `<img src="${student.profile_image}" class="student-photo" alt="Profile">`
      : `<div class="student-photo-placeholder">${initials}</div>`;
      
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>#${student.id}</strong></td>
      <td>${photoHTML}</td>
      <td>${student.full_name}</td>
      <td><span class="class-badge">${student.class_name}</span></td>
      <td>${student.email}</td>
      <td>${student.mobile}</td>
      <td>${student.gender}</td>
      <td>${student.dob}</td>
      <td>
        <div class="actions-cell">
          <button onclick="editStudent(${JSON.stringify(student).replace(/"/g, '&quot;')})" class="btn-icon btn-icon-warning" title="Edit Student">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button onclick="deleteStudent(${student.id})" class="btn-icon btn-icon-danger" title="Delete Student">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// MODAL CONTROLS
function openModal(mode, studentData = null) {
  const modal = document.getElementById('student-modal');
  const title = document.getElementById('modal-title');
  const form = document.getElementById('student-form');
  
  form.reset();
  document.getElementById('student-form-id').value = '';
  resetImagePreview();
  
  if (mode === 'add') {
    title.textContent = "Add New Student Record";
    document.getElementById('save-btn').textContent = "Add Student";
  } else if (mode === 'edit' && studentData) {
    title.textContent = "Edit Student Record";
    document.getElementById('save-btn').textContent = "Save Changes";
    
    // Fill fields
    document.getElementById('student-form-id').value = studentData.id;
    document.getElementById('form-name').value = studentData.full_name;
    document.getElementById('form-class').value = studentData.class_name;
    document.getElementById('form-email').value = studentData.email;
    document.getElementById('form-mobile').value = studentData.mobile;
    document.getElementById('form-gender').value = studentData.gender;
    document.getElementById('form-dob').value = studentData.dob;
    document.getElementById('form-address').value = studentData.address;
    
    if (studentData.profile_image) {
      const preview = document.getElementById('image-preview');
      preview.innerHTML = `<img src="${studentData.profile_image}" alt="Preview"><span>Replace profile image</span>`;
    }
  }
  
  modal.classList.add('active');
}

function closeModal() {
  document.getElementById('student-modal').classList.remove('active');
}

// Preview Selected Image
function previewImage(input) {
  const preview = document.getElementById('image-preview');
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.innerHTML = `<img src="${e.target.result}" alt="Preview"><span>Change image file</span>`;
    };
    reader.readAsDataURL(input.files[0]);
  } else {
    resetImagePreview();
  }
}

function resetImagePreview() {
  const preview = document.getElementById('image-preview');
  preview.innerHTML = `
    <i class="fa-solid fa-cloud-arrow-up"></i>
    <span>Choose photo file...</span>
  `;
}

// Form Submission (Add or Update)
async function handleStudentSubmit(e) {
  e.preventDefault();
  
  const studentId = document.getElementById('student-form-id').value;
  const isEdit = studentId !== '';
  
  const formData = new FormData();
  formData.append('full_name', document.getElementById('form-name').value);
  formData.append('class_name', document.getElementById('form-class').value);
  formData.append('email', document.getElementById('form-email').value);
  formData.append('mobile', document.getElementById('form-mobile').value);
  formData.append('gender', document.getElementById('form-gender').value);
  formData.append('dob', document.getElementById('form-dob').value);
  formData.append('address', document.getElementById('form-address').value);
  
  const imgInput = document.getElementById('form-image');
  if (imgInput.files && imgInput.files[0]) {
    formData.append('profile_image', imgInput.files[0]);
  }

  const url = isEdit ? `/api/students/${studentId}` : '/api/students';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      body: formData // Body is multipart/form-data
    });
    
    const data = await response.json();
    if (data.success) {
      showToast(isEdit ? "Record updated successfully!" : "New student record added!");
      closeModal();
      loadAllStudents();
    } else {
      showToast(data.message || "Failed to save student record", true);
    }
  } catch (error) {
    showToast("Error saving record to database", true);
  }
}

function editStudent(student) {
  openModal('edit', student);
}

// DELETE STUDENT
async function deleteStudent(id) {
  const confirmDelete = confirm(`Are you sure you want to delete student ID #${id}?`);
  if (!confirmDelete) return;
  
  try {
    const response = await fetch(`/api/students/${id}`, {
      method: 'DELETE'
    });
    const data = await response.json();
    if (data.success) {
      showToast("Student record deleted successfully");
      loadAllStudents();
    } else {
      showToast(data.message || "Failed to delete student record", true);
    }
  } catch (error) {
    showToast("Error communicating with server", true);
  }
}
