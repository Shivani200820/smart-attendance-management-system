from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_roles, get_current_active_user
from app.models.user import User
from app.models.enums import UserRole, SessionStatus
from app.schemas.attendance_session import (
    AttendanceSessionCreate,
    AttendanceSessionResponse,
)
from app.services import attendance_session_service

router = APIRouter(prefix="/attendance-sessions", tags=["Attendance Session Management"])


@router.post(
    "",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Attendance Session (Admin & Teacher)",
    description="Creates a new attendance session with ACTIVE status. Teachers can only create sessions for themselves."
)
def create_attendance_session(
    data: AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or data.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only create attendance sessions for themselves"
            )
    return attendance_session_service.create_attendance_session(db, data)


@router.get(
    "",
    response_model=List[AttendanceSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Attendance Sessions (Authenticated Users)",
    description="Retrieves attendance sessions with optional filtering. Automatically evaluates past active sessions as EXPIRED."
)
def list_attendance_sessions(
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    division_id: Optional[int] = Query(None, description="Filter by Division ID"),
    batch_id: Optional[int] = Query(None, description="Filter by Batch ID"),
    subject_id: Optional[int] = Query(None, description="Filter by Subject ID"),
    teacher_id: Optional[int] = Query(None, description="Filter by Teacher ID"),
    session_date: Optional[date] = Query(None, description="Filter by Session Date"),
    session_status: Optional[SessionStatus] = Query(None, alias="status", description="Filter by Session Status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return attendance_session_service.list_attendance_sessions(
        db,
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        division_id=division_id,
        batch_id=batch_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        session_date=session_date,
        session_status=session_status
    )


@router.get(
    "/token/{session_token}",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session by Unique Token (Authenticated Users)",
    description="Retrieves attendance session details using a secure session token."
)
def get_attendance_session_by_token(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return attendance_session_service.get_attendance_session_by_token(db, session_token)


@router.get(
    "/{session_id}",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Attendance Session by ID (Authenticated Users)",
    description="Returns detailed session information for a specific session ID."
)
def get_attendance_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return attendance_session_service.get_attendance_session(db, session_id)


@router.patch(
    "/{session_id}/close",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Close Attendance Session (Admin & Session Teacher)",
    description="Closes an ACTIVE attendance session and records `closed_at` timestamp. Teachers can only close their own sessions."
)
def close_attendance_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    session_obj = attendance_session_service.get_attendance_session(db, session_id)
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or session_obj.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only close their own attendance sessions"
            )
    return attendance_session_service.close_attendance_session(db, session_id)


@router.patch(
    "/{session_id}/cancel",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Attendance Session (Admin & Session Teacher)",
    description="Cancels an ACTIVE attendance session. Teachers can only cancel their own sessions."
)
def cancel_attendance_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    session_obj = attendance_session_service.get_attendance_session(db, session_id)
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or session_obj.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only cancel their own attendance sessions"
            )
    return attendance_session_service.cancel_attendance_session(db, session_id)
