import sys
from sqlalchemy import create_engine, inspect
from app.core.config import settings

def main():
    print(f"Connecting to MySQL host '{settings.DB_HOST}:{settings.DB_PORT}' database '{settings.DB_NAME}'...")
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    
    tables = sorted(inspector.get_table_names())
    print(f"\nFound {len(tables)} tables in database '{settings.DB_NAME}':")
    for t in tables:
        print(f"  - {t}")
        
    expected_tables = [
        "academic_classes",
        "academic_years",
        "attendance_corrections",
        "attendance_records",
        "attendance_sessions",
        "batches",
        "class_subject_assignments",
        "departments",
        "divisions",
        "semesters",
        "students",
        "subjects",
        "teacher_assignments",
        "teachers",
        "timetable",
        "users"
    ]
    
    missing = [t for t in expected_tables if t not in tables]
    if missing:
        print(f"\n[FAIL] Missing tables: {missing}")
        sys.exit(1)
        
    print(f"\n[PASS] Total table count: {len(tables)} / 16 expected tables present.")
    
    # Detailed schema verification for primary keys, foreign keys, and unique constraints
    print("\n--- Verifying Core Table Constraints ---")
    
    # Check 1: Check primary keys exist on all expected tables
    for t in expected_tables:
        pk = inspector.get_pk_constraint(t)
        pk_cols = pk.get("constrained_columns", [])
        if not pk_cols:
            print(f"[FAIL] Table '{t}' is missing a primary key!")
            sys.exit(1)
    print("[PASS] All 16 tables have valid Primary Key constraints.")
    
    # Check 2: Foreign Key verification on key relationship tables
    fk_checks = {
        "semesters": ["academic_year_id"],
        "academic_classes": ["department_id"],
        "divisions": ["academic_class_id", "academic_year_id", "semester_id"],
        "batches": ["division_id"],
        "students": ["department_id", "academic_class_id", "division_id", "batch_id", "academic_year_id", "semester_id"],
        "teachers": ["department_id"],
        "subjects": ["department_id", "semester_id"],
        "class_subject_assignments": ["academic_class_id", "subject_id", "academic_year_id", "semester_id"],
        "teacher_assignments": ["teacher_id", "subject_id", "academic_class_id", "academic_year_id", "semester_id"],
        "timetable": ["academic_year_id", "semester_id", "division_id", "subject_id", "teacher_id"],
        "attendance_sessions": ["academic_year_id", "semester_id", "division_id", "subject_id", "teacher_id"],
        "attendance_records": ["attendance_session_id", "student_id"],
        "attendance_corrections": ["attendance_id", "corrected_by"]
    }
    
    for table_name, req_fk_cols in fk_checks.items():
        fks = inspector.get_foreign_keys(table_name)
        constrained_cols = set()
        for fk in fks:
            constrained_cols.update(fk.get("constrained_columns", []))
        missing_fks = [c for c in req_fk_cols if c not in constrained_cols]
        if missing_fks:
            print(f"[FAIL] Table '{table_name}' missing expected foreign keys for columns: {missing_fks}")
            sys.exit(1)
    print("[PASS] Foreign key relationships verified across all relational entities.")
    
    # Check 3: Specifically verify Unique Constraint on (student_id, attendance_session_id) in attendance_records
    attendance_records_uqs = inspector.get_unique_constraints("attendance_records")
    student_session_uq_found = False
    
    for uq in attendance_records_uqs:
        cols = set(uq.get("column_names", []))
        if {"student_id", "attendance_session_id"}.issubset(cols):
            student_session_uq_found = True
            print(f"[PASS] Verified mandatory unique constraint '{uq.get('name')}' on attendance_records (student_id + attendance_session_id).")
            break
            
    if not student_session_uq_found:
        print("[FAIL] Missing mandatory unique constraint on (student_id, attendance_session_id) in attendance_records!")
        sys.exit(1)

    print("\n[SUCCESS] All Module 1B database architecture verification checks PASSED!")
    sys.exit(0)

if __name__ == "__main__":
    main()
