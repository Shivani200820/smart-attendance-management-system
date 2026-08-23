import sys
from datetime import date, time as time_type, datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.profiles import Teacher, Student
from app.models.academic import Department, AcademicClass, Division, Batch, AcademicYear, Semester
from app.models.subject import Subject
from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceCorrection
from app.models.enums import UserRole, SessionStatus, AttendanceStatus, AttendanceSource

client = TestClient(app)


def print_step(title: str):
    print(f"\n==========================================", flush=True)
    print(f"  {title}", flush=True)
    print(f"==========================================", flush=True)


def cleanup_m1h_test_data():
    db = SessionLocal()
    try:
        # Delete corrections
        db.query(AttendanceCorrection).filter(
            AttendanceCorrection.corrector.has(User.username.like("m1h_%"))
        ).delete(synchronize_session=False)

        # Delete records
        db.query(AttendanceRecord).filter(
            AttendanceRecord.student.has(Student.student_id.like("M1H_%"))
        ).delete(synchronize_session=False)

        # Delete sessions
        db.query(AttendanceSession).filter(
            AttendanceSession.academic_year.has(AcademicYear.name.like("M1H_%"))
        ).delete(synchronize_session=False)

        # Delete students & teachers profiles first
        for st in db.query(Student).filter(Student.student_id.like("M1H_%")).all():
            db.delete(st)

        for t in db.query(Teacher).filter(Teacher.employee_id.like("M1H_%")).all():
            db.delete(t)

        for username in ["m1h_admin", "m1h_teacher", "m1h_s1_user", "m1h_s2_user"]:
            u = db.query(User).filter(User.username == username).first()
            if u:
                db.delete(u)

        db.commit()

        # Delete academic structure
        db.query(Subject).filter(Subject.code.like("M1H_%")).delete(synchronize_session=False)
        db.query(Batch).filter(Batch.name.like("M1H_%")).delete(synchronize_session=False)
        db.query(Division).filter(Division.name.like("M1H_%")).delete(synchronize_session=False)
        db.query(AcademicClass).filter(AcademicClass.code.like("M1H_%")).delete(synchronize_session=False)
        db.query(Department).filter(Department.code.like("M1H_%")).delete(synchronize_session=False)
        db.query(Semester).filter(Semester.name.like("M1H_%")).delete(synchronize_session=False)
        db.query(AcademicYear).filter(AcademicYear.name.like("M1H_%")).delete(synchronize_session=False)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Test data cleanup encountered: {e}", flush=True)
    finally:
        db.close()


def setup_prerequisite_m1h_data():
    db = SessionLocal()
    try:
        # Admin
        admin = db.query(User).filter(User.username == "m1h_admin").first()
        if not admin:
            admin = User(username="m1h_admin", email="m1h_admin@test.com", password_hash=hash_password("Pass123!"), role=UserRole.ADMIN)
            db.add(admin)
            db.commit()

        # Dept
        dept = db.query(Department).filter(Department.code == "M1H_CS").first()
        if not dept:
            dept = Department(name="M1H Dept", code="M1H_CS")
            db.add(dept)
            db.commit()

        # Year
        year = db.query(AcademicYear).filter(AcademicYear.name == "M1H_2026-27").first()
        if not year:
            year = AcademicYear(name="M1H_2026-27", start_date=date(2026, 6, 1), end_date=date(2027, 5, 31))
            db.add(year)
            db.commit()

        # Semester
        sem = db.query(Semester).filter(Semester.name == "M1H_Sem 5").first()
        if not sem:
            sem = Semester(academic_year_id=year.id, semester_number=5, name="M1H_Sem 5")
            db.add(sem)
            db.commit()

        # Academic Class
        ac_class = db.query(AcademicClass).filter(AcademicClass.code == "M1H_TE").first()
        if not ac_class:
            ac_class = AcademicClass(department_id=dept.id, name="M1H Class", code="M1H_TE")
            db.add(ac_class)
            db.commit()

        # Divisions
        div_a = db.query(Division).filter(Division.name == "M1H_Div A").first()
        if not div_a:
            div_a = Division(academic_class_id=ac_class.id, academic_year_id=year.id, semester_id=sem.id, name="M1H_Div A")
            db.add(div_a)
            db.commit()

        div_b = db.query(Division).filter(Division.name == "M1H_Div B").first()
        if not div_b:
            div_b = Division(academic_class_id=ac_class.id, academic_year_id=year.id, semester_id=sem.id, name="M1H_Div B")
            db.add(div_b)
            db.commit()

        # Batches
        batch_a1 = db.query(Batch).filter(Batch.name == "M1H_A1").first()
        if not batch_a1:
            batch_a1 = Batch(division_id=div_a.id, name="M1H_A1")
            db.add(batch_a1)
            db.commit()

        batch_b1 = db.query(Batch).filter(Batch.name == "M1H_B1").first()
        if not batch_b1:
            batch_b1 = Batch(division_id=div_b.id, name="M1H_B1")
            db.add(batch_b1)
            db.commit()

        # Subject
        subject = db.query(Subject).filter(Subject.code == "M1H_SE101").first()
        if not subject:
            subject = Subject(department_id=dept.id, semester_id=sem.id, name="M1H Software Engg", code="M1H_SE101")
            db.add(subject)
            db.commit()

        # Teacher
        t_user = db.query(User).filter(User.username == "m1h_teacher").first()
        if not t_user:
            t_user = User(username="m1h_teacher", email="m1h_t@test.com", password_hash=hash_password("Pass123!"), role=UserRole.TEACHER)
            db.add(t_user)
            db.commit()

        teacher = db.query(Teacher).filter(Teacher.employee_id == "M1H_T01").first()
        if not teacher:
            teacher = Teacher(user_id=t_user.id, employee_id="M1H_T01", full_name="M1H Prof Smith", email="m1h_t@test.com", department_id=dept.id)
            db.add(teacher)
            db.commit()

        # Student 1
        s1_user = db.query(User).filter(User.username == "m1h_s1_user").first()
        if not s1_user:
            s1_user = User(username="m1h_s1_user", email="m1h_s1@test.com", password_hash=hash_password("Pass123!"), role=UserRole.STUDENT)
            db.add(s1_user)
            db.commit()

        s1_profile = db.query(Student).filter(Student.student_id == "M1H_S01").first()
        if not s1_profile:
            s1_profile = Student(
                user_id=s1_user.id, student_id="M1H_S01", roll_number="101", enrollment_number="M1H_EN101",
                full_name="Student One", email="m1h_s1@test.com", department_id=dept.id, academic_class_id=ac_class.id,
                division_id=div_a.id, batch_id=batch_a1.id, academic_year_id=year.id, semester_id=sem.id
            )
            db.add(s1_profile)
            db.commit()

        # Student 2
        s2_user = db.query(User).filter(User.username == "m1h_s2_user").first()
        if not s2_user:
            s2_user = User(username="m1h_s2_user", email="m1h_s2@test.com", password_hash=hash_password("Pass123!"), role=UserRole.STUDENT)
            db.add(s2_user)
            db.commit()

        s2_profile = db.query(Student).filter(Student.student_id == "M1H_S02").first()
        if not s2_profile:
            s2_profile = Student(
                user_id=s2_user.id, student_id="M1H_S02", roll_number="201", enrollment_number="M1H_EN201",
                full_name="Student Two", email="m1h_s2@test.com", department_id=dept.id, academic_class_id=ac_class.id,
                division_id=div_b.id, batch_id=batch_b1.id, academic_year_id=year.id, semester_id=sem.id
            )
            db.add(s2_profile)
            db.commit()

        t_token = create_access_token(subject=t_user.id, extra_data={"role": UserRole.TEACHER.value, "username": t_user.username})
        s1_token = create_access_token(subject=s1_user.id, extra_data={"role": UserRole.STUDENT.value, "username": s1_user.username})
        s2_token = create_access_token(subject=s2_user.id, extra_data={"role": UserRole.STUDENT.value, "username": s2_user.username})

        t_headers = {"Authorization": f"Bearer {t_token}"}
        s1_headers = {"Authorization": f"Bearer {s1_token}"}
        s2_headers = {"Authorization": f"Bearer {s2_token}"}

        ids = {
            "year_id": year.id, "sem_id": sem.id, "div_a_id": div_a.id, "div_b_id": div_b.id,
            "batch_a1_id": batch_a1.id, "sub_id": subject.id, "teacher_id": teacher.id,
            "s1_id": s1_profile.id, "s2_id": s2_profile.id
        }

        return t_headers, s1_headers, s2_headers, ids
    finally:
        db.close()


def test_module_1h_functional(t_h, s1_h, s2_h, ids):
    print_step("Testing Module 1H Attendance Marking Functionality")

    # 1. Teacher creates active session for Div A
    exp_time = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    session_payload = {
        "academic_year_id": ids["year_id"],
        "semester_id": ids["sem_id"],
        "division_id": ids["div_a_id"],
        "batch_id": ids["batch_a1_id"],
        "subject_id": ids["sub_id"],
        "teacher_id": ids["teacher_id"],
        "session_date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "expires_at": exp_time
    }

    r_create = client.post("/api/attendance-sessions", json=session_payload, headers=t_h)
    if r_create.status_code != 201:
        print(f"FAILED CREATE SESSION: {r_create.status_code} - {r_create.text}", flush=True)
    assert r_create.status_code == 201, f"Session create failed: {r_create.text}"
    session_id = r_create.json()["id"]
    token = r_create.json()["session_token"]
    print(f"[PASS] Created active session ID {session_id} with token {token[:10]}...", flush=True)

    # 2. Unauthenticated student mark attempt -> HTTP 401
    r_unauth = client.post("/api/attendance/mark", json={"session_token": token})
    assert r_unauth.status_code == 401
    print("[PASS] Unauthenticated mark attempt rejected with HTTP 401 Unauthorized.", flush=True)

    # 3. Student 2 (Div B) attempts to mark attendance for Div A session -> HTTP 403 Forbidden
    r_s2_mark = client.post("/api/attendance/mark", json={"session_token": token}, headers=s2_h)
    assert r_s2_mark.status_code == 403, f"Cross division mark should fail: {r_s2_mark.text}"
    print("[PASS] Cross-division student mark attempt rejected with HTTP 403 Forbidden.", flush=True)

    # 4. Student 1 (Div A, Batch A1) marks attendance -> HTTP 201 Created
    r_s1_mark = client.post("/api/attendance/mark", json={"session_token": token}, headers=s1_h)
    assert r_s1_mark.status_code == 201, f"Student mark failed: {r_s1_mark.text}"
    rec = r_s1_mark.json()
    assert rec["status"] == "PRESENT"
    assert rec["source"] == "QR"
    assert rec["student_roll_number"] == "101"
    print(f"[PASS] Student 1 marked attendance successfully (Record ID: {rec['id']}, Status: PRESENT).", flush=True)

    # 5. Student 1 attempts to mark AGAIN -> HTTP 409 Conflict (Duplicate)
    r_dup = client.post("/api/attendance/mark", json={"session_token": token}, headers=s1_h)
    assert r_dup.status_code == 409, f"Duplicate mark should fail: {r_dup.text}"
    print("[PASS] Duplicate attendance marking rejected with HTTP 409 Conflict.", flush=True)

    # 6. Teacher manual marking endpoint test
    manual_payload = {
        "records": [
            {"student_id": ids["s1_id"], "status": "PRESENT"}
        ]
    }
    r_manual = client.post(f"/api/attendance/sessions/{session_id}/manual-mark", json=manual_payload, headers=t_h)
    assert r_manual.status_code == 200, f"Manual mark failed: {r_manual.text}"
    print(f"[PASS] Teacher manual batch marking verified (Updated {len(r_manual.json())} record).", flush=True)

    # 7. Teacher views session records -> HTTP 200
    r_records = client.get(f"/api/attendance/sessions/{session_id}/records", headers=t_h)
    assert r_records.status_code == 200
    assert len(r_records.json()) >= 1
    print(f"[PASS] Retrieved session attendance records successfully ({len(r_records.json())} items).", flush=True)


def main():
    print_step("RUNNING MODULE 1H AUTOMATED VERIFICATION SUITE")
    cleanup_m1h_test_data()
    t_h, s1_h, s2_h, ids = setup_prerequisite_m1h_data()
    test_module_1h_functional(t_h, s1_h, s2_h, ids)
    print_step("[SUCCESS] ALL MODULE 1H VERIFICATION CHECKS PASSED PERFECTLY!")


if __name__ == "__main__":
    main()
