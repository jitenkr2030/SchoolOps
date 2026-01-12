"""
Reports API Router
"""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.report_service import ReportService
from app.schema.report_schema import (
    DashboardStatsResponse, AdminDashboardResponse,
    StudentStatsResponse, StaffStatsResponse, AcademicStatsResponse,
    FinanceStatsResponse, AttendanceStatsResponse,
    TransportStatsResponse, HostelStatsResponse, LibraryStatsResponse,
    AttendanceReportRequest, AttendanceReportResponse,
    FeeCollectionReportRequest, FeeCollectionReportResponse,
    AcademicReportRequest, AcademicReportResponse,
    TransportUtilizationReportRequest, TransportUtilizationReportResponse,
    HostelOccupancyReportResponse
)
from app.core.security import get_current_user
from app.db.models.models import User


router = APIRouter(prefix="/reports", tags=["Reports"])


# ==================== Dashboard Endpoints ====================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    service = ReportService(db)
    return await service.get_dashboard_stats()


@router.get("/dashboard/admin", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive admin dashboard"""
    service = ReportService(db)
    return await service.get_admin_dashboard()


# ==================== Student Statistics ====================

@router.get("/students", response_model=StudentStatsResponse)
async def get_student_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student statistics"""
    service = ReportService(db)
    return await service.get_student_stats()


# ==================== Staff Statistics ====================

@router.get("/staff", response_model=StaffStatsResponse)
async def get_staff_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get staff statistics"""
    service = ReportService(db)
    return await service.get_staff_stats()


# ==================== Academic Statistics ====================

@router.get("/academics", response_model=AcademicStatsResponse)
async def get_academic_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get academic statistics"""
    service = ReportService(db)
    return await service.get_academic_stats()


# ==================== Finance Statistics ====================

@router.get("/finance", response_model=FinanceStatsResponse)
async def get_finance_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get finance statistics"""
    service = ReportService(db)
    return await service.get_finance_stats()


@router.get("/finance/collection", response_model=FeeCollectionReportResponse)
async def get_fee_collection_report(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fee collection report"""
    service = ReportService(db)
    return await service.get_fee_collection_report(start_date, end_date)


# ==================== Attendance Statistics ====================

@router.get("/attendance", response_model=AttendanceStatsResponse)
async def get_attendance_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance statistics"""
    service = ReportService(db)
    return await service.get_attendance_stats()


@router.get("/attendance/report", response_model=AttendanceReportResponse)
async def get_attendance_report(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    class_id: Optional[int] = Query(None, description="Filter by class"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed attendance report"""
    service = ReportService(db)
    return await service.get_attendance_report(start_date, end_date, class_id)


# ==================== Transport Statistics ====================

@router.get("/transport", response_model=TransportStatsResponse)
async def get_transport_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transport statistics"""
    service = ReportService(db)
    return await service.get_transport_stats()


@router.get("/transport/utilization", response_model=TransportUtilizationReportResponse)
async def get_transport_utilization_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transport utilization report"""
    service = ReportService(db)
    return await service.get_transport_utilization_report()


# ==================== Hostel Statistics ====================

@router.get("/hostel", response_model=HostelStatsResponse)
async def get_hostel_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hostel statistics"""
    service = ReportService(db)
    return await service.get_hostel_stats()


@router.get("/hostel/occupancy", response_model=HostelOccupancyReportResponse)
async def get_hostel_occupancy_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hostel occupancy report"""
    service = ReportService(db)
    return await service.get_hostel_occupancy_report()


# ==================== Library Statistics ====================

@router.get("/library", response_model=LibraryStatsResponse)
async def get_library_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get library statistics"""
    service = ReportService(db)
    return await service.get_library_stats()
