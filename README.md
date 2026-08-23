# ATTENDANCE MANAGEMENT SYSTEM — COMPLETE PROJECT DOCUMENTATION

Welcome to the **Attendance Management System**, a secure, full-stack final-year academic attendance system built with **FastAPI**, **SQLAlchemy**, **MySQL 8.0**, and **React (Vite)**.

---

## Technical Architecture

- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, PyJWT, Bcrypt, Pydantic v2
- **Database**: MySQL Server 8.0 (16 relational tables with strict foreign key constraints & unique indexes)
- **Frontend**: React, Vite, Lucide Icons, QRCode SVG, Custom Glassmorphism CSS Design System
- **Authentication**: JWT Bearer token authentication with Role-Based Access Control (`ADMIN`, `TEACHER`, `STUDENT`)

---

## Features Overview

1. **User Authentication & Role-Based Access Control**:
   - Secure login, password hashing with bcrypt, JWT token validation.
   - Dedicated endpoints for `ADMIN`, `TEACHER`, and `STUDENT`.

2. **Academic Structure Management**:
   - Departments, Academic Classes (FE, SE, TE, BE), Divisions, Batches, Subjects, Academic Years, and Semesters.

3. **Timetable Management & Teacher Assignments**:
   - Day-wise class timetable slots and subject teacher mapping.

4. **Attendance Session Lifecycle (QR Token Based)**:
   - Teachers generate active attendance sessions with dynamic QR tokens and expiration timers.
   - Auto-evaluation of session expiration (`ACTIVE` -> `EXPIRED` / `CLOSED` / `CANCELLED`).

5. **Student QR / Token Attendance Marking**:
   - Student scans QR token to submit attendance.
   - Strictly enforces division & batch enrollment checks and prevents duplicate submissions (`HTTP 409 Conflict`).

6. **Teacher Manual Marking & Audit Trail Corrections**:
   - Batch manual attendance entry by teachers.
   - Status corrections logged in `attendance_corrections` table with auditor ID and reason.

7. **Reports & Defaulter Analytics**:
   - Student overall and subject-wise attendance percentage breakdown.
   - Automatic Defaulters List generation (<75% threshold).

---

## Quick Setup & How to Run

### 1. Database Configuration
Ensure MySQL 8.0 is running and create the database:
```sql
CREATE DATABASE IF NOT EXISTS attendance_management;
```

### 2. Run Backend API
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Base API URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Run Frontend Web Application
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
- **Web App URL**: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## Test & Verification Suite

Run the master automated verification suite covering all 9 modules:
```powershell
cd backend
.\.venv\Scripts\python.exe verify_all_modules.py
```

Run live HTTP server tests against `http://127.0.0.1:8000`:
```powershell
cd backend
.\.venv\Scripts\python.exe live_api_verify.py
```
