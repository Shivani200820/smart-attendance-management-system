from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.user import User
from app.models.profiles import Teacher, Student
from app.models.academic import Department, AcademicClass, Division, Batch, AcademicYear, Semester
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate, TeacherCreate, StudentCreate, TeacherUpdate, StudentUpdate


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Fetch a User by primary key ID along with associated Teacher/Student profiles.
    Raises HTTP 404 if not found.
    """
    user = (
        db.query(User)
        .options(
            joinedload(User.teacher_profile),
            joinedload(User.student_profile)
        )
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


def create_user_with_profile(db: Session, user_in: UserCreate) -> User:
    """
    Creates a User and associated Teacher/Student profile within a single database transaction.
    Validates role consistency, FK references, and uniqueness constraints.
    """
    # 1. Validate Username and User Email uniqueness
    existing_user = db.query(User).filter(
        or_(User.username == user_in.username, User.email == user_in.email)
    ).first()
    if existing_user:
        if existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_in.username}' is already registered."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' is already registered."
        )

    # 2. Validate Role & Profile Consistency
    if user_in.role == UserRole.TEACHER:
        if not user_in.teacher_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher profile details are required when creating a TEACHER user."
            )
        _validate_teacher_create(db, user_in.teacher_profile)

    elif user_in.role == UserRole.STUDENT:
        if not user_in.student_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student profile details are required when creating a STUDENT user."
            )
        _validate_student_create(db, user_in.student_profile)

    elif user_in.role == UserRole.ADMIN:
        if user_in.teacher_profile or user_in.student_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ADMIN users should not have Teacher or Student profiles attached."
            )

    # 3. Transactional Creation
    try:
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            role=user_in.role,
            is_active=True
        )
        db.add(new_user)
        db.flush()  # Obtain new_user.id for FK binding

        if user_in.role == UserRole.TEACHER and user_in.teacher_profile:
            tp = user_in.teacher_profile
            teacher = Teacher(
                user_id=new_user.id,
                employee_id=tp.employee_id,
                full_name=tp.full_name,
                email=tp.email,
                department_id=tp.department_id,
                is_active=True
            )
            db.add(teacher)

        elif user_in.role == UserRole.STUDENT and user_in.student_profile:
            sp = user_in.student_profile
            student = Student(
                user_id=new_user.id,
                student_id=sp.student_id,
                roll_number=sp.roll_number,
                enrollment_number=sp.enrollment_number,
                full_name=sp.full_name,
                email=sp.email,
                department_id=sp.department_id,
                academic_class_id=sp.academic_class_id,
                division_id=sp.division_id,
                batch_id=sp.batch_id,
                academic_year_id=sp.academic_year_id,
                semester_id=sp.semester_id,
                is_active=True
            )
            db.add(student)

        db.commit()
        db.refresh(new_user)
        return get_user_by_id(db, new_user.id)

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> Tuple[List[User], int]:
    """
    Retrieves paginated users with optional role, status, and text search filters.
    Returns (user_list, total_count).
    """
    query = (
        db.query(User)
        .outerjoin(User.teacher_profile)
        .outerjoin(User.student_profile)
        .options(
            joinedload(User.teacher_profile),
            joinedload(User.student_profile)
        )
    )

    if role is not None:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                Teacher.full_name.ilike(search_pattern),
                Teacher.employee_id.ilike(search_pattern),
                Student.full_name.ilike(search_pattern),
                Student.student_id.ilike(search_pattern),
                Student.enrollment_number.ilike(search_pattern)
            )
        )

    # Calculate total count before pagination limit/offset
    total_count = query.distinct().count()

    users = (
        query.order_by(User.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return users, total_count


def update_user_and_profile(db: Session, user_id: int, user_in: UserUpdate) -> User:
    """
    Updates user account and linked profile fields within a transaction.
    """
    user = get_user_by_id(db, user_id)

    try:
        # Check Username uniqueness if changed
        if user_in.username and user_in.username != user.username:
            existing = db.query(User).filter(User.username == user_in.username).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{user_in.username}' is already in use."
                )
            user.username = user_in.username

        # Check Email uniqueness if changed
        if user_in.email and user_in.email != user.email:
            existing = db.query(User).filter(User.email == user_in.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{user_in.email}' is already in use."
                )
            user.email = user_in.email
            # Also update email in linked teacher/student profile for consistency if present
            if user.teacher_profile:
                user.teacher_profile.email = user_in.email
            if user.student_profile:
                user.student_profile.email = user_in.email

        # Update Password if provided
        if user_in.password:
            user.password_hash = hash_password(user_in.password)

        # Update Teacher profile if teacher
        if user.role == UserRole.TEACHER and user.teacher_profile and user_in.teacher_profile:
            tp = user_in.teacher_profile
            if tp.department_id and tp.department_id != user.teacher_profile.department_id:
                _verify_fk_exists(db, Department, tp.department_id, "Department")
                user.teacher_profile.department_id = tp.department_id

            if tp.full_name:
                user.teacher_profile.full_name = tp.full_name

            if tp.email and tp.email != user.teacher_profile.email:
                _check_teacher_email_unique(db, tp.email, exclude_id=user.teacher_profile.id)
                user.teacher_profile.email = tp.email

        # Update Student profile if student
        if user.role == UserRole.STUDENT and user.student_profile and user_in.student_profile:
            sp = user_in.student_profile
            if sp.roll_number:
                user.student_profile.roll_number = sp.roll_number
            if sp.full_name:
                user.student_profile.full_name = sp.full_name
            if sp.email and sp.email != user.student_profile.email:
                _check_student_email_unique(db, sp.email, exclude_id=user.student_profile.id)
                user.student_profile.email = sp.email

            if sp.department_id:
                _verify_fk_exists(db, Department, sp.department_id, "Department")
                user.student_profile.department_id = sp.department_id
            if sp.academic_class_id:
                _verify_fk_exists(db, AcademicClass, sp.academic_class_id, "Academic Class")
                user.student_profile.academic_class_id = sp.academic_class_id
            if sp.division_id:
                _verify_fk_exists(db, Division, sp.division_id, "Division")
                user.student_profile.division_id = sp.division_id
            if sp.batch_id:
                _verify_fk_exists(db, Batch, sp.batch_id, "Batch")
                user.student_profile.batch_id = sp.batch_id
            if sp.academic_year_id:
                _verify_fk_exists(db, AcademicYear, sp.academic_year_id, "Academic Year")
                user.student_profile.academic_year_id = sp.academic_year_id
            if sp.semester_id:
                _verify_fk_exists(db, Semester, sp.semester_id, "Semester")
                user.student_profile.semester_id = sp.semester_id

        db.commit()
        db.refresh(user)
        return get_user_by_id(db, user.id)

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


def update_user_status(db: Session, user_id: int, is_active: bool) -> User:
    """
    Activates or deactivates a user account and synchronizes status with associated profiles.
    Deactivated users will be blocked from logging in.
    """
    user = get_user_by_id(db, user_id)
    user.is_active = is_active

    if user.teacher_profile:
        user.teacher_profile.is_active = is_active

    if user.student_profile:
        user.student_profile.is_active = is_active

    db.commit()
    db.refresh(user)
    return get_user_by_id(db, user.id)


# --- Helper Validation Functions ---

def _validate_teacher_create(db: Session, tp: TeacherCreate):
    # Check FK Department exists
    _verify_fk_exists(db, Department, tp.department_id, "Department")

    # Check employee_id uniqueness
    existing_emp = db.query(Teacher).filter(Teacher.employee_id == tp.employee_id).first()
    if existing_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher Employee ID '{tp.employee_id}' is already registered."
        )

    # Check teacher email uniqueness
    existing_email = db.query(Teacher).filter(Teacher.email == tp.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher email '{tp.email}' is already registered."
        )


def _validate_student_create(db: Session, sp: StudentCreate):
    # Check FKs
    _verify_fk_exists(db, Department, sp.department_id, "Department")
    _verify_fk_exists(db, AcademicClass, sp.academic_class_id, "Academic Class")
    _verify_fk_exists(db, Division, sp.division_id, "Division")
    _verify_fk_exists(db, Batch, sp.batch_id, "Batch")
    _verify_fk_exists(db, AcademicYear, sp.academic_year_id, "Academic Year")
    _verify_fk_exists(db, Semester, sp.semester_id, "Semester")

    # Check student_id uniqueness
    existing_sid = db.query(Student).filter(Student.student_id == sp.student_id).first()
    if existing_sid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID '{sp.student_id}' is already registered."
        )

    # Check enrollment_number uniqueness
    existing_en = db.query(Student).filter(Student.enrollment_number == sp.enrollment_number).first()
    if existing_en:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Enrollment Number '{sp.enrollment_number}' is already registered."
        )

    # Check student email uniqueness
    existing_email = db.query(Student).filter(Student.email == sp.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student email '{sp.email}' is already registered."
        )


def _verify_fk_exists(db: Session, model_cls, fk_id: int, entity_name: str):
    obj = db.query(model_cls).filter(model_cls.id == fk_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referenced {entity_name} with ID {fk_id} does not exist."
        )


def _check_teacher_email_unique(db: Session, email: str, exclude_id: int):
    existing = db.query(Teacher).filter(Teacher.email == email, Teacher.id != exclude_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher email '{email}' is already registered to another teacher."
        )


def _check_student_email_unique(db: Session, email: str, exclude_id: int):
    existing = db.query(Student).filter(Student.email == email, Student.id != exclude_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student email '{email}' is already registered to another student."
        )
