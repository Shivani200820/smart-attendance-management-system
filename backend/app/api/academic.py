from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin, get_current_active_user
from app.models.user import User
from app.schemas.academic import (
    StatusUpdate,
    AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse,
    SemesterCreate, SemesterUpdate, SemesterResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    AcademicClassCreate, AcademicClassUpdate, AcademicClassResponse,
    DivisionCreate, DivisionUpdate, DivisionResponse,
    BatchCreate, BatchUpdate, BatchResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    ClassSubjectAssignmentCreate, ClassSubjectAssignmentUpdate, ClassSubjectAssignmentResponse,
    TeacherAssignmentCreate, TeacherAssignmentUpdate, TeacherAssignmentResponse,
)
from app.services import academic_service

router = APIRouter(tags=["Academic Structure Management"])


# ==================================================
# 1. ACADEMIC YEARS
# ==================================================

@router.post(
    "/academic-years",
    response_model=AcademicYearResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Year (Admin only)"
)
def create_academic_year(
    data: AcademicYearCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_academic_year(db, data)


@router.get(
    "/academic-years",
    response_model=List[AcademicYearResponse],
    status_code=status.HTTP_200_OK,
    summary="List Academic Years (Admin only)"
)
def list_academic_years(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_academic_years(db, is_active=is_active)


@router.get(
    "/academic-years/{year_id}",
    response_model=AcademicYearResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Academic Year by ID"
)
def get_academic_year(
    year_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_academic_year(db, year_id)


@router.put(
    "/academic-years/{year_id}",
    response_model=AcademicYearResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Academic Year (Admin only)"
)
def update_academic_year(
    year_id: int,
    data: AcademicYearUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_academic_year(db, year_id, data)


@router.patch(
    "/academic-years/{year_id}/status",
    response_model=AcademicYearResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Academic Year (Admin only)"
)
def update_academic_year_status(
    year_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_academic_year_status(db, year_id, status_in.is_active)


# ==================================================
# 2. SEMESTERS
# ==================================================

@router.post(
    "/semesters",
    response_model=SemesterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Semester (Admin only)"
)
def create_semester(
    data: SemesterCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_semester(db, data)


@router.get(
    "/semesters",
    response_model=List[SemesterResponse],
    status_code=status.HTTP_200_OK,
    summary="List Semesters (Admin only)"
)
def list_semesters(
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_semesters(db, academic_year_id=academic_year_id, is_active=is_active)


@router.get(
    "/semesters/{semester_id}",
    response_model=SemesterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Semester by ID"
)
def get_semester(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_semester(db, semester_id)


@router.put(
    "/semesters/{semester_id}",
    response_model=SemesterResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Semester (Admin only)"
)
def update_semester(
    semester_id: int,
    data: SemesterUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_semester(db, semester_id, data)


@router.patch(
    "/semesters/{semester_id}/status",
    response_model=SemesterResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Semester (Admin only)"
)
def update_semester_status(
    semester_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_semester_status(db, semester_id, status_in.is_active)


# ==================================================
# 3. DEPARTMENTS
# ==================================================

@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Department (Admin only)"
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_department(db, data)


@router.get(
    "/departments",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Departments (Admin only)"
)
def list_departments(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_departments(db, is_active=is_active)


@router.get(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Department by ID"
)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_department(db, dept_id)


@router.put(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Department (Admin only)"
)
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_department(db, dept_id, data)


@router.patch(
    "/departments/{dept_id}/status",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Department (Admin only)"
)
def update_department_status(
    dept_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_department_status(db, dept_id, status_in.is_active)


# ==================================================
# 4. ACADEMIC CLASSES
# ==================================================

@router.post(
    "/academic-classes",
    response_model=AcademicClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Class (Admin only)"
)
def create_academic_class(
    data: AcademicClassCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_academic_class(db, data)


@router.get(
    "/academic-classes",
    response_model=List[AcademicClassResponse],
    status_code=status.HTTP_200_OK,
    summary="List Academic Classes (Admin only)"
)
def list_academic_classes(
    department_id: Optional[int] = Query(None, description="Filter by Department ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_academic_classes(db, department_id=department_id, is_active=is_active)


@router.get(
    "/academic-classes/{class_id}",
    response_model=AcademicClassResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Academic Class by ID"
)
def get_academic_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_academic_class(db, class_id)


@router.put(
    "/academic-classes/{class_id}",
    response_model=AcademicClassResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Academic Class (Admin only)"
)
def update_academic_class(
    class_id: int,
    data: AcademicClassUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_academic_class(db, class_id, data)


@router.patch(
    "/academic-classes/{class_id}/status",
    response_model=AcademicClassResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Academic Class (Admin only)"
)
def update_academic_class_status(
    class_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_academic_class_status(db, class_id, status_in.is_active)


# ==================================================
# 5. DIVISIONS
# ==================================================

@router.post(
    "/divisions",
    response_model=DivisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Division (Admin only)"
)
def create_division(
    data: DivisionCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_division(db, data)


@router.get(
    "/divisions",
    response_model=List[DivisionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Divisions (Admin only)"
)
def list_divisions(
    academic_class_id: Optional[int] = Query(None, description="Filter by Academic Class ID"),
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_divisions(
        db,
        academic_class_id=academic_class_id,
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        is_active=is_active
    )


@router.get(
    "/divisions/{division_id}",
    response_model=DivisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Division by ID"
)
def get_division(
    division_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_division(db, division_id)


@router.put(
    "/divisions/{division_id}",
    response_model=DivisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Division (Admin only)"
)
def update_division(
    division_id: int,
    data: DivisionUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_division(db, division_id, data)


@router.patch(
    "/divisions/{division_id}/status",
    response_model=DivisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Division (Admin only)"
)
def update_division_status(
    division_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_division_status(db, division_id, status_in.is_active)


# ==================================================
# 6. BATCHES
# ==================================================

@router.post(
    "/batches",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Batch (Admin only)"
)
def create_batch(
    data: BatchCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_batch(db, data)


@router.get(
    "/batches",
    response_model=List[BatchResponse],
    status_code=status.HTTP_200_OK,
    summary="List Batches (Admin only)"
)
def list_batches(
    division_id: Optional[int] = Query(None, description="Filter by Division ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_batches(db, division_id=division_id, is_active=is_active)


@router.get(
    "/batches/{batch_id}",
    response_model=BatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Batch by ID"
)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_batch(db, batch_id)


@router.put(
    "/batches/{batch_id}",
    response_model=BatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Batch (Admin only)"
)
def update_batch(
    batch_id: int,
    data: BatchUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_batch(db, batch_id, data)


@router.patch(
    "/batches/{batch_id}/status",
    response_model=BatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Batch (Admin only)"
)
def update_batch_status(
    batch_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_batch_status(db, batch_id, status_in.is_active)


# ==================================================
# 7. SUBJECTS
# ==================================================

@router.post(
    "/subjects",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Subject (Admin only)"
)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_subject(db, data)


@router.get(
    "/subjects",
    response_model=List[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Subjects (Admin only)"
)
def list_subjects(
    department_id: Optional[int] = Query(None, description="Filter by Department ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_subjects(
        db, department_id=department_id, semester_id=semester_id, is_active=is_active
    )


@router.get(
    "/subjects/{subject_id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Subject by ID"
)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_subject(db, subject_id)


@router.put(
    "/subjects/{subject_id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Subject (Admin only)"
)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_subject(db, subject_id, data)


@router.patch(
    "/subjects/{subject_id}/status",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Subject (Admin only)"
)
def update_subject_status(
    subject_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_subject_status(db, subject_id, status_in.is_active)


# ==================================================
# 8. CLASS-SUBJECT ASSIGNMENTS
# ==================================================

@router.post(
    "/class-subject-assignments",
    response_model=ClassSubjectAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Class-Subject Assignment (Admin only)"
)
def create_class_subject_assignment(
    data: ClassSubjectAssignmentCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_class_subject_assignment(db, data)


@router.get(
    "/class-subject-assignments",
    response_model=List[ClassSubjectAssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Class-Subject Assignments (Admin only)"
)
def list_class_subject_assignments(
    academic_class_id: Optional[int] = Query(None, description="Filter by Academic Class ID"),
    division_id: Optional[int] = Query(None, description="Filter by Division ID"),
    subject_id: Optional[int] = Query(None, description="Filter by Subject ID"),
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_class_subject_assignments(
        db,
        academic_class_id=academic_class_id,
        division_id=division_id,
        subject_id=subject_id,
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        is_active=is_active
    )


@router.get(
    "/class-subject-assignments/{assignment_id}",
    response_model=ClassSubjectAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Class-Subject Assignment by ID"
)
def get_class_subject_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_class_subject_assignment(db, assignment_id)


@router.put(
    "/class-subject-assignments/{assignment_id}",
    response_model=ClassSubjectAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Class-Subject Assignment (Admin only)"
)
def update_class_subject_assignment(
    assignment_id: int,
    data: ClassSubjectAssignmentUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_class_subject_assignment(db, assignment_id, data)


@router.patch(
    "/class-subject-assignments/{assignment_id}/status",
    response_model=ClassSubjectAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Class-Subject Assignment (Admin only)"
)
def update_class_subject_assignment_status(
    assignment_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_class_subject_assignment_status(db, assignment_id, status_in.is_active)


# ==================================================
# 9. TEACHER ASSIGNMENTS
# ==================================================

@router.post(
    "/teacher-assignments",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Teacher Assignment (Admin only)"
)
def create_teacher_assignment(
    data: TeacherAssignmentCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.create_teacher_assignment(db, data)


@router.get(
    "/teacher-assignments",
    response_model=List[TeacherAssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Teacher Assignments (Admin only)"
)
def list_teacher_assignments(
    teacher_id: Optional[int] = Query(None, description="Filter by Teacher ID"),
    subject_id: Optional[int] = Query(None, description="Filter by Subject ID"),
    academic_class_id: Optional[int] = Query(None, description="Filter by Academic Class ID"),
    division_id: Optional[int] = Query(None, description="Filter by Division ID"),
    batch_id: Optional[int] = Query(None, description="Filter by Batch ID"),
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.list_teacher_assignments(
        db,
        teacher_id=teacher_id,
        subject_id=subject_id,
        academic_class_id=academic_class_id,
        division_id=division_id,
        batch_id=batch_id,
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        is_active=is_active
    )


@router.get(
    "/teacher-assignments/{assignment_id}",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Teacher Assignment by ID"
)
def get_teacher_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return academic_service.get_teacher_assignment(db, assignment_id)


@router.put(
    "/teacher-assignments/{assignment_id}",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Teacher Assignment (Admin only)"
)
def update_teacher_assignment(
    assignment_id: int,
    data: TeacherAssignmentUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_teacher_assignment(db, assignment_id, data)


@router.patch(
    "/teacher-assignments/{assignment_id}/status",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Teacher Assignment (Admin only)"
)
def update_teacher_assignment_status(
    assignment_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return academic_service.update_teacher_assignment_status(db, assignment_id, status_in.is_active)
