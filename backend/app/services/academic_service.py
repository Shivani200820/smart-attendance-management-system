from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.academic import AcademicYear, Semester, Department, AcademicClass, Division, Batch
from app.models.subject import Subject
from app.models.assignments import ClassSubjectAssignment, TeacherAssignment
from app.models.profiles import Teacher
from app.schemas.academic import (
    AcademicYearCreate, AcademicYearUpdate,
    SemesterCreate, SemesterUpdate,
    DepartmentCreate, DepartmentUpdate,
    AcademicClassCreate, AcademicClassUpdate,
    DivisionCreate, DivisionUpdate,
    BatchCreate, BatchUpdate,
    SubjectCreate, SubjectUpdate,
    ClassSubjectAssignmentCreate, ClassSubjectAssignmentUpdate,
    TeacherAssignmentCreate, TeacherAssignmentUpdate,
)


# ==================================================
# 1. ACADEMIC YEAR SERVICE
# ==================================================

def create_academic_year(db: Session, data: AcademicYearCreate) -> AcademicYear:
    if data.start_date >= data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be strictly before end_date"
        )
    existing = db.execute(
        select(AcademicYear).where(AcademicYear.name == data.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with name '{data.name}' already exists"
        )
    year = AcademicYear(
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=data.is_active
    )
    db.add(year)
    db.commit()
    db.refresh(year)
    return year


def list_academic_years(db: Session, is_active: Optional[bool] = None) -> List[AcademicYear]:
    query = select(AcademicYear)
    if is_active is not None:
        query = query.where(AcademicYear.is_active == is_active)
    return list(db.execute(query.order_by(AcademicYear.id.desc())).scalars().all())


def get_academic_year(db: Session, year_id: int) -> AcademicYear:
    year = db.get(AcademicYear, year_id)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic year with ID {year_id} not found"
        )
    return year


def update_academic_year(db: Session, year_id: int, data: AcademicYearUpdate) -> AcademicYear:
    year = get_academic_year(db, year_id)
    
    new_start = data.start_date if data.start_date is not None else year.start_date
    new_end = data.end_date if data.end_date is not None else year.end_date
    if new_start >= new_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be strictly before end_date"
        )

    if data.name is not None and data.name != year.name:
        existing = db.execute(
            select(AcademicYear).where(AcademicYear.name == data.name)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Academic year with name '{data.name}' already exists"
            )
        year.name = data.name

    if data.start_date is not None:
        year.start_date = data.start_date
    if data.end_date is not None:
        year.end_date = data.end_date
    if data.is_active is not None:
        year.is_active = data.is_active

    db.commit()
    db.refresh(year)
    return year


def update_academic_year_status(db: Session, year_id: int, is_active: bool) -> AcademicYear:
    year = get_academic_year(db, year_id)
    year.is_active = is_active
    db.commit()
    db.refresh(year)
    return year


# ==================================================
# 2. SEMESTER SERVICE
# ==================================================

def create_semester(db: Session, data: SemesterCreate) -> Semester:
    year = db.get(AcademicYear, data.academic_year_id)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if data.semester_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="semester_number must be a positive integer"
        )
    existing = db.execute(
        select(Semester).where(
            Semester.academic_year_id == data.academic_year_id,
            Semester.semester_number == data.semester_number
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester number {data.semester_number} already exists in academic year {data.academic_year_id}"
        )
    if data.start_date and data.end_date and data.start_date >= data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be strictly before end_date"
        )
    sem = Semester(
        academic_year_id=data.academic_year_id,
        semester_number=data.semester_number,
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=data.is_active
    )
    db.add(sem)
    db.commit()
    db.refresh(sem)
    return sem


def list_semesters(
    db: Session,
    academic_year_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Semester]:
    query = select(Semester)
    if academic_year_id is not None:
        query = query.where(Semester.academic_year_id == academic_year_id)
    if is_active is not None:
        query = query.where(Semester.is_active == is_active)
    return list(db.execute(query.order_by(Semester.id.desc())).scalars().all())


def get_semester(db: Session, semester_id: int) -> Semester:
    sem = db.get(Semester, semester_id)
    if not sem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Semester with ID {semester_id} not found"
        )
    return sem


def update_semester(db: Session, semester_id: int, data: SemesterUpdate) -> Semester:
    sem = get_semester(db, semester_id)

    target_year_id = data.academic_year_id if data.academic_year_id is not None else sem.academic_year_id
    target_sem_num = data.semester_number if data.semester_number is not None else sem.semester_number

    if data.academic_year_id is not None:
        year = db.get(AcademicYear, data.academic_year_id)
        if not year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Academic year with ID {data.academic_year_id} does not exist"
            )

    if (data.academic_year_id is not None or data.semester_number is not None) and (
        target_year_id != sem.academic_year_id or target_sem_num != sem.semester_number
    ):
        existing = db.execute(
            select(Semester).where(
                Semester.academic_year_id == target_year_id,
                Semester.semester_number == target_sem_num
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Semester number {target_sem_num} already exists in academic year {target_year_id}"
            )

    new_start = data.start_date if data.start_date is not None else sem.start_date
    new_end = data.end_date if data.end_date is not None else sem.end_date
    if new_start and new_end and new_start >= new_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be strictly before end_date"
        )

    if data.academic_year_id is not None:
        sem.academic_year_id = data.academic_year_id
    if data.semester_number is not None:
        sem.semester_number = data.semester_number
    if data.name is not None:
        sem.name = data.name
    if data.start_date is not None:
        sem.start_date = data.start_date
    if data.end_date is not None:
        sem.end_date = data.end_date
    if data.is_active is not None:
        sem.is_active = data.is_active

    db.commit()
    db.refresh(sem)
    return sem


def update_semester_status(db: Session, semester_id: int, is_active: bool) -> Semester:
    sem = get_semester(db, semester_id)
    sem.is_active = is_active
    db.commit()
    db.refresh(sem)
    return sem


# ==================================================
# 3. DEPARTMENT SERVICE
# ==================================================

def create_department(db: Session, data: DepartmentCreate) -> Department:
    existing = db.execute(
        select(Department).where(Department.code == data.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with code '{data.code}' already exists"
        )
    dept = Department(
        name=data.name,
        code=data.code,
        is_active=data.is_active
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def list_departments(db: Session, is_active: Optional[bool] = None) -> List[Department]:
    query = select(Department)
    if is_active is not None:
        query = query.where(Department.is_active == is_active)
    return list(db.execute(query.order_by(Department.id.desc())).scalars().all())


def get_department(db: Session, dept_id: int) -> Department:
    dept = db.get(Department, dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )
    return dept


def update_department(db: Session, dept_id: int, data: DepartmentUpdate) -> Department:
    dept = get_department(db, dept_id)

    if data.code is not None and data.code != dept.code:
        existing = db.execute(
            select(Department).where(Department.code == data.code)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with code '{data.code}' already exists"
            )
        dept.code = data.code

    if data.name is not None:
        dept.name = data.name
    if data.is_active is not None:
        dept.is_active = data.is_active

    db.commit()
    db.refresh(dept)
    return dept


def update_department_status(db: Session, dept_id: int, is_active: bool) -> Department:
    dept = get_department(db, dept_id)
    dept.is_active = is_active
    db.commit()
    db.refresh(dept)
    return dept


# ==================================================
# 4. ACADEMIC CLASS SERVICE
# ==================================================

def create_academic_class(db: Session, data: AcademicClassCreate) -> AcademicClass:
    dept = db.get(Department, data.department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with ID {data.department_id} does not exist"
        )
    existing = db.execute(
        select(AcademicClass).where(
            AcademicClass.department_id == data.department_id,
            AcademicClass.code == data.code
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Class with code '{data.code}' already exists in department {data.department_id}"
        )
    ac_class = AcademicClass(
        department_id=data.department_id,
        name=data.name,
        code=data.code,
        is_active=data.is_active
    )
    db.add(ac_class)
    db.commit()
    db.refresh(ac_class)
    return ac_class


def list_academic_classes(
    db: Session,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[AcademicClass]:
    query = select(AcademicClass)
    if department_id is not None:
        query = query.where(AcademicClass.department_id == department_id)
    if is_active is not None:
        query = query.where(AcademicClass.is_active == is_active)
    return list(db.execute(query.order_by(AcademicClass.id.desc())).scalars().all())


def get_academic_class(db: Session, class_id: int) -> AcademicClass:
    ac_class = db.get(AcademicClass, class_id)
    if not ac_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic class with ID {class_id} not found"
        )
    return ac_class


def update_academic_class(db: Session, class_id: int, data: AcademicClassUpdate) -> AcademicClass:
    ac_class = get_academic_class(db, class_id)

    target_dept_id = data.department_id if data.department_id is not None else ac_class.department_id
    target_code = data.code if data.code is not None else ac_class.code

    if data.department_id is not None:
        dept = db.get(Department, data.department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {data.department_id} does not exist"
            )

    if (data.department_id is not None or data.code is not None) and (
        target_dept_id != ac_class.department_id or target_code != ac_class.code
    ):
        existing = db.execute(
            select(AcademicClass).where(
                AcademicClass.department_id == target_dept_id,
                AcademicClass.code == target_code
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class with code '{target_code}' already exists in department {target_dept_id}"
            )

    if data.department_id is not None:
        ac_class.department_id = data.department_id
    if data.name is not None:
        ac_class.name = data.name
    if data.code is not None:
        ac_class.code = data.code
    if data.is_active is not None:
        ac_class.is_active = data.is_active

    db.commit()
    db.refresh(ac_class)
    return ac_class


def update_academic_class_status(db: Session, class_id: int, is_active: bool) -> AcademicClass:
    ac_class = get_academic_class(db, class_id)
    ac_class.is_active = is_active
    db.commit()
    db.refresh(ac_class)
    return ac_class


# ==================================================
# 5. DIVISION SERVICE
# ==================================================

def create_division(db: Session, data: DivisionCreate) -> Division:
    if not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    existing = db.execute(
        select(Division).where(
            Division.academic_class_id == data.academic_class_id,
            Division.academic_year_id == data.academic_year_id,
            Division.semester_id == data.semester_id,
            Division.name == data.name
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division '{data.name}' already exists for class {data.academic_class_id}, year {data.academic_year_id}, semester {data.semester_id}"
        )

    division = Division(
        academic_class_id=data.academic_class_id,
        academic_year_id=data.academic_year_id,
        semester_id=data.semester_id,
        name=data.name,
        is_active=data.is_active
    )
    db.add(division)
    db.commit()
    db.refresh(division)
    return division


def list_divisions(
    db: Session,
    academic_class_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Division]:
    query = select(Division)
    if academic_class_id is not None:
        query = query.where(Division.academic_class_id == academic_class_id)
    if academic_year_id is not None:
        query = query.where(Division.academic_year_id == academic_year_id)
    if semester_id is not None:
        query = query.where(Division.semester_id == semester_id)
    if is_active is not None:
        query = query.where(Division.is_active == is_active)
    return list(db.execute(query.order_by(Division.id.desc())).scalars().all())


def get_division(db: Session, division_id: int) -> Division:
    div = db.get(Division, division_id)
    if not div:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Division with ID {division_id} not found"
        )
    return div


def update_division(db: Session, division_id: int, data: DivisionUpdate) -> Division:
    div = get_division(db, division_id)

    target_class_id = data.academic_class_id if data.academic_class_id is not None else div.academic_class_id
    target_year_id = data.academic_year_id if data.academic_year_id is not None else div.academic_year_id
    target_sem_id = data.semester_id if data.semester_id is not None else div.semester_id
    target_name = data.name if data.name is not None else div.name

    if data.academic_class_id is not None and not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if data.academic_year_id is not None and not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if data.semester_id is not None and not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    if (
        target_class_id != div.academic_class_id
        or target_year_id != div.academic_year_id
        or target_sem_id != div.semester_id
        or target_name != div.name
    ):
        existing = db.execute(
            select(Division).where(
                Division.academic_class_id == target_class_id,
                Division.academic_year_id == target_year_id,
                Division.semester_id == target_sem_id,
                Division.name == target_name
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Division '{target_name}' already exists for class {target_class_id}, year {target_year_id}, semester {target_sem_id}"
            )

    if data.academic_class_id is not None:
        div.academic_class_id = data.academic_class_id
    if data.academic_year_id is not None:
        div.academic_year_id = data.academic_year_id
    if data.semester_id is not None:
        div.semester_id = data.semester_id
    if data.name is not None:
        div.name = data.name
    if data.is_active is not None:
        div.is_active = data.is_active

    db.commit()
    db.refresh(div)
    return div


def update_division_status(db: Session, division_id: int, is_active: bool) -> Division:
    div = get_division(db, division_id)
    div.is_active = is_active
    db.commit()
    db.refresh(div)
    return div


# ==================================================
# 6. BATCH SERVICE
# ==================================================

def create_batch(db: Session, data: BatchCreate) -> Batch:
    if not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    existing = db.execute(
        select(Batch).where(
            Batch.division_id == data.division_id,
            Batch.name == data.name
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch '{data.name}' already exists in division {data.division_id}"
        )
    batch = Batch(
        division_id=data.division_id,
        name=data.name,
        is_active=data.is_active
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def list_batches(
    db: Session,
    division_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Batch]:
    query = select(Batch)
    if division_id is not None:
        query = query.where(Batch.division_id == division_id)
    if is_active is not None:
        query = query.where(Batch.is_active == is_active)
    return list(db.execute(query.order_by(Batch.id.desc())).scalars().all())


def get_batch(db: Session, batch_id: int) -> Batch:
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found"
        )
    return batch


def update_batch(db: Session, batch_id: int, data: BatchUpdate) -> Batch:
    batch = get_batch(db, batch_id)

    target_div_id = data.division_id if data.division_id is not None else batch.division_id
    target_name = data.name if data.name is not None else batch.name

    if data.division_id is not None and not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )

    if target_div_id != batch.division_id or target_name != batch.name:
        existing = db.execute(
            select(Batch).where(
                Batch.division_id == target_div_id,
                Batch.name == target_name
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch '{target_name}' already exists in division {target_div_id}"
            )

    if data.division_id is not None:
        batch.division_id = data.division_id
    if data.name is not None:
        batch.name = data.name
    if data.is_active is not None:
        batch.is_active = data.is_active

    db.commit()
    db.refresh(batch)
    return batch


def update_batch_status(db: Session, batch_id: int, is_active: bool) -> Batch:
    batch = get_batch(db, batch_id)
    batch.is_active = is_active
    db.commit()
    db.refresh(batch)
    return batch


# ==================================================
# 7. SUBJECT SERVICE
# ==================================================

def create_subject(db: Session, data: SubjectCreate) -> Subject:
    if not db.get(Department, data.department_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with ID {data.department_id} does not exist"
        )
    if not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    existing = db.execute(
        select(Subject).where(
            Subject.code == data.code,
            Subject.department_id == data.department_id,
            Subject.semester_id == data.semester_id
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with code '{data.code}' already exists for department {data.department_id} and semester {data.semester_id}"
        )

    subject = Subject(
        name=data.name,
        code=data.code,
        department_id=data.department_id,
        semester_id=data.semester_id,
        is_active=data.is_active
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def list_subjects(
    db: Session,
    department_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Subject]:
    query = select(Subject)
    if department_id is not None:
        query = query.where(Subject.department_id == department_id)
    if semester_id is not None:
        query = query.where(Subject.semester_id == semester_id)
    if is_active is not None:
        query = query.where(Subject.is_active == is_active)
    return list(db.execute(query.order_by(Subject.id.desc())).scalars().all())


def get_subject(db: Session, subject_id: int) -> Subject:
    subj = db.get(Subject, subject_id)
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return subj


def update_subject(db: Session, subject_id: int, data: SubjectUpdate) -> Subject:
    subj = get_subject(db, subject_id)

    target_code = data.code if data.code is not None else subj.code
    target_dept_id = data.department_id if data.department_id is not None else subj.department_id
    target_sem_id = data.semester_id if data.semester_id is not None else subj.semester_id

    if data.department_id is not None and not db.get(Department, data.department_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with ID {data.department_id} does not exist"
        )
    if data.semester_id is not None and not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    if (
        target_code != subj.code
        or target_dept_id != subj.department_id
        or target_sem_id != subj.semester_id
    ):
        existing = db.execute(
            select(Subject).where(
                Subject.code == target_code,
                Subject.department_id == target_dept_id,
                Subject.semester_id == target_sem_id
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subject with code '{target_code}' already exists for department {target_dept_id} and semester {target_sem_id}"
            )

    if data.name is not None:
        subj.name = data.name
    if data.code is not None:
        subj.code = data.code
    if data.department_id is not None:
        subj.department_id = data.department_id
    if data.semester_id is not None:
        subj.semester_id = data.semester_id
    if data.is_active is not None:
        subj.is_active = data.is_active

    db.commit()
    db.refresh(subj)
    return subj


def update_subject_status(db: Session, subject_id: int, is_active: bool) -> Subject:
    subj = get_subject(db, subject_id)
    subj.is_active = is_active
    db.commit()
    db.refresh(subj)
    return subj


# ==================================================
# 8. CLASS-SUBJECT ASSIGNMENT SERVICE
# ==================================================

def create_class_subject_assignment(
    db: Session, data: ClassSubjectAssignmentCreate
) -> ClassSubjectAssignment:
    if not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if data.division_id is not None and not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    if not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    # Check unique constraint (academic_class_id, division_id, subject_id, academic_year_id, semester_id)
    query = select(ClassSubjectAssignment).where(
        ClassSubjectAssignment.academic_class_id == data.academic_class_id,
        ClassSubjectAssignment.subject_id == data.subject_id,
        ClassSubjectAssignment.academic_year_id == data.academic_year_id,
        ClassSubjectAssignment.semester_id == data.semester_id,
    )
    if data.division_id is None:
        query = query.where(ClassSubjectAssignment.division_id.is_(None))
    else:
        query = query.where(ClassSubjectAssignment.division_id == data.division_id)

    existing = db.execute(query).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class subject assignment with these parameters already exists"
        )

    assignment = ClassSubjectAssignment(
        academic_class_id=data.academic_class_id,
        division_id=data.division_id,
        subject_id=data.subject_id,
        academic_year_id=data.academic_year_id,
        semester_id=data.semester_id,
        is_active=data.is_active
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def list_class_subject_assignments(
    db: Session,
    academic_class_id: Optional[int] = None,
    division_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[ClassSubjectAssignment]:
    query = select(ClassSubjectAssignment)
    if academic_class_id is not None:
        query = query.where(ClassSubjectAssignment.academic_class_id == academic_class_id)
    if division_id is not None:
        query = query.where(ClassSubjectAssignment.division_id == division_id)
    if subject_id is not None:
        query = query.where(ClassSubjectAssignment.subject_id == subject_id)
    if academic_year_id is not None:
        query = query.where(ClassSubjectAssignment.academic_year_id == academic_year_id)
    if semester_id is not None:
        query = query.where(ClassSubjectAssignment.semester_id == semester_id)
    if is_active is not None:
        query = query.where(ClassSubjectAssignment.is_active == is_active)
    return list(db.execute(query.order_by(ClassSubjectAssignment.id.desc())).scalars().all())


def get_class_subject_assignment(db: Session, assignment_id: int) -> ClassSubjectAssignment:
    assignment = db.get(ClassSubjectAssignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class subject assignment with ID {assignment_id} not found"
        )
    return assignment


def update_class_subject_assignment(
    db: Session, assignment_id: int, data: ClassSubjectAssignmentUpdate
) -> ClassSubjectAssignment:
    assignment = get_class_subject_assignment(db, assignment_id)

    target_class_id = data.academic_class_id if data.academic_class_id is not None else assignment.academic_class_id
    target_div_id = data.division_id if data.division_id is not None else assignment.division_id
    target_sub_id = data.subject_id if data.subject_id is not None else assignment.subject_id
    target_year_id = data.academic_year_id if data.academic_year_id is not None else assignment.academic_year_id
    target_sem_id = data.semester_id if data.semester_id is not None else assignment.semester_id

    if data.academic_class_id is not None and not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if data.division_id is not None and not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    if data.subject_id is not None and not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if data.academic_year_id is not None and not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if data.semester_id is not None and not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    # Check unique constraint
    query = select(ClassSubjectAssignment).where(
        ClassSubjectAssignment.academic_class_id == target_class_id,
        ClassSubjectAssignment.subject_id == target_sub_id,
        ClassSubjectAssignment.academic_year_id == target_year_id,
        ClassSubjectAssignment.semester_id == target_sem_id,
        ClassSubjectAssignment.id != assignment_id
    )
    if target_div_id is None:
        query = query.where(ClassSubjectAssignment.division_id.is_(None))
    else:
        query = query.where(ClassSubjectAssignment.division_id == target_div_id)

    existing = db.execute(query).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class subject assignment with these parameters already exists"
        )

    if data.academic_class_id is not None:
        assignment.academic_class_id = data.academic_class_id
    if data.division_id is not None:
        assignment.division_id = data.division_id
    if data.subject_id is not None:
        assignment.subject_id = data.subject_id
    if data.academic_year_id is not None:
        assignment.academic_year_id = data.academic_year_id
    if data.semester_id is not None:
        assignment.semester_id = data.semester_id
    if data.is_active is not None:
        assignment.is_active = data.is_active

    db.commit()
    db.refresh(assignment)
    return assignment


def update_class_subject_assignment_status(
    db: Session, assignment_id: int, is_active: bool
) -> ClassSubjectAssignment:
    assignment = get_class_subject_assignment(db, assignment_id)
    assignment.is_active = is_active
    db.commit()
    db.refresh(assignment)
    return assignment


# ==================================================
# 9. TEACHER ASSIGNMENT SERVICE
# ==================================================

def create_teacher_assignment(
    db: Session, data: TeacherAssignmentCreate
) -> TeacherAssignment:
    if not db.get(Teacher, data.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher with ID {data.teacher_id} does not exist"
        )
    if not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if data.division_id is not None and not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    if data.batch_id is not None and not db.get(Batch, data.batch_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch with ID {data.batch_id} does not exist"
        )
    if not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    # Check unique constraint (teacher_id, subject_id, academic_class_id, division_id, batch_id, academic_year_id, semester_id)
    query = select(TeacherAssignment).where(
        TeacherAssignment.teacher_id == data.teacher_id,
        TeacherAssignment.subject_id == data.subject_id,
        TeacherAssignment.academic_class_id == data.academic_class_id,
        TeacherAssignment.academic_year_id == data.academic_year_id,
        TeacherAssignment.semester_id == data.semester_id,
    )
    if data.division_id is None:
        query = query.where(TeacherAssignment.division_id.is_(None))
    else:
        query = query.where(TeacherAssignment.division_id == data.division_id)

    if data.batch_id is None:
        query = query.where(TeacherAssignment.batch_id.is_(None))
    else:
        query = query.where(TeacherAssignment.batch_id == data.batch_id)

    existing = db.execute(query).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher assignment with these parameters already exists"
        )

    assignment = TeacherAssignment(
        teacher_id=data.teacher_id,
        subject_id=data.subject_id,
        academic_class_id=data.academic_class_id,
        division_id=data.division_id,
        batch_id=data.batch_id,
        academic_year_id=data.academic_year_id,
        semester_id=data.semester_id,
        is_active=data.is_active
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def list_teacher_assignments(
    db: Session,
    teacher_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_class_id: Optional[int] = None,
    division_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[TeacherAssignment]:
    query = select(TeacherAssignment)
    if teacher_id is not None:
        query = query.where(TeacherAssignment.teacher_id == teacher_id)
    if subject_id is not None:
        query = query.where(TeacherAssignment.subject_id == subject_id)
    if academic_class_id is not None:
        query = query.where(TeacherAssignment.academic_class_id == academic_class_id)
    if division_id is not None:
        query = query.where(TeacherAssignment.division_id == division_id)
    if batch_id is not None:
        query = query.where(TeacherAssignment.batch_id == batch_id)
    if academic_year_id is not None:
        query = query.where(TeacherAssignment.academic_year_id == academic_year_id)
    if semester_id is not None:
        query = query.where(TeacherAssignment.semester_id == semester_id)
    if is_active is not None:
        query = query.where(TeacherAssignment.is_active == is_active)
    return list(db.execute(query.order_by(TeacherAssignment.id.desc())).scalars().all())


def get_teacher_assignment(db: Session, assignment_id: int) -> TeacherAssignment:
    assignment = db.get(TeacherAssignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher assignment with ID {assignment_id} not found"
        )
    return assignment


def update_teacher_assignment(
    db: Session, assignment_id: int, data: TeacherAssignmentUpdate
) -> TeacherAssignment:
    assignment = get_teacher_assignment(db, assignment_id)

    target_teacher_id = data.teacher_id if data.teacher_id is not None else assignment.teacher_id
    target_sub_id = data.subject_id if data.subject_id is not None else assignment.subject_id
    target_class_id = data.academic_class_id if data.academic_class_id is not None else assignment.academic_class_id
    target_div_id = data.division_id if data.division_id is not None else assignment.division_id
    target_batch_id = data.batch_id if data.batch_id is not None else assignment.batch_id
    target_year_id = data.academic_year_id if data.academic_year_id is not None else assignment.academic_year_id
    target_sem_id = data.semester_id if data.semester_id is not None else assignment.semester_id

    if data.teacher_id is not None and not db.get(Teacher, data.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher with ID {data.teacher_id} does not exist"
        )
    if data.subject_id is not None and not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if data.academic_class_id is not None and not db.get(AcademicClass, data.academic_class_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic class with ID {data.academic_class_id} does not exist"
        )
    if data.division_id is not None and not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    if data.batch_id is not None and not db.get(Batch, data.batch_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch with ID {data.batch_id} does not exist"
        )
    if data.academic_year_id is not None and not db.get(AcademicYear, data.academic_year_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Academic year with ID {data.academic_year_id} does not exist"
        )
    if data.semester_id is not None and not db.get(Semester, data.semester_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Semester with ID {data.semester_id} does not exist"
        )

    # Check unique constraint
    query = select(TeacherAssignment).where(
        TeacherAssignment.teacher_id == target_teacher_id,
        TeacherAssignment.subject_id == target_sub_id,
        TeacherAssignment.academic_class_id == target_class_id,
        TeacherAssignment.academic_year_id == target_year_id,
        TeacherAssignment.semester_id == target_sem_id,
        TeacherAssignment.id != assignment_id
    )
    if target_div_id is None:
        query = query.where(TeacherAssignment.division_id.is_(None))
    else:
        query = query.where(TeacherAssignment.division_id == target_div_id)

    if target_batch_id is None:
        query = query.where(TeacherAssignment.batch_id.is_(None))
    else:
        query = query.where(TeacherAssignment.batch_id == target_batch_id)

    existing = db.execute(query).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher assignment with these parameters already exists"
        )

    if data.teacher_id is not None:
        assignment.teacher_id = data.teacher_id
    if data.subject_id is not None:
        assignment.subject_id = data.subject_id
    if data.academic_class_id is not None:
        assignment.academic_class_id = data.academic_class_id
    if data.division_id is not None:
        assignment.division_id = data.division_id
    if data.batch_id is not None:
        assignment.batch_id = data.batch_id
    if data.academic_year_id is not None:
        assignment.academic_year_id = data.academic_year_id
    if data.semester_id is not None:
        assignment.semester_id = data.semester_id
    if data.is_active is not None:
        assignment.is_active = data.is_active

    db.commit()
    db.refresh(assignment)
    return assignment


def update_teacher_assignment_status(
    db: Session, assignment_id: int, is_active: bool
) -> TeacherAssignment:
    assignment = get_teacher_assignment(db, assignment_id)
    assignment.is_active = is_active
    db.commit()
    db.refresh(assignment)
    return assignment
