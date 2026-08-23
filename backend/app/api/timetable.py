from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin, get_current_active_user
from app.models.user import User
from app.models.enums import DayOfWeek
from app.schemas.timetable import (
    TimetableCreate,
    TimetableUpdate,
    TimetableStatusUpdate,
    TimetableResponse,
)
from app.services import timetable_service

router = APIRouter(prefix="/timetable", tags=["Timetable Management"])


@router.post(
    "",
    response_model=TimetableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Timetable Entry (Admin only)",
    description="Creates a new timetable schedule entry. Protected by ADMIN role guard."
)
def create_timetable(
    data: TimetableCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return timetable_service.create_timetable(db, data)


@router.get(
    "",
    response_model=List[TimetableResponse],
    status_code=status.HTTP_200_OK,
    summary="List Timetable Entries (Authenticated Users)",
    description="Retrieves timetable entries with optional filtering by year, semester, class, division, batch, subject, teacher, day of week, or active status."
)
def list_timetables(
    academic_year_id: Optional[int] = Query(None, description="Filter by Academic Year ID"),
    semester_id: Optional[int] = Query(None, description="Filter by Semester ID"),
    division_id: Optional[int] = Query(None, description="Filter by Division ID"),
    batch_id: Optional[int] = Query(None, description="Filter by Batch ID"),
    subject_id: Optional[int] = Query(None, description="Filter by Subject ID"),
    teacher_id: Optional[int] = Query(None, description="Filter by Teacher ID"),
    day_of_week: Optional[DayOfWeek] = Query(None, description="Filter by Day of Week"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return timetable_service.list_timetables(
        db,
        academic_year_id=academic_year_id,
        semester_id=semester_id,
        division_id=division_id,
        batch_id=batch_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        is_active=is_active
    )


@router.get(
    "/{timetable_id}",
    response_model=TimetableResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Timetable Entry by ID (Authenticated Users)",
    description="Returns full schedule details for a specific timetable entry ID."
)
def get_timetable(
    timetable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return timetable_service.get_timetable(db, timetable_id)


@router.put(
    "/{timetable_id}",
    response_model=TimetableResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Timetable Entry (Admin only)",
    description="Updates fields of an existing timetable entry. Protected by ADMIN role guard."
)
def update_timetable(
    timetable_id: int,
    data: TimetableUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return timetable_service.update_timetable(db, timetable_id, data)


@router.patch(
    "/{timetable_id}/status",
    response_model=TimetableResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate / Deactivate Timetable Entry (Admin only)",
    description="Toggles the `is_active` status of a timetable entry. Protected by ADMIN role guard."
)
def update_timetable_status(
    timetable_id: int,
    status_in: TimetableStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return timetable_service.update_timetable_status(db, timetable_id, status_in.is_active)
