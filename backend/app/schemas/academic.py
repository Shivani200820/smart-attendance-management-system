from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Generic Active Status Schema ---

class StatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Active status flag")


# --- 1. Academic Year Schemas ---

class AcademicYearCreate(BaseModel):
    name: str = Field(..., description="Unique Academic Year Name", example="2026-2027")
    start_date: date = Field(..., description="Start Date of Academic Year", example="2026-07-01")
    end_date: date = Field(..., description="End Date of Academic Year", example="2027-06-30")
    is_active: bool = Field(True, description="Active status")


class AcademicYearUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated Academic Year Name")
    start_date: Optional[date] = Field(None, description="Updated Start Date")
    end_date: Optional[date] = Field(None, description="Updated End Date")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class AcademicYearResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 2. Semester Schemas ---

class SemesterCreate(BaseModel):
    academic_year_id: int = Field(..., description="Parent Academic Year ID", example=1)
    semester_number: int = Field(..., ge=1, description="Semester number (1, 2, etc.)", example=1)
    name: str = Field(..., description="Semester Name", example="Semester 1")
    start_date: Optional[date] = Field(None, description="Semester Start Date")
    end_date: Optional[date] = Field(None, description="Semester End Date")
    is_active: bool = Field(True, description="Active status")


class SemesterUpdate(BaseModel):
    academic_year_id: Optional[int] = Field(None, description="Updated Academic Year ID")
    semester_number: Optional[int] = Field(None, ge=1, description="Updated Semester number")
    name: Optional[str] = Field(None, description="Updated Semester Name")
    start_date: Optional[date] = Field(None, description="Updated Start Date")
    end_date: Optional[date] = Field(None, description="Updated End Date")
    is_active: Optional[bool] = Field(None, description="Updated Active status")



class SemesterResponse(BaseModel):
    id: int
    academic_year_id: int
    semester_number: int
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 3. Department Schemas ---

class DepartmentCreate(BaseModel):
    name: str = Field(..., description="Department Name", example="Computer Engineering")
    code: str = Field(..., description="Unique Department Code", example="COMP")
    is_active: bool = Field(True, description="Active status")


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated Department Name")
    code: Optional[str] = Field(None, description="Updated Department Code")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 4. Academic Class Schemas ---

class AcademicClassCreate(BaseModel):
    department_id: int = Field(..., description="Department ID", example=1)
    name: str = Field(..., description="Academic Class Name", example="Second Year")
    code: str = Field(..., description="Class Code", example="SE")
    is_active: bool = Field(True, description="Active status")


class AcademicClassUpdate(BaseModel):
    department_id: Optional[int] = Field(None, description="Updated Department ID")
    name: Optional[str] = Field(None, description="Updated Class Name")
    code: Optional[str] = Field(None, description="Updated Class Code")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class AcademicClassResponse(BaseModel):
    id: int
    department_id: int
    name: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 5. Division Schemas ---

class DivisionCreate(BaseModel):
    academic_class_id: int = Field(..., description="Academic Class ID", example=1)
    academic_year_id: int = Field(..., description="Academic Year ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    name: str = Field(..., description="Division Name", example="A")
    is_active: bool = Field(True, description="Active status")


class DivisionUpdate(BaseModel):
    academic_class_id: Optional[int] = Field(None, description="Updated Class ID")
    academic_year_id: Optional[int] = Field(None, description="Updated Year ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")
    name: Optional[str] = Field(None, description="Updated Division Name")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class DivisionResponse(BaseModel):
    id: int
    academic_class_id: int
    academic_year_id: int
    semester_id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 6. Batch Schemas ---

class BatchCreate(BaseModel):
    division_id: int = Field(..., description="Division ID", example=1)
    name: str = Field(..., description="Batch Name", example="B1")
    is_active: bool = Field(True, description="Active status")


class BatchUpdate(BaseModel):
    division_id: Optional[int] = Field(None, description="Updated Division ID")
    name: Optional[str] = Field(None, description="Updated Batch Name")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class BatchResponse(BaseModel):
    id: int
    division_id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 7. Subject Schemas ---

class SubjectCreate(BaseModel):
    name: str = Field(..., description="Subject Name", example="Data Structures & Algorithms")
    code: str = Field(..., description="Subject Code", example="CS201")
    department_id: int = Field(..., description="Department ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    is_active: bool = Field(True, description="Active status")


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated Subject Name")
    code: Optional[str] = Field(None, description="Updated Subject Code")
    department_id: Optional[int] = Field(None, description="Updated Department ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    department_id: int
    semester_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 8. Class-Subject Assignment Schemas ---

class ClassSubjectAssignmentCreate(BaseModel):
    academic_class_id: int = Field(..., description="Academic Class ID", example=1)
    division_id: Optional[int] = Field(None, description="Optional Division ID", example=1)
    subject_id: int = Field(..., description="Subject ID", example=1)
    academic_year_id: int = Field(..., description="Academic Year ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    is_active: bool = Field(True, description="Active status")


class ClassSubjectAssignmentUpdate(BaseModel):
    academic_class_id: Optional[int] = Field(None, description="Updated Class ID")
    division_id: Optional[int] = Field(None, description="Updated Division ID")
    subject_id: Optional[int] = Field(None, description="Updated Subject ID")
    academic_year_id: Optional[int] = Field(None, description="Updated Year ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class ClassSubjectAssignmentResponse(BaseModel):
    id: int
    academic_class_id: int
    division_id: Optional[int] = None
    subject_id: int
    academic_year_id: int
    semester_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 9. Teacher Assignment Schemas ---

class TeacherAssignmentCreate(BaseModel):
    teacher_id: int = Field(..., description="Teacher ID", example=1)
    subject_id: int = Field(..., description="Subject ID", example=1)
    academic_class_id: int = Field(..., description="Academic Class ID", example=1)
    division_id: Optional[int] = Field(None, description="Optional Division ID", example=1)
    batch_id: Optional[int] = Field(None, description="Optional Batch ID", example=1)
    academic_year_id: int = Field(..., description="Academic Year ID", example=1)
    semester_id: int = Field(..., description="Semester ID", example=1)
    is_active: bool = Field(True, description="Active status")


class TeacherAssignmentUpdate(BaseModel):
    teacher_id: Optional[int] = Field(None, description="Updated Teacher ID")
    subject_id: Optional[int] = Field(None, description="Updated Subject ID")
    academic_class_id: Optional[int] = Field(None, description="Updated Class ID")
    division_id: Optional[int] = Field(None, description="Updated Division ID")
    batch_id: Optional[int] = Field(None, description="Updated Batch ID")
    academic_year_id: Optional[int] = Field(None, description="Updated Year ID")
    semester_id: Optional[int] = Field(None, description="Updated Semester ID")
    is_active: Optional[bool] = Field(None, description="Updated Active status")


class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    subject_id: int
    academic_class_id: int
    division_id: Optional[int] = None
    batch_id: Optional[int] = None
    academic_year_id: int
    semester_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
