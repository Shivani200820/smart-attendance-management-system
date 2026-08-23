from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceCorrection
from app.models.profiles import Student, Teacher
from app.models.academic import Division, Batch, AcademicClass, Department
from app.models.subject import Subject
from app.models.user import User
from app.models.enums import UserRole, SessionStatus, AttendanceStatus, AttendanceSource
from app.schemas.attendance import (
    StudentAttendanceMarkRequest,
    ManualAttendanceMarkRequest,
    AttendanceRecordResponse,
    AttendanceCorrectionRequest,
    AttendanceCorrectionResponse,
    StudentAttendanceReport,
    SubjectAttendanceSummary,
    DefaulterStudent,
    DefaulterReportResponse
)


def _enrich_record_response(record: AttendanceRecord) -> AttendanceRecordResponse:
    res = AttendanceRecordResponse.model_validate(record)
    if record.student:
        res.student_roll_number = record.student.roll_number
        res.student_full_name = record.student.full_name
        res.student_code = record.student.student_id
        res.student_email = record.student.email
    return res


def mark_student_attendance(
    db: Session,
    current_user: User,
    data: StudentAttendanceMarkRequest
) -> AttendanceRecordResponse:
    if current_user.role != UserRole.STUDENT or not current_user.student_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated student accounts can mark attendance"
        )
    
    student = current_user.student_profile

    # Fetch session by token
    session_obj = db.query(AttendanceSession).filter(
        AttendanceSession.session_token == data.session_token
    ).first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid attendance session token"
        )

    # Expiry validation
    now_utc = datetime.now(timezone.utc)
    expires_at = session_obj.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now_utc > expires_at or session_obj.status == SessionStatus.EXPIRED:
        if session_obj.status == SessionStatus.ACTIVE:
            session_obj.status = SessionStatus.EXPIRED
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance session has expired"
        )

    if session_obj.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attendance session is {session_obj.status.value} and does not accept attendance"
        )

    # Academic Structure Match
    if student.division_id != session_obj.division_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not assigned to the division of this attendance session"
        )

    if session_obj.batch_id is not None and student.batch_id != session_obj.batch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not assigned to the batch of this attendance session"
        )

    # Duplicate check
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.attendance_session_id == session_obj.id,
        AttendanceRecord.student_id == student.id
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance has already been marked for this session"
        )

    # Create record
    record = AttendanceRecord(
        attendance_session_id=session_obj.id,
        student_id=student.id,
        status=AttendanceStatus.PRESENT,
        marked_by=current_user.id,
        source=AttendanceSource.QR
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return _enrich_record_response(record)


def manual_mark_attendance(
    db: Session,
    session_id: int,
    data: ManualAttendanceMarkRequest,
    current_user: User
) -> List[AttendanceRecordResponse]:
    session_obj = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance session not found"
        )

    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or session_obj.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only mark attendance for their own sessions"
            )

    result_records = []
    for item in data.records:
        student = db.query(Student).filter(Student.id == item.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student ID {item.student_id} not found"
            )

        if student.division_id != session_obj.division_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {student.full_name} does not belong to session's division"
            )

        record = db.query(AttendanceRecord).filter(
            AttendanceRecord.attendance_session_id == session_id,
            AttendanceRecord.student_id == item.student_id
        ).first()

        if record:
            record.status = item.status
            record.marked_by = current_user.id
            record.source = AttendanceSource.MANUAL
        else:
            record = AttendanceRecord(
                attendance_session_id=session_id,
                student_id=item.student_id,
                status=item.status,
                marked_by=current_user.id,
                source=AttendanceSource.MANUAL
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        result_records.append(_enrich_record_response(record))

    return result_records


def get_session_attendance_records(
    db: Session,
    session_id: int,
    current_user: User
) -> List[AttendanceRecordResponse]:
    session_obj = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance session not found"
        )

    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or session_obj.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only view attendance for their own sessions"
            )

    records = db.query(AttendanceRecord).options(
        joinedload(AttendanceRecord.student)
    ).filter(AttendanceRecord.attendance_session_id == session_id).all()

    return [_enrich_record_response(r) for r in records]


def correct_attendance_record(
    db: Session,
    record_id: int,
    data: AttendanceCorrectionRequest,
    current_user: User
) -> AttendanceCorrectionResponse:
    record = db.query(AttendanceRecord).options(
        joinedload(AttendanceRecord.session)
    ).filter(AttendanceRecord.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    # Authorization Check
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or record.session.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only correct attendance for their own sessions"
            )
    elif current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot modify attendance records"
        )

    old_status = record.status

    # Create correction audit log
    correction = AttendanceCorrection(
        attendance_id=record.id,
        corrected_by=current_user.id,
        old_status=old_status,
        new_status=data.new_status,
        reason=data.reason
    )
    db.add(correction)

    # Update record
    record.status = data.new_status
    record.source = AttendanceSource.CORRECTION

    db.commit()
    db.refresh(correction)

    return AttendanceCorrectionResponse.model_validate(correction)


def get_student_attendance_summary(
    db: Session,
    student_id: int,
    current_user: User
) -> StudentAttendanceReport:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Authorization check
    if current_user.role == UserRole.STUDENT:
        if not current_user.student_profile or current_user.student_profile.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own attendance records"
            )

    # Total relevant sessions for student's division
    total_sessions_query = db.query(AttendanceSession).filter(
        AttendanceSession.division_id == student.division_id
    )
    total_sessions_count = total_sessions_query.count()

    # Total attended by student
    attended_records = db.query(AttendanceRecord).join(AttendanceSession).filter(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.status == AttendanceStatus.PRESENT,
        AttendanceSession.division_id == student.division_id
    ).all()
    attended_count = len(attended_records)

    overall_pct = round((attended_count / total_sessions_count * 100.0), 2) if total_sessions_count > 0 else 100.0

    # Subject breakdown
    subjects = db.query(Subject).filter(Subject.semester_id == student.semester_id).all()
    subject_summaries = []
    for sub in subjects:
        sub_total = db.query(AttendanceSession).filter(
            AttendanceSession.division_id == student.division_id,
            AttendanceSession.subject_id == sub.id
        ).count()
        sub_attended = db.query(AttendanceRecord).join(AttendanceSession).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == AttendanceStatus.PRESENT,
            AttendanceSession.subject_id == sub.id
        ).count()
        sub_pct = round((sub_attended / sub_total * 100.0), 2) if sub_total > 0 else 100.0

        subject_summaries.append(SubjectAttendanceSummary(
            subject_id=sub.id,
            subject_code=sub.code,
            subject_name=sub.name,
            total_sessions=sub_total,
            attended_sessions=sub_attended,
            percentage=sub_pct
        ))

    return StudentAttendanceReport(
        student_id=student.id,
        roll_number=student.roll_number,
        full_name=student.full_name,
        department_name=student.department.name if student.department else None,
        division_name=student.division.name if student.division else None,
        total_sessions=total_sessions_count,
        attended_sessions=attended_count,
        overall_percentage=overall_pct,
        subject_breakdown=subject_summaries
    )


def get_defaulter_report(
    db: Session,
    academic_year_id: Optional[int] = None,
    division_id: Optional[int] = None,
    threshold_percentage: float = 75.0
) -> DefaulterReportResponse:
    query = db.query(Student)
    if academic_year_id:
        query = query.filter(Student.academic_year_id == academic_year_id)
    if division_id:
        query = query.filter(Student.division_id == division_id)

    students = query.all()
    defaulters_list = []

    for st in students:
        total_sess = db.query(AttendanceSession).filter(
            AttendanceSession.division_id == st.division_id
        ).count()
        attended_sess = db.query(AttendanceRecord).join(AttendanceSession).filter(
            AttendanceRecord.student_id == st.id,
            AttendanceRecord.status == AttendanceStatus.PRESENT,
            AttendanceSession.division_id == st.division_id
        ).count()

        pct = round((attended_sess / total_sess * 100.0), 2) if total_sess > 0 else 100.0

        if pct < threshold_percentage:
            defaulters_list.append(DefaulterStudent(
                student_id=st.id,
                roll_number=st.roll_number,
                full_name=st.full_name,
                email=st.email,
                division_name=st.division.name if st.division else None,
                total_sessions=total_sess,
                attended_sessions=attended_sess,
                attendance_percentage=pct
            ))

    return DefaulterReportResponse(
        academic_year_id=academic_year_id,
        division_id=division_id,
        threshold_percentage=threshold_percentage,
        defaulters_count=len(defaulters_list),
        defaulters=defaulters_list
    )


def get_attendance_audit_logs(db: Session, current_user: User) -> List[dict]:
    corrections = db.query(AttendanceCorrection).options(
        joinedload(AttendanceCorrection.attendance_record).joinedload(AttendanceRecord.student),
        joinedload(AttendanceCorrection.corrector)
    ).order_by(AttendanceCorrection.corrected_at.desc()).all()

    result = []
    for c in corrections:
        rec = c.attendance_record
        student_name = rec.student.full_name if rec and rec.student else "Unknown Student"
        student_roll = rec.student.roll_number if rec and rec.student else "-"
        corrector_name = c.corrector.username if c.corrector else "System"

        result.append({
            "id": c.id,
            "attendance_id": c.attendance_id,
            "student_roll_number": student_roll,
            "student_full_name": student_name,
            "corrected_by_name": corrector_name,
            "old_status": c.old_status.value if hasattr(c.old_status, 'value') else str(c.old_status),
            "new_status": c.new_status.value if hasattr(c.new_status, 'value') else str(c.new_status),
            "reason": c.reason,
            "created_at": c.corrected_at.isoformat() if c.corrected_at else None
        })
    return result


def get_student_attendance_history(db: Session, student_id: int) -> List[dict]:
    records = db.query(AttendanceRecord).options(
        joinedload(AttendanceRecord.session).joinedload(AttendanceSession.subject)
    ).filter(
        AttendanceRecord.student_id == student_id
    ).order_by(AttendanceRecord.marked_at.desc()).all()

    result = []
    for r in records:
        sess = r.session
        subject_name = sess.subject.name if sess and sess.subject else "General Session"
        subject_code = sess.subject.code if sess and sess.subject else ""

        result.append({
            "id": r.id,
            "session_id": r.attendance_session_id,
            "subject_name": subject_name,
            "subject_code": subject_code,
            "session_date": sess.session_date.isoformat() if sess and sess.session_date else "",
            "status": r.status.value if hasattr(r.status, 'value') else str(r.status),
            "source": r.source.value if hasattr(r.source, 'value') else str(r.source),
            "marked_at": r.marked_at.isoformat() if r.marked_at else None
        })
    return result

