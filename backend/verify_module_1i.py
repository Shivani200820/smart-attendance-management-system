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


def cleanup_m1i_test_data():
    db = SessionLocal()
    try:
        db.query(AttendanceCorrection).filter(
            AttendanceCorrection.corrector.has(User.username.like("m1i_%"))
        ).delete(synchronize_session=False)

        db.query(AttendanceRecord).filter(
            AttendanceRecord.student.has(Student.student_id.like("M1I_%"))
        ).delete(synchronize_session=False)

        db.query(AttendanceSession).filter(
            AttendanceSession.academic_year.has(AcademicYear.name.like("M1I_%"))
        ).delete(synchronize_session=False)

        for st in db.query(Student).filter(Student.student_id.like("M1I_%")).all():
            db.delete(st)

        for t in db.query(Teacher).filter(Teacher.employee_id.like("M1I_%")).all():
            db.delete(t)

        for username in ["m1i_admin", "m1i_teacher", "m1i_student"]:
            u = db.query(User).filter(User.username == username).first()
            if u:
                db.delete(u)

        db.commit()

        db.query(Subject).filter(Subject.code.like("M1I_%")).delete(synchronize_session=False)
        db.query(Batch).filter(Batch.name.like("M1I_%")).delete(synchronize_session=False)
        db.query(Division).filter(Division.name.like("M1I_%")).delete(synchronize_session=False)
        db.query(AcademicClass).filter(AcademicClass.code.like("M1I_%")).delete(synchronize_session=False)
        db.query(Department).filter(Department.code.like("M1I_%")).delete(synchronize_session=False)
        db.query(Semester).filter(Semester.name.like("M1I_%")).delete(synchronize_session=False)
        db.query(AcademicYear).filter(AcademicYear.name.like("M1I_%")).delete(synchronize_session=False)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Test data cleanup encountered: {e}", flush=True)
    finally:
        db.close()


def setup_prerequisite_m1i_data():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "m1i_admin").first()
        if not admin:
            admin = User(username="m1i_admin", email="m1i_admin@test.com", password_hash=hash_password("Pass123!"), role=UserRole.ADMIN)
            db.add(admin)
            db.commit()

        dept = db.query(Department).filter(Department.code == "M1I_CS").first()
        if not dept:
            dept = Department(name="M1I Dept", code="M1I_CS")
            db.add(dept)
            db.commit()

        year = db.query(AcademicYear).filter(AcademicYear.name == "M1I_2026-27").first()
        if not year:
            year = AcademicYear(name="M1I_2026-27", start_date=date(2026, 6, 1), end_date=date(2027, 5, 31))
            db.add(year)
            db.commit()

        sem = db.query(Semester).filter(Semester.name == "M1I_Sem 5").first()
        if not sem:
            sem = Semester(academic_year_id=year.id, semester_number=5, name="M1I_Sem 5")
            db.add(sem)
            db.commit()

        ac_class = db.query(AcademicClass).filter(AcademicClass.code == "M1I_TE").first()
        if not ac_class:
            ac_class = AcademicClass(department_id=dept.id, name="M1I Class", code="M1I_TE")
            db.add(ac_class)
            db.commit()

        div = db.query(Division).filter(Division.name == "M1I_Div A").first()
        if not div:
            div = Division(academic_class_id=ac_class.id, academic_year_id=year.id, semester_id=sem.id, name="M1I_Div A")
            db.add(div)
            db.commit()

        batch = db.query(Batch).filter(Batch.name == "M1I_A1").first()
        if not batch:
            batch = Batch(division_id=div.id, name="M1I_A1")
            db.add(batch)
            db.commit()

        subject = db.query(Subject).filter(Subject.code == "M1I_SE101").first()
        if not subject:
            subject = Subject(department_id=dept.id, semester_id=sem.id, name="M1I Subject", code="M1I_SE101")
            db.add(subject)
            db.commit()

        t_user = db.query(User).filter(User.username == "m1i_teacher").first()
        if not t_user:
            t_user = User(username="m1i_teacher", email="m1i_t@test.com", password_hash=hash_password("Pass123!"), role=UserRole.TEACHER)
            db.add(t_user)
            db.commit()

        teacher = db.query(Teacher).filter(Teacher.employee_id == "M1I_T01").first()
        if not teacher:
            teacher = Teacher(user_id=t_user.id, employee_id="M1I_T01", full_name="M1I Teacher", email="m1i_t@test.com", department_id=dept.id)
            db.add(teacher)
            db.commit()

        s_user = db.query(User).filter(User.username == "m1i_student").first()
        if not s_user:
            s_user = User(username="m1i_student", email="m1i_s@test.com", password_hash=hash_password("Pass123!"), role=UserRole.STUDENT)
            db.add(s_user)
            db.commit()

        student = db.query(Student).filter(Student.student_id == "M1I_S01").first()
        if not student:
            student = Student(
                user_id=s_user.id, student_id="M1I_S01", roll_number="301", enrollment_number="M1I_EN301",
                full_name="M1I Student", email="m1i_s@test.com", department_id=dept.id, academic_class_id=ac_class.id,
                division_id=div.id, batch_id=batch.id, academic_year_id=year.id, semester_id=sem.id
            )
            db.add(student)
            db.commit()

        t_token = create_access_token(subject=t_user.id, extra_data={"role": UserRole.TEACHER.value, "username": t_user.username})
        s_token = create_access_token(subject=s_user.id, extra_data={"role": UserRole.STUDENT.value, "username": s_user.username})

        t_headers = {"Authorization": f"Bearer {t_token}"}
        s_headers = {"Authorization": f"Bearer {s_token}"}

        ids = {
            "year_id": year.id, "sem_id": sem.id, "div_id": div.id, "batch_id": batch.id,
            "sub_id": subject.id, "teacher_id": teacher.id, "student_id": student.id
        }

        return t_headers, s_headers, ids
    finally:
        db.close()


def test_module_1i_functional(t_h, s_h, ids):
    print_step("Testing Module 1I Attendance Corrections & Audit Trail")

    # 1. Create session and mark student as ABSENT
    exp_time = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    session_payload = {
        "academic_year_id": ids["year_id"],
        "semester_id": ids["sem_id"],
        "division_id": ids["div_id"],
        "batch_id": ids["batch_id"],
        "subject_id": ids["sub_id"],
        "teacher_id": ids["teacher_id"],
        "session_date": str(date.today()),
        "start_time": "11:00:00",
        "end_time": "12:00:00",
        "expires_at": exp_time
    }
    r_sess = client.post("/api/attendance-sessions", json=session_payload, headers=t_h)
    assert r_sess.status_code == 201
    sess_id = r_sess.json()["id"]

    # Mark initial ABSENT status via teacher manual mark
    r_init = client.post(f"/api/attendance/sessions/{sess_id}/manual-mark", json={
        "records": [{"student_id": ids["student_id"], "status": "ABSENT"}]
    }, headers=t_h)
    assert r_init.status_code == 200
    rec_id = r_init.json()[0]["id"]
    print(f"[PASS] Created initial AttendanceRecord ID {rec_id} with status ABSENT.", flush=True)

    # 2. Student attempts to correct record -> HTTP 403 Forbidden
    r_student_correct = client.patch(f"/api/attendance/records/{rec_id}/correct", json={
        "new_status": "PRESENT",
        "reason": "Student attempt"
    }, headers=s_h)
    assert r_student_correct.status_code == 403
    print("[PASS] Student correction attempt rejected with HTTP 403 Forbidden.", flush=True)

    # 3. Teacher corrects record from ABSENT to PRESENT with reason -> HTTP 200 OK
    corr_payload = {
        "new_status": "PRESENT",
        "reason": "Submitted valid medical leave certificate"
    }
    r_corr = client.patch(f"/api/attendance/records/{rec_id}/correct", json=corr_payload, headers=t_h)
    assert r_corr.status_code == 200, f"Correction failed: {r_corr.text}"
    corr_res = r_corr.json()
    assert corr_res["old_status"] == "ABSENT"
    assert corr_res["new_status"] == "PRESENT"
    assert corr_res["reason"] == corr_payload["reason"]
    print(f"[PASS] Teacher corrected AttendanceRecord ID {rec_id} to PRESENT with audit entry ID {corr_res['id']}.", flush=True)

    # 4. Verify record status is updated to PRESENT and source is CORRECTION
    r_recs = client.get(f"/api/attendance/sessions/{sess_id}/records", headers=t_h)
    assert r_recs.status_code == 200
    updated_rec = [r for r in r_recs.json() if r["id"] == rec_id][0]
    assert updated_rec["status"] == "PRESENT"
    assert updated_rec["source"] == "CORRECTION"
    print("[PASS] AttendanceRecord status verified as PRESENT with source=CORRECTION.", flush=True)


def main():
    print_step("RUNNING MODULE 1I AUTOMATED VERIFICATION SUITE")
    cleanup_m1i_test_data()
    t_h, s_h, ids = setup_prerequisite_m1i_data()
    test_module_1i_functional(t_h, s_h, ids)
    print_step("[SUCCESS] ALL MODULE 1I VERIFICATION CHECKS PASSED PERFECTLY!")


if __name__ == "__main__":
    main()
