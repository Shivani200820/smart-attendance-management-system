import secrets
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.attendance import AttendanceSession
from app.models.academic import AcademicYear, Semester, Division, Batch
from app.models.subject import Subject
from app.models.profiles import Teacher
from app.models.timetable import Timetable
from app.models.enums import SessionStatus
from app.schemas.attendance_session import AttendanceSessionCreate


def _get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _evaluate_expired_sessions(db: Session) -> None:
    now_utc = _get_utc_now()
    active_sessions = db.execute(
        select(AttendanceSession).where(AttendanceSession.status == SessionStatus.ACTIVE)
    ).scalars().all()

    modified = False
    for session in active_sessions:
        exp = session.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp <= now_utc:
            session.status = SessionStatus.EXPIRED
            modified = True

    if modified:
        db.commit()


def create_attendance_session(db: Session, data: AttendanceSessionCreate) -> AttendanceSession:
    _evaluate_expired_sessions(db)

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be strictly before end_time"
        )

    now_utc = _get_utc_now()
    exp_dt = data.expires_at
    if exp_dt.tzinfo is None:
        exp_dt = exp_dt.replace(tzinfo=timezone.utc)

    if exp_dt <= now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expires_at must be a future timestamp"
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
    if data.timetable_id is not None and not db.get(Timetable, data.timetable_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Timetable entry with ID {data.timetable_id} does not exist"
        )

    # Prevent duplicate active session conflict
    batch_cond = (
        AttendanceSession.batch_id == data.batch_id
        if data.batch_id is not None
        else AttendanceSession.batch_id.is_(None)
    )
    existing_active = db.execute(
        select(AttendanceSession).where(
            and_(
                AttendanceSession.division_id == data.division_id,
                batch_cond,
                AttendanceSession.subject_id == data.subject_id,
                AttendanceSession.teacher_id == data.teacher_id,
                AttendanceSession.session_date == data.session_date,
                AttendanceSession.status == SessionStatus.ACTIVE
            )
        )
    ).scalars().first()

    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active attendance session already exists for this division, subject, teacher, and date"
        )

    token = secrets.token_urlsafe(32)

    session_obj = AttendanceSession(
        session_token=token,
        academic_year_id=data.academic_year_id,
        semester_id=data.semester_id,
        division_id=data.division_id,
        batch_id=data.batch_id,
        subject_id=data.subject_id,
        teacher_id=data.teacher_id,
        timetable_id=data.timetable_id,
        session_date=data.session_date,
        start_time=data.start_time,
        end_time=data.end_time,
        expires_at=data.expires_at,
        status=SessionStatus.ACTIVE
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj


def list_attendance_sessions(
    db: Session,
    academic_year_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    division_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    session_date: Optional[date] = None,
    session_status: Optional[SessionStatus] = None
) -> List[AttendanceSession]:
    _evaluate_expired_sessions(db)

    query = select(AttendanceSession)
    if academic_year_id is not None:
        query = query.where(AttendanceSession.academic_year_id == academic_year_id)
    if semester_id is not None:
        query = query.where(AttendanceSession.semester_id == semester_id)
    if division_id is not None:
        query = query.where(AttendanceSession.division_id == division_id)
    if batch_id is not None:
        query = query.where(AttendanceSession.batch_id == batch_id)
    if subject_id is not None:
        query = query.where(AttendanceSession.subject_id == subject_id)
    if teacher_id is not None:
        query = query.where(AttendanceSession.teacher_id == teacher_id)
    if session_date is not None:
        query = query.where(AttendanceSession.session_date == session_date)
    if session_status is not None:
        query = query.where(AttendanceSession.status == session_status)

    return list(db.execute(query.order_by(AttendanceSession.id.desc())).scalars().all())


def get_attendance_session(db: Session, session_id: int) -> AttendanceSession:
    _evaluate_expired_sessions(db)
    session_obj = db.get(AttendanceSession, session_id)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance session with ID {session_id} not found"
        )
    return session_obj


def get_attendance_session_by_token(db: Session, session_token: str) -> AttendanceSession:
    _evaluate_expired_sessions(db)
    session_obj = db.execute(
        select(AttendanceSession).where(AttendanceSession.session_token == session_token)
    ).scalars().first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance session token '{session_token}' not found"
        )
    return session_obj


def close_attendance_session(db: Session, session_id: int) -> AttendanceSession:
    _evaluate_expired_sessions(db)
    session_obj = get_attendance_session(db, session_id)

    if session_obj.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot close session with status {session_obj.status.value}"
        )

    session_obj.status = SessionStatus.CLOSED
    session_obj.closed_at = _get_utc_now()
    db.commit()
    db.refresh(session_obj)
    return session_obj


def cancel_attendance_session(db: Session, session_id: int) -> AttendanceSession:
    _evaluate_expired_sessions(db)
    session_obj = get_attendance_session(db, session_id)

    if session_obj.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel session with status {session_obj.status.value}"
        )

    session_obj.status = SessionStatus.CANCELLED
    db.commit()
    db.refresh(session_obj)
    return session_obj
