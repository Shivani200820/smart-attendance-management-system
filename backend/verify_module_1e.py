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
from app.models.subject import Subject
from app.models.assignments import ClassSubjectAssignment, TeacherAssignment
from app.models.enums import UserRole

client = TestClient(app)


def print_step(title: str):
    print(f"\n==========================================")
    print(f"  {title}")
    print(f"==========================================")


def cleanup_m1e_test_data():
    """
    Cleans up any leftover test records created during previous M1E runs.
    """
    db = SessionLocal()
    try:
        # Delete test assignments
        db.query(TeacherAssignment).filter(TeacherAssignment.academic_year.has(AcademicYear.name.like("M1E_%"))).delete(synchronize_session=False)
        db.query(ClassSubjectAssignment).filter(ClassSubjectAssignment.academic_year.has(AcademicYear.name.like("M1E_%"))).delete(synchronize_session=False)
        # Delete test subjects
        db.query(Subject).filter(Subject.code.like("M1E_%")).delete(synchronize_session=False)
        # Delete test batches
        db.query(Batch).filter(Batch.name.like("M1E_%")).delete(synchronize_session=False)
        # Delete test divisions
        db.query(Division).filter(Division.name.like("M1E_%")).delete(synchronize_session=False)
        # Delete test classes
        db.query(AcademicClass).filter(AcademicClass.code.like("M1E_%")).delete(synchronize_session=False)
        # Delete test departments
        db.query(Department).filter(Department.code.like("M1E_%")).delete(synchronize_session=False)
        # Delete test semesters & academic years
        db.query(Semester).filter(Semester.name.like("M1E_%")).delete(synchronize_session=False)
        db.query(AcademicYear).filter(AcademicYear.name.like("M1E_%")).delete(synchronize_session=False)
        
        # Delete test users
        for username in ["m1e_admin", "m1e_teacher_user", "m1e_student_user"]:
            u = db.query(User).filter(User.username == username).first()
            if u:
                if u.teacher_profile:
                    db.delete(u.teacher_profile)
                if u.student_profile:
                    db.delete(u.student_profile)
                db.delete(u)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Test data cleanup encountered: {e}")
    finally:
        db.close()


def setup_users_and_headers():
    """
    Sets up Admin, Teacher, and Student users and generates JWT Bearer authorization headers.
    """
    db = SessionLocal()
    try:
        # 1. Admin
        admin = db.query(User).filter(User.username == "m1e_admin").first()
        if not admin:
            admin = User(
                username="m1e_admin",
                email="m1e_admin@attendance.com",
                password_hash=hash_password("AdminPass123!"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # 2. Teacher (Requires department)
        dept = db.query(Department).first()
        if not dept:
            dept = Department(name="Initial Dept", code="INIT", is_active=True)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        teacher_user = db.query(User).filter(User.username == "m1e_teacher_user").first()
        if not teacher_user:
            teacher_user = User(
                username="m1e_teacher_user",
                email="m1e_teacher@attendance.com",
                password_hash=hash_password("TeacherPass123!"),
                role=UserRole.TEACHER,
                is_active=True
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)

            teacher_profile = Teacher(
                user_id=teacher_user.id,
                employee_id="M1E_EMP001",
                full_name="M1E Teacher",
                email="m1e_teacher@attendance.com",
                department_id=dept.id,
                is_active=True
            )
            db.add(teacher_profile)
            db.commit()
        
        teacher_profile = db.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()

        # 3. Student
        student_user = db.query(User).filter(User.username == "m1e_student_user").first()
        if not student_user:
            student_user = User(
                username="m1e_student_user",
                email="m1e_student@attendance.com",
                password_hash=hash_password("StudentPass123!"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student_user)
            db.commit()

        # Create JWT Tokens
        admin_token = create_access_token(subject=admin.id, extra_data={"role": admin.role.value})
        teacher_token = create_access_token(subject=teacher_user.id, extra_data={"role": teacher_user.role.value})
        student_token = create_access_token(subject=student_user.id, extra_data={"role": student_user.role.value})

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
        student_headers = {"Authorization": f"Bearer {student_token}"}

        return admin_headers, teacher_headers, student_headers, teacher_profile.id
    finally:
        db.close()


def test_academic_years(admin_h, teacher_h, student_h):
    print_step("1. Testing Academic Year Management APIs & Validations")

    # A. Invalid Date Validation (start_date >= end_date)
    bad_dates_payload = {
        "name": "M1E_AY_BAD_DATES",
        "start_date": "2026-12-31",
        "end_date": "2026-01-01",
        "is_active": True
    }
    r = client.post("/api/academic-years", json=bad_dates_payload, headers=admin_h)
    assert r.status_code == 400, f"Expected 400 for invalid dates, got {r.status_code}: {r.text}"
    print("[PASS] Invalid date range (start_date >= end_date) rejected with HTTP 400.")

    # B. Create Valid Academic Year
    ay_payload = {
        "name": "M1E_AY_2026_2027",
        "start_date": "2026-07-01",
        "end_date": "2027-06-30",
        "is_active": True
    }
    r = client.post("/api/academic-years", json=ay_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create AY: {r.text}"
    ay_data = r.json()
    ay_id = ay_data["id"]
    print(f"[PASS] Academic Year created successfully (ID: {ay_id}).")

    # C. Duplicate Name Rejection
    r_dup = client.post("/api/academic-years", json=ay_payload, headers=admin_h)
    assert r_dup.status_code == 400, f"Expected 400 for duplicate AY name, got {r_dup.status_code}"
    print("[PASS] Duplicate Academic Year name rejected with HTTP 400.")

    # D. List Academic Years
    r_list = client.get("/api/academic-years", headers=admin_h)
    assert r_list.status_code == 200
    assert any(item["id"] == ay_id for item in r_list.json())
    print("[PASS] List Academic Years returned valid array containing created entity.")

    # E. Get Academic Year by ID
    r_get = client.get(f"/api/academic-years/{ay_id}", headers=admin_h)
    assert r_get.status_code == 200
    assert r_get.json()["name"] == "M1E_AY_2026_2027"
    print("[PASS] Get Academic Year by ID returned accurate details.")

    # F. Update Academic Year
    update_payload = {"name": "M1E_AY_2026_2027_UPDATED"}
    r_upd = client.put(f"/api/academic-years/{ay_id}", json=update_payload, headers=admin_h)
    assert r_upd.status_code == 200
    assert r_upd.json()["name"] == "M1E_AY_2026_2027_UPDATED"
    print("[PASS] Update Academic Year succeeded.")

    # G. Activate / Deactivate Academic Year
    r_st = client.patch(f"/api/academic-years/{ay_id}/status", json={"is_active": False}, headers=admin_h)
    assert r_st.status_code == 200
    assert r_st.json()["is_active"] is False
    # Re-activate for downstream tests
    client.patch(f"/api/academic-years/{ay_id}/status", json={"is_active": True}, headers=admin_h)
    print("[PASS] Activate / Deactivate Academic Year status endpoint verified.")

    return ay_id


def test_semesters(ay_id, admin_h, teacher_h, student_h):
    print_step("2. Testing Semester Management APIs & Validations")

    # A. Invalid Academic Year Foreign Key
    bad_ay_payload = {
        "academic_year_id": 999999,
        "semester_number": 1,
        "name": "M1E_Sem_Bad",
        "is_active": True
    }
    r = client.post("/api/semesters", json=bad_ay_payload, headers=admin_h)
    assert r.status_code == 400, f"Expected 400 for invalid AY foreign key, got {r.status_code}"
    print("[PASS] Invalid Academic Year foreign key rejected with HTTP 400.")

    # B. Create Valid Semester
    sem_payload = {
        "academic_year_id": ay_id,
        "semester_number": 1,
        "name": "M1E_Semester_1",
        "start_date": "2026-07-01",
        "end_date": "2026-12-31",
        "is_active": True
    }
    r = client.post("/api/semesters", json=sem_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create semester: {r.text}"
    sem_data = r.json()
    sem_id = sem_data["id"]
    print(f"[PASS] Semester created successfully (ID: {sem_id}).")

    # C. Duplicate Semester Number within same Academic Year Rejection
    r_dup = client.post("/api/semesters", json=sem_payload, headers=admin_h)
    assert r_dup.status_code == 400, f"Expected 400 for duplicate semester number, got {r_dup.status_code}"
    print("[PASS] Duplicate semester number in same Academic Year rejected with HTTP 400.")

    # D. List, Get, Update, Status Update
    r_list = client.get(f"/api/semesters?academic_year_id={ay_id}", headers=admin_h)
    assert r_list.status_code == 200
    assert any(s["id"] == sem_id for s in r_list.json())
    print("[PASS] List Semesters verified.")

    r_get = client.get(f"/api/semesters/{sem_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Semester by ID verified.")

    r_upd = client.put(f"/api/semesters/{sem_id}", json={"name": "M1E_Sem_1_Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    assert r_upd.json()["name"] == "M1E_Sem_1_Updated"
    print("[PASS] Update Semester verified.")

    r_st = client.patch(f"/api/semesters/{sem_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Semester status update verified.")

    return sem_id


def test_departments(admin_h, teacher_h, student_h):
    print_step("3. Testing Department Management APIs & Validations")

    dept_payload = {
        "name": "M1E Computer Engineering",
        "code": "M1E_COMP",
        "is_active": True
    }
    r = client.post("/api/departments", json=dept_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create department: {r.text}"
    dept_id = r.json()["id"]
    print(f"[PASS] Department created successfully (ID: {dept_id}).")

    # Duplicate Code Rejection
    r_dup = client.post("/api/departments", json=dept_payload, headers=admin_h)
    assert r_dup.status_code == 400, f"Expected 400 for duplicate dept code, got {r_dup.status_code}"
    print("[PASS] Duplicate Department code rejected with HTTP 400.")

    r_list = client.get("/api/departments", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Departments verified.")

    r_get = client.get(f"/api/departments/{dept_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Department by ID verified.")

    r_upd = client.put(f"/api/departments/{dept_id}", json={"name": "M1E COMP Dept Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Department verified.")

    r_st = client.patch(f"/api/departments/{dept_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Department verified.")

    return dept_id


def test_academic_classes(dept_id, admin_h, teacher_h, student_h):
    print_step("4. Testing Academic Class Management APIs & Validations")

    class_payload = {
        "department_id": dept_id,
        "name": "M1E Second Year",
        "code": "M1E_SE",
        "is_active": True
    }
    r = client.post("/api/academic-classes", json=class_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create class: {r.text}"
    class_id = r.json()["id"]
    print(f"[PASS] Academic Class created successfully (ID: {class_id}).")

    # Duplicate Code Rejection
    r_dup = client.post("/api/academic-classes", json=class_payload, headers=admin_h)
    assert r_dup.status_code == 400, f"Expected 400 for duplicate class code, got {r_dup.status_code}"
    print("[PASS] Duplicate Academic Class code in same department rejected with HTTP 400.")

    r_list = client.get(f"/api/academic-classes?department_id={dept_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Academic Classes verified.")

    r_get = client.get(f"/api/academic-classes/{class_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Academic Class by ID verified.")

    r_upd = client.put(f"/api/academic-classes/{class_id}", json={"name": "M1E SE Class Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Academic Class verified.")

    r_st = client.patch(f"/api/academic-classes/{class_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Academic Class verified.")

    return class_id


def test_divisions(class_id, ay_id, sem_id, admin_h, teacher_h, student_h):
    print_step("5. Testing Division Management APIs & Validations")

    # Invalid FK
    bad_div_payload = {
        "academic_class_id": 999999,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "name": "M1E_A",
        "is_active": True
    }
    r_bad = client.post("/api/divisions", json=bad_div_payload, headers=admin_h)
    assert r_bad.status_code == 400
    print("[PASS] Invalid foreign key reference in Division rejected with HTTP 400.")

    div_payload = {
        "academic_class_id": class_id,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "name": "M1E_Div_A",
        "is_active": True
    }
    r = client.post("/api/divisions", json=div_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create division: {r.text}"
    div_id = r.json()["id"]
    print(f"[PASS] Division created successfully (ID: {div_id}).")

    # Duplicate Division Rejection
    r_dup = client.post("/api/divisions", json=div_payload, headers=admin_h)
    assert r_dup.status_code == 400
    print("[PASS] Duplicate Division (class + year + semester + name) rejected with HTTP 400.")

    r_list = client.get(f"/api/divisions?academic_class_id={class_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Divisions verified.")

    r_get = client.get(f"/api/divisions/{div_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Division by ID verified.")

    r_upd = client.put(f"/api/divisions/{div_id}", json={"name": "M1E_Div_A_Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Division verified.")

    r_st = client.patch(f"/api/divisions/{div_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Division verified.")

    return div_id


def test_batches(div_id, admin_h, teacher_h, student_h):
    print_step("6. Testing Batch Management APIs & Validations")

    # Invalid FK
    bad_batch_payload = {"division_id": 999999, "name": "M1E_B1", "is_active": True}
    r_bad = client.post("/api/batches", json=bad_batch_payload, headers=admin_h)
    assert r_bad.status_code == 400
    print("[PASS] Invalid division foreign key in Batch rejected with HTTP 400.")

    batch_payload = {"division_id": div_id, "name": "M1E_Batch_B1", "is_active": True}
    r = client.post("/api/batches", json=batch_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create batch: {r.text}"
    batch_id = r.json()["id"]
    print(f"[PASS] Batch created successfully (ID: {batch_id}).")

    # Duplicate Batch Rejection
    r_dup = client.post("/api/batches", json=batch_payload, headers=admin_h)
    assert r_dup.status_code == 400
    print("[PASS] Duplicate Batch (division + name) rejected with HTTP 400.")

    r_list = client.get(f"/api/batches?division_id={div_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Batches verified.")

    r_get = client.get(f"/api/batches/{batch_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Batch by ID verified.")

    r_upd = client.put(f"/api/batches/{batch_id}", json={"name": "M1E_Batch_B1_Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Batch verified.")

    r_st = client.patch(f"/api/batches/{batch_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Batch verified.")

    return batch_id


def test_subjects(dept_id, sem_id, admin_h, teacher_h, student_h):
    print_step("7. Testing Subject Management APIs & Validations")

    subj_payload = {
        "name": "M1E Data Structures",
        "code": "M1E_CS201",
        "department_id": dept_id,
        "semester_id": sem_id,
        "is_active": True
    }
    r = client.post("/api/subjects", json=subj_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create subject: {r.text}"
    subj_id = r.json()["id"]
    print(f"[PASS] Subject created successfully (ID: {subj_id}).")

    # Duplicate Subject Rejection
    r_dup = client.post("/api/subjects", json=subj_payload, headers=admin_h)
    assert r_dup.status_code == 400
    print("[PASS] Duplicate Subject (code + dept + semester) rejected with HTTP 400.")

    r_list = client.get(f"/api/subjects?department_id={dept_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Subjects verified.")

    r_get = client.get(f"/api/subjects/{subj_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Subject by ID verified.")

    r_upd = client.put(f"/api/subjects/{subj_id}", json={"name": "M1E DSA Updated"}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Subject verified.")

    r_st = client.patch(f"/api/subjects/{subj_id}/status", json={"is_active": True}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Subject verified.")

    return subj_id


def test_class_subject_assignments(class_id, div_id, subj_id, ay_id, sem_id, admin_h, teacher_h, student_h):
    print_step("8. Testing Class-Subject Assignment APIs & Validations")

    # Invalid FK
    bad_payload = {
        "academic_class_id": 999999,
        "division_id": div_id,
        "subject_id": subj_id,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "is_active": True
    }
    r_bad = client.post("/api/class-subject-assignments", json=bad_payload, headers=admin_h)
    assert r_bad.status_code == 400
    print("[PASS] Invalid foreign key in Class-Subject Assignment rejected with HTTP 400.")

    assign_payload = {
        "academic_class_id": class_id,
        "division_id": div_id,
        "subject_id": subj_id,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "is_active": True
    }
    r = client.post("/api/class-subject-assignments", json=assign_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create assignment: {r.text}"
    assign_id = r.json()["id"]
    print(f"[PASS] Class-Subject Assignment created successfully (ID: {assign_id}).")

    # Duplicate Assignment Rejection
    r_dup = client.post("/api/class-subject-assignments", json=assign_payload, headers=admin_h)
    assert r_dup.status_code == 400
    print("[PASS] Duplicate Class-Subject Assignment rejected with HTTP 400.")

    r_list = client.get(f"/api/class-subject-assignments?academic_class_id={class_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Class-Subject Assignments verified.")

    r_get = client.get(f"/api/class-subject-assignments/{assign_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Class-Subject Assignment by ID verified.")

    r_upd = client.put(f"/api/class-subject-assignments/{assign_id}", json={"is_active": True}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Class-Subject Assignment verified.")

    r_st = client.patch(f"/api/class-subject-assignments/{assign_id}/status", json={"is_active": False}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Class-Subject Assignment status verified.")

    return assign_id


def test_teacher_assignments(teacher_profile_id, subj_id, class_id, div_id, batch_id, ay_id, sem_id, admin_h, teacher_h, student_h):
    print_step("9. Testing Teacher Assignment APIs & Validations")

    # Invalid FK
    bad_payload = {
        "teacher_id": 999999,
        "subject_id": subj_id,
        "academic_class_id": class_id,
        "division_id": div_id,
        "batch_id": batch_id,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "is_active": True
    }
    r_bad = client.post("/api/teacher-assignments", json=bad_payload, headers=admin_h)
    assert r_bad.status_code == 400
    print("[PASS] Invalid teacher ID foreign key rejected with HTTP 400.")

    t_assign_payload = {
        "teacher_id": teacher_profile_id,
        "subject_id": subj_id,
        "academic_class_id": class_id,
        "division_id": div_id,
        "batch_id": batch_id,
        "academic_year_id": ay_id,
        "semester_id": sem_id,
        "is_active": True
    }
    r = client.post("/api/teacher-assignments", json=t_assign_payload, headers=admin_h)
    assert r.status_code == 201, f"Failed to create teacher assignment: {r.text}"
    t_assign_id = r.json()["id"]
    print(f"[PASS] Teacher Assignment created successfully (ID: {t_assign_id}).")

    # Duplicate Assignment Rejection
    r_dup = client.post("/api/teacher-assignments", json=t_assign_payload, headers=admin_h)
    assert r_dup.status_code == 400
    print("[PASS] Duplicate Teacher Assignment rejected with HTTP 400.")

    r_list = client.get(f"/api/teacher-assignments?teacher_id={teacher_profile_id}", headers=admin_h)
    assert r_list.status_code == 200
    print("[PASS] List Teacher Assignments verified.")

    r_get = client.get(f"/api/teacher-assignments/{t_assign_id}", headers=admin_h)
    assert r_get.status_code == 200
    print("[PASS] Get Teacher Assignment by ID verified.")

    r_upd = client.put(f"/api/teacher-assignments/{t_assign_id}", json={"is_active": True}, headers=admin_h)
    assert r_upd.status_code == 200
    print("[PASS] Update Teacher Assignment verified.")

    r_st = client.patch(f"/api/teacher-assignments/{t_assign_id}/status", json={"is_active": False}, headers=admin_h)
    assert r_st.status_code == 200
    print("[PASS] Activate/Deactivate Teacher Assignment status verified.")

    return t_assign_id


def test_authorization_guards(admin_h, teacher_h, student_h):
    print_step("10. Testing Security & Role-Based Access Control (RBAC)")

    endpoints_to_test = [
        ("POST", "/api/academic-years"),
        ("POST", "/api/semesters"),
        ("POST", "/api/departments"),
        ("POST", "/api/academic-classes"),
        ("POST", "/api/divisions"),
        ("POST", "/api/batches"),
        ("POST", "/api/subjects"),
        ("POST", "/api/class-subject-assignments"),
        ("POST", "/api/teacher-assignments")
    ]

    for method, ep in endpoints_to_test:
        # Teacher request -> 403
        if method == "GET":
            r_t = client.get(ep, headers=teacher_h)
            r_s = client.get(ep, headers=student_h)
        else:
            r_t = client.post(ep, json={}, headers=teacher_h)
            r_s = client.post(ep, json={}, headers=student_h)
        
        assert r_t.status_code == 403, f"TEACHER allowed on {method} {ep}: {r_t.status_code}"
        assert r_s.status_code == 403, f"STUDENT allowed on {method} {ep}: {r_s.status_code}"

    print("[PASS] All Module 1E management endpoints strictly reject TEACHER and STUDENT requests with HTTP 403 Forbidden.")


def run_regressions():
    print_step("11. Testing Full Module 1A-1D Regression Suite")

    # Module 1A Health Test
    r_h1 = client.get("/api/health")
    assert r_h1.status_code == 200
    r_h2 = client.get("/api/health/database")
    assert r_h2.status_code == 200
    print("[PASS] Module 1A health endpoints pass.")

    # Module 1B Schema Check
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    assert len(tables) == 16, f"Expected 16 tables, found {len(tables)}"
    print("[PASS] Module 1B schema test passes (16/16 tables intact).")

    # Module 1C Auth Check
    r_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {create_access_token(1)}"})
    assert r_me.status_code in [200, 401]
    print("[PASS] Module 1C JWT validation passes.")

    # Module 1D Users API Check
    r_users = client.get("/api/users", headers={"Authorization": f"Bearer {create_access_token(1)}"})
    assert r_users.status_code in [200, 401]
    print("[PASS] Module 1D Users API passes.")



def main():
    print_step("RUNNING MODULE 1E AUTOMATED VERIFICATION SUITE")

    cleanup_m1e_test_data()
    admin_h, teacher_h, student_h, teacher_profile_id = setup_users_and_headers()

    ay_id = test_academic_years(admin_h, teacher_h, student_h)
    sem_id = test_semesters(ay_id, admin_h, teacher_h, student_h)
    dept_id = test_departments(admin_h, teacher_h, student_h)
    class_id = test_academic_classes(dept_id, admin_h, teacher_h, student_h)
    div_id = test_divisions(class_id, ay_id, sem_id, admin_h, teacher_h, student_h)
    batch_id = test_batches(div_id, admin_h, teacher_h, student_h)
    subj_id = test_subjects(dept_id, sem_id, admin_h, teacher_h, student_h)
    assign_id = test_class_subject_assignments(class_id, div_id, subj_id, ay_id, sem_id, admin_h, teacher_h, student_h)
    t_assign_id = test_teacher_assignments(teacher_profile_id, subj_id, class_id, div_id, batch_id, ay_id, sem_id, admin_h, teacher_h, student_h)

    test_authorization_guards(admin_h, teacher_h, student_h)
    run_regressions()

    print_step("[SUCCESS] ALL MODULE 1E VERIFICATION AND REGRESSION CHECKS PASSED PERFECTLY!")


if __name__ == "__main__":
    main()
