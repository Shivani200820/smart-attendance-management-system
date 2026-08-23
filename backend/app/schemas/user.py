from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole


# --- Teacher Profile Schemas ---

class TeacherCreate(BaseModel):
    employee_id: str = Field(..., description="Unique Teacher Employee ID", example="EMP1001")
    full_name: str = Field(..., description="Teacher Full Name", example="Dr. Alan Turing")
    email: EmailStr = Field(..., description="Teacher Email Address", example="turing@attendance.com")
    department_id: Optional[int] = Field(1, description="Associated Department ID", example=1)


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Updated Full Name")
    email: Optional[EmailStr] = Field(None, description="Updated Email Address")
    department_id: Optional[int] = Field(None, description="Updated Department ID")


class TeacherResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    employee_id: str
    full_name: str
    email: str
    department_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Student Profile Schemas ---

class StudentCreate(BaseModel):
    student_id: Optional[str] = Field(None, description="Unique Student ID", example="STU2026001")
    roll_number: str = Field(..., description="Roll Number in Class", example="CS001")
    enrollment_number: Optional[str] = Field(None, description="University Enrollment Number", example="EN20269988")
    full_name: str = Field(..., description="Student Full Name", example="Ada Lovelace")
    email: EmailStr = Field(..., description="Student Email Address", example="ada@attendance.com")
    department_id: Optional[int] = Field(1, description="Department ID", example=1)
    academic_class_id: Optional[int] = Field(1, description="Academic Class Level ID", example=1)
    division_id: Optional[int] = Field(1, description="Division ID", example=1)
    batch_id: Optional[int] = Field(1, description="Batch ID", example=1)
    academic_year_id: Optional[int] = Field(1, description="Academic Year ID", example=1)
    semester_id: Optional[int] = Field(1, description="Semester ID", example=1)


class StudentUpdate(BaseModel):
    roll_number: Optional[str] = Field(None, description="Updated Roll Number")
    full_name: Optional[str] = Field(None, description="Updated Full Name")
    email: Optional[EmailStr] = Field(None, description="Updated Email Address")
    department_id: Optional[int] = Field(None, description="Updated Department ID")
    academic_class_id: Optional[int] = Field(None, description="Updated Class ID")
    division_id: Optional[int] = Field(None, description="Updated Division ID")
    batch_id: Optional[int] = Field(None, description="Updated Batch ID")
    academic_year_id: Optional[int] = Field(None, description="Updated Academic Year ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")


class StudentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    student_id: str
    roll_number: str
    enrollment_number: str
    full_name: str
    email: str
    department_id: int
    academic_class_id: int
    division_id: int
    batch_id: int
    academic_year_id: int
    semester_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- User Schemas ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, description="Unique Username", example="turing_a")
    email: EmailStr = Field(..., description="User Email Address", example="turing@attendance.com")
    password: str = Field(..., min_length=6, description="User Password", example="TeacherPass@123")
    role: UserRole = Field(..., description="Role (ADMIN, TEACHER, STUDENT)")
    teacher_profile: Optional[TeacherCreate] = Field(None, description="Required profile payload if role is TEACHER")
    student_profile: Optional[StudentCreate] = Field(None, description="Required profile payload if role is STUDENT")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="Updated Username")
    email: Optional[EmailStr] = Field(None, description="Updated User Email")
    password: Optional[str] = Field(None, min_length=6, description="Updated Password")
    teacher_profile: Optional[TeacherUpdate] = Field(None, description="Profile updates if user is TEACHER")
    student_profile: Optional[StudentUpdate] = Field(None, description="Profile updates if user is STUDENT")


class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="User active status flag")


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    teacher_profile: Optional[TeacherResponse] = None
    student_profile: Optional[StudentResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserPaginatedResponse(BaseModel):
    items: List[UserDetailResponse]
    total: int
    page: int
    page_size: int
