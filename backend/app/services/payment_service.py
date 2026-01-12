"""
Payment Service - Factory Pattern for Provider Selection

Central service for payment operations with provider abstraction.
Automatically selects the appropriate payment provider based on method.

Budget-Aware Features:
- Free manual payments (cash/cheque) for offline transactions
- Stripe integration for online payments with test mode
- Unified interface regardless of provider
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import (
    Payment, FeeRecord, FeeStructure, Student, User, UserProfile,
    AcademicYear, PaymentStatus, FeeStatus, PaymentMethod
)
from app.schema.payment_schema import (
    PaymentCreate, PaymentFilter, PaymentApiResponse,
    PaymentPaginatedResponse, ReceiptResponse
)
from app.services.payment_gateway.base import (
    PaymentProviderType, PaymentResult
)
from app.services.payment_gateway.manual_provider import (
    ManualPaymentProvider, BankTransferProvider
)
from app.services.payment_gateway.stripe_provider import StripePaymentProvider
from app.services.receipt_service import ReceiptGenerator


class PaymentService:
    """
    Payment service with provider factory pattern.
    
    Handles:
    - Provider selection based on payment method
    - Payment processing and recording
    - Refund processing
    - Receipt generation
    """
    
    # Provider mapping
    PROVIDERS = {
        PaymentProviderType.MANUAL: ManualPaymentProvider(),
        PaymentProviderType.BANK: BankTransferProvider(),
        PaymentProviderType.STRIPE: StripePaymentProvider(),
        PaymentProviderType.RAZORPAY: None,  # TODO: Implement
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.receipt_generator = ReceiptGenerator()
    
    def _get_provider(self, method: PaymentMethod) -> Optional[Any]:
        """
        Get the appropriate payment provider for the method.
        """
        provider_type_map = {
            PaymentMethod.CASH: PaymentProviderType.MANUAL,
            PaymentMethod.CHEQUE: PaymentProviderType.MANUAL,
            PaymentMethod.BANK_TRANSFER: PaymentProviderType.BANK,
            PaymentMethod.CARD: PaymentProviderType.STRIPE,
            PaymentMethod.UPI: PaymentProviderType.STRIPE,
            PaymentMethod.ONLINE: PaymentProviderType.STRIPE,
        }
        
        provider_type = provider_type_map.get(method)
        if provider_type:
            return self.PROVIDERS.get(provider_type)
        return None
    
    def _generate_receipt_number(self) -> str:
        """Generate unique receipt number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"RCP-{timestamp}-{uuid.uuid4().hex[:6].upper()}"
    
    async def process_payment(
        self,
        student_id: int,
        fee_record_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        transaction_reference: Optional[str] = None,
        notes: Optional[str] = None
    ) -> PaymentApiResponse:
        """
        Process a payment for a fee record.
        
        Args:
            student_id: Student making the payment
            fee_record_id: Fee record being paid
            amount: Payment amount
            payment_method: Payment method used
            transaction_reference: External transaction reference
            notes: Additional notes
            
        Returns:
            PaymentApiResponse with payment details
        """
        # Get fee record
        result = await self.db.execute(
            select(FeeRecord)
            .options(selectinload(FeeRecord.fee_structure))
            .where(FeeRecord.id == fee_record_id)
        )
        fee_record = result.scalar_one_or_none()
        
        if not fee_record:
            return PaymentApiResponse(
                success=False,
                message="Fee record not found"
            )
        
        # Validate amount
        remaining = fee_record.amount_due - fee_record.amount_paid
        if amount > remaining:
            return PaymentApiResponse(
                success=False,
                message=f"Payment amount exceeds due amount. Remaining: ₹{remaining}"
            )
        
        # Get student info
        student_result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.user).selectinload(User.profile))
            .where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        
        if not student:
            return PaymentApiResponse(
                success=False,
                message="Student not found"
            )
        
        # Get provider and process payment
        provider = self._get_provider(payment_method)
        
        if provider and provider.is_available():
            result = await provider.process_payment(
                amount=amount,
                currency="INR",
                reference=f"Fee payment for {student.user.profile.first_name if student.user.profile else 'Student'}",
                metadata={
                    "student_id": student_id,
                    "fee_record_id": fee_record_id
                }
            )
            
            if not result.success:
                return PaymentApiResponse(
                    success=False,
                    message=f"Payment failed: {result.message}"
                )
            
            transaction_id = result.transaction_id
        else:
            # Fallback for unavailable providers
            timestamp = datetime.now().strftime("%Y%m%d")
            transaction_id = f"PAY-{timestamp}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create payment record
        receipt_number = self._generate_receipt_number()
        
        payment = Payment(
            fee_record_id=fee_record_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            receipt_number=receipt_number,
            status=PaymentStatus.COMPLETED,
            notes=notes,
            transaction_reference=transaction_reference
        )
        self.db.add(payment)
        
        # Update fee record
        new_amount_paid = fee_record.amount_paid + amount
        new_status = FeeStatus.PAID if new_amount_paid >= fee_record.amount_due else FeeStatus.PARTIAL
        
        await self.db.execute(
            update(FeeRecord)
            .where(FeeRecord.id == fee_record_id)
            .values(
                amount_paid=new_amount_paid,
                status=new_status,
                payment_date=datetime.now()
            )
        )
        
        await self.db.commit()
        await self.db.refresh(payment)
        
        return PaymentApiResponse(
            success=True,
            message="Payment processed successfully",
            data={
                "payment_id": payment.id,
                "receipt_number": payment.receipt_number,
                "transaction_id": payment.transaction_id,
                "amount_paid": float(payment.amount),
                "status": payment.status.value
            }
        )
    
    async def get_payment_history(
        self,
        student_id: Optional[int] = None,
        fee_record_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaymentPaginatedResponse:
        """
        Get payment history with filters and pagination.
        """
        query = select(Payment)
        
        if student_id:
            query = query.join(FeeRecord).where(FeeRecord.student_id == student_id)
        if fee_record_id:
            query = query.where(Payment.fee_record_id == fee_record_id)
        if start_date:
            query = query.where(Payment.payment_date >= start_date)
        if end_date:
            query = query.where(Payment.payment_date <= end_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.order_by(Payment.payment_date.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Execute
        result = await self.db.execute(query)
        payments = result.scalars().all()
        
        # Build response
        data = [{
            "id": p.id,
            "receipt_number": p.receipt_number,
            "amount": float(p.amount),
            "payment_method": p.payment_method.value,
            "status": p.status.value,
            "transaction_id": p.transaction_id,
            "payment_date": p.payment_date.isoformat()
        } for p in payments]
        
        total_pages = (total + per_page - 1) // per_page
        
        return PaymentPaginatedResponse(
            success=True,
            message="Payments retrieved successfully",
            data=data,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    async def generate_receipt(
        self,
        payment_id: int,
        school_name: str = "SchoolOps",
        school_address: str = ""
    ) -> Optional[ReceiptResponse]:
        """
        Generate receipt data for a payment.
        """
        # Get payment with relationships
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.fee_record).selectinload(FeeRecord.fee_structure),
                selectinload(Payment.fee_record).selectinload(FeeRecord.student)
                .selectinload(Student.user).selectinload(User.profile)
            )
            .where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
        
        student = payment.fee_record.student
        profile = student.user.profile
        
        # Calculate totals
        result2 = await self.db.execute(
            select(
                func.sum(FeeRecord.amount_paid).label("total_paid"),
                func.sum(FeeRecord.amount_due - FeeRecord.amount_paid).label("balance")
            )
            .where(FeeRecord.student_id == student.id)
        )
        totals = result2.one()
        total_paid = totals.total_paid or Decimal("0")
        balance_due = totals.balance or Decimal("0")
        
        return ReceiptResponse(
            receipt_number=payment.receipt_number,
            payment_date=payment.payment_date,
            school_name=school_name,
            school_address=school_address,
            student_name=f"{profile.first_name} {profile.last_name}" if profile else "Unknown",
            admission_number=student.admission_number,
            class_name="",  # Would need to join with Class table
            fee_name=payment.fee_record.fee_structure.name,
            amount_paid=float(payment.amount),
            payment_method=payment.payment_method.value,
            transaction_reference=payment.transaction_reference,
            total_paid=float(total_paid),
            balance_due=float(balance_due)
        )
    
    async def get_fee_defaulters(
        self,
        school_id: int,
        days_overdue: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get list of students with overdue fees.
        
        Useful for:
        - Sending payment reminders
        - Generating defaulter reports
        - AI analysis for at-risk identification
        """
        from datetime import timedelta
        
        overdue_date = datetime.now().date() - timedelta(days=days_overdue)
        
        result = await self.db.execute(
            select(Student)
            .options(
                selectinload(Student.user).selectinload(User.profile),
                selectinload(Student.fee_records)
            )
            .where(
                and_(
                    Student.school_id == school_id,
                    Student.status == "active"
                )
            )
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
                    fr.amount_due - fr.amount_paid
                    for fr in overdue_fees
                )
                profile = student.user.profile
                
                defaulters.append({
                    "student_id": student.id,
                    "student_name": f"{profile.first_name} {profile.last_name}" if profile else "Unknown",
                    "admission_number": student.admission_number,
                    "total_due": float(total_due),
                    "overdue_fees_count": len(overdue_fees),
                    "days_overdue": days_overdue
                })
        
        return sorted(defaulters, key=lambda x: x["total_due"], reverse=True)


# Dependency factory
async def get_payment_service() -> PaymentService:
    """Dependency to get payment service instance"""
    async with async_session_maker() as session:
        yield PaymentService(session)


from app.db.database import async_session_maker
