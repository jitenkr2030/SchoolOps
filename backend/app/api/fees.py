"""
Fee Structure API endpoints
Management of fee structures and fee categories
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, or_
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.db.database import get_db
from app.schema.payment_schema import (
    FeeStructureCreate, FeeStructureUpdate, FeeStructureResponse,
    FeeStructureListResponse, FeeRecordFilter, FeeRecordResponse,
    FeeRecordDetailResponse, FeeCollectionSummary, FeeDefaultersReport,
    FeeRecordFilter as FeeRecordFilterSchema,
    PaymentPaginatedResponse, PaymentApiResponse
)
from app.models.models import (
    FeeStructure, FeeRecord, Student, User, UserProfile, Class,
    AcademicYear, School, FeeStatus, Payment, PaymentMethod
)
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/fees", tags=["Fees Management"])


# ==================== Fee Structure Endpoints ====================

@router.get("", response_model=List[FeeStructureListResponse])
async def get_fee_structures(
    school_id: Optional[int] = Query(None, description="Filter by school"),
    academic_year_id: Optional[int] = Query(None, description="Filter by academic year"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all fee structures with optional filters.
    """
    query = select(FeeStructure)
    
    if school_id:
        # Join with academic year to filter by school
        query = query.join(AcademicYear).where(AcademicYear.school_id == school_id)
    if academic_year_id:
        query = query.where(FeeStructure.academic_year_id == academic_year_id)
    if is_active is not None:
        query = query.where(FeeStructure.is_active == is_active)
    
    query = query.order_by(FeeStructure.name)
    
    result = await db.execute(query)
    fee_structures = result.scalars().all()
    
    return fee_structures


@router.get("/{fee_structure_id}", response_model=FeeStructureResponse)
async def get_fee_structure(
    fee_structure_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed fee structure by ID.
    """
    result = await db.execute(
        select(FeeStructure).where(FeeStructure.id == fee_structure_id)
    )
    fee_structure = result.scalar_one_or_none()
    
    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )
    
    return fee_structure


@router.post("", response_model=PaymentApiResponse, status_code=status.HTTP_201_CREATED)
async def create_fee_structure(
    fee_data: FeeStructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new fee structure.
    Requires admin privileges.
    """
    # Verify academic year exists
    result = await db.execute(
        select(AcademicYear).where(AcademicYear.id == fee_data.academic_year_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Academic year not found"
        )
    
    fee_structure = FeeStructure(
        name=fee_data.name,
        description=fee_data.description,
        amount=fee_data.amount,
        currency=fee_data.currency,
        frequency=fee_data.frequency.value,
        academic_year_id=fee_data.academic_year_id,
        due_date=fee_data.due_date,
        late_fee_amount=fee_data.late_fee_amount,
        is_optional=fee_data.is_optional,
        is_active=True
    )
    
    db.add(fee_structure)
    await db.commit()
    await db.refresh(fee_structure)
    
    return PaymentApiResponse(
        success=True,
        message="Fee structure created successfully",
        data={"fee_structure_id": fee_structure.id, "name": fee_structure.name}
    )


@router.put("/{fee_structure_id}", response_model=PaymentApiResponse)
async def update_fee_structure(
    fee_structure_id: int,
    fee_data: FeeStructureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update an existing fee structure.
    Requires admin privileges.
    """
    result = await db.execute(
        select(FeeStructure).where(FeeStructure.id == fee_structure_id)
    )
    fee_structure = result.scalar_one_or_none()
    
    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )
    
    # Build update dict
    update_data = fee_data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(FeeStructure)
            .where(FeeStructure.id == fee_structure_id)
            .values(**update_data)
        )
        await db.commit()
    
    return PaymentApiResponse(
        success=True,
        message="Fee structure updated successfully"
    )


@router.delete("/{fee_structure_id}", response_model=PaymentApiResponse)
async def deactivate_fee_structure(
    fee_structure_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deactivate a fee structure (soft delete).
    Requires admin privileges.
    """
    result = await db.execute(
        select(FeeStructure).where(FeeStructure.id == fee_structure_id)
    )
    fee_structure = result.scalar_one_or_none()
    
    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )
    
    await db.execute(
        update(FeeStructure)
        .where(FeeStructure.id == fee_structure_id)
        .values(is_active=False)
    )
    await db.commit()
    
    return PaymentApiResponse(
        success=True,
        message="Fee structure deactivated"
    )


# ==================== Fee Record Endpoints ====================

@router.get("/records", response_model=PaymentPaginatedResponse)
async def get_fee_records(
    school_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    academic_year_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get fee records with filters and pagination.
    """
    query = select(FeeRecord)
    
    # Join with student for filters
    if school_id or class_id:
        query = query.join(Student)
    
    if school_id:
        query = query.where(Student.school_id == school_id)
    if student_id:
        query = query.where(FeeRecord.student_id == student_id)
    if class_id:
        query = query.where(Student.class_id == class_id)
    if status:
        query = query.where(FeeRecord.status == status)
    if academic_year_id:
        query = query.where(FeeRecord.academic_year_id == academic_year_id)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Paginate
    query = query.order_by(FeeRecord.due_date)
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    data = [{
        "id": r.id,
        "student_id": r.student_id,
        "fee_structure_id": r.fee_structure_id,
        "amount_due": float(r.amount_due),
        "amount_paid": float(r.amount_paid),
        "status": r.status.value if r.status else "pending",
        "due_date": r.due_date.isoformat() if r.due_date else None,
        "payment_date": r.payment_date.isoformat() if r.payment_date else None
    } for r in records]
    
    return PaymentPaginatedResponse(
        success=True,
        message="Fee records retrieved",
        data=data,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/records/{record_id}", response_model=FeeRecordDetailResponse)
async def get_fee_record_detail(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed fee record with student and fee info.
    """
    result = await db.execute(
        select(FeeRecord)
        .options(
            selectinload(FeeRecord.student).selectinload(Student.user).selectinload(UserProfile),
            selectinload(FeeRecord.fee_structure)
        )
        .where(FeeRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found"
        )
    
    student = record.student
    profile = student.user.profile
    
    return FeeRecordDetailResponse(
        id=record.id,
        student_id=record.student_id,
        fee_structure_id=record.fee_structure_id,
        amount_due=float(record.amount_due),
        amount_paid=float(record.amount_paid),
        status=record.status,
        due_date=record.due_date,
        payment_date=record.payment_date,
        concession_amount=float(record.concession_amount),
        concession_reason=record.concession_reason,
        student_name=f"{profile.first_name} {profile.last_name}" if profile else "Unknown",
        admission_number=student.admission_number,
        fee_name=record.fee_structure.name,
        class_name=""  # Would need to join with Class
    )


# ==================== Collection Reports ====================

@router.get("/reports/collection", response_model=PaymentApiResponse)
async def get_collection_report(
    school_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Get fee collection report for a school.
    Requires admin privileges.
    """
    # Calculate totals
    query = select(
        func.sum(Payment.amount).label("total_collected"),
        func.count(Payment.id).label("count")
    ).where(Payment.status == "completed")
    
    if start_date:
        query = query.where(Payment.payment_date >= start_date)
    if end_date:
        query = query.where(Payment.payment_date <= end_date)
    
    result = await db.execute(query)
    totals = result.one()
    
    # Pending and overdue
    pending_query = select(func.sum(FeeRecord.amount_due - FeeRecord.amount_paid)).where(
        FeeRecord.status.in_([FeeStatus.PENDING, FeeStatus.OVERDUE])
    )
    
    pending_result = await db.execute(pending_query)
    pending = pending_result.scalar() or 0
    
    return PaymentApiResponse(
        success=True,
        message="Collection report generated",
        data={
            "total_collected": float(totals.total_collected or 0),
            "transaction_count": totals.count or 0,
            "total_pending": float(pending),
            "report_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    )


@router.get("/reports/defaulters", response_model=PaymentApiResponse)
async def get_defaulters_report(
    school_id: int,
    days_overdue: int = Query(30, description="Days overdue to consider as defaulter"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Get list of students with overdue fees.
    Requires admin privileges.
    """
    from datetime import timedelta
    overdue_date = datetime.now().date() - timedelta(days=days_overdue)
    
    # Get students with overdue fees
    result = await db.execute(
        select(Student)
        .options(
            selectinload(Student.user).selectinload(UserProfile),
            selectinload(Student.fee_records)
        )
        .where(Student.school_id == school_id)
    )
    students = result.scalars().all()
    
    defaulters = []
    for student in students:
        overdue_fees = [
            fr for fr in student.fee_records
            if fr.status in [FeeStatus.PENDING, FeeStatus.OVERDUE]
            and fr.due_date and fr.due_date < overdue_date
        ]
        
        if overdue_fees:
            total_due = sum(
                float(fr.amount_due - fr.amount_paid)
                for fr in overdue_fees
            )
            profile = student.user.profile
            
            defaulters.append({
                "student_id": student.id,
                "student_name": f"{profile.first_name} {profile.last_name}" if profile else "Unknown",
                "admission_number": student.admission_number,
                "total_due": total_due,
                "overdue_fees_count": len(overdue_fees)
            })
    
    defaulters.sort(key=lambda x: x["total_due"], reverse=True)
    
    return PaymentApiResponse(
        success=True,
        message="Defaulters report generated",
        data={
            "total_defaulters": len(defaulters),
            "defaulters": defaulters[:100],  # Limit to 100
            "days_overdue": days_overdue
        }
    )
