from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Teacher(Base):
    """
    Teacher profile entity linked to Department and optional User account.
    """
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True
    )
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="teacher_profile")
    department: Mapped["Department"] = relationship("Department", back_populates="teachers")


class Student(Base):
    """
    Student profile entity linked to Department, AcademicClass, Division, Batch, Semester, AcademicYear.
    """
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint(
            "division_id", "academic_year_id", "semester_id", "roll_number",
            name="uq_division_academic_roll"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True
    )
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    roll_number: Mapped[str] = mapped_column(String(50), nullable=False)
    enrollment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    academic_class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_classes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    division_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("divisions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="student_profile")
    department: Mapped["Department"] = relationship("Department", back_populates="students")
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="students")
    division: Mapped["Division"] = relationship("Division", back_populates="students")
    batch: Mapped["Batch"] = relationship("Batch", back_populates="students")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", back_populates="students")
    semester: Mapped["Semester"] = relationship("Semester", back_populates="students")
