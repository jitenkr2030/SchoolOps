"""
Payment API endpoints
Payment processing, history, and receipt generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from app.db.database import get_db
from app.schema.payment_schema import (
    PaymentCreate, PaymentResponse, PaymentDetailResponse,
    PaymentApiResponse, PaymentPaginatedResponse, PaymentFilter,
    FeePaymentRequest, ReceiptResponse
)
from app.models.models import (
    Payment, FeeRecord, Student, User, UserProfile, Class,
    FeeStructure, PaymentStatus, PaymentMethod, FeeStatus
)
from app.core.security import get_current_user, require_admin, require_staff
from app.services.payment_service import PaymentService
from app.services.receipt_service import ReceiptGenerator

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentApiResponse)
async def process_payment(
    payment_data: FeePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Process a payment for a fee.
    
    Supports:
    - Cash payments (manual recording)
    - Bank transfers
    - Online payments (Stripe integration)
    """
    service = PaymentService(db)
    
    result = await service.process_payment(
        student_id=current_user.id if current_user.role.value == "student" else payment_data.fee_record_id,
        fee_record_id=payment_data.fee_record_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_reference=payment_data.transaction_reference,
        notes=payment_data.notes
    )
    
    return result


@router.get("", response_model=PaymentPaginatedResponse)
async def get_payments(
    student_id: Optional[int] = Query(None, description="Filter by student"),
    fee_record_id: Optional[int] = Query(None, description="Filter by fee record"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get payment history with filters.
    Students can only see their own payments.
    Staff can see all payments for their school.
    """
    # Students can only see their own payments
    if current_user.role.value == "student":
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        student = student_result.scalar_one_or_none()
        if student:
            student_id = student.id
        else:
            return PaymentPaginatedResponse(
                success=False,
                message="Student record not found",
                data=[],
                total=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )
    
    service = PaymentService(db)
    
    return await service.get_payment_history(
        student_id=student_id if current_user.role.value == "student" else student_id,
        fee_record_id=fee_record_id,
        start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
        end_date=datetime.combine(end_date, datetime.min.time()) if end_date else None,
        page=page,
        per_page=per_page
    )


@router.get("/{payment_id}", response_model=PaymentDetailResponse)
async def get_payment_detail(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed payment information.
    """
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.fee_record)
            .selectinload(FeeRecord.fee_structure),
            selectinload(Payment.fee_record)
            .selectinload(FeeRecord.student)
            .selectinload(Student.user)
            .selectinload(UserProfile)
        )
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Students can only view their own payments
    if current_user.role.value == "student":
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        student = student_result.scalar_one_or_none()
        if not student or payment.fee_record.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    student = payment.fee_record.student
    profile = student.user.profile
    
    return PaymentDetailResponse(
        id=payment.id,
        fee_record_id=payment.fee_record_id,
        amount=float(payment.amount),
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_id=payment.transaction_id,
        receipt_number=payment.receipt_number,
        payment_date=payment.payment_date,
        student_name=f"{profile.first_name} {profile.last_name}" if profile else "Unknown",
        admission_number=student.admission_number,
        fee_name=payment.fee_record.fee_structure.name,
        class_name=""  # Would need Class join
    )


@router.get("/{payment_id}/receipt")
async def download_receipt(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Download payment receipt as PDF.
    
    Returns a PDF file for download/print.
    """
    service = PaymentService(db)
    
    receipt_data = await service.generate_receipt(
        payment_id=payment_id,
        school_name="SchoolOps",
        school_address=""
    )
    
    if not receipt_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Generate PDF
    generator = ReceiptGenerator()
    pdf_buffer = generator.generate_receipt(
        receipt_number=receipt_data.receipt_number,
        payment_date=receipt_data.payment_date,
        student_name=receipt_data.student_name,
        admission_number=receipt_data.admission_number,
        class_name=receipt_data.class_name,
        fee_name=receipt_data.fee_name,
        amount_paid=Decimal(str(receipt_data.amount_paid)),
        payment_method=receipt_data.payment_method,
        transaction_reference=receipt_data.transaction_reference,
        total_paid=Decimal(str(receipt_data.total_paid)),
        balance_due=Decimal(str(receipt_data.balance_due))
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=receipt_{receipt_data.receipt_number}.pdf"
        }
    )


@router.get("/{payment_id}/receipt/data", response_model=ReceiptResponse)
async def get_receipt_data(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get receipt data as JSON (for custom receipt generation).
    """
    service = PaymentService(db)
    
    receipt_data = await service.generate_receipt(
        payment_id=payment_id,
        school_name="SchoolOps",
        school_address=""
    )
    
    if not receipt_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return receipt_data


# ==================== Refund Endpoints ====================

@router.post("/{payment_id}/refund", response_model=PaymentApiResponse)
async def refund_payment(
    payment_id: int,
    reason: Optional[str] = Query(None, description="Reason for refund"),
    amount: Optional[Decimal] = Query(None, description="Refund amount (full if not specified)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Process a refund for a payment.
    Requires admin privileges.
    """
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund completed payments"
        )
    
    # Update payment status
    await db.execute(
        select(Payment)
        .where(Payment.id == payment_id)
        .values(status=PaymentStatus.REFUNDED)
    )
    
    # Update fee record
    fee_record = payment.fee_record
    new_amount_paid = fee_record.amount_paid - (amount or payment.amount)
    
    # Determine new status
    if new_amount_paid <= 0:
        new_status = FeeStatus.PENDING
    else:
        new_status = FeeStatus.PARTIAL
    
    await db.execute(
        update(FeeRecord)
        .where(FeeRecord.id == fee_record.id)
        .values(
            amount_paid=max(new_amount_paid, Decimal("0")),
            status=new_status,
            payment_date=None
        )
    )
    
    await db.commit()
    
    return PaymentApiResponse(
        success=True,
        message="Refund processed successfully",
        data={
            "payment_id": payment_id,
            "refund_amount": float(amount or payment.amount),
            "reason": reason
        }
    )


# ==================== Dashboard Stats ====================

@router.get("/stats/dashboard", response_model=PaymentApiResponse)
async def get_payment_dashboard_stats(
    school_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff)
):
    """
    Get payment statistics for dashboard.
    """
    year = year or datetime.now().year
    month = month or datetime.now().month
    
    # Total collected this month
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    
    collected_result = await db.execute(
        select(func.sum(Payment.amount))
        .where(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.payment_date >= start_date,
                Payment.payment_date < end_date
            )
        )
    )
    total_collected = collected_result.scalar() or 0
    
    # Transaction count
    count_result = await db.execute(
        select(func.count(Payment.id))
        .where(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.payment_date >= start_date,
                Payment.payment_date < end_date
            )
        )
    )
    transaction_count = count_result.scalar() or 0
    
    # Pending fees
    pending_result = await db.execute(
        select(func.sum(FeeRecord.amount_due - FeeRecord.amount_paid))
        .where(
            FeeRecord.status.in_([FeeStatus.PENDING, FeeStatus.OVERDUE])
        )
    )
    pending_amount = pending_result.scalar() or 0
    
    # Collection rate
    due_result = await db.execute(
        select(func.sum(FeeRecord.amount_due))
    )
    total_due = due_result.scalar() or 1  # Avoid division by zero
    collection_rate = (float(total_collected) / float(total_due)) * 100
    
    return PaymentApiResponse(
        success=True,
        message="Dashboard stats retrieved",
        data={
            "month": f"{year}-{month:02d}",
            "total_collected": float(total_collected),
            "transaction_count": transaction_count,
            "pending_amount": float(pending_amount),
            "collection_rate": round(collection_rate, 2),
            "overdue_count": 0  # Would need additional query
        }
    )
