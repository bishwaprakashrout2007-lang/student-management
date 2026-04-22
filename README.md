# Property Portal

A full-stack real estate web application modeled after MagicBricks.com. The application allows users to search for properties across major Indian cities (Bangalore, Mumbai, New Delhi, Bhubaneswar, and Hyderabad) with filtering options for property type (Rent/Buy) and budget constraints.

## Project Structure

This repository contains both the frontend and backend applications in a single monorepo structure:

- `/frontend` - React user interface
- `/backend` - FastAPI Python server with SQLite database

---

## 🚀 Backend Setup (FastAPI)

The backend provides a robust RESTful API to serve property data, utilizing SQLite for lightweight, reliable storage.

### Prerequisites
- Python 3.8+

### Installation & Running

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Activate the virtual environment (if used from root):**
   ```bash
   # On Windows (from root)
   ..\venv\Scripts\activate
   # Or create one inside backend:
   # python -m venv venv
   # venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn
   # If there is a requirements.txt:
   # pip install -r requirements.txt
   ```

4. **Start the FastAPI server:**
   ```bash
   # Assuming your main file is main.py
   uvicorn main:app --reload
   ```

The backend server will typically start on `http://127.0.0.1:8000`. You can access the automatic API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## 🎨 Frontend Setup (React)

The frontend provides a dynamic, responsive user interface for searching and viewing properties.

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation & Running

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # (or npm start, depending on your setup)
   ```

The frontend application will start and usually be accessible at `http://localhost:5173` (if using Vite) or `http://localhost:3000` (if using Create React App).

## Features
- **City-based Search:** Find properties in Bangalore, Mumbai, New Delhi, Bhubaneswar, and Hyderabad.
- **Advanced Filtering:** Filter properties by intention (Rent/Buy) and specify minimum and maximum budget ranges.
- **Mock Dataset:** Pre-populated with 10 realistic mock properties per city for testing and demonstration purposes.

## Technologies Used
- **Frontend:** React, HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, SQLite, Uvicorn
