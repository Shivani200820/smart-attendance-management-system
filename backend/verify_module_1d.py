import sys
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.profiles import Teacher, Student
from app.models.academic import Department, AcademicClass, Division, Batch, AcademicYear, Semester
from app.models.enums import UserRole

client = TestClient(app)


def print_step(title: str):
    print(f"\n==========================================")
    print(f"  {title}")
    print(f"==========================================")


def cleanup_m1d_test_users():
    """
    Cleans up any leftover test users created during previous test runs to ensure idempotency.
    """
    db = SessionLocal()
    try:
        test_usernames = ["m1d_new_admin", "m1d_teacher_user", "m1d_student_user"]
        for un in test_usernames:
            u = db.query(User).filter(User.username == un).first()
            if u:
                if u.teacher_profile:
                    db.delete(u.teacher_profile)
                if u.student_profile:
                    db.delete(u.student_profile)
                db.delete(u)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Test user cleanup encountered: {e}")
    finally:
        db.close()



def setup_prerequisite_academic_data():
    """
    Ensures prerequisite academic entities (Department, AcademicYear, Semester, Class, Division, Batch)
    exist in the database so foreign key validation tests pass cleanly.
    """
    db = SessionLocal()
    try:
        # 1. Department
        dept = db.query(Department).filter(Department.code == "CS").first()
        if not dept:
            dept = Department(name="Computer Science & Engineering", code="CS", is_active=True)
            db.add(dept)
            db.flush()

        # 2. Academic Year
        ay = db.query(AcademicYear).filter(AcademicYear.name == "2026-2027").first()
        if not ay:
            ay = AcademicYear(name="2026-2027", start_date=date(2026, 7, 1), end_date=date(2027, 6, 30), is_active=True)
            db.add(ay)
            db.flush()

        # 3. Semester
        sem = db.query(Semester).filter(Semester.academic_year_id == ay.id, Semester.semester_number == 1).first()
        if not sem:
            sem = Semester(academic_year_id=ay.id, semester_number=1, name="Semester 1", is_active=True)
            db.add(sem)
            db.flush()

        # 4. Academic Class
        ac = db.query(AcademicClass).filter(AcademicClass.department_id == dept.id, AcademicClass.code == "FE").first()
        if not ac:
            ac = AcademicClass(department_id=dept.id, name="First Year", code="FE", is_active=True)
            db.add(ac)
            db.flush()

        # 5. Division
        div = db.query(Division).filter(
            Division.academic_class_id == ac.id,
            Division.academic_year_id == ay.id,
            Division.semester_id == sem.id,
            Division.name == "Div-A"
        ).first()
        if not div:
            div = Division(
                academic_class_id=ac.id,
                academic_year_id=ay.id,
                semester_id=sem.id,
                name="Div-A",
                is_active=True
            )
            db.add(div)
            db.flush()

        # 6. Batch
        batch = db.query(Batch).filter(Batch.division_id == div.id, Batch.name == "Batch-A1").first()
        if not batch:
            batch = Batch(division_id=div.id, name="Batch-A1", is_active=True)
            db.add(batch)
            db.flush()

        db.commit()
        return {
            "department_id": dept.id,
            "academic_year_id": ay.id,
            "semester_id": sem.id,
            "academic_class_id": ac.id,
            "division_id": div.id,
            "batch_id": batch.id
        }
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed setting up prerequisite academic data: {e}")
        sys.exit(1)
    finally:
        db.close()


def setup_test_users():
    """
    Creates temporary Teacher and Student users for role authorization tests if absent.
    """
    db = SessionLocal()
    try:
        teacher = db.query(User).filter(User.username == "test_teacher_m1d").first()
        if not teacher:
            teacher = User(
                username="test_teacher_m1d",
                email="teacher_m1d@attendance.com",
                password_hash=hash_password("TeacherPass@123"),
                role=UserRole.TEACHER,
                is_active=True
            )
            db.add(teacher)

        student = db.query(User).filter(User.username == "test_student_m1d").first()
        if not student:
            student = User(
                username="test_student_m1d",
                email="student_m1d@attendance.com",
                password_hash=hash_password("StudentPass@123"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed setting up test users: {e}")
        sys.exit(1)
    finally:
        db.close()


def test_module_1a_health_regression():
    print_step("1. Testing Module 1A Health Endpoints Regression")
    resp1 = client.get("/api/health")
    assert resp1.status_code == 200, f"Expected 200, got {resp1.status_code}"
    assert resp1.json()["status"] == "ok"
    print("[PASS] Basic API health (/api/health) returned HTTP 200 OK.")

    resp2 = client.get("/api/health/database")
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}"
    assert resp2.json()["database"] == "connected"
    print("[PASS] Database health (/api/health/database) returned HTTP 200 OK.")


def test_module_1b_schema_regression():
    print_step("2. Testing Module 1B Database Schema & Constraints Regression")
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)

    tables = sorted(inspector.get_table_names())
    expected_tables = [
        "academic_classes", "academic_years", "attendance_corrections", "attendance_records",
        "attendance_sessions", "batches", "class_subject_assignments", "departments",
        "divisions", "semesters", "students", "subjects", "teacher_assignments",
        "teachers", "timetable", "users"
    ]
    missing = [t for t in expected_tables if t not in tables]
    assert not missing, f"Missing database tables: {missing}"
    print(f"[PASS] All 16 database tables preserved intact: {len(tables)} tables.")

    # Verify primary keys on all tables
    for t in expected_tables:
        pk = inspector.get_pk_constraint(t)
        assert pk.get("constrained_columns"), f"Table {t} missing primary key"
    print("[PASS] All 16 tables retain valid primary keys.")

    # Verify unique constraint on attendance_records
    uqs = inspector.get_unique_constraints("attendance_records")
    uq_found = any({"student_id", "attendance_session_id"}.issubset(set(u["column_names"])) for u in uqs)
    assert uq_found, "Missing unique constraint on attendance_records (student_id + attendance_session_id)"
    print("[PASS] Unique constraint on attendance_records (student_id + attendance_session_id) intact.")


def test_module_1c_auth_regression():
    print_step("3. Testing Module 1C Auth & JWT Validation Regression")
    # Login as initial Admin
    resp = client.post("/api/auth/login", json={
        "username": settings.INIT_ADMIN_USERNAME,
        "password": settings.INIT_ADMIN_PASSWORD
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    token = resp.json()["access_token"]

    # Verify GET /api/auth/me
    resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    assert resp_me.json()["username"] == settings.INIT_ADMIN_USERNAME
    print("[PASS] Admin login and /api/auth/me working correctly.")
    return token


def test_user_creation_and_profiles(admin_token: str, ref_data: dict):
    print_step("4. Testing Admin User Creation with Profiles (ADMIN, TEACHER, STUDENT)")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin creates an ADMIN user
    admin_payload = {
        "username": "m1d_new_admin",
        "email": "m1d_admin@attendance.com",
        "password": "AdminPass123!#",
        "role": "ADMIN"
    }
    resp = client.post("/api/users", json=admin_payload, headers=headers)
    assert resp.status_code == 201, f"Create ADMIN failed: {resp.status_code} - {resp.text}"
    data_admin = resp.json()
    assert data_admin["username"] == "m1d_new_admin"
    assert data_admin["role"] == "ADMIN"
    assert "password_hash" not in data_admin
    assert "password" not in data_admin
    print("[PASS] Admin successfully created an ADMIN user without password hash exposure.")

    # 2. Admin creates a TEACHER user
    teacher_payload = {
        "username": "m1d_teacher_user",
        "email": "m1d_teacher_u@attendance.com",
        "password": "TeacherPass123!#",
        "role": "TEACHER",
        "teacher_profile": {
            "employee_id": "EMP_M1D_001",
            "full_name": "Prof. Charles Babbage",
            "email": "babbage_m1d@attendance.com",
            "department_id": ref_data["department_id"]
        }
    }
    resp = client.post("/api/users", json=teacher_payload, headers=headers)
    assert resp.status_code == 201, f"Create TEACHER failed: {resp.status_code} - {resp.text}"
    data_teacher = resp.json()
    assert data_teacher["username"] == "m1d_teacher_user"
    assert data_teacher["role"] == "TEACHER"
    assert data_teacher["teacher_profile"] is not None
    assert data_teacher["teacher_profile"]["employee_id"] == "EMP_M1D_001"
    assert data_teacher["teacher_profile"]["full_name"] == "Prof. Charles Babbage"
    assert "password_hash" not in data_teacher
    teacher_user_id = data_teacher["id"]
    print("[PASS] Admin successfully created a TEACHER user with linked teacher profile.")

    # 3. Admin creates a STUDENT user
    student_payload = {
        "username": "m1d_student_user",
        "email": "m1d_student_u@attendance.com",
        "password": "StudentPass123!#",
        "role": "STUDENT",
        "student_profile": {
            "student_id": "STU_M1D_99",
            "roll_number": "R-101",
            "enrollment_number": "ENR_M1D_9999",
            "full_name": "Grace Hopper",
            "email": "grace_m1d@attendance.com",
            "department_id": ref_data["department_id"],
            "academic_class_id": ref_data["academic_class_id"],
            "division_id": ref_data["division_id"],
            "batch_id": ref_data["batch_id"],
            "academic_year_id": ref_data["academic_year_id"],
            "semester_id": ref_data["semester_id"]
        }
    }
    resp = client.post("/api/users", json=student_payload, headers=headers)
    assert resp.status_code == 201, f"Create STUDENT failed: {resp.status_code} - {resp.text}"
    data_student = resp.json()
    assert data_student["username"] == "m1d_student_user"
    assert data_student["role"] == "STUDENT"
    assert data_student["student_profile"] is not None
    assert data_student["student_profile"]["student_id"] == "STU_M1D_99"
    assert data_student["student_profile"]["enrollment_number"] == "ENR_M1D_9999"
    assert "password_hash" not in data_student
    student_user_id = data_student["id"]
    print("[PASS] Admin successfully created a STUDENT user with linked student profile.")

    return teacher_user_id, student_user_id


def test_uniqueness_and_validation(admin_token: str, ref_data: dict):
    print_step("5. Testing Uniqueness Constraints & FK Validation")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Duplicate Username
    resp = client.post("/api/users", json={
        "username": "m1d_new_admin",
        "email": "different_email@attendance.com",
        "password": "Password123!",
        "role": "ADMIN"
    }, headers=headers)
    assert resp.status_code == 400, f"Expected 400 for duplicate username, got {resp.status_code}"
    print("[PASS] Duplicate username registration rejected with HTTP 400.")

    # 2. Duplicate Email
    resp = client.post("/api/users", json={
        "username": "unique_uname_123",
        "email": "m1d_admin@attendance.com",
        "password": "Password123!",
        "role": "ADMIN"
    }, headers=headers)
    assert resp.status_code == 400, f"Expected 400 for duplicate email, got {resp.status_code}"
    print("[PASS] Duplicate email registration rejected with HTTP 400.")

    # 3. Duplicate Teacher Employee ID
    resp = client.post("/api/users", json={
        "username": "another_teacher",
        "email": "another_t@attendance.com",
        "password": "Password123!",
        "role": "TEACHER",
        "teacher_profile": {
            "employee_id": "EMP_M1D_001",
            "full_name": "Teacher Two",
            "email": "teacher2_p@attendance.com",
            "department_id": ref_data["department_id"]
        }
    }, headers=headers)
    assert resp.status_code == 400, f"Expected 400 for duplicate employee ID, got {resp.status_code}"
    print("[PASS] Duplicate Teacher Employee ID rejected with HTTP 400.")

    # 4. Duplicate Student ID
    resp = client.post("/api/users", json={
        "username": "another_student",
        "email": "another_s@attendance.com",
        "password": "Password123!",
        "role": "STUDENT",
        "student_profile": {
            "student_id": "STU_M1D_99",
            "roll_number": "R-102",
            "enrollment_number": "ENR_M1D_NEW",
            "full_name": "Student Two",
            "email": "student2_p@attendance.com",
            "department_id": ref_data["department_id"],
            "academic_class_id": ref_data["academic_class_id"],
            "division_id": ref_data["division_id"],
            "batch_id": ref_data["batch_id"],
            "academic_year_id": ref_data["academic_year_id"],
            "semester_id": ref_data["semester_id"]
        }
    }, headers=headers)
    assert resp.status_code == 400, f"Expected 400 for duplicate student ID, got {resp.status_code}"
    print("[PASS] Duplicate Student ID rejected with HTTP 400.")

    # 5. Invalid Foreign Key (Non-existent Department ID)
    resp = client.post("/api/users", json={
        "username": "invalid_fk_teacher",
        "email": "invalid_fk@attendance.com",
        "password": "Password123!",
        "role": "TEACHER",
        "teacher_profile": {
            "employee_id": "EMP_INVALID_FK",
            "full_name": "No Dept Teacher",
            "email": "nodept@attendance.com",
            "department_id": 999999
        }
    }, headers=headers)
    assert resp.status_code in [400, 404], f"Expected 400/404 for invalid FK, got {resp.status_code}"
    print("[PASS] Non-existent Department foreign key reference rejected.")


def test_user_listing_retrieval_and_updates(admin_token: str, teacher_user_id: int):
    print_step("6. Testing User Listing, Pagination, Search, Retrieval, and Updates")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. GET /api/users
    resp = client.get("/api/users", headers=headers)
    assert resp.status_code == 200, f"List users failed: {resp.text}"
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3
    print(f"[PASS] GET /api/users returned {len(data['items'])} items (Total: {data['total']}).")

    # 2. GET /api/users with role filter
    resp_role = client.get("/api/users?role=TEACHER", headers=headers)
    assert resp_role.status_code == 200
    for u in resp_role.json()["items"]:
        assert u["role"] == "TEACHER"
    print("[PASS] GET /api/users?role=TEACHER filtered correctly.")

    # 3. GET /api/users with search
    resp_search = client.get("/api/users?search=Babbage", headers=headers)
    assert resp_search.status_code == 200
    assert resp_search.json()["total"] >= 1
    print("[PASS] GET /api/users?search=Babbage returned matching user.")

    # 4. GET /api/users/{user_id}
    resp_single = client.get(f"/api/users/{teacher_user_id}", headers=headers)
    assert resp_single.status_code == 200
    single_user = resp_single.json()
    assert single_user["id"] == teacher_user_id
    assert single_user["teacher_profile"]["full_name"] == "Prof. Charles Babbage"
    assert "password_hash" not in single_user
    print("[PASS] GET /api/users/{id} returned detailed safe user model.")

    # 5. PUT /api/users/{user_id}
    update_payload = {
        "teacher_profile": {
            "full_name": "Prof. Sir Charles Babbage"
        }
    }
    resp_update = client.put(f"/api/users/{teacher_user_id}", json=update_payload, headers=headers)
    assert resp_update.status_code == 200, f"Update user failed: {resp_update.text}"
    updated_user = resp_update.json()
    assert updated_user["teacher_profile"]["full_name"] == "Prof. Sir Charles Babbage"
    assert "password_hash" not in updated_user
    print("[PASS] PUT /api/users/{id} successfully updated user profile.")


def test_user_deactivation_flow(admin_token: str, teacher_user_id: int):
    print_step("7. Testing User Account Deactivation and Authentication Blocking")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin deactivates teacher user
    resp_deact = client.patch(
        f"/api/users/{teacher_user_id}/status",
        json={"is_active": False},
        headers=headers
    )
    assert resp_deact.status_code == 200, f"Deactivate failed: {resp_deact.text}"
    assert resp_deact.json()["is_active"] is False
    print("[PASS] Admin successfully deactivated user via PATCH /api/users/{id}/status.")

    # 2. Attempt login as deactivated user -> HTTP 401
    resp_login = client.post("/api/auth/login", json={
        "username": "m1d_teacher_user",
        "password": "TeacherPass123!#"
    })
    assert resp_login.status_code == 401, f"Expected 401 for deactivated user login, got {resp_login.status_code}"
    print("[PASS] Deactivated user authentication attempt rejected with HTTP 401 Unauthorized.")

    # 3. Admin reactivates teacher user
    resp_react = client.patch(
        f"/api/users/{teacher_user_id}/status",
        json={"is_active": True},
        headers=headers
    )
    assert resp_react.status_code == 200
    assert resp_react.json()["is_active"] is True
    print("[PASS] Admin successfully reactivated user.")

    # 4. Login after reactivation -> HTTP 200
    resp_relogin = client.post("/api/auth/login", json={
        "username": "m1d_teacher_user",
        "password": "TeacherPass123!#"
    })
    assert resp_relogin.status_code == 200, f"Reactivated login failed: {resp_relogin.text}"
    print("[PASS] Reactivated user successfully authenticated with HTTP 200 OK.")


def test_role_authorization_guards(admin_token: str):
    print_step("8. Testing RBAC Access Control Guards on /api/users")

    # Obtain Teacher & Student JWT Tokens
    resp_teacher_auth = client.post("/api/auth/login", json={"username": "test_teacher_m1d", "password": "TeacherPass@123"})
    teacher_token = resp_teacher_auth.json()["access_token"]

    resp_student_auth = client.post("/api/auth/login", json={"username": "test_student_m1d", "password": "StudentPass@123"})
    student_token = resp_student_auth.json()["access_token"]

    # 1. TEACHER tries GET /api/users -> HTTP 403 Forbidden
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {teacher_token}"})
    assert resp.status_code == 403, f"Expected 403 for TEACHER list users, got {resp.status_code}"
    print("[PASS] TEACHER access to GET /api/users denied with HTTP 403 Forbidden.")

    # 2. TEACHER tries POST /api/users -> HTTP 403 Forbidden
    resp = client.post("/api/users", json={"username": "x", "email": "x@x.com", "password": "x", "role": "STUDENT"}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert resp.status_code == 403, f"Expected 403 for TEACHER create user, got {resp.status_code}"
    print("[PASS] TEACHER access to POST /api/users denied with HTTP 403 Forbidden.")

    # 3. STUDENT tries GET /api/users -> HTTP 403 Forbidden
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 403, f"Expected 403 for STUDENT list users, got {resp.status_code}"
    print("[PASS] STUDENT access to GET /api/users denied with HTTP 403 Forbidden.")

    # 4. STUDENT tries POST /api/users -> HTTP 403 Forbidden
    resp = client.post("/api/users", json={"username": "y", "email": "y@y.com", "password": "y", "role": "STUDENT"}, headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 403, f"Expected 403 for STUDENT create user, got {resp.status_code}"
    print("[PASS] STUDENT access to POST /api/users denied with HTTP 403 Forbidden.")


def main():
    print("\n==========================================")
    print("  RUNNING MODULE 1D AUTOMATED VERIFICATION SUITE")
    print("==========================================")

    cleanup_m1d_test_users()
    ref_data = setup_prerequisite_academic_data()
    setup_test_users()


    test_module_1a_health_regression()
    test_module_1b_schema_regression()
    admin_token = test_module_1c_auth_regression()

    teacher_id, student_id = test_user_creation_and_profiles(admin_token, ref_data)
    test_uniqueness_and_validation(admin_token, ref_data)
    test_user_listing_retrieval_and_updates(admin_token, teacher_id)
    test_user_deactivation_flow(admin_token, teacher_id)
    test_role_authorization_guards(admin_token)

    print("\n==========================================")
    print("  [SUCCESS] ALL MODULE 1D VERIFICATION CHECKS PASSED PERFECTLY!")
    print("==========================================")


if __name__ == "__main__":
    main()
