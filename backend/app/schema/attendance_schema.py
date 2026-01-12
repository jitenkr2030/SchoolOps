"""
Pydantic schemas for Attendance and Timetable Management
Comprehensive schemas for tracking attendance and managing schedules
"""

from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


class AttendanceStatusEnum(str, Enum):
    """Student attendance status"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    HALF_DAY = "half_day"


class StaffAttendanceStatusEnum(str, Enum):
    """Staff attendance status"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_DUTY = "on_duty"
    WORK_FROM_HOME = "wfh"


# ==================== Student Attendance Schemas ====================

class AttendanceMarkBase(BaseModel):
    """Base schema for marking attendance"""
    student_id: int
    date: date
    status: AttendanceStatusEnum
    period: Optional[int] = Field(None, description="Period number for period-based attendance")
    check_in_time: Optional[datetime] = None
    remarks: Optional[str] = None


class AttendanceMarkCreate(AttendanceMarkBase):
    """Schema for creating single attendance record"""
    class_id: int = Field(..., description="Class for verification")


class AttendanceBulkCreate(BaseModel):
    """Schema for bulk attendance marking"""
    class_id: int
    date: date
    period: Optional[int] = None
    marked_by: int = Field(..., description="Staff ID who marked attendance")
    records: List[Dict[str, Any]] = Field(
        ..., 
        description="List of {'student_id': int, 'status': str, 'remarks': optional}"
    )


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance"""
    status: Optional[AttendanceStatusEnum] = None
    check_in_time: Optional[datetime] = None
    remarks: Optional[str] = None


class AttendanceResponse(AttendanceMarkBase):
    """Schema for attendance response"""
    id: int
    class_id: int
    marked_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceDetailResponse(BaseModel):
    """Detailed attendance with student info"""
    id: int
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    date: date
    status: str
    period: Optional[int]
    check_in_time: Optional[datetime]
    remarks: Optional[str]
    marked_by: int
    
    class Config:
        from_attributes = True


# ==================== Attendance Report Schemas ====================

class StudentAttendanceReport(BaseModel):
    """Individual student attendance report"""
    student_id: int
    student_name: str
    admission_number: str
    class_name: str
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_percentage: Decimal
    status: str  # Satisfactory, At Risk, Critical


class ClassAttendanceSummary(BaseModel):
    """Daily class attendance summary"""
    class_id: int
    class_name: str
    date: date
    total_students: int
    present: int
    absent: int
    late: int
    attendance_percentage: Decimal


class MonthlyAttendanceReport(BaseModel):
    """Monthly attendance report for a class"""
    class_id: int
    class_name: str
    month: int
    year: int
    daily_summaries: List[ClassAttendanceSummary]
    overall_attendance: Decimal


class AttendanceFilter(BaseModel):
    """Schema for filtering attendance records"""
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AttendanceStatusEnum] = None
    period: Optional[int] = None


# ==================== Staff Attendance Schemas ====================

class StaffAttendanceCreate(BaseModel):
    """Schema for creating staff attendance"""
    staff_id: int
    date: date
    status: StaffAttendanceStatusEnum
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    remarks: Optional[str] = None


class StaffAttendanceResponse(BaseModel):
    """Staff attendance response"""
    id: int
    staff_id: int
    staff_name: str
    date: date
    status: str
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    working_hours: Optional[Decimal]
    remarks: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== Timetable Schemas ====================

class DayOfWeekEnum(int, Enum):
    """Day of week enumeration"""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class TimetableSlotCreate(BaseModel):
    """Schema for creating timetable slot"""
    class_id: int
    day_of_week: DayOfWeekEnum
    period_number: int = Field(..., ge=1, le=10)
    subject_id: int
    staff_id: int
    room_number: Optional[str] = None
    start_time: time
    end_time: time
    is_active: bool = True


class TimetableSlotUpdate(BaseModel):
    """Schema for updating timetable slot"""
    subject_id: Optional[int] = None
    staff_id: Optional[int] = None
    room_number: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None


class TimetableSlotResponse(BaseModel):
    """Timetable slot response"""
    id: int
    class_id: int
    day_of_week: int
    period_number: int
    subject_id: int
    staff_id: int
    room_number: Optional[str]
    start_time: time
    end_time: time
    is_active: bool
    
    class Config:
        from_attributes = True


class TimetableDetailResponse(BaseModel):
    """Detailed timetable slot with names"""
    id: int
    class_id: int
    class_name: str
    day_of_week: int
    day_name: str
    period_number: int
    subject_id: int
    subject_name: str
    staff_id: int
    staff_name: str
    room_number: Optional[str]
    start_time: time
    end_time: time
    
    class Config:
        from_attributes = True


class WeeklyTimetableResponse(BaseModel):
    """Weekly timetable for a class or teacher"""
    entity_id: int
    entity_type: str  # "class" or "teacher"
    entity_name: str
    weekly_schedule: Dict[int, List[TimetableDetailResponse]]  # Day -> Slots


class TimetableFilter(BaseModel):
    """Schema for filtering timetable"""
    class_id: Optional[int] = None
    staff_id: Optional[int] = None
    subject_id: Optional[int] = None
    day_of_week: Optional[DayOfWeekEnum] = None


# ==================== Conflict Detection Schemas ====================

class TimetableConflict(BaseModel):
    """Schema for timetable conflict"""
    conflict_type: str  # "teacher", "room", "class"
    existing_slot: Dict[str, Any]
    new_slot: Dict[str, Any]
    message: str


class ConflictCheckResult(BaseModel):
    """Result of conflict check"""
    has_conflicts: bool
    conflicts: List[TimetableConflict]


# ==================== API Response Schemas ====================

class AttendanceApiResponse(BaseModel):
    """Generic attendance API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class AttendancePaginatedResponse(BaseModel):
    """Paginated attendance response"""
    success: bool
    message: str
    data: List[AttendanceDetailResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class TimetableApiResponse(BaseModel):
    """Generic timetable API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
