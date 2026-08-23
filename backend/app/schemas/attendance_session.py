from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import SessionStatus


class AttendanceSessionCreate(BaseModel):
    academic_year_id: int = Field(..., description="Academic Year ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    division_id: int = Field(..., description="Division ID", example=1)
    batch_id: Optional[int] = Field(None, description="Optional Batch ID", example=1)
    subject_id: int = Field(..., description="Subject ID", example=1)
    teacher_id: int = Field(..., description="Teacher ID", example=1)
    timetable_id: Optional[int] = Field(None, description="Optional Timetable ID", example=1)
    session_date: date = Field(..., description="Session date (YYYY-MM-DD)", example="2026-08-19")
    start_time: time = Field(..., description="Session start time (HH:MM:SS)", example="09:00:00")
    end_time: time = Field(..., description="Session end time (HH:MM:SS)", example="10:00:00")
    expires_at: datetime = Field(..., description="Session expiration datetime", example="2026-08-19T10:15:00Z")


class AttendanceSessionResponse(BaseModel):
    id: int
    session_token: str
    academic_year_id: int
    semester_id: int
    division_id: int
    batch_id: Optional[int] = None
    subject_id: int
    teacher_id: int
    timetable_id: Optional[int] = None
    session_date: date
    start_time: time
    end_time: time
    expires_at: datetime
    status: SessionStatus
    created_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
