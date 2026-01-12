"""
Attendance API endpoints
Student and staff attendance tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, datetime

from app.db.database import get_db
from app.schema.attendance_schema import (
    AttendanceBulkCreate, AttendanceFilter, AttendanceApiResponse,
    AttendancePaginatedResponse, StaffAttendanceCreate, StaffAttendanceResponse,
    StudentAttendanceReport, ClassAttendanceSummary
)
from app.services.attendance_service import AttendanceService
from app.core.security import get_current_user, require_admin, require_staff, require_teacher


router = APIRouter(prefix="/attendance", tags=["Attendance Management"])


# ==================== Student Attendance Endpoints ====================

@router.post("/bulk", response_model=AttendanceApiResponse)
async def mark_bulk_attendance(
    data: AttendanceBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """
    Mark attendance for multiple students in a class.
    Teachers can mark attendance for their assigned classes.
    """
    service = AttendanceService(db)
    
    result = await service.mark_attendance(
        class_id=data.class_id,
        date_=data.date,
        records=data.records,
        marked_by=current_user.id,
        period=data.period
    )
    
    return result


@router.get("/student/{student_id}", response_model=AttendanceApiResponse)
async def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get attendance history for a student.
    Students can only view their own attendance.
    """
    # Students can only view their own
    if current_user.role.value == "student":
        from app.models.models import Student
        result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        student = result.scalar_one_or_none()
        if not student or student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other student's attendance"
            )
    
    service = AttendanceService(db)
    
    try:
        report = await service.get_student_attendance(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return AttendanceApiResponse(
            success=True,
            message="Attendance report retrieved",
            data=report
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/class/{class_id}/summary", response_model=AttendanceApiResponse)
async def get_class_attendance_summary(
    class_id: int,
    date_: date = Query(..., description="Date for summary"),
    period: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """
    Get daily attendance summary for a class.
    """
    service = AttendanceService(db)
    
    summary = await service.get_class_attendance_summary(
        class_id=class_id,
        date_=date_,
        period=period
    )
    
    return AttendanceApiResponse(
        success=True,
        message="Summary retrieved",
        data=summary
    )


@router.get("/class/{class_id}/report", response_model=AttendanceApiResponse)
async def get_monthly_class_report(
    class_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """
    Get monthly attendance report for a class.
    """
    service = AttendanceService(db)
    
    try:
        report = await service.get_monthly_attendance_report(
            class_id=class_id,
            month=month,
            year=year
        )
        
        return AttendanceApiResponse(
            success=True,
            message="Monthly report retrieved",
            data=report
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/class/{class_id}", response_model=AttendancePaginatedResponse)
async def get_class_attendance(
    class_id: int,
    attendance_date: date = Query(..., description="Date to fetch"),
    period: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """
    Get all attendance records for a class on a specific date.
    """
    from app.models.models import Attendance, Student, UserProfile
    
    query = (
        select(Attendance, Student, UserProfile)
        .join(Student, Attendance.student_id == Student.id)
        .join(UserProfile, Student.user_id == UserProfile.user_id)
        .where(
            and_(
                Attendance.class_id == class_id,
                Attendance.date == attendance_date
            )
        )
    )
    
    if period:
        query = query.where(Attendance.period == period)
    
    query = query.order_by(Student.roll_number)
    
    result = await db.execute(query)
    records = result.all()
    
    data = [
        {
            "id": att.id,
            "student_id": student.id,
            "student_name": f"{profile.first_name} {profile.last_name}",
            "admission_number": student.admission_number,
            "date": att.date,
            "status": att.status.value,
            "period": att.period,
            "remarks": att.remarks
        }
        for att, student, profile in records
    ]
    
    return AttendancePaginatedResponse(
        success=True,
        message="Attendance records retrieved",
        data=data,
        total=len(data),
        page=1,
        per_page=len(data),
        total_pages=1
    )


# ==================== Staff Attendance Endpoints ====================

@router.post("/staff", response_model=AttendanceApiResponse)
async def mark_staff_attendance(
    data: StaffAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark staff attendance.
    Staff can mark their own attendance.
    Admins can mark attendance for others.
    """
    service = AttendanceService(db)
    
    # Staff can only mark their own unless admin
    if current_user.role.value not in ["super_admin", "school_admin", "principal"]:
        if data.staff_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only mark your own attendance"
            )
    
    return await service.mark_staff_attendance(
        staff_id=data.staff_id,
        date_=data.date,
        status=data.status,
        check_in=data.check_in,
        check_out=data.check_out,
        remarks=data.remarks
    )


@router.get("/staff/{staff_id}", response_model=AttendanceApiResponse)
async def get_staff_attendance(
    staff_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get attendance history for a staff member.
    """
    # Staff can only view their own unless admin
    if current_user.role.value not in ["super_admin", "school_admin", "principal"]:
        if staff_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other staff attendance"
            )
    
    from app.models.models import StaffAttendance, Staff
    
    query = (
        select(StaffAttendance, Staff)
        .join(Staff, StaffAttendance.staff_id == Staff.id)
        .where(StaffAttendance.staff_id == staff_id)
    )
    
    if start_date:
        query = query.where(StaffAttendance.date >= start_date)
    if end_date:
        query = query.where(StaffAttendance.date <= end_date)
    
    query = query.order_by(StaffAttendance.date.desc())
    
    result = await db.execute(query)
    records = result.all()
    
    # Calculate working hours and summary
    total_days = len(records)
    present = sum(1 for r, s in records if r.status == "present")
    
    data = {
        "staff_id": staff_id,
        "total_days": total_days,
        "present_days": present,
        "absent_days": total_days - present,
        "records": [
            {
                "id": r.id,
                "date": r.date,
                "status": r.status,
                "check_in": r.check_in,
                "check_out": r.check_out,
                "working_hours": str(r.working_hours) if r.working_hours else None,
                "remarks": r.remarks
            }
            for r, s in records
        ]
    }
    
    return AttendanceApiResponse(
        success=True,
        message="Staff attendance retrieved",
        data=data
    )


# ==================== Analytics Endpoints ====================

@router.get("/analytics/at-risk-students", response_model=AttendanceApiResponse)
async def get_at_risk_students(
    school_id: int = Query(..., description="School ID"),
    attendance_threshold: float = Query(75.0, description="Attendance percentage threshold"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Get list of students with attendance below threshold.
    Useful for identifying students who need attention.
    """
    from app.models.models import Student, UserProfile, Attendance
    from sqlalchemy import cast, String
    
    # Get students with low attendance
    result = await db.execute(
        select(Student, UserProfile)
        .join(UserProfile, Student.user_id == UserProfile.user_id)
        .where(Student.school_id == school_id)
        .where(Student.status == "active")
    )
    students = result.all()
    
    at_risk = []
    service = AttendanceService(db)
    
    for student, profile in students:
        report = await service.get_student_attendance(student.id)
        
        if report["attendance_percentage"] < attendance_threshold:
            at_risk.append({
                "student_id": student.id,
                "student_name": f"{profile.first_name} {profile.last_name}",
                "admission_number": student.admission_number,
                "attendance_percentage": report["attendance_percentage"],
                "absent_days": report["absent_days"]
            })
    
    return AttendanceApiResponse(
        success=True,
        message=f"Found {len(at_risk)} at-risk students",
        data={
            "threshold": attendance_threshold,
            "at_risk_count": len(at_risk),
            "students": sorted(at_risk, key=lambda x: x["attendance_percentage"])
        }
    )
