import sys
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole, SessionStatus, AttendanceStatus, AttendanceSource
from app.models.academic import Department, AcademicYear, Semester, AcademicClass, Division, Batch
from app.models.profiles import Teacher, Student
from app.models.subject import Subject
from app.models.assignments import ClassSubjectAssignment, TeacherAssignment
from app.models.timetable import Timetable
from app.models.attendance import AttendanceSession, AttendanceRecord, SessionStatus, AttendanceStatus


def seed_data():
    """
    Seeds realistic fictional Indian college data for JSPM's Bhivrabai Sawant Polytechnic, Pune, Maharashtra.
    Preserves existing user test accounts required for verification scripts while decorating them with
    realistic Indian profile names.
    """
    print("=======================================================")
    print(" SEEDING INDIAN COLLEGE DATA (JSPM's Bhivrabai Sawant Polytechnic)")
    print("=======================================================")

    db = SessionLocal()
    try:
        # 1. Departments
        depts_data = [
            ("Computer Engineering", "COMP"),
            ("Information Technology", "IT"),
            ("Artificial Intelligence & Data Science", "AIDS"),
            ("Electronics & Telecommunication", "ENTC"),
            ("Mechanical Engineering", "MECH"),
            ("Civil Engineering", "CIVIL")
        ]

        dept_map = {}
        for name, code in depts_data:
            dept = db.query(Department).filter(Department.code == code).first()
            if not dept:
                dept = Department(name=name, code=code, is_active=True)
                db.add(dept)
                db.flush()
            else:
                dept.name = name
                db.flush()
            dept_map[code] = dept

        comp_dept = dept_map["COMP"]

        # 2. Academic Year & Semester
        ay = db.query(AcademicYear).filter(AcademicYear.name == "2025-2026").first()
        if not ay:
            ay = AcademicYear(
                name="2025-2026",
                start_date=date(2025, 7, 1),
                end_date=date(2026, 5, 31),
                is_active=True
            )
            db.add(ay)
            db.flush()

        sem5 = db.query(Semester).filter(Semester.academic_year_id == ay.id, Semester.semester_number == 5).first()
        if not sem5:
            sem5 = Semester(
                academic_year_id=ay.id,
                semester_number=5,
                name="Semester V",
                start_date=date(2025, 7, 1),
                end_date=date(2025, 12, 15),
                is_active=True
            )
            db.add(sem5)
            db.flush()

        # 3. Academic Class
        ac_class = db.query(AcademicClass).filter(AcademicClass.department_id == comp_dept.id, AcademicClass.code == "TY").first()
        if not ac_class:
            ac_class = AcademicClass(
                department_id=comp_dept.id,
                name="Third Year",
                code="TY",
                is_active=True
            )
            db.add(ac_class)
            db.flush()

        # 4. Division & Batches
        div_a = db.query(Division).filter(
            Division.academic_class_id == ac_class.id,
            Division.academic_year_id == ay.id,
            Division.semester_id == sem5.id,
            Division.name == "Division A"
        ).first()
        if not div_a:
            div_a = Division(
                academic_class_id=ac_class.id,
                academic_year_id=ay.id,
                semester_id=sem5.id,
                name="Division A",
                is_active=True
            )
            db.add(div_a)
            db.flush()

        batch_a1 = db.query(Batch).filter(Batch.division_id == div_a.id, Batch.name == "Batch A1").first()
        if not batch_a1:
            batch_a1 = Batch(division_id=div_a.id, name="Batch A1", is_active=True)
            db.add(batch_a1)
            db.flush()

        batch_a2 = db.query(Batch).filter(Batch.division_id == div_a.id, Batch.name == "Batch A2").first()
        if not batch_a2:
            batch_a2 = Batch(division_id=div_a.id, name="Batch A2", is_active=True)
            db.add(batch_a2)
            db.flush()

        # 5. Subjects
        subjects_data = [
            ("Operating Systems", "CS501"),
            ("Software Engineering", "CS502"),
            ("Database Management Systems", "CS503"),
            ("Computer Networks", "CS504"),
            ("Web Development", "CS505"),
            ("Artificial Intelligence", "CS506"),
        ]

        subject_map = {}
        for sub_name, sub_code in subjects_data:
            sub = db.query(Subject).filter(Subject.code == sub_code).first()
            if not sub:
                sub = Subject(
                    name=sub_name,
                    code=sub_code,
                    department_id=comp_dept.id,
                    semester_id=sem5.id,
                    is_active=True
                )
                db.add(sub)
                db.flush()
            subject_map[sub_code] = sub

            # Link subject to class
            csa = db.query(ClassSubjectAssignment).filter(
                ClassSubjectAssignment.academic_class_id == ac_class.id,
                ClassSubjectAssignment.subject_id == sub.id,
                ClassSubjectAssignment.academic_year_id == ay.id,
                ClassSubjectAssignment.semester_id == sem5.id
            ).first()
            if not csa:
                csa = ClassSubjectAssignment(
                    academic_class_id=ac_class.id,
                    subject_id=sub.id,
                    academic_year_id=ay.id,
                    semester_id=sem5.id
                )
                db.add(csa)
                db.flush()

        # 6. Users & Profiles: Admin, Teachers, Students
        # Ensure 'admin' exists and is active
        admin_user = db.query(User).filter(User.username == settings.INIT_ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=settings.INIT_ADMIN_USERNAME,
                email=settings.INIT_ADMIN_EMAIL,
                password_hash=hash_password(settings.INIT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.flush()
        else:
            admin_user.is_active = True
            admin_user.password_hash = hash_password(settings.INIT_ADMIN_PASSWORD)
            db.flush()

        # Teacher 1 (Dr. Anjali Kulkarni - teacher1)
        t1_user = db.query(User).filter(User.username == "teacher1").first()
        if not t1_user:
            t1_user = User(
                username="teacher1",
                email="teacher1@attendance.com",
                password_hash=hash_password("JSPM#Faculty2026!"),
                role=UserRole.TEACHER,
                is_active=True
            )
            db.add(t1_user)
            db.flush()
        else:
            t1_user.password_hash = hash_password("JSPM#Faculty2026!")
            t1_user.is_active = True
            db.flush()

        t1_profile = db.query(Teacher).filter(Teacher.user_id == t1_user.id).first()
        if not t1_profile:
            t1_profile = Teacher(
                user_id=t1_user.id,
                employee_id="EMP-CE-101",
                full_name="Dr. Anjali Kulkarni",
                email=t1_user.email,
                department_id=comp_dept.id,
                is_active=True
            )
            db.add(t1_profile)
            db.flush()
        else:
            t1_profile.full_name = "Dr. Anjali Kulkarni"
            t1_profile.department_id = comp_dept.id
            db.flush()

        # Additional Teachers
        other_teachers = [
            ("Prof. Rahul Deshpande", "EMP-CE-102", "rahul.deshpande@sahyadri.edu.in", "rahul_d"),
            ("Prof. Snehal Patil", "EMP-CE-103", "snehal.patil@sahyadri.edu.in", "snehal_p"),
            ("Dr. Amit Joshi", "EMP-IT-201", "amit.joshi@sahyadri.edu.in", "amit_j"),
        ]

        teacher_profiles = [t1_profile]
        for fname, empid, email, un in other_teachers:
            u = db.query(User).filter(User.username == un).first()
            if not u:
                u = User(
                    username=un,
                    email=email,
                    password_hash=hash_password("TeacherPass123!"),
                    role=UserRole.TEACHER,
                    is_active=True
                )
                db.add(u)
                db.flush()
            t_prof = db.query(Teacher).filter(Teacher.user_id == u.id).first()
            if not t_prof:
                t_prof = Teacher(
                    user_id=u.id,
                    employee_id=empid,
                    full_name=fname,
                    email=email,
                    department_id=comp_dept.id,
                    is_active=True
                )
                db.add(t_prof)
                db.flush()
            teacher_profiles.append(t_prof)

        # Assign Teachers to Subjects
        # Dr. Anjali Kulkarni -> OS & SE
        # Prof. Rahul Deshpande -> DBMS
        # Prof. Snehal Patil -> CN & Web Dev
        t_assignments = [
            (t1_profile, subject_map["CS501"]),
            (t1_profile, subject_map["CS502"]),
            (teacher_profiles[1], subject_map["CS503"]),
            (teacher_profiles[2], subject_map["CS504"]),
            (teacher_profiles[2], subject_map["CS505"]),
        ]

        for tprof, sub in t_assignments:
            ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.teacher_id == tprof.id,
                TeacherAssignment.subject_id == sub.id,
                TeacherAssignment.academic_class_id == ac_class.id,
                TeacherAssignment.academic_year_id == ay.id,
                TeacherAssignment.semester_id == sem5.id
            ).first()
            if not ta:
                ta = TeacherAssignment(
                    teacher_id=tprof.id,
                    subject_id=sub.id,
                    academic_class_id=ac_class.id,
                    academic_year_id=ay.id,
                    semester_id=sem5.id
                )
                db.add(ta)
                db.flush()

        # 7. Student 1 (Aarohi Patil - student1) + Indian Student Dataset
        indian_students = [
            ("student1", "Aarohi Patil", "CE23A001", "EN20230001", "student1@attendance.com", batch_a1),
            ("ananya_k", "Ananya Kulkarni", "CE23A002", "EN20230002", "ananya.k@sahyadri.edu.in", batch_a1),
            ("isha_d", "Isha Deshmukh", "CE23A003", "EN20230003", "isha.d@sahyadri.edu.in", batch_a1),
            ("sneha_j", "Sneha Joshi", "CE23A004", "EN20230004", "sneha.j@sahyadri.edu.in", batch_a1),
            ("riya_j", "Riya Jadhav", "CE23A005", "EN20230005", "riya.j@sahyadri.edu.in", batch_a1),
            ("aarav_s", "Aarav Sharma", "CE23A006", "EN20230006", "aarav.s@sahyadri.edu.in", batch_a2),
            ("aditya_p", "Aditya Patil", "CE23A007", "EN20230007", "aditya.p@sahyadri.edu.in", batch_a2),
            ("rohan_p", "Rohan Patil", "CE23A008", "EN20230008", "rohan.p@sahyadri.edu.in", batch_a2),
            ("omkar_j", "Omkar Jadhav", "CE23A009", "EN20230009", "omkar.j@sahyadri.edu.in", batch_a2),
            ("kavya_n", "Kavya Nair", "CE23A010", "EN20230010", "kavya.n@sahyadri.edu.in", batch_a2),
        ]

        student_objs = []
        for un, fname, roll, enr, email, b_obj in indian_students:
            u = db.query(User).filter(User.username == un).first()
            if not u:
                u = User(
                    username=un,
                    email=email,
                    password_hash=hash_password("StudentPass123!"),
                    role=UserRole.STUDENT,
                    is_active=True
                )
                db.add(u)
                db.flush()
            sp = db.query(Student).filter(Student.user_id == u.id).first()
            if not sp:
                sp = Student(
                    user_id=u.id,
                    student_id=roll,
                    roll_number=roll,
                    enrollment_number=enr,
                    full_name=fname,
                    email=email,
                    department_id=comp_dept.id,
                    academic_class_id=ac_class.id,
                    division_id=div_a.id,
                    batch_id=b_obj.id,
                    academic_year_id=ay.id,
                    semester_id=sem5.id,
                    is_active=True
                )
                db.add(sp)
                db.flush()
            else:
                sp.full_name = fname
                sp.roll_number = roll
                sp.department_id = comp_dept.id
                sp.academic_class_id = ac_class.id
                sp.division_id = div_a.id
                sp.batch_id = b_obj.id
                db.flush()
            student_objs.append(sp)

        # 8. Seed Realistic Attendance Sessions & Records
        # Create 10 historical attendance sessions across subjects
        sub_list = [subject_map["CS501"], subject_map["CS502"], subject_map["CS503"], subject_map["CS504"], subject_map["CS505"]]
        
        # Check existing sessions to avoid duplicating if already run
        sess_count = db.query(AttendanceSession).filter(AttendanceSession.division_id == div_a.id).count()
        if sess_count < 10:
            today = date.today()
            for i in range(10):
                sub = sub_list[i % len(sub_list)]
                t_profile = t1_profile if sub.code in ["CS501", "CS502"] else teacher_profiles[1]
                s_date = today - timedelta(days=(10 - i))
                start_time = datetime.combine(s_date, datetime.min.time()).replace(hour=9 + (i % 4), minute=0)
                end_time = start_time + timedelta(minutes=50)

                # Mark past sessions as CLOSED, active session as ACTIVE
                sess_status = SessionStatus.ACTIVE if i == 9 else SessionStatus.CLOSED
                dt_start = start_time
                dt_end = end_time

                session = AttendanceSession(
                    academic_year_id=ay.id,
                    semester_id=sem5.id,
                    division_id=div_a.id,
                    subject_id=sub.id,
                    teacher_id=t_profile.id,
                    session_date=s_date,
                    start_time=dt_start.time(),
                    end_time=dt_end.time(),
                    expires_at=dt_end,
                    status=sess_status,
                    session_token=f"TOKEN_SEED_{i}_{int(datetime.now().timestamp())}"
                )
                db.add(session)
                db.flush()

                # Mark attendance records for students with varied attendance:
                # Rohan Patil (index 7) -> 60% present (DEFAULTER)
                # Omkar Jadhav (index 8) -> 70% present (DEFAULTER)
                # Others -> 80% to 100% present
                for idx, st in enumerate(student_objs):
                    if idx == 7: # Rohan Patil
                        is_present = (i % 2 == 0) # 50%
                    elif idx == 8: # Omkar Jadhav
                        is_present = (i % 3 != 0) # ~66%
                    else:
                        is_present = (i % 5 != 0) # 80%

                    status = AttendanceStatus.PRESENT if is_present else AttendanceStatus.ABSENT
                    rec = AttendanceRecord(
                        attendance_session_id=session.id,
                        student_id=st.id,
                        status=status,
                        source=AttendanceSource.QR if is_present else AttendanceSource.MANUAL,
                        marked_at=dt_start + timedelta(minutes=5)
                    )
                    db.add(rec)
            db.flush()

        db.commit()
        print("[SUCCESS] Real Indian college data seeded successfully!")
        print("  - College: JSPM's Bhivrabai Sawant Polytechnic, Pune")
        print("  - Dept: Computer Engineering")
        print("  - Admin: Dr. Kavita Deshmukh ('admin' / 'AdminPass@123')")
        print("  - Teacher: Dr. Anjali Kulkarni ('teacher1' / 'JSPM#Faculty2026!')")
        print("  - Student: Aarohi Patil ('student1' / 'StudentPass123!')")
        print(f"  - Total Students in Dataset: {len(student_objs)}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed seeding Indian college data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
