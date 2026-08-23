from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClassSubjectAssignment(Base):
    """
    Association model connecting Academic Class, optional Division, Subject, Academic Year, and Semester.
    """
    __tablename__ = "class_subject_assignments"
    __table_args__ = (
        UniqueConstraint(
            "academic_class_id", "division_id", "subject_id", "academic_year_id", "semester_id",
            name="uq_class_div_sub_assignment"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    academic_class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    division_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass")
    division: Mapped[Optional["Division"]] = relationship("Division")
    subject: Mapped["Subject"] = relationship("Subject")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear")
    semester: Mapped["Semester"] = relationship("Semester")


class TeacherAssignment(Base):
    """
    Association model assigning Teachers to Subject, Academic Class, optional Division/Batch, Academic Year, and Semester.
    """
    __tablename__ = "teacher_assignments"
    __table_args__ = (
        UniqueConstraint(
            "teacher_id", "subject_id", "academic_class_id", "division_id", "batch_id", "academic_year_id", "semester_id",
            name="uq_teacher_subject_assignment"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    division_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=True, index=True
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    teacher: Mapped["Teacher"] = relationship("Teacher")
    subject: Mapped["Subject"] = relationship("Subject")
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass")
    division: Mapped[Optional["Division"]] = relationship("Division")
    batch: Mapped[Optional["Batch"]] = relationship("Batch")
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear")
    semester: Mapped["Semester"] = relationship("Semester")
