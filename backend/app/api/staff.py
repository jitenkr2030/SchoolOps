"""
Staff API endpoints
Management of teachers and administrative staff
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.database import get_db
from app.schema.academic_schema import (
    StaffCreate, StaffUpdate, StaffResponse, StaffListResponse,
    StaffFilter, ApiResponse, AcademicPaginatedResponse
)
from app.services.academic_service import StaffService
from app.core.security import get_current_user, require_admin, require_staff


router = APIRouter(prefix="/staff", tags=["Staff Management"])


@router.get("", response_model=AcademicPaginatedResponse)
async def get_staff_list(
    school_id: Optional[int] = Query(None, description="Filter by school"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search name/email/ID"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of all staff members with filters.
    """
    service = StaffService(db)
    
    # Get user's school_id if not provided
    if not school_id and hasattr(current_user, 'school_id'):
        school_id = current_user.school_id
    
    return await service.get_staff_list(
        school_id=school_id,
        department=department,
        status=status,
        search=search,
        page=page,
        per_page=per_page
    )


@router.get("/{staff_id}", response_model=ApiResponse)
async def get_staff_detail(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed staff information including subject assignments.
    """
    service = StaffService(db)
    staff = await service.get_staff_detail(staff_id)
    
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    return ApiResponse(
        success=True,
        message="Staff details retrieved",
        data=staff
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff_data: StaffCreate,
    school_id: int = Query(..., description="School ID for the staff member"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new staff member.
    Requires admin privileges.
    """
    service = StaffService(db)
    
    try:
        result = await service.create_staff(staff_data, school_id)
        return ApiResponse(
            success=True,
            message="Staff member created successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{staff_id}", response_model=ApiResponse)
async def update_staff(
    staff_id: int,
    update_data: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update staff member information.
    Requires admin privileges.
    """
    service = StaffService(db)
    
    try:
        result = await service.update_staff(staff_id, update_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{staff_id}", response_model=ApiResponse)
async def deactivate_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deactivate a staff member (soft delete).
    Requires admin privileges.
    """
    from app.models.models import Staff
    
    result = await db.execute(
        select(Staff).where(Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    staff.status = "terminated"
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="Staff member deactivated"
    )


@router.get("/{staff_id}/assignments", response_model=ApiResponse)
async def get_staff_assignments(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all subject/class assignments for a staff member.
    """
    from app.services.academic_service import SubjectService
    
    service = SubjectService(db)
    assignments = await service.get_subject_assignments(staff_id)
    
    return ApiResponse(
        success=True,
        message="Assignments retrieved",
        data={"assignments": assignments}
    )
