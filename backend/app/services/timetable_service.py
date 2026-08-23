from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.timetable import Timetable
from app.models.academic import AcademicYear, Semester, Division, Batch
from app.models.subject import Subject
from app.models.profiles import Teacher
from app.models.enums import DayOfWeek
from app.schemas.timetable import TimetableCreate, TimetableUpdate


def create_timetable(db: Session, data: TimetableCreate) -> Timetable:
    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be strictly before end_time"
        )

    # Validate foreign keys
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
    if not db.get(Division, data.division_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with ID {data.division_id} does not exist"
        )
    if data.batch_id is not None and not db.get(Batch, data.batch_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch with ID {data.batch_id} does not exist"
        )
    if not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if not db.get(Teacher, data.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher with ID {data.teacher_id} does not exist"
        )

    entry = Timetable(
        academic_year_id=data.academic_year_id,
        semester_id=data.semester_id,
        division_id=data.division_id,
        batch_id=data.batch_id,
        subject_id=data.subject_id,
        teacher_id=data.teacher_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        room=data.room,
        is_active=data.is_active
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_timetables(
    db: Session,
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    division_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    day_of_week: Optional[DayOfWeek] = None,
    is_active: Optional[bool] = None
) -> List[Timetable]:
    query = select(Timetable)
    if academic_year_id is not None:
        query = query.where(Timetable.academic_year_id == academic_year_id)
    if semester_id is not None:
        query = query.where(Timetable.semester_id == semester_id)
    if division_id is not None:
        query = query.where(Timetable.division_id == division_id)
    if batch_id is not None:
        query = query.where(Timetable.batch_id == batch_id)
    if subject_id is not None:
        query = query.where(Timetable.subject_id == subject_id)
    if teacher_id is not None:
        query = query.where(Timetable.teacher_id == teacher_id)
    if day_of_week is not None:
        query = query.where(Timetable.day_of_week == day_of_week)
    if is_active is not None:
        query = query.where(Timetable.is_active == is_active)

    return list(db.execute(query.order_by(Timetable.id.desc())).scalars().all())


def get_timetable(db: Session, timetable_id: int) -> Timetable:
    entry = db.get(Timetable, timetable_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable entry with ID {timetable_id} not found"
        )
    return entry


def update_timetable(db: Session, timetable_id: int, data: TimetableUpdate) -> Timetable:
    entry = get_timetable(db, timetable_id)

    new_start = data.start_time if data.start_time is not None else entry.start_time
    new_end = data.end_time if data.end_time is not None else entry.end_time
    if new_start >= new_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be strictly before end_time"
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
    if data.subject_id is not None and not db.get(Subject, data.subject_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with ID {data.subject_id} does not exist"
        )
    if data.teacher_id is not None and not db.get(Teacher, data.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher with ID {data.teacher_id} does not exist"
        )

    if data.academic_year_id is not None:
        entry.academic_year_id = data.academic_year_id
    if data.semester_id is not None:
        entry.semester_id = data.semester_id
    if data.division_id is not None:
        entry.division_id = data.division_id
    if data.batch_id is not None:
        entry.batch_id = data.batch_id
    if data.subject_id is not None:
        entry.subject_id = data.subject_id
    if data.teacher_id is not None:
        entry.teacher_id = data.teacher_id
    if data.day_of_week is not None:
        entry.day_of_week = data.day_of_week
    if data.start_time is not None:
        entry.start_time = data.start_time
    if data.end_time is not None:
        entry.end_time = data.end_time
    if data.room is not None:
        entry.room = data.room
    if data.is_active is not None:
        entry.is_active = data.is_active

    db.commit()
    db.refresh(entry)
    return entry


def update_timetable_status(db: Session, timetable_id: int, is_active: bool) -> Timetable:
    entry = get_timetable(db, timetable_id)
    entry.is_active = is_active
    db.commit()
    db.refresh(entry)
    return entry
