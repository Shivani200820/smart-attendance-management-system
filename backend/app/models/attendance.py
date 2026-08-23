from datetime import date, time, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Date, Time, Text, Enum, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SessionStatus, AttendanceStatus, AttendanceSource


class AttendanceSession(Base):
    """
    Attendance session model initiated by teachers for QR or manual attendance marking.
    """
    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    division_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timetable_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("timetable.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear")
    semester: Mapped["Semester"] = relationship("Semester")
    division: Mapped["Division"] = relationship("Division")
    batch: Mapped[Optional["Batch"]] = relationship("Batch")
    subject: Mapped["Subject"] = relationship("Subject")
    teacher: Mapped["Teacher"] = relationship("Teacher")
    timetable: Mapped[Optional["Timetable"]] = relationship("Timetable")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(
        "AttendanceRecord", back_populates="session", cascade="all, delete-orphan"
    )


class AttendanceRecord(Base):
    """
    Individual student attendance record for a specific session.
    """
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("student_id", "attendance_session_id", name="uq_student_attendance_session"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attendance_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    marked_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[AttendanceSource] = mapped_column(
        Enum(AttendanceSource), default=AttendanceSource.QR, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["AttendanceSession"] = relationship("AttendanceSession", back_populates="attendance_records")
    student: Mapped["Student"] = relationship("Student")
    marker: Mapped[Optional["User"]] = relationship("User", foreign_keys=[marked_by])
    corrections: Mapped[List["AttendanceCorrection"]] = relationship(
        "AttendanceCorrection", back_populates="attendance_record", cascade="all, delete-orphan"
    )


class AttendanceCorrection(Base):
    """
    Audit record for attendance corrections made by authorized users.
    """
    __tablename__ = "attendance_corrections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attendance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    corrected_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    old_status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    new_status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    attendance_record: Mapped["AttendanceRecord"] = relationship("AttendanceRecord", back_populates="corrections")
    corrector: Mapped["User"] = relationship("User", foreign_keys=[corrected_by])
