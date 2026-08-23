from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_roles, get_current_active_user
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.attendance import (
    StudentAttendanceMarkRequest,
    ManualAttendanceMarkRequest,
    AttendanceRecordResponse,
    AttendanceCorrectionRequest,
    AttendanceCorrectionResponse,
    StudentAttendanceReport
)
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance Records & Marking"])


@router.post(
    "/mark",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark Attendance via QR / Token (Student Only)",
    description="Allows an authenticated student to mark attendance for an active session using a valid session token."
)
def mark_attendance(
    data: StudentAttendanceMarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.STUDENT))
):
    return attendance_service.mark_student_attendance(db, current_user, data)


@router.post(
    "/sessions/{session_id}/manual-mark",
    response_model=List[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Manual / Batch Mark Attendance (Admin & Teacher)",
    description="Allows a teacher or admin to manually mark attendance for multiple students in a session."
)
def manual_mark_attendance(
    session_id: int,
    data: ManualAttendanceMarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    return attendance_service.manual_mark_attendance(db, session_id, data, current_user)


@router.get(
    "/sessions/{session_id}/records",
    response_model=List[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Attendance Records for Session (Admin & Teacher)",
    description="Retrieves all attendance records for a specific session with student details."
)
def get_session_records(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    return attendance_service.get_session_attendance_records(db, session_id, current_user)


@router.patch(
    "/records/{record_id}/correct",
    response_model=AttendanceCorrectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Correct Attendance Record (Admin & Session Teacher)",
    description="Modifies an existing attendance record status and logs an audit record in attendance_corrections."
)
def correct_attendance_record(
    record_id: int,
    data: AttendanceCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    return attendance_service.correct_attendance_record(db, record_id, data, current_user)


@router.get(
    "/my-summary",
    response_model=StudentAttendanceReport,
    status_code=status.HTTP_200_OK,
    summary="Get Student Personal Attendance Summary (Student)",
    description="Retrieves attendance percentage and subject breakdown for the currently logged-in student."
)
def get_my_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.STUDENT))
):
    if not current_user.student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for user"
        )
    return attendance_service.get_student_attendance_summary(db, current_user.student_profile.id, current_user)


@router.get(
    "/students/{student_id}/summary",
    response_model=StudentAttendanceReport,
    status_code=status.HTTP_200_OK,
    summary="Get Attendance Summary for Specific Student (Admin, Teacher, Student)",
    description="Retrieves attendance percentage and subject breakdown for a given student ID."
)
def get_student_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return attendance_service.get_student_attendance_summary(db, student_id, current_user)


@router.get(
    "/audit-logs",
    status_code=status.HTTP_200_OK,
    summary="Get Attendance Corrections Audit Logs (Admin & Teacher)",
    description="Retrieves a list of all attendance status corrections and audit reasons."
)
def get_attendance_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))
):
    return attendance_service.get_attendance_audit_logs(db, current_user)


@router.get(
    "/my-history",
    status_code=status.HTTP_200_OK,
    summary="Get Logged-in Student Attendance History (Student)",
    description="Retrieves chronological attendance records marked by the logged-in student."
)
def get_my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.STUDENT))
):
    if not current_user.student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for user"
        )
    return attendance_service.get_student_attendance_history(db, current_user.student_profile.id)

