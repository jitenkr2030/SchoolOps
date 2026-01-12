"""
Library Database Models
SQLAlchemy models for library management
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Decimal, DateTime, Text, 
    ForeignKey, Enum, Boolean, Date, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class BookCategory(str, PyEnum):
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


class MemberType(str, PyEnum):
    """Library member type"""
    STUDENT = "STUDENT"
    STAFF = "STAFF"


class MemberStatus(str, PyEnum):
    """Library member status"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class TransactionStatus(str, PyEnum):
    """Book transaction status"""
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    LOST = "LOST"
    RENEWED = "RENEWED"


class ReservationStatus(str, PyEnum):
    """Book reservation status"""
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class BookCatalog(Base):
    """
    Book catalog model
    
    Stores information about books in the library collection.
    """
    __tablename__ = "book_catalog"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isbn = Column(String(20), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=False)
    publisher = Column(String(200), nullable=True)
    publication_year = Column(Integer, nullable=True)
    edition = Column(String(50), nullable=True)
    
    category = Column(Enum(BookCategory), default=BookCategory.OTHER)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    
    shelf_location = Column(String(100), nullable=True)  # e.g., "A-12-3"
    DeweyDecimal = Column(String(20), nullable=True)  # Dewey Decimal Classification
    
    # Physical details
    pages = Column(Integer, nullable=True)
    language = Column(String(50), default="English")
    
    # Cost and acquisition
    cost = Column(Decimal(12, 2), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    
    # Description and notes
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("BookTransaction", back_populates="book", lazy="dynamic")
    reservations = relationship("BookReservation", back_populates="book", lazy="dynamic")
    
    def __repr__(self):
        return f"<BookCatalog(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"


class BookCopy(Base):
    """
    Individual book copy model
    
    Tracks individual physical copies of books.
    Useful for tracking specific copies with barcodes.
    """
    __tablename__ = "book_copies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book_catalog.id"), nullable=False)
    barcode = Column(String(50), nullable=False, unique=True, index=True)
    
    # Location and status
    shelf_location = Column(String(100), nullable=True)
    status = Column(String(20), default="AVAILABLE")  # AVAILABLE, ISSUED, LOST, DAMAGED
    
    # Condition tracking
    condition = Column(String(50), default="GOOD")  # NEW, GOOD, FAIR, DAMAGED
    last_condition_check = Column(Date, nullable=True)
    
    # Audit
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    book = relationship("BookCatalog", backref="copies")
    
    def __repr__(self):
        return f"<BookCopy(id={self.id}, barcode='{self.barcode}', status='{self.status}')>"


class LibraryMember(Base):
    """
    Library member model
    
    Represents students and staff who can borrow books.
    """
    __tablename__ = "library_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    member_type = Column(Enum(MemberType), nullable=False)
    status = Column(Enum(MemberStatus), default=MemberStatus.ACTIVE)
    
    # Membership details
    card_number = Column(String(50), nullable=False, unique=True, index=True)
    registration_date = Column(Date, default=date.today)
    expiry_date = Column(Date, nullable=True)  # None for perpetual
    
    # Borrowing limits
    max_books = Column(Integer, default=3)  # Student default: 3, Staff: 5
    max_days = Column(Integer, default=14)  # Max loan period in days
    
    # Current issues count
    current_issues = Column(Integer, default=0)
    
    # Fine tracking
    total_fines = Column(Decimal(12, 2), default=Decimal("0.00"))
    unpaid_fines = Column(Decimal(12, 2), default=Decimal("0.00"))
    
    # Notes
    notes = Column(Text, nullable=True)
    suspension_reason = Column(Text, nullable=True)
    suspension_end_date = Column(Date, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    transactions = relationship("BookTransaction", back_populates="member", lazy="dynamic")
    reservations = relationship("BookReservation", back_populates="member", lazy="dynamic")
    
    @property
    def can_borrow(self) -> bool:
        """Check if member can borrow books"""
        return (
            self.status == MemberStatus.ACTIVE and
            self.current_issues < self.max_books and
            (self.suspension_end_date is None or self.suspension_end_date < date.today())
        )
    
    def __repr__(self):
        return f"<LibraryMember(id={self.id}, card='{self.card_number}', user_id={self.user_id})>"


class BookTransaction(Base):
    """
    Book transaction model
    
    Records all book issue and return transactions.
    """
    __tablename__ = "book_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book_catalog.id"), nullable=False)
    copy_id = Column(UUID(as_uuid=True), ForeignKey("book_copies.id"), nullable=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("library_members.id"), nullable=False)
    
    # Dates
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    actual_return_date = Column(DateTime, nullable=True)  # When actually returned
    
    # Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.ISSUED)
    
    # Renewal tracking
    renewal_count = Column(Integer, default=0)
    max_renewals = Column(Integer, default=2)  # Max times can renew
    
    # Fine tracking
    fine_per_day = Column(Decimal(10, 2), default=Decimal("1.00"))
    fine_amount = Column(Decimal(12, 2), default=Decimal("0.00"))
    fine_paid = Column(Decimal(12, 2), default=Decimal("0.00"))
    fine_status = Column(String(20), default="PENDING")  # PENDING, PAID, WAIVED
    
    # Notes
    issue_notes = Column(Text, nullable=True)
    return_notes = Column(Text, nullable=True)
    condition_on_return = Column(String(50), nullable=True)
    
    # Processed by
    issued_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    book = relationship("BookCatalog", back_populates="transactions")
    copy = relationship("BookCopy")
    member = relationship("LibraryMember", back_populates="transactions")
    
    @property
    def is_overdue(self) -> bool:
        """Check if book is overdue"""
        if self.status in [TransactionStatus.RETURNED, TransactionStatus.LOST]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def overdue_days(self) -> int:
        """Calculate overdue days"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    def calculate_fine(self) -> Decimal:
        """Calculate fine based on overdue days"""
        days = self.overdue_days
        if days <= 0:
            return Decimal("0.00")
        return days * self.fine_per_day
    
    def __repr__(self):
        return f"<BookTransaction(id={self.id}, book_id={self.book_id}, member_id={self.member_id}, status={self.status})>"


class BookReservation(Base):
    """
    Book reservation model
    
    Tracks holds/reservations on books that are currently unavailable.
    """
    __tablename__ = "book_reservations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book_catalog.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("library_members.id"), nullable=False)
    
    # Reservation dates
    reservation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=False)  # Typically 7 days from reservation
    
    # Status
    status = Column(Enum(ReservationStatus), default=ReservationStatus.ACTIVE)
    
    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    notification_date = Column(DateTime, nullable=True)
    
    # Fulfillment details
    fulfilled_date = Column(DateTime, nullable=True)
    days_waited = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    book = relationship("BookCatalog", back_populates="reservations")
    member = relationship("LibraryMember", back_populates="reservations")
    
    def __repr__(self):
        return f"<BookReservation(id={self.id}, book_id={self.book_id}, member_id={self.member_id}, status={self.status})>"


class FineRecord(Base):
    """
    Fine record model
    
    Tracks fines imposed on members for overdue or damaged books.
    """
    __tablename__ = "fine_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("book_transactions.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("library_members.id"), nullable=False)
    
    # Fine details
    fine_type = Column(String(50), default="OVERDUE")  # OVERDEE, DAMAGE, LOST
    amount = Column(Decimal(12, 2), nullable=False)
    paid_amount = Column(Decimal(12, 2), default=Decimal("0.00"))
    
    # Status
    status = Column(String(20), default="PENDING")  # PENDING, PARTIAL, PAID, WAIVED
    
    # Waiver details
    waived_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    waiver_reason = Column(Text, nullable=True)
    waived_date = Column(DateTime, nullable=True)
    
    # Payment details
    paid_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<FineRecord(id={self.id}, amount={self.amount}, status={self.status})>"


class LibrarySettings(Base):
    """
    Library configuration settings
    
    Stores configurable settings for library operations.
    """
    __tablename__ = "library_settings"
    
    id = Column(Integer, primary_key=True, default=1)
    
    # Borrowing limits
    student_max_books = Column(Integer, default=3)
    student_max_days = Column(Integer, default=14)
    staff_max_books = Column(Integer, default=5)
    staff_max_days = Column(Integer, default=30)
    
    # Renewal settings
    max_renewals = Column(Integer, default=2)
    renewal_extends_days = Column(Integer, default=7)
    
    # Fine settings
    fine_per_day = Column(Decimal(10, 2), default=Decimal("1.00"))
    max_fine_cap = Column(Decimal(10, 2), default=Decimal("50.00"))
    
    # Reservation settings
    reservation_expiry_days = Column(Integer, default=7)
    max_reservations_per_member = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
