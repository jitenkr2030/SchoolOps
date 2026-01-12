"""
Pydantic schemas for Payment and Fee Management operations
Comprehensive schemas for Finance Module CRUD operations
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from decimal import Decimal


class FeeFrequencyEnum(str, Enum):
    """Fee payment frequency"""
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class FeeStatusEnum(str, Enum):
    """Fee record status"""
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIAL = "partial"
    WAIVED = "waived"


class PaymentMethodEnum(str, Enum):
    """Payment method options"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CARD = "card"
    UPI = "upi"
    ONLINE = "online"


class PaymentStatusEnum(str, Enum):
    """Payment transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# ==================== Fee Structure Schemas ====================

class FeeStructureBase(BaseModel):
    """Base fee structure schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Fee name")
    description: Optional[str] = Field(None, description="Fee description")
    amount: Decimal = Field(..., gt=0, description="Fee amount")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    frequency: FeeFrequencyEnum = Field(..., description="Payment frequency")
    academic_year_id: int = Field(..., description="Academic year ID")
    due_date: Optional[date] = Field(None, description="Payment due date")
    late_fee_amount: Decimal = Field(default=Decimal("0"), gt=0, description="Late fee amount")
    is_optional: bool = Field(default=False, description="Optional fee (e.g., transport)")


class FeeStructureCreate(FeeStructureBase):
    """Schema for creating fee structure"""
    applicable_grades: List[int] = Field(default_factory=list, description="Applicable grade levels")
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class FeeStructureUpdate(BaseModel):
    """Schema for updating fee structure"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[date] = None
    late_fee_amount: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None


class FeeStructureResponse(FeeStructureBase):
    """Schema for fee structure response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeeStructureListResponse(BaseModel):
    """Fee structure list item"""
    id: int
    name: str
    description: Optional[str]
    amount: float
    frequency: str
    due_date: Optional[date]
    is_active: bool
    
    class Config:
        from_attributes = True


# ==================== Fee Record Schemas ====================

class FeeRecordCreate(BaseModel):
    """Schema for creating fee record (auto-generated on student admission)"""
    student_id: int
    fee_structure_id: int
    academic_year_id: int
    amount_due: Decimal
    due_date: date


class FeeRecordResponse(BaseModel):
    """Schema for fee record response"""
    id: int
    student_id: int
    fee_structure_id: int
    amount_due: float
    amount_paid: float
    status: FeeStatusEnum
    due_date: date
    payment_date: Optional[datetime]
    concession_amount: float
    concession_reason: Optional[str]
    
    class Config:
        from_attributes = True


class FeeRecordDetailResponse(FeeRecordResponse):
    """Detailed fee record with related data"""
    student_name: str
    admission_number: str
    fee_name: str
    class_name: str
    
    class Config:
        from_attributes = True


class FeePaymentRequest(BaseModel):
    """Request to pay a fee record"""
    fee_record_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethodEnum
    transaction_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PartialPaymentRequest(BaseModel):
    """Request for partial payment"""
    fee_record_id: int
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethodEnum
    transaction_reference: Optional[str] = None


class ConcessionRequest(BaseModel):
    """Request for fee concession"""
    fee_record_id: int
    concession_amount: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=10, description="Concession reason")


# ==================== Payment Schemas ====================

class PaymentBase(BaseModel):
    """Base payment schema"""
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethodEnum
    transaction_reference: Optional[str] = Field(None, max_length=100)


class PaymentCreate(PaymentBase):
    """Schema for creating payment"""
    fee_record_id: int


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: int
    fee_record_id: int
    status: PaymentStatusEnum
    transaction_id: str
    receipt_number: str
    payment_date: datetime
    
    class Config:
        from_attributes = True


class PaymentDetailResponse(PaymentResponse):
    """Detailed payment response"""
    student_name: str
    admission_number: str
    fee_name: str
    class_name: str
    
    class Config:
        from_attributes = True


# ==================== Receipt Schemas ====================

class ReceiptResponse(BaseModel):
    """Payment receipt schema"""
    receipt_number: str
    payment_date: datetime
    school_name: str
    school_address: Optional[str]
    student_name: str
    admission_number: str
    class_name: str
    fee_name: str
    amount_paid: float
    payment_method: str
    transaction_reference: Optional[str]
    total_paid: float
    balance_due: float
    
    class Config:
        from_attributes = True


# ==================== Collection Report Schemas ====================

class FeeCollectionSummary(BaseModel):
    """Daily/monthly collection summary"""
    date: date
    total_collected: float
    total_pending: float
    total_overdue: float
    collection_count: int
    cash_collection: float
    online_collection: float


class FeeDefaultersReport(BaseModel):
    """List of fee defaulters"""
    student_id: int
    student_name: str
    admission_number: str
    class_name: str
    total_due: float
    overdue_days: int
    last_payment_date: Optional[date]


class RevenueAnalytics(BaseModel):
    """Revenue analytics data"""
    total_revenue: float
    pending_amount: float
    collection_rate: float
    monthly_comparison: List[dict]
    grade_wise_collection: List[dict]


# ==================== Filter Schemas ====================

class PaymentFilter(BaseModel):
    """Schema for filtering payments"""
    school_id: Optional[int] = None
    student_id: Optional[int] = None
    class_id: Optional[int] = None
    fee_structure_id: Optional[int] = None
    payment_method: Optional[PaymentMethodEnum] = None
    status: Optional[PaymentStatusEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class FeeRecordFilter(BaseModel):
    """Schema for filtering fee records"""
    school_id: Optional[int] = None
    student_id: Optional[int] = None
    class_id: Optional[int] = None
    status: Optional[FeeStatusEnum] = None
    academic_year_id: Optional[int] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


# ==================== API Response Schemas ====================

class PaymentApiResponse(BaseModel):
    """Generic payment API response"""
    success: bool
    message: str
    data: Optional[dict] = None


class PaymentPaginatedResponse(BaseModel):
    """Paginated payment response"""
    success: bool
    message: str
    data: list
    total: int
    page: int
    per_page: int
    total_pages: int
