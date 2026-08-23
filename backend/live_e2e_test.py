import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000/api"

def api_call(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        return e.code, json.loads(resp_body) if resp_body else {}

def run_e2e_tests():
    print("=== LIVE E2E END-TO-END WORKFLOW VERIFICATION ===")

    # 1. Admin Login & Data Verification
    print("\n1. Testing Admin Portal APIs...")
    status, res = api_call("/auth/login", method="POST", data={"username": "admin", "password": "AdminPass@123"})
    if status != 200:
        status, res = api_call("/auth/login", method="POST", data={"username": "admin", "password": "AdminPass123!"})
    assert status == 200, f"Admin login failed: {res}"
    admin_token = res["access_token"]
    print("   [PASS] Admin Login successful")

    status, users_res = api_call("/users", token=admin_token)
    assert status == 200, f"Get users failed: {users_res}"
    print(f"   [PASS] User Management API returned {users_res['total']} users")

    status, depts_res = api_call("/departments", token=admin_token)
    assert status == 200, f"Get departments failed: {depts_res}"
    print(f"   [PASS] Academic Departments API returned {len(depts_res)} departments")

    status, audit_res = api_call("/attendance/audit-logs", token=admin_token)
    assert status == 200
    print(f"   [PASS] Audit Logs API returned {len(audit_res)} audit log entries")

    # 2. Teacher Login & Session Creation
    print("\n2. Testing Teacher Portal APIs & Attendance Session Creation...")
    status, res = api_call("/auth/login", method="POST", data={"username": "teacher1", "password": "TeacherPass123!"})
    assert status == 200
    teacher_token = res["access_token"]
    teacher_user = res["user"]
    print("   [PASS] Teacher Login successful")

    status, me_res = api_call("/auth/me", token=teacher_token)
    assert status == 200 and me_res.get("teacher_profile"), f"Teacher profile missing for teacher1: {me_res}"
    teacher_profile_id = me_res["teacher_profile"]["id"]
    print(f"   [PASS] Resolved Teacher Profile ID: {teacher_profile_id}")

    status, subs_res = api_call("/subjects", token=admin_token)
    assert status == 200 and len(subs_res) > 0, f"No subjects found: {subs_res}"
    valid_subject = subs_res[0]

    # Get student1 profile first to find division_id
    status, st_login = api_call("/auth/login", method="POST", data={"username": "student1", "password": "StudentPass123!"})
    assert status == 200
    status, st_me = api_call("/auth/me", token=st_login["access_token"])
    assert status == 200 and st_me.get("student_profile"), f"Student profile missing: {st_me}"
    student_profile = st_me["student_profile"]

    session_payload = {
        "academic_year_id": student_profile["academic_year_id"],
        "semester_id": student_profile["semester_id"],
        "division_id": student_profile["division_id"],
        "subject_id": valid_subject["id"],
        "teacher_id": teacher_profile_id,
        "session_date": "2026-08-20",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "expires_at": "2026-08-20T23:59:59Z"
    }
    status, session_data = api_call("/attendance-sessions", method="POST", data=session_payload, token=teacher_token)
    assert status == 201, f"Session creation failed: {session_data}"
    session_token_str = session_data["session_token"]
    session_id = session_data["id"]
    print(f"   [PASS] Teacher created Attendance Session #{session_id} with token: {session_token_str[:12]}...")

    # 3. Student Login & Marking Attendance
    print("\n3. Testing Student Portal APIs & QR/Token Attendance Marking...")
    status, res = api_call("/auth/login", method="POST", data={"username": "student1", "password": "StudentPass123!"})
    assert status == 200
    student_token = res["access_token"]
    print("   [PASS] Student Login successful")

    # Mark attendance with valid token
    status, mark_res = api_call("/attendance/mark", method="POST", data={"session_token": session_token_str}, token=student_token)
    assert status == 201, f"Mark attendance failed: {mark_res}"
    print(f"   [PASS] Student marked present! Status: {mark_res['status']} via {mark_res['source']}")

    # Test duplicate prevention (409 Conflict)
    status, dup_res = api_call("/attendance/mark", method="POST", data={"session_token": session_token_str}, token=student_token)
    assert status == 409, f"Duplicate prevention failed: {dup_res}"
    print("   [PASS] Duplicate attendance attempt correctly blocked with 409 CONFLICT!")

    # Student Summary & History
    status, sum_data = api_call("/attendance/my-summary", token=student_token)
    assert status == 200
    print(f"   [PASS] Student Summary API returned Overall Percentage: {sum_data['overall_percentage']}%")

    status, history_res = api_call("/attendance/my-history", token=student_token)
    assert status == 200
    print(f"   [PASS] Student History API returned {len(history_res)} marked session logs")

    # 4. Teacher Manual Override / Correction Audit
    print("\n4. Testing Teacher Audit Correction...")
    status, records_res = api_call(f"/attendance/sessions/{session_id}/records", token=teacher_token)
    assert status == 200
    rec_id = records_res[0]["id"]

    status, corr_res = api_call(
        f"/attendance/records/{rec_id}/correct",
        method="PATCH",
        data={"new_status": "ABSENT", "reason": "Medical leave audit verification"},
        token=teacher_token
    )
    assert status == 200, f"Correction failed: {corr_res}"
    print("   [PASS] Attendance Record status corrected with mandatory audit reason!")

    print("\n=======================================================")
    print(" ALL LIVE END-TO-END WORKFLOW TESTS PASSED PERFECTLY! ")
    print("=======================================================")

if __name__ == "__main__":
    run_e2e_tests()
