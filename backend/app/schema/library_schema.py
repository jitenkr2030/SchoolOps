"""
Library Management Schemas
Pydantic models for library operations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==================== Enums ====================

class BookCategory(str, Enum):
    """Book category classification"""
    FICTION = "FICTION"
    NON_FICTION = "NON_FICTION"
    REFERENCE = "REFERENCE"
    TEXTBOOK = "TEXTBOOK"
    SCIENCE = "SCIENCE"
    MATHEMATICS = "MATHEMATICS"
    HISTORY = "HISTORY"
    GEOGRAPHY = "GEOGRAPHY"
    LITERATURE = "LITERATURE"
    ART = "ART"
    MUSIC = "MUSIC"
    SPORTS = "SPORTS"
    COMPUTER = "COMPUTER"
    LANGUAGE = "LANGUAGE"
    RELIGION = "RELIGION"
    OTHER = "OTHER"


class MemberType(str, Enum):
    """Library member type"""
    STUDENT = "STUDENT"
    STAFF = "STAFF"


class MemberStatus(str, Enum):
    """Library member status"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class TransactionStatus(str, Enum):
    """Book transaction status"""
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    LOST = "LOST"
    RENEWED = "RENEWED"


class ReservationStatus(str, Enum):
    """Book reservation status"""
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# ==================== Book Schemas ====================

class BookBase(BaseModel):
    """Base book schema"""
    isbn: str = Field(..., min_length=10, max_length=20)
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1800, le=2100)
    edition: Optional[str] = Field(None, max_length=50)
    category: BookCategory = BookCategory.OTHER
    total_copies: int = Field(default=1, ge=1)
    shelf_location: Optional[str] = Field(None, max_length=100)
    DeweyDecimal: Optional[str] = Field(None, max_length=20)
    pages: Optional[int] = Field(None, ge=1)
    language: str = Field(default="English", max_length=50)
    cost: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=500)


class BookCreate(BookBase):
    """Schema for creating a book"""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1800, le=2100)
    edition: Optional[str] = Field(None, max_length=50)
    category: Optional[BookCategory] = None
    shelf_location: Optional[str] = Field(None, max_length=100)
    DeweyDecimal: Optional[str] = Field(None, max_length=20)
    pages: Optional[int] = Field(None, ge=1)
    language: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class BookResponse(BookBase):
    """Schema for book response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    available_copies: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_available: bool
    next_available_date: Optional[datetime] = None


class BookDetailResponse(BookResponse):
    """Detailed book response with transaction history"""
    transactions: List[Dict[str, Any]] = []
    reservations: List[Dict[str, Any]] = []


class BookSearchParams(BaseModel):
    """Book search parameters"""
    search: Optional[str] = None
    category: Optional[BookCategory] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    available_only: bool = False
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class BookListResponse(BaseModel):
    """Paginated book list response"""
    books: List[BookResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Book Copy Schemas ====================

class BookCopyBase(BaseModel):
    """Base book copy schema"""
    book_id: str
    barcode: str = Field(..., min_length=1, max_length=50)
    shelf_location: Optional[str] = Field(None, max_length=100)
    condition: str = Field(default="GOOD", max_length=50)


class BookCopyCreate(BookCopyBase):
    """Schema for creating a book copy"""
    pass


class BookCopyResponse(BaseModel):
    """Schema for book copy response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    book_id: str
    barcode: str
    shelf_location: Optional[str]
    status: str
    condition: str
    last_condition_check: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== Library Member Schemas ====================

class MemberBase(BaseModel):
    """Base library member schema"""
    user_id: int
    member_type: MemberType
    max_books: int = Field(default=3, ge=1)
    max_days: int = Field(default=14, ge=1)
    expiry_date: Optional[date] = None


class MemberCreate(MemberBase):
    """Schema for creating a library member"""
    pass


class MemberUpdate(BaseModel):
    """Schema for updating a library member"""
    max_books: Optional[int] = Field(None, ge=1)
    max_days: Optional[int] = Field(None, ge=1)
    expiry_date: Optional[date] = None
    status: Optional[MemberStatus] = None
    notes: Optional[str] = None
    suspension_reason: Optional[str] = None
    suspension_end_date: Optional[date] = None


class MemberResponse(MemberBase):
    """Schema for member response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    card_number: str
    registration_date: date
    current_issues: int
    total_fines: Decimal
    unpaid_fines: Decimal
    status: MemberStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    can_borrow: bool
    remaining_books: int


class MemberDetailResponse(MemberResponse):
    """Detailed member response with transactions"""
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    current_transactions: List[Dict[str, Any]] = []
    fine_history: List[Dict[str, Any]] = []


class MemberListResponse(BaseModel):
    """Paginated member list response"""
    members: List[MemberResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Book Transaction Schemas ====================

class BookIssueRequest(BaseModel):
    """Schema for issuing a book"""
    book_id: str
    member_id: str
    copy_id: Optional[str] = None
    days: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


class BookReturnRequest(BaseModel):
    """Schema for returning a book"""
    transaction_id: str
    condition_notes: Optional[str] = None
    condition: Optional[str] = Field(None, max_length=50)


class BookRenewRequest(BaseModel):
    """Schema for renewing a book"""
    transaction_id: str
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    book_id: str
    member_id: str
    copy_id: Optional[str]
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    actual_return_date: Optional[datetime]
    status: TransactionStatus
    renewal_count: int
    fine_amount: Decimal
    fine_paid: Decimal
    fine_status: str
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_overdue: bool
    overdue_days: int
    current_fine: Decimal


class TransactionDetailResponse(TransactionResponse):
    """Detailed transaction response"""
    book_title: Optional[str] = None
    book_isbn: Optional[str] = None
    member_card: Optional[str] = None
    member_name: Optional[str] = None


class TransactionListResponse(BaseModel):
    """Paginated transaction list response"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Reservation Schemas ====================

class ReservationCreate(BaseModel):
    """Schema for creating a reservation"""
    book_id: str
    member_id: str
    notes: Optional[str] = None


class ReservationResponse(BaseModel):
    """Schema for reservation response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    book_id: str
    member_id: str
    reservation_date: datetime
    expiry_date: datetime
    status: ReservationStatus
    notification_sent: bool
    notification_date: Optional[datetime]
    fulfilled_date: Optional[datetime]
    days_waited: Optional[int]
    created_at: datetime
    updated_at: datetime


class ReservationListResponse(BaseModel):
    """Paginated reservation list response"""
    reservations: List[ReservationResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Fine Schemas ====================

class FineResponse(BaseModel):
    """Schema for fine response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    transaction_id: str
    member_id: str
    fine_type: str
    amount: Decimal
    paid_amount: Decimal
    status: str
    waived_date: Optional[datetime]
    paid_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class FinePaymentRequest(BaseModel):
    """Schema for paying a fine"""
    fine_id: str
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)


class FineWaiveRequest(BaseModel):
    """Schema for waiving a fine"""
    fine_id: str
    reason: str = Field(..., min_length=1)


class FineListResponse(BaseModel):
    """Paginated fine list response"""
    fines: List[FineResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Overdue Schemas ====================

class OverdueItem(BaseModel):
    """Schema for overdue item"""
    transaction_id: str
    book_id: str
    book_title: str
    book_isbn: str
    member_id: str
    member_card: str
    member_name: str
    due_date: datetime
    overdue_days: int
    fine_amount: Decimal
    status: str


class OverdueReport(BaseModel):
    """Schema for overdue report"""
    items: List[OverdueItem]
    total_overdue: int
    total_fines: Decimal
    generated_at: datetime


# ==================== Library Settings Schemas ====================

class LibrarySettingsResponse(BaseModel):
    """Schema for library settings response"""
    student_max_books: int
    student_max_days: int
    staff_max_books: int
    staff_max_days: int
    max_renewals: int
    renewal_extends_days: int
    fine_per_day: Decimal
    max_fine_cap: Decimal
    reservation_expiry_days: int
    max_reservations_per_member: int


class LibraryStatsResponse(BaseModel):
    """Schema for library statistics"""
    total_books: int
    total_copies: int
    available_copies: int
    total_members: int
    active_members: int
    total_transactions: int
    active_transactions: int
    overdue_count: int
    total_fines_pending: Decimal
    most_popular_books: List[Dict[str, Any]]
    most_active_members: List[Dict[str, Any]]


# ==================== Common Schemas ====================

class IdResponse(BaseModel):
    """Standard ID response"""
    id: str
    message: Optional[str] = None


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class IssueReceipt(BaseModel):
    """Book issue receipt"""
    transaction_id: str
    book_title: str
    book_isbn: str
    member_name: str
    member_card: str
    issue_date: datetime
    due_date: datetime
    days_allowed: int
    renewal_count: int
    max_renewals: int


class ReturnReceipt(BaseModel):
    """Book return receipt"""
    transaction_id: str
    book_title: str
    book_isbn: str
    member_name: str
    member_card: str
    issued_date: datetime
    due_date: datetime
    returned_date: datetime
    overdue_days: int
    fine_amount: Decimal
    fine_paid: Decimal
    fine_status: str
