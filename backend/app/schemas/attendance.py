from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import AttendanceStatus, AttendanceSource, SessionStatus


class StudentAttendanceMarkRequest(BaseModel):
    session_token: str = Field(..., description="Unique QR session token scanned by student", example="abc123token")


class ManualAttendanceItem(BaseModel):
    student_id: int = Field(..., description="ID of student to mark", example=1)
    status: AttendanceStatus = Field(..., description="Attendance status (PRESENT or ABSENT)", example="PRESENT")


class ManualAttendanceMarkRequest(BaseModel):
    records: List[ManualAttendanceItem] = Field(..., description="List of attendance status items for students")


class AttendanceRecordResponse(BaseModel):
    id: int
    attendance_session_id: int
    student_id: int
    status: AttendanceStatus
    marked_at: datetime
    marked_by: Optional[int] = None
    source: AttendanceSource
    created_at: datetime
    updated_at: datetime

    # Student details
    student_roll_number: Optional[str] = None
    student_full_name: Optional[str] = None
    student_code: Optional[str] = None
    student_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceCorrectionRequest(BaseModel):
    new_status: AttendanceStatus = Field(..., description="Target attendance status", example="PRESENT")
    reason: str = Field(..., description="Reason for attendance status modification", example="Student presented valid medical certificate")


class AttendanceCorrectionResponse(BaseModel):
    id: int
    attendance_id: int
    corrected_by: int
    old_status: AttendanceStatus
    new_status: AttendanceStatus
    reason: str
    corrected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubjectAttendanceSummary(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    total_sessions: int
    attended_sessions: int
    percentage: float


class StudentAttendanceReport(BaseModel):
    student_id: int
    roll_number: str
    full_name: str
    department_name: Optional[str] = None
    division_name: Optional[str] = None
    total_sessions: int
    attended_sessions: int
    overall_percentage: float
    subject_breakdown: List[SubjectAttendanceSummary]


class DefaulterStudent(BaseModel):
    student_id: int
    roll_number: str
    full_name: str
    email: str
    division_name: Optional[str] = None
    total_sessions: int
    attended_sessions: int
    attendance_percentage: float


class DefaulterReportResponse(BaseModel):
    academic_year_id: Optional[int] = None
    division_id: Optional[int] = None
    threshold_percentage: float
    defaulters_count: int
    defaulters: List[DefaulterStudent]
