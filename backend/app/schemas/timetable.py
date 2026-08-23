from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import DayOfWeek


class TimetableStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Active status flag")


class TimetableCreate(BaseModel):
    academic_year_id: int = Field(..., description="Academic Year ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    division_id: int = Field(..., description="Division ID", example=1)
    batch_id: Optional[int] = Field(None, description="Optional Batch ID", example=1)
    subject_id: int = Field(..., description="Subject ID", example=1)
    teacher_id: int = Field(..., description="Teacher ID", example=1)
    day_of_week: DayOfWeek = Field(..., description="Day of the week (e.g. MONDAY)", example="MONDAY")
    start_time: time = Field(..., description="Class start time (HH:MM:SS)", example="09:00:00")
    end_time: time = Field(..., description="Class end time (HH:MM:SS)", example="10:00:00")
    room: Optional[str] = Field(None, description="Optional Classroom or Lab", example="Room 302")
    is_active: bool = Field(True, description="Active status")


class TimetableUpdate(BaseModel):
    academic_year_id: Optional[int] = Field(None, description="Updated Academic Year ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")
    division_id: Optional[int] = Field(None, description="Updated Division ID")
    batch_id: Optional[int] = Field(None, description="Updated Batch ID")
    subject_id: Optional[int] = Field(None, description="Updated Subject ID")
    teacher_id: Optional[int] = Field(None, description="Updated Teacher ID")
    day_of_week: Optional[DayOfWeek] = Field(None, description="Updated Day of the week")
    start_time: Optional[time] = Field(None, description="Updated Class start time")
    end_time: Optional[time] = Field(None, description="Updated Class end time")
    room: Optional[str] = Field(None, description="Updated Classroom or Lab")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class TimetableResponse(BaseModel):
    id: int
    academic_year_id: int
    semester_id: int
    division_id: int
    batch_id: Optional[int] = None
    subject_id: int
    teacher_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
