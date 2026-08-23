from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Date, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AcademicYear(Base):
    """
    Represents an Academic Year (e.g. 2026-27).
    """
    __tablename__ = "academic_years"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    semesters: Mapped[List["Semester"]] = relationship("Semester", back_populates="academic_year", cascade="all, delete-orphan")
    divisions: Mapped[List["Division"]] = relationship("Division", back_populates="academic_year")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="academic_year")


class Semester(Base):
    """
    Represents a Semester belonging to an Academic Year.
    """
    __tablename__ = "semesters"
    __table_args__ = (
        UniqueConstraint("academic_year_id", "semester_number", name="uq_academic_year_semester"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", back_populates="semesters")
    divisions: Mapped[List["Division"]] = relationship("Division", back_populates="semester")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="semester")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="semester")


class Department(Base):
    """
    Represents an Academic Department (e.g., Computer Engineering).
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    academic_classes: Mapped[List["AcademicClass"]] = relationship("AcademicClass", back_populates="department", cascade="all, delete-orphan")
    teachers: Mapped[List["Teacher"]] = relationship("Teacher", back_populates="department")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="department")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="department")


class AcademicClass(Base):
    """
    Represents Academic Year/Class Level (e.g. FE, SE, TE, BE).
    """
    __tablename__ = "academic_classes"
    __table_args__ = (
        UniqueConstraint("department_id", "code", name="uq_department_class_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="academic_classes")
    divisions: Mapped[List["Division"]] = relationship("Division", back_populates="academic_class", cascade="all, delete-orphan")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="academic_class")


class Division(Base):
    """
    Represents a Division belonging to an Academic Class, Semester, and Academic Year.
    """
    __tablename__ = "divisions"
    __table_args__ = (
        UniqueConstraint(
            "academic_class_id", "academic_year_id", "semester_id", "name",
            name="uq_class_year_semester_division"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    academic_class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="divisions")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", back_populates="divisions")
    semester: Mapped["Semester"] = relationship("Semester", back_populates="divisions")
    batches: Mapped[List["Batch"]] = relationship("Batch", back_populates="division", cascade="all, delete-orphan")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="division")


class Batch(Base):
    """
    Represents a practical/tutorial batch belonging to a Division.
    """
    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("division_id", "name", name="uq_division_batch"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    division_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    division: Mapped["Division"] = relationship("Division", back_populates="batches")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="batch")
