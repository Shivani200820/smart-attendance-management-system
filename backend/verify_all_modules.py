import subprocess
import sys

modules = [
    ("Module 1B - Auth & Users", "verify_module_1b.py"),
    ("Module 1C - Academic Structure", "verify_module_1c.py"),
    ("Module 1D - Profiles & Subject Assignments", "verify_module_1d.py"),
    ("Module 1E - Timetable Management", "verify_module_1e.py"),
    ("Module 1F - Enrolment & Class Linking", "verify_module_1f.py"),
    ("Module 1G - Attendance Session Management", "verify_module_1g.py"),
    ("Module 1H - Attendance Marking & Duplicate Rules", "verify_module_1h.py"),
    ("Module 1I - Attendance Corrections & Audit", "verify_module_1i.py"),
    ("Module 1J - Attendance Reports & Defaulter Analytics", "verify_module_1j.py"),
]

def main():
    print("\n=======================================================")
    print("   ATTENDANCE MANAGEMENT SYSTEM - MASTER VERIFICATION")
    print("=======================================================\n")
    
    passed = 0
    failed = 0

    for name, script in modules:
        print(f"--> Running {name} ({script})...", flush=True)
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [PASS] {name} passed successfully!\n", flush=True)
            passed += 1
        else:
            print(f"    [FAIL] {name} failed with exit code {res.returncode}")
            print(res.stdout)
            print(res.stderr)
            failed += 1

    print("=======================================================")
    print(f" SUMMARY: {passed}/{len(modules)} Modules Passed ({failed} Failed)")
    print("=======================================================\n")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
