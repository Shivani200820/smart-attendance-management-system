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
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.enums import UserRole, SessionStatus, AttendanceStatus, AttendanceSource

client = TestClient(app)


def print_step(title: str):
    print(f"\n==========================================", flush=True)
    print(f"  {title}", flush=True)
    print(f"==========================================", flush=True)


def cleanup_m1j_test_data():
    db = SessionLocal()
    try:
        db.query(AttendanceRecord).filter(
            AttendanceRecord.student.has(Student.student_id.like("M1J_%"))
        ).delete(synchronize_session=False)

        db.query(AttendanceSession).filter(
            AttendanceSession.academic_year.has(AcademicYear.name.like("M1J_%"))
        ).delete(synchronize_session=False)

        for st in db.query(Student).filter(Student.student_id.like("M1J_%")).all():
            db.delete(st)

        for t in db.query(Teacher).filter(Teacher.employee_id.like("M1J_%")).all():
            db.delete(t)

        for username in ["m1j_admin", "m1j_teacher", "m1j_good_student", "m1j_defaulter_student"]:
            u = db.query(User).filter(User.username == username).first()
            if u:
                db.delete(u)

        db.commit()

        db.query(Subject).filter(Subject.code.like("M1J_%")).delete(synchronize_session=False)
        db.query(Batch).filter(Batch.name.like("M1J_%")).delete(synchronize_session=False)
        db.query(Division).filter(Division.name.like("M1J_%")).delete(synchronize_session=False)
        db.query(AcademicClass).filter(AcademicClass.code.like("M1J_%")).delete(synchronize_session=False)
        db.query(Department).filter(Department.code.like("M1J_%")).delete(synchronize_session=False)
        db.query(Semester).filter(Semester.name.like("M1J_%")).delete(synchronize_session=False)
        db.query(AcademicYear).filter(AcademicYear.name.like("M1J_%")).delete(synchronize_session=False)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Test data cleanup encountered: {e}", flush=True)
    finally:
        db.close()


def setup_prerequisite_m1j_data():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "m1j_admin").first()
        if not admin:
            admin = User(username="m1j_admin", email="m1j_admin@test.com", password_hash=hash_password("Pass123!"), role=UserRole.ADMIN)
            db.add(admin)
            db.commit()

        dept = db.query(Department).filter(Department.code == "M1J_CS").first()
        if not dept:
            dept = Department(name="M1J Dept", code="M1J_CS")
            db.add(dept)
            db.commit()

        year = db.query(AcademicYear).filter(AcademicYear.name == "M1J_2026-27").first()
        if not year:
            year = AcademicYear(name="M1J_2026-27", start_date=date(2026, 6, 1), end_date=date(2027, 5, 31))
            db.add(year)
            db.commit()

        sem = db.query(Semester).filter(Semester.name == "M1J_Sem 5").first()
        if not sem:
            sem = Semester(academic_year_id=year.id, semester_number=5, name="M1J_Sem 5")
            db.add(sem)
            db.commit()

        ac_class = db.query(AcademicClass).filter(AcademicClass.code == "M1J_TE").first()
        if not ac_class:
            ac_class = AcademicClass(department_id=dept.id, name="M1J Class", code="M1J_TE")
            db.add(ac_class)
            db.commit()

        div = db.query(Division).filter(Division.name == "M1J_Div A").first()
        if not div:
            div = Division(academic_class_id=ac_class.id, academic_year_id=year.id, semester_id=sem.id, name="M1J_Div A")
            db.add(div)
            db.commit()

        batch = db.query(Batch).filter(Batch.name == "M1J_A1").first()
        if not batch:
            batch = Batch(division_id=div.id, name="M1J_A1")
            db.add(batch)
            db.commit()

        sub1 = db.query(Subject).filter(Subject.code == "M1J_SE101").first()
        if not sub1:
            sub1 = Subject(department_id=dept.id, semester_id=sem.id, name="M1J Software Engg", code="M1J_SE101")
            db.add(sub1)
            db.commit()

        sub2 = db.query(Subject).filter(Subject.code == "M1J_DB102").first()
        if not sub2:
            sub2 = Subject(department_id=dept.id, semester_id=sem.id, name="M1J Database Systems", code="M1J_DB102")
            db.add(sub2)
            db.commit()

        t_user = db.query(User).filter(User.username == "m1j_teacher").first()
        if not t_user:
            t_user = User(username="m1j_teacher", email="m1j_t@test.com", password_hash=hash_password("Pass123!"), role=UserRole.TEACHER)
            db.add(t_user)
            db.commit()

        teacher = db.query(Teacher).filter(Teacher.employee_id == "M1J_T01").first()
        if not teacher:
            teacher = Teacher(user_id=t_user.id, employee_id="M1J_T01", full_name="M1J Teacher", email="m1j_t@test.com", department_id=dept.id)
            db.add(teacher)
            db.commit()

        # Good Student (Attends 100% of sessions)
        gs_user = db.query(User).filter(User.username == "m1j_good_student").first()
        if not gs_user:
            gs_user = User(username="m1j_good_student", email="m1j_gs@test.com", password_hash=hash_password("Pass123!"), role=UserRole.STUDENT)
            db.add(gs_user)
            db.commit()

        good_student = db.query(Student).filter(Student.student_id == "M1J_S01").first()
        if not good_student:
            good_student = Student(
                user_id=gs_user.id, student_id="M1J_S01", roll_number="401", enrollment_number="M1J_EN401",
                full_name="Good Student", email="m1j_gs@test.com", department_id=dept.id, academic_class_id=ac_class.id,
                division_id=div.id, batch_id=batch.id, academic_year_id=year.id, semester_id=sem.id
            )
            db.add(good_student)
            db.commit()

        # Defaulter Student (Attends 0% of sessions)
        ds_user = db.query(User).filter(User.username == "m1j_defaulter_student").first()
        if not ds_user:
            ds_user = User(username="m1j_defaulter_student", email="m1j_ds@test.com", password_hash=hash_password("Pass123!"), role=UserRole.STUDENT)
            db.add(ds_user)
            db.commit()

        defaulter_student = db.query(Student).filter(Student.student_id == "M1J_S02").first()
        if not defaulter_student:
            defaulter_student = Student(
                user_id=ds_user.id, student_id="M1J_S02", roll_number="402", enrollment_number="M1J_EN402",
                full_name="Defaulter Student", email="m1j_ds@test.com", department_id=dept.id, academic_class_id=ac_class.id,
                division_id=div.id, batch_id=batch.id, academic_year_id=year.id, semester_id=sem.id
            )
            db.add(defaulter_student)
            db.commit()

        admin_token = create_access_token(subject=admin.id, extra_data={"role": UserRole.ADMIN.value, "username": admin.username})
        t_token = create_access_token(subject=t_user.id, extra_data={"role": UserRole.TEACHER.value, "username": t_user.username})
        gs_token = create_access_token(subject=gs_user.id, extra_data={"role": UserRole.STUDENT.value, "username": gs_user.username})

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        t_headers = {"Authorization": f"Bearer {t_token}"}
        gs_headers = {"Authorization": f"Bearer {gs_token}"}

        ids = {
            "year_id": year.id, "sem_id": sem.id, "div_id": div.id, "batch_id": batch.id,
            "sub1_id": sub1.id, "sub2_id": sub2.id, "teacher_id": teacher.id,
            "good_student_id": good_student.id, "defaulter_student_id": defaulter_student.id
        }

        return admin_headers, t_headers, gs_headers, ids
    finally:
        db.close()


def test_module_1j_functional(admin_h, t_h, gs_h, ids):
    print_step("Testing Module 1J Attendance Reports & Analytics")

    # 1. Create sessions for Subject 1 and Subject 2
    exp_time = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    s1_payload = {
        "academic_year_id": ids["year_id"], "semester_id": ids["sem_id"], "division_id": ids["div_id"],
        "batch_id": ids["batch_id"], "subject_id": ids["sub1_id"], "teacher_id": ids["teacher_id"],
        "session_date": str(date.today()), "start_time": "09:00:00", "end_time": "10:00:00", "expires_at": exp_time
    }
    r_s1 = client.post("/api/attendance-sessions", json=s1_payload, headers=t_h)
    assert r_s1.status_code == 201
    s1_id = r_s1.json()["id"]

    s2_payload = {
        "academic_year_id": ids["year_id"], "semester_id": ids["sem_id"], "division_id": ids["div_id"],
        "batch_id": ids["batch_id"], "subject_id": ids["sub2_id"], "teacher_id": ids["teacher_id"],
        "session_date": str(date.today()), "start_time": "10:00:00", "end_time": "11:00:00", "expires_at": exp_time
    }
    r_s2 = client.post("/api/attendance-sessions", json=s2_payload, headers=t_h)
    assert r_s2.status_code == 201
    s2_id = r_s2.json()["id"]

    # 2. Mark good_student PRESENT for both, defaulter ABSENT for both
    client.post(f"/api/attendance/sessions/{s1_id}/manual-mark", json={
        "records": [
            {"student_id": ids["good_student_id"], "status": "PRESENT"},
            {"student_id": ids["defaulter_student_id"], "status": "ABSENT"}
        ]
    }, headers=t_h)

    client.post(f"/api/attendance/sessions/{s2_id}/manual-mark", json={
        "records": [
            {"student_id": ids["good_student_id"], "status": "PRESENT"},
            {"student_id": ids["defaulter_student_id"], "status": "ABSENT"}
        ]
    }, headers=t_h)
    print("[PASS] Created test attendance records (Good Student: 100%, Defaulter Student: 0%).", flush=True)

    # 3. Test Student Personal Summary Endpoint
    r_my_summary = client.get("/api/attendance/my-summary", headers=gs_h)
    assert r_my_summary.status_code == 200, f"Summary failed: {r_my_summary.text}"
    summary = r_my_summary.json()
    assert summary["overall_percentage"] == 100.0
    assert len(summary["subject_breakdown"]) >= 2
    print(f"[PASS] Student personal summary verified (Overall: {summary['overall_percentage']}%, Subjects: {len(summary['subject_breakdown'])}).", flush=True)

    # 4. Test Defaulter Report (<75%)
    r_defaulter = client.get(f"/api/reports/defaulters?division_id={ids['div_id']}&threshold_percentage=75.0", headers=admin_h)
    assert r_defaulter.status_code == 200, f"Defaulter report failed: {r_defaulter.text}"
    defaulter_rep = r_defaulter.json()
    assert defaulter_rep["defaulters_count"] >= 1
    defaulters_ids = [d["student_id"] for d in defaulter_rep["defaulters"]]
    assert ids["defaulter_student_id"] in defaulters_ids
    assert ids["good_student_id"] not in defaulters_ids
    print(f"[PASS] Defaulters report verified (Found {defaulter_rep['defaulters_count']} defaulter(s), Defaulter Student ID {ids['defaulter_student_id']} accurately identified).", flush=True)


def main():
    print_step("RUNNING MODULE 1J AUTOMATED VERIFICATION SUITE")
    cleanup_m1j_test_data()
    admin_h, t_h, gs_h, ids = setup_prerequisite_m1j_data()
    test_module_1j_functional(admin_h, t_h, gs_h, ids)
    print_step("[SUCCESS] ALL MODULE 1J VERIFICATION CHECKS PASSED PERFECTLY!")


if __name__ == "__main__":
    main()
