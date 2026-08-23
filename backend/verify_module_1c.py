import sys
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.enums import UserRole

client = TestClient(app)


def print_step(title: str):
    print(f"\n==========================================")
    print(f"  {title}")
    print(f"==========================================")


def setup_test_users():
    """
    Creates temporary Teacher, Student, and Inactive users for role testing if they don't exist.
    """
    db = SessionLocal()
    try:
        # Create Teacher user
        teacher = db.query(User).filter(User.username == "test_teacher").first()
        if not teacher:
            teacher = User(
                username="test_teacher",
                email="teacher@attendance.com",
                password_hash=hash_password("TeacherPass@123"),
                role=UserRole.TEACHER,
                is_active=True
            )
            db.add(teacher)

        # Create Student user
        student = db.query(User).filter(User.username == "test_student").first()
        if not student:
            student = User(
                username="test_student",
                email="student@attendance.com",
                password_hash=hash_password("StudentPass@123"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)

        # Create Inactive user
        inactive = db.query(User).filter(User.username == "test_inactive").first()
        if not inactive:
            inactive = User(
                username="test_inactive",
                email="inactive@attendance.com",
                password_hash=hash_password("InactivePass@123"),
                role=UserRole.STUDENT,
                is_active=False
            )
            db.add(inactive)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed setting up test users: {e}")
        sys.exit(1)
    finally:
        db.close()


def test_module_1a_health():
    print_step("1. Testing Module 1A Health Endpoints")

    # Basic API health
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["status"] == "ok"
    print("[PASS] Basic API health endpoint (/api/health) returned HTTP 200 OK.")

    # Database health
    resp = client.get("/api/health/database")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["database"] == "connected"
    print("[PASS] Database health endpoint (/api/health/database) returned HTTP 200 OK.")


def test_authentication_flow():
    print_step("2. Testing Authentication Flow & Credential Validation")

    # 1. Successful Login with Admin credentials
    login_payload = {
        "username": settings.INIT_ADMIN_USERNAME,
        "password": settings.INIT_ADMIN_PASSWORD
    }
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, f"Login failed: {resp.status_code} - {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == settings.INIT_ADMIN_USERNAME
    assert data["user"]["role"] == "ADMIN"
    print("[PASS] Successful login returns valid JWT token and user info.")
    admin_token = data["access_token"]

    # 2. Login via Email address
    email_login_payload = {
        "username": settings.INIT_ADMIN_EMAIL,
        "password": settings.INIT_ADMIN_PASSWORD
    }
    resp = client.post("/api/auth/login", json=email_login_payload)
    assert resp.status_code == 200, f"Email login failed: {resp.status_code} - {resp.text}"
    print("[PASS] Successful login via Email address verified.")

    # 3. Invalid password
    resp = client.post("/api/auth/login", json={
        "username": settings.INIT_ADMIN_USERNAME,
        "password": "WrongPassword123"
    })
    assert resp.status_code == 401, f"Expected 401 for wrong password, got {resp.status_code}"
    print("[PASS] Invalid password returns HTTP 401 Unauthorized.")

    # 4. Unknown user
    resp = client.post("/api/auth/login", json={
        "username": "nonexistent_user_9999",
        "password": "Password123"
    })
    assert resp.status_code == 401, f"Expected 401 for unknown user, got {resp.status_code}"
    print("[PASS] Unknown user login returns HTTP 401 Unauthorized.")

    # 5. Inactive user authentication attempt
    resp = client.post("/api/auth/login", json={
        "username": "test_inactive",
        "password": "InactivePass@123"
    })
    assert resp.status_code == 401, f"Expected 401 for inactive user, got {resp.status_code}"
    print("[PASS] Inactive user login returns HTTP 401 Unauthorized.")

    return admin_token


def test_token_validation_and_me_endpoint(admin_token: str):
    print_step("3. Testing Token Validation & GET /api/auth/me")

    # 1. Missing token
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401, f"Expected 401 for missing token, got {resp.status_code}"
    print("[PASS] Missing JWT returns HTTP 401 Unauthorized.")

    # 2. Invalid JWT token
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert resp.status_code == 401, f"Expected 401 for invalid token, got {resp.status_code}"
    print("[PASS] Invalid JWT returns HTTP 401 Unauthorized.")

    # 3. Expired JWT token
    expired_token = create_access_token(
        subject=1,
        expires_delta=timedelta(seconds=-10)
    )
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401, f"Expected 401 for expired token, got {resp.status_code}"
    print("[PASS] Expired JWT returns HTTP 401 Unauthorized.")

    # 4. Valid JWT on /api/auth/me
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    user_data = resp.json()
    assert user_data["username"] == settings.INIT_ADMIN_USERNAME
    assert user_data["role"] == "ADMIN"
    print("[PASS] GET /api/auth/me with valid JWT returns authenticated user details.")


def test_role_authorization():
    print_step("4. Testing Role-Based Authorization Guards")

    # Obtain tokens for each role
    resp_admin = client.post("/api/auth/login", json={"username": settings.INIT_ADMIN_USERNAME, "password": settings.INIT_ADMIN_PASSWORD})
    admin_token = resp_admin.json()["access_token"]

    resp_teacher = client.post("/api/auth/login", json={"username": "test_teacher", "password": "TeacherPass@123"})
    teacher_token = resp_teacher.json()["access_token"]

    resp_student = client.post("/api/auth/login", json={"username": "test_student", "password": "StudentPass@123"})
    student_token = resp_student.json()["access_token"]

    # --- ADMIN Endpoint Tests ---
    res = client.get("/api/auth/test/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200, f"ADMIN should access ADMIN endpoint, got {res.status_code}"
    print("[PASS] ADMIN successfully accessed ADMIN endpoint.")

    res = client.get("/api/auth/test/admin", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 403, f"TEACHER should NOT access ADMIN endpoint, got {res.status_code}"
    print("[PASS] TEACHER denied access to ADMIN endpoint (HTTP 403).")

    res = client.get("/api/auth/test/admin", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403, f"STUDENT should NOT access ADMIN endpoint, got {res.status_code}"
    print("[PASS] STUDENT denied access to ADMIN endpoint (HTTP 403).")

    # --- TEACHER Endpoint Tests ---
    res = client.get("/api/auth/test/teacher", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 200, f"TEACHER should access TEACHER endpoint, got {res.status_code}"
    print("[PASS] TEACHER successfully accessed TEACHER endpoint.")

    res = client.get("/api/auth/test/teacher", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403, f"STUDENT should NOT access TEACHER endpoint, got {res.status_code}"
    print("[PASS] STUDENT denied access to TEACHER endpoint (HTTP 403).")

    res = client.get("/api/auth/test/teacher", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 403, f"ADMIN should NOT access TEACHER endpoint directly (strict role check), got {res.status_code}"
    print("[PASS] ADMIN denied access to strict TEACHER endpoint (HTTP 403).")

    # --- STUDENT Endpoint Tests ---
    res = client.get("/api/auth/test/student", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200, f"STUDENT should access STUDENT endpoint, got {res.status_code}"
    print("[PASS] STUDENT successfully accessed STUDENT endpoint.")

    res = client.get("/api/auth/test/student", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 403, f"TEACHER should NOT access STUDENT endpoint, got {res.status_code}"
    print("[PASS] TEACHER denied access to STUDENT endpoint (HTTP 403).")


def test_module_1b_regression():
    print_step("5. Testing Module 1B Database Schema & Constraints Regression")

    engine = create_engine(settings.database_url)
    inspector = inspect(engine)

    tables = sorted(inspector.get_table_names())
    assert len(tables) == 16, f"Expected 16 tables, found {len(tables)}"
    print(f"[PASS] All 16 database tables preserved intact: {tables}")

    expected_tables = [
        "academic_classes", "academic_years", "attendance_corrections", "attendance_records",
        "attendance_sessions", "batches", "class_subject_assignments", "departments",
        "divisions", "semesters", "students", "subjects", "teacher_assignments",
        "teachers", "timetable", "users"
    ]
    missing = [t for t in expected_tables if t not in tables]
    assert not missing, f"Missing tables: {missing}"

    # Verify primary keys on all 16 tables
    for t in expected_tables:
        pk = inspector.get_pk_constraint(t)
        assert pk.get("constrained_columns"), f"Table {t} missing primary key"
    print("[PASS] All 16 tables retain valid primary keys.")

    # Verify attendance_records unique constraint
    uqs = inspector.get_unique_constraints("attendance_records")
    uq_found = any({"student_id", "attendance_session_id"}.issubset(set(u["column_names"])) for u in uqs)
    assert uq_found, "Missing unique constraint on attendance_records (student_id + attendance_session_id)"
    print("[PASS] Verified unique constraint (student_id + attendance_session_id) in attendance_records.")


def main():
    print("\n==========================================")
    print("  RUNNING MODULE 1C AUTOMATED VERIFICATION SUITE")
    print("==========================================")

    setup_test_users()
    test_module_1a_health()
    admin_token = test_authentication_flow()
    test_token_validation_and_me_endpoint(admin_token)
    test_role_authorization()
    test_module_1b_regression()

    print("\n==========================================")
    print("  [SUCCESS] ALL MODULE 1C VERIFICATION CHECKS PASSED PERFECTLY!")
    print("==========================================")


if __name__ == "__main__":
    main()
