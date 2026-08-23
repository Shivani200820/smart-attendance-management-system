import sys
import time
import httpx
from sqlalchemy import create_engine, inspect

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.profiles import Teacher

BASE_URL = "http://127.0.0.1:8000"

results = []

def record(endpoint_name, method, url, status, expected, passed, note=""):
    results.append({
        "name": endpoint_name,
        "method": method,
        "url": url,
        "status": status,
        "expected": expected,
        "passed": passed,
        "note": note
    })
    status_str = "PASS" if passed else "FAIL"
    print(f"[{status_str}] {method} {url} -> Got HTTP {status} (Expected {expected}) {note}", flush=True)


def main():
    print("==========================================", flush=True)
    print("  LIVE API VERIFICATION FOR MODULE 1E", flush=True)
    print(f"  Target Server: {BASE_URL}", flush=True)
    print("==========================================", flush=True)

    ts = int(time.time())

    # Generate Authorization Headers for ADMIN, TEACHER, STUDENT
    admin_token = create_access_token(subject=1, extra_data={"role": "ADMIN"})
    teacher_token = create_access_token(subject=2, extra_data={"role": "TEACHER"})
    student_token = create_access_token(subject=3, extra_data={"role": "STUDENT"})

    admin_h = {"Authorization": f"Bearer {admin_token}"}
    teacher_h = {"Authorization": f"Bearer {teacher_token}"}
    student_h = {"Authorization": f"Bearer {student_token}"}

    # --------------------------------------------------
    # REGRESSION CHECKS (Modules 1A, 1B, 1C, 1D)
    # --------------------------------------------------
    print("\n--- Regression Checks (Modules 1A, 1B, 1C, 1D) ---", flush=True)

    r_h = httpx.get(f"{BASE_URL}/api/health")
    record("Module 1A Health API", "GET", "/api/health", r_h.status_code, 200, r_h.status_code == 200)

    r_hdb = httpx.get(f"{BASE_URL}/api/health/database")
    record("Module 1A DB Health API", "GET", "/api/health/database", r_hdb.status_code, 200, r_hdb.status_code == 200)

    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    record("Module 1B Database 16 Tables Intact", "DB Check", "attendance_management", len(tables), 16, len(tables) == 16)

    r_me = httpx.get(f"{BASE_URL}/api/auth/me", headers=admin_h)
    record("Module 1C Auth /api/auth/me", "GET", "/api/auth/me", r_me.status_code, 200, r_me.status_code == 200)

    r_users = httpx.get(f"{BASE_URL}/api/users", headers=admin_h)
    record("Module 1D List Users /api/users", "GET", "/api/users", r_users.status_code, 200, r_users.status_code == 200)

    # --------------------------------------------------
    # MODULE 1E LIVE ENDPOINT TESTING
    # --------------------------------------------------

    # 1. ACADEMIC YEARS
    print("\n--- 1. Academic Years ---", flush=True)
    r_bad_dates = httpx.post(f"{BASE_URL}/api/academic-years", json={"name": f"AY_BAD_{ts}", "start_date": "2026-12-31", "end_date": "2026-01-01", "is_active": True}, headers=admin_h)
    record("Academic Years Validation (start_date >= end_date)", "POST", "/api/academic-years", r_bad_dates.status_code, 400, r_bad_dates.status_code == 400)

    ay_name = f"AY_{ts}"
    ay_body = {"name": ay_name, "start_date": "2026-07-01", "end_date": "2027-06-30", "is_active": True}
    r_ay_post = httpx.post(f"{BASE_URL}/api/academic-years", json=ay_body, headers=admin_h)
    record("Academic Years (Create)", "POST", "/api/academic-years", r_ay_post.status_code, 201, r_ay_post.status_code == 201)
    ay_id = r_ay_post.json().get("id") if r_ay_post.status_code == 201 else 1

    r_ay_dup = httpx.post(f"{BASE_URL}/api/academic-years", json=ay_body, headers=admin_h)
    record("Academic Years Validation (Duplicate Name)", "POST", "/api/academic-years", r_ay_dup.status_code, 400, r_ay_dup.status_code == 400)

    r_ay_list = httpx.get(f"{BASE_URL}/api/academic-years", headers=admin_h)
    record("Academic Years (List)", "GET", "/api/academic-years", r_ay_list.status_code, 200, r_ay_list.status_code == 200)

    r_ay_get = httpx.get(f"{BASE_URL}/api/academic-years/{ay_id}", headers=admin_h)
    record("Academic Years (Get by ID)", "GET", f"/api/academic-years/{ay_id}", r_ay_get.status_code, 200, r_ay_get.status_code == 200)

    r_ay_put = httpx.put(f"{BASE_URL}/api/academic-years/{ay_id}", json={"name": f"{ay_name}_UPD"}, headers=admin_h)
    record("Academic Years (Update)", "PUT", f"/api/academic-years/{ay_id}", r_ay_put.status_code, 200, r_ay_put.status_code == 200)

    r_ay_patch = httpx.patch(f"{BASE_URL}/api/academic-years/{ay_id}/status", json={"is_active": True}, headers=admin_h)
    record("Academic Years (Activate/Deactivate Status)", "PATCH", f"/api/academic-years/{ay_id}/status", r_ay_patch.status_code, 200, r_ay_patch.status_code == 200)

    # 2. SEMESTERS
    print("\n--- 2. Semesters ---", flush=True)
    r_sem_bad_fk = httpx.post(f"{BASE_URL}/api/semesters", json={"academic_year_id": 99999, "semester_number": 99, "name": "Bad FK", "is_active": True}, headers=admin_h)
    record("Semesters Validation (Invalid AY FK)", "POST", "/api/semesters", r_sem_bad_fk.status_code, 400, r_sem_bad_fk.status_code == 400)

    sem_body = {"academic_year_id": ay_id, "semester_number": (ts % 1000) + 1, "name": f"Sem_1_{ts}", "is_active": True}
    r_sem_post = httpx.post(f"{BASE_URL}/api/semesters", json=sem_body, headers=admin_h)
    record("Semesters (Create)", "POST", "/api/semesters", r_sem_post.status_code, 201, r_sem_post.status_code == 201)
    sem_id = r_sem_post.json().get("id") if r_sem_post.status_code == 201 else 1

    r_sem_dup = httpx.post(f"{BASE_URL}/api/semesters", json=sem_body, headers=admin_h)
    record("Semesters Validation (Duplicate Number in AY)", "POST", "/api/semesters", r_sem_dup.status_code, 400, r_sem_dup.status_code == 400)

    r_sem_list = httpx.get(f"{BASE_URL}/api/semesters", headers=admin_h)
    record("Semesters (List)", "GET", "/api/semesters", r_sem_list.status_code, 200, r_sem_list.status_code == 200)

    r_sem_get = httpx.get(f"{BASE_URL}/api/semesters/{sem_id}", headers=admin_h)
    record("Semesters (Get by ID)", "GET", f"/api/semesters/{sem_id}", r_sem_get.status_code, 200, r_sem_get.status_code == 200)

    r_sem_put = httpx.put(f"{BASE_URL}/api/semesters/{sem_id}", json={"name": f"Sem_1_{ts}_UPD"}, headers=admin_h)
    record("Semesters (Update)", "PUT", f"/api/semesters/{sem_id}", r_sem_put.status_code, 200, r_sem_put.status_code == 200)

    r_sem_patch = httpx.patch(f"{BASE_URL}/api/semesters/{sem_id}/status", json={"is_active": True}, headers=admin_h)
    record("Semesters (Activate/Deactivate Status)", "PATCH", f"/api/semesters/{sem_id}/status", r_sem_patch.status_code, 200, r_sem_patch.status_code == 200)

    # 3. DEPARTMENTS
    print("\n--- 3. Departments ---", flush=True)
    dept_code = f"DP_{ts % 10000}"
    dept_body = {"name": f"Department_{ts}", "code": dept_code, "is_active": True}
    r_dept_post = httpx.post(f"{BASE_URL}/api/departments", json=dept_body, headers=admin_h)
    record("Departments (Create)", "POST", "/api/departments", r_dept_post.status_code, 201, r_dept_post.status_code == 201)
    dept_id = r_dept_post.json().get("id") if r_dept_post.status_code == 201 else 1

    r_dept_dup = httpx.post(f"{BASE_URL}/api/departments", json=dept_body, headers=admin_h)
    record("Departments Validation (Duplicate Code)", "POST", "/api/departments", r_dept_dup.status_code, 400, r_dept_dup.status_code == 400)

    r_dept_list = httpx.get(f"{BASE_URL}/api/departments", headers=admin_h)
    record("Departments (List)", "GET", "/api/departments", r_dept_list.status_code, 200, r_dept_list.status_code == 200)

    r_dept_get = httpx.get(f"{BASE_URL}/api/departments/{dept_id}", headers=admin_h)
    record("Departments (Get by ID)", "GET", f"/api/departments/{dept_id}", r_dept_get.status_code, 200, r_dept_get.status_code == 200)

    r_dept_put = httpx.put(f"{BASE_URL}/api/departments/{dept_id}", json={"name": f"Department_{ts}_UPD"}, headers=admin_h)
    record("Departments (Update)", "PUT", f"/api/departments/{dept_id}", r_dept_put.status_code, 200, r_dept_put.status_code == 200)

    r_dept_patch = httpx.patch(f"{BASE_URL}/api/departments/{dept_id}/status", json={"is_active": True}, headers=admin_h)
    record("Departments (Activate/Deactivate Status)", "PATCH", f"/api/departments/{dept_id}/status", r_dept_patch.status_code, 200, r_dept_patch.status_code == 200)

    # 4. ACADEMIC CLASSES
    print("\n--- 4. Academic Classes ---", flush=True)
    class_code = f"CL_{ts % 10000}"
    class_body = {"department_id": dept_id, "name": f"Class_{ts}", "code": class_code, "is_active": True}
    r_class_post = httpx.post(f"{BASE_URL}/api/academic-classes", json=class_body, headers=admin_h)
    record("Academic Classes (Create)", "POST", "/api/academic-classes", r_class_post.status_code, 201, r_class_post.status_code == 201)
    class_id = r_class_post.json().get("id") if r_class_post.status_code == 201 else 1

    r_class_dup = httpx.post(f"{BASE_URL}/api/academic-classes", json=class_body, headers=admin_h)
    record("Academic Classes Validation (Duplicate Code in Dept)", "POST", "/api/academic-classes", r_class_dup.status_code, 400, r_class_dup.status_code == 400)

    r_class_list = httpx.get(f"{BASE_URL}/api/academic-classes", headers=admin_h)
    record("Academic Classes (List)", "GET", "/api/academic-classes", r_class_list.status_code, 200, r_class_list.status_code == 200)

    r_class_get = httpx.get(f"{BASE_URL}/api/academic-classes/{class_id}", headers=admin_h)
    record("Academic Classes (Get by ID)", "GET", f"/api/academic-classes/{class_id}", r_class_get.status_code, 200, r_class_get.status_code == 200)

    r_class_put = httpx.put(f"{BASE_URL}/api/academic-classes/{class_id}", json={"name": f"Class_{ts}_UPD"}, headers=admin_h)
    record("Academic Classes (Update)", "PUT", f"/api/academic-classes/{class_id}", r_class_put.status_code, 200, r_class_put.status_code == 200)

    r_class_patch = httpx.patch(f"{BASE_URL}/api/academic-classes/{class_id}/status", json={"is_active": True}, headers=admin_h)
    record("Academic Classes (Activate/Deactivate Status)", "PATCH", f"/api/academic-classes/{class_id}/status", r_class_patch.status_code, 200, r_class_patch.status_code == 200)

    # 5. DIVISIONS
    print("\n--- 5. Divisions ---", flush=True)
    r_div_bad_fk = httpx.post(f"{BASE_URL}/api/divisions", json={"academic_class_id": 99999, "academic_year_id": ay_id, "semester_id": sem_id, "name": "Div_Bad", "is_active": True}, headers=admin_h)
    record("Divisions Validation (Invalid Class FK)", "POST", "/api/divisions", r_div_bad_fk.status_code, 400, r_div_bad_fk.status_code == 400)

    div_name = f"Div_{ts % 1000}"
    div_body = {"academic_class_id": class_id, "academic_year_id": ay_id, "semester_id": sem_id, "name": div_name, "is_active": True}
    r_div_post = httpx.post(f"{BASE_URL}/api/divisions", json=div_body, headers=admin_h)
    record("Divisions (Create)", "POST", "/api/divisions", r_div_post.status_code, 201, r_div_post.status_code == 201)
    div_id = r_div_post.json().get("id") if r_div_post.status_code == 201 else 1

    r_div_dup = httpx.post(f"{BASE_URL}/api/divisions", json=div_body, headers=admin_h)
    record("Divisions Validation (Duplicate Combination)", "POST", "/api/divisions", r_div_dup.status_code, 400, r_div_dup.status_code == 400)

    r_div_list = httpx.get(f"{BASE_URL}/api/divisions", headers=admin_h)
    record("Divisions (List)", "GET", "/api/divisions", r_div_list.status_code, 200, r_div_list.status_code == 200)

    r_div_get = httpx.get(f"{BASE_URL}/api/divisions/{div_id}", headers=admin_h)
    record("Divisions (Get by ID)", "GET", f"/api/divisions/{div_id}", r_div_get.status_code, 200, r_div_get.status_code == 200)

    r_div_put = httpx.put(f"{BASE_URL}/api/divisions/{div_id}", json={"name": f"{div_name}_UPD"}, headers=admin_h)
    record("Divisions (Update)", "PUT", f"/api/divisions/{div_id}", r_div_put.status_code, 200, r_div_put.status_code == 200)

    r_div_patch = httpx.patch(f"{BASE_URL}/api/divisions/{div_id}/status", json={"is_active": True}, headers=admin_h)
    record("Divisions (Activate/Deactivate Status)", "PATCH", f"/api/divisions/{div_id}/status", r_div_patch.status_code, 200, r_div_patch.status_code == 200)

    # 6. BATCHES
    print("\n--- 6. Batches ---", flush=True)
    r_batch_bad_fk = httpx.post(f"{BASE_URL}/api/batches", json={"division_id": 99999, "name": "Batch_Bad", "is_active": True}, headers=admin_h)
    record("Batches Validation (Invalid Division FK)", "POST", "/api/batches", r_batch_bad_fk.status_code, 400, r_batch_bad_fk.status_code == 400)

    batch_name = f"B1_{ts % 1000}"
    batch_body = {"division_id": div_id, "name": batch_name, "is_active": True}
    r_batch_post = httpx.post(f"{BASE_URL}/api/batches", json=batch_body, headers=admin_h)
    record("Batches (Create)", "POST", "/api/batches", r_batch_post.status_code, 201, r_batch_post.status_code == 201)
    batch_id = r_batch_post.json().get("id") if r_batch_post.status_code == 201 else 1

    r_batch_dup = httpx.post(f"{BASE_URL}/api/batches", json=batch_body, headers=admin_h)
    record("Batches Validation (Duplicate Name in Division)", "POST", "/api/batches", r_batch_dup.status_code, 400, r_batch_dup.status_code == 400)

    r_batch_list = httpx.get(f"{BASE_URL}/api/batches", headers=admin_h)
    record("Batches (List)", "GET", "/api/batches", r_batch_list.status_code, 200, r_batch_list.status_code == 200)

    r_batch_get = httpx.get(f"{BASE_URL}/api/batches/{batch_id}", headers=admin_h)
    record("Batches (Get by ID)", "GET", f"/api/batches/{batch_id}", r_batch_get.status_code, 200, r_batch_get.status_code == 200)

    r_batch_put = httpx.put(f"{BASE_URL}/api/batches/{batch_id}", json={"name": f"{batch_name}_UPD"}, headers=admin_h)
    record("Batches (Update)", "PUT", f"/api/batches/{batch_id}", r_batch_put.status_code, 200, r_batch_put.status_code == 200)

    r_batch_patch = httpx.patch(f"{BASE_URL}/api/batches/{batch_id}/status", json={"is_active": True}, headers=admin_h)
    record("Batches (Activate/Deactivate Status)", "PATCH", f"/api/batches/{batch_id}/status", r_batch_patch.status_code, 200, r_batch_patch.status_code == 200)

    # 7. SUBJECTS
    print("\n--- 7. Subjects ---", flush=True)
    subj_code = f"SB_{ts % 10000}"
    subj_body = {"name": f"Subject_{ts}", "code": subj_code, "department_id": dept_id, "semester_id": sem_id, "is_active": True}
    r_subj_post = httpx.post(f"{BASE_URL}/api/subjects", json=subj_body, headers=admin_h)
    record("Subjects (Create)", "POST", "/api/subjects", r_subj_post.status_code, 201, r_subj_post.status_code == 201)
    subj_id = r_subj_post.json().get("id") if r_subj_post.status_code == 201 else 1

    r_subj_dup = httpx.post(f"{BASE_URL}/api/subjects", json=subj_body, headers=admin_h)
    record("Subjects Validation (Duplicate Code in Dept & Sem)", "POST", "/api/subjects", r_subj_dup.status_code, 400, r_subj_dup.status_code == 400)

    r_subj_list = httpx.get(f"{BASE_URL}/api/subjects", headers=admin_h)
    record("Subjects (List)", "GET", "/api/subjects", r_subj_list.status_code, 200, r_subj_list.status_code == 200)

    r_subj_get = httpx.get(f"{BASE_URL}/api/subjects/{subj_id}", headers=admin_h)
    record("Subjects (Get by ID)", "GET", f"/api/subjects/{subj_id}", r_subj_get.status_code, 200, r_subj_get.status_code == 200)

    r_subj_put = httpx.put(f"{BASE_URL}/api/subjects/{subj_id}", json={"name": f"Subject_{ts}_UPD"}, headers=admin_h)
    record("Subjects (Update)", "PUT", f"/api/subjects/{subj_id}", r_subj_put.status_code, 200, r_subj_put.status_code == 200)

    r_subj_patch = httpx.patch(f"{BASE_URL}/api/subjects/{subj_id}/status", json={"is_active": True}, headers=admin_h)
    record("Subjects (Activate/Deactivate Status)", "PATCH", f"/api/subjects/{subj_id}/status", r_subj_patch.status_code, 200, r_subj_patch.status_code == 200)

    # 8. CLASS-SUBJECT ASSIGNMENTS
    print("\n--- 8. Class-Subject Assignments ---", flush=True)
    r_assign_bad_fk = httpx.post(f"{BASE_URL}/api/class-subject-assignments", json={"academic_class_id": 99999, "division_id": div_id, "subject_id": subj_id, "academic_year_id": ay_id, "semester_id": sem_id, "is_active": True}, headers=admin_h)
    record("Class-Subject Assignment Validation (Invalid Class FK)", "POST", "/api/class-subject-assignments", r_assign_bad_fk.status_code, 400, r_assign_bad_fk.status_code == 400)

    assign_body = {"academic_class_id": class_id, "division_id": div_id, "subject_id": subj_id, "academic_year_id": ay_id, "semester_id": sem_id, "is_active": True}
    r_assign_post = httpx.post(f"{BASE_URL}/api/class-subject-assignments", json=assign_body, headers=admin_h)
    record("Class-Subject Assignment (Create)", "POST", "/api/class-subject-assignments", r_assign_post.status_code, 201, r_assign_post.status_code == 201)
    assign_id = r_assign_post.json().get("id") if r_assign_post.status_code == 201 else 1

    r_assign_dup = httpx.post(f"{BASE_URL}/api/class-subject-assignments", json=assign_body, headers=admin_h)
    record("Class-Subject Assignment Validation (Duplicate Assignment)", "POST", "/api/class-subject-assignments", r_assign_dup.status_code, 400, r_assign_dup.status_code == 400)

    r_assign_list = httpx.get(f"{BASE_URL}/api/class-subject-assignments", headers=admin_h)
    record("Class-Subject Assignment (List)", "GET", "/api/class-subject-assignments", r_assign_list.status_code, 200, r_assign_list.status_code == 200)

    r_assign_get = httpx.get(f"{BASE_URL}/api/class-subject-assignments/{assign_id}", headers=admin_h)
    record("Class-Subject Assignment (Get by ID)", "GET", f"/api/class-subject-assignments/{assign_id}", r_assign_get.status_code, 200, r_assign_get.status_code == 200)

    r_assign_put = httpx.put(f"{BASE_URL}/api/class-subject-assignments/{assign_id}", json={"is_active": True}, headers=admin_h)
    record("Class-Subject Assignment (Update)", "PUT", f"/api/class-subject-assignments/{assign_id}", r_assign_put.status_code, 200, r_assign_put.status_code == 200)

    r_assign_patch = httpx.patch(f"{BASE_URL}/api/class-subject-assignments/{assign_id}/status", json={"is_active": False}, headers=admin_h)
    record("Class-Subject Assignment (Activate/Deactivate Status)", "PATCH", f"/api/class-subject-assignments/{assign_id}/status", r_assign_patch.status_code, 200, r_assign_patch.status_code == 200)

    # 9. TEACHER ASSIGNMENTS
    print("\n--- 9. Teacher Assignments ---", flush=True)
    r_tassign_bad_fk = httpx.post(f"{BASE_URL}/api/teacher-assignments", json={"teacher_id": 99999, "subject_id": subj_id, "academic_class_id": class_id, "academic_year_id": ay_id, "semester_id": sem_id, "is_active": True}, headers=admin_h)
    record("Teacher Assignment Validation (Invalid Teacher FK)", "POST", "/api/teacher-assignments", r_tassign_bad_fk.status_code, 400, r_tassign_bad_fk.status_code == 400)

    db_sess = SessionLocal()
    t_entity = db_sess.query(Teacher).first()
    valid_teacher_id = t_entity.id if t_entity else 1
    db_sess.close()

    tassign_body = {"teacher_id": valid_teacher_id, "subject_id": subj_id, "academic_class_id": class_id, "division_id": div_id, "batch_id": batch_id, "academic_year_id": ay_id, "semester_id": sem_id, "is_active": True}
    r_tassign_post = httpx.post(f"{BASE_URL}/api/teacher-assignments", json=tassign_body, headers=admin_h)
    record("Teacher Assignment (Create)", "POST", "/api/teacher-assignments", r_tassign_post.status_code, 201, r_tassign_post.status_code == 201)
    tassign_id = r_tassign_post.json().get("id") if r_tassign_post.status_code == 201 else 1

    r_tassign_dup = httpx.post(f"{BASE_URL}/api/teacher-assignments", json=tassign_body, headers=admin_h)
    record("Teacher Assignment Validation (Duplicate Assignment)", "POST", "/api/teacher-assignments", r_tassign_dup.status_code, 400, r_tassign_dup.status_code == 400)

    r_tassign_list = httpx.get(f"{BASE_URL}/api/teacher-assignments", headers=admin_h)
    record("Teacher Assignment (List)", "GET", "/api/teacher-assignments", r_tassign_list.status_code, 200, r_tassign_list.status_code == 200)

    r_tassign_get = httpx.get(f"{BASE_URL}/api/teacher-assignments/{tassign_id}", headers=admin_h)
    record("Teacher Assignment (Get by ID)", "GET", f"/api/teacher-assignments/{tassign_id}", r_tassign_get.status_code, 200, r_tassign_get.status_code == 200)

    r_tassign_put = httpx.put(f"{BASE_URL}/api/teacher-assignments/{tassign_id}", json={"is_active": True}, headers=admin_h)
    record("Teacher Assignment (Update)", "PUT", f"/api/teacher-assignments/{tassign_id}", r_tassign_put.status_code, 200, r_tassign_put.status_code == 200)

    r_tassign_patch = httpx.patch(f"{BASE_URL}/api/teacher-assignments/{tassign_id}/status", json={"is_active": False}, headers=admin_h)
    record("Teacher Assignment (Activate/Deactivate Status)", "PATCH", f"/api/teacher-assignments/{tassign_id}/status", r_tassign_patch.status_code, 200, r_tassign_patch.status_code == 200)

    # 10. SECURITY & RBAC REJECTION
    print("\n--- 10. Security & Role-Based Access Control (RBAC Guards) ---", flush=True)
    rbac_paths = [
        "/api/academic-years", "/api/semesters", "/api/departments", "/api/academic-classes",
        "/api/divisions", "/api/batches", "/api/subjects", "/api/class-subject-assignments", "/api/teacher-assignments"
    ]

    for path in rbac_paths:
        rt_g = httpx.get(f"{BASE_URL}{path}", headers=teacher_h)
        rs_g = httpx.get(f"{BASE_URL}{path}", headers=student_h)
        record(f"RBAC Guard TEACHER GET Rejection ({path})", "GET", path, rt_g.status_code, 403, rt_g.status_code == 403)
        record(f"RBAC Guard STUDENT GET Rejection ({path})", "GET", path, rs_g.status_code, 403, rs_g.status_code == 403)

        rt_p = httpx.post(f"{BASE_URL}{path}", json={}, headers=teacher_h)
        rs_p = httpx.post(f"{BASE_URL}{path}", json={}, headers=student_h)
        record(f"RBAC Guard TEACHER POST Rejection ({path})", "POST", path, rt_p.status_code, 403, rt_p.status_code == 403)
        record(f"RBAC Guard STUDENT POST Rejection ({path})", "POST", path, rs_p.status_code, 403, rs_p.status_code == 403)

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print("\n==========================================", flush=True)
    print(f"  LIVE API VERIFICATION SUMMARY: {passed_count} / {total_count} PASSED", flush=True)
    print("==========================================", flush=True)

    if passed_count != total_count:
        sys.exit(1)

if __name__ == "__main__":
    main()
