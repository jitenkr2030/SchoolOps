"""
Report Pydantic Schemas
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ReportTypeEnum(str, Enum):
    ATTENDANCE = "attendance"
    ACADEMIC = "academic"
    FINANCE = "finance"
    TRANSPORT = "transport"
    HOSTEL = "hostel"
    INVENTORY = "inventory"
    LIBRARY = "library"


class ReportFormatEnum(str, Enum):
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"


# ==================== Dashboard Schemas ====================

class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    model_config = ConfigDict(from_attributes=True)
    
    total_students: int
    total_teachers: int
    total_staff: int
    total_classes: int
    
    # Attendance stats
    today_attendance_percentage: float
    week_attendance_percentage: float
    
    # Finance stats
    total_fee_collection: float
    pending_fee_amount: float
    today_collection: float
    
    # Transport stats
    total_vehicles: int
    active_allocations: int
    
    # Hostel stats
    total_hostel_students: int
    hostel_occupancy_percentage: float
    
    # Library stats
    books_issued: int
    books_overdue: int
    
    # Date
    report_date: datetime


class AdminDashboardResponse(BaseModel):
    """Admin dashboard with comprehensive stats"""
    students: StudentStatsResponse
    staff: StaffStatsResponse
    academics: AcademicStatsResponse
    finance: FinanceStatsResponse
    attendance: AttendanceStatsResponse
    transport: TransportStatsResponse
    hostel: HostelStatsResponse
    library: LibraryStatsResponse
    generated_at: datetime


class StudentStatsResponse(BaseModel):
    """Student statistics"""
    total_students: int
    active_students: int
    new_admissions_this_month: int
    students_by_class: List[dict]
    students_by_section: List[dict]


class StaffStatsResponse(BaseModel):
    """Staff statistics"""
    total_teachers: int
    total_staff: int
    teachers_by_department: List[dict]
    staff_by_role: List[dict]


class AcademicStatsResponse(BaseModel):
    """Academic statistics"""
    total_classes: int
    total_subjects: int
    total_examscheduled: int
    exams_completed: int
    passing_percentage: float


class FinanceStatsResponse(BaseModel):
    """Finance statistics"""
    total_fee_collection: float
    pending_fee_amount: float
    today_collection: float
    week_collection: float
    month_collection: float
    collection_by_class: List[dict]
    defaulters_count: int
    defaulters_amount: float


class AttendanceStatsResponse(BaseModel):
    """Attendance statistics"""
    today_present: int
    today_absent: int
    today_leave: int
    today_percentage: float
    week_present: int
    week_absent: int
    week_percentage: float
    month_present: int
    month_absent: int
    month_percentage: float


class TransportStatsResponse(BaseModel):
    """Transport statistics"""
    total_vehicles: int
    active_vehicles: int
    vehicles_in_maintenance: int
    total_routes: int
    total_allocations: int
    active_allocations: int
    vehicle_utilization: List[dict]
    revenue_collected: float
    pending_fees: float


class HostelStatsResponse(BaseModel):
    """Hostel statistics"""
    total_blocks: int
    total_rooms: int
    total_capacity: int
    total_occupancy: int
    occupancy_percentage: float
    boys_occupancy: int
    girls_occupancy: int
    available_beds: int
    pending_maintenance: int


class LibraryStatsResponse(BaseModel):
    """Library statistics"""
    total_books: int
    total_members: int
    books_issued: int
    books_returned_today: int
    books_overdue: int
    overdue_fines_collected: float
    popular_books: List[dict]


# ==================== Report Request Schemas ====================

class ReportGenerateRequest(BaseModel):
    """Request schema for generating a report"""
    report_type: ReportTypeEnum
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    format: ReportFormatEnum = ReportFormatEnum.JSON


class ReportResponse(BaseModel):
    """Generic report response"""
    report_type: str
    generated_at: datetime
    data: dict
    summary: Optional[dict] = None


# ==================== Specific Report Schemas ====================

class AttendanceReportRequest(BaseModel):
    """Attendance report request"""
    start_date: date
    end_date: date
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    student_id: Optional[int] = None
    include_summary: bool = True


class AttendanceReportResponse(BaseModel):
    """Attendance report response"""
    period: dict
    total_students: int
    total_days: int
    overall_attendance_percentage: float
    student_wise_data: List[dict]
    class_wise_data: List[dict]
    daily_data: List[dict]


class FeeCollectionReportRequest(BaseModel):
    """Fee collection report request"""
    start_date: date
    end_date: date
    class_id: Optional[int] = None
    fee_type: Optional[str] = None
    payment_mode: Optional[str] = None


class FeeCollectionReportResponse(BaseModel):
    """Fee collection report response"""
    period: dict
    total_collected: float
    total_pending: float
    collection_by_date: List[dict]
    collection_by_class: List[dict]
    collection_by_payment_mode: List[dict]
    top_defaulters: List[dict]
    collection_trend: List[dict]


class AcademicReportRequest(BaseModel):
    """Academic report request"""
    exam_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    subject_id: Optional[int] = None


class AcademicReportResponse(BaseModel):
    """Academic report response"""
    exam_details: dict
    total_students: int
    appeared: int
    passed: int
    failed: int
    passing_percentage: float
    grade_distribution: dict
    subject_wise_performance: List[dict]
    top_performers: List[dict]


class TransportUtilizationReportRequest(BaseModel):
    """Transport utilization report request"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    route_id: Optional[int] = None
    vehicle_id: Optional[int] = None


class TransportUtilizationReportResponse(BaseModel):
    """Transport utilization report response"""
    period: dict
    vehicles: List[dict]
    routes: List[dict]
    overall_utilization: float
    revenue_summary: dict


class HostelOccupancyReportResponse(BaseModel):
    """Hostel occupancy report response"""
    total_blocks: int
    total_rooms: int
    total_beds: int
    occupied_beds: int
    available_beds: int
    occupancy_percentage: float
    block_wise_data: List[dict]
    room_type_distribution: List[dict]


# ==================== Export Schemas ====================

class ReportExportRequest(BaseModel):
    """Request to export report"""
    report_type: ReportTypeEnum
    format: ReportFormatEnum
    filters: dict = {}


class ReportExportResponse(BaseModel):
    """Report export response"""
    success: bool
    message: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    record_count: int
