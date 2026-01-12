"""
Library Service
Business logic for library management and book circulation
"""

import logging
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    BookCatalog, BookCopy, LibraryMember, BookTransaction, 
    BookReservation, FineRecord, LibrarySettings,
    BookCategory, MemberType, MemberStatus, TransactionStatus, ReservationStatus
)
from app.schema.library_schema import (
    BookCreate, BookUpdate, BookIssueRequest, BookReturnRequest, BookRenewRequest,
    ReservationCreate, FinePaymentRequest, FineWaiveRequest,
    IssueReceipt, ReturnReceipt, OverdueItem
)

logger = logging.getLogger(__name__)


class LibraryService:
    """
    Service for library management and book circulation
    
    Provides business logic for book catalog management, 
    circulation tracking, reservations, and fine management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== Settings ====================
    
    async def get_settings(self) -> LibrarySettings:
        """Get library settings"""
        result = await self.db.execute(
            select(LibrarySettings).where(LibrarySettings.id == 1)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Create default settings
            settings = LibrarySettings(id=1)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return settings
    
    async def _get_member_limits(self, member_type: MemberType) -> Tuple[int, int]:
        """Get borrowing limits for member type"""
        settings = await self.get_settings()
        
        if member_type == MemberType.STAFF:
            return settings.staff_max_books, settings.staff_max_days
        return settings.student_max_books, settings.student_max_days
    
    # ==================== Book Catalog ====================
    
    async def get_book_by_id(self, book_id: str) -> Optional[BookCatalog]:
        """Get book by ID"""
        result = await self.db.execute(
            select(BookCatalog)
            .options(selectinload(BookCatalog.transactions))
            .where(BookCatalog.id == uuid.UUID(book_id))
        )
        return result.scalar_one_or_none()
    
    async def get_book_by_isbn(self, isbn: str) -> Optional[BookCatalog]:
        """Get book by ISBN"""
        result = await self.db.execute(
            select(BookCatalog).where(BookCatalog.isbn == isbn)
        )
        return result.scalar_one_or_none()
    
    async def search_books(
        self,
        search: Optional[str] = None,
        category: Optional[BookCategory] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        available_only: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[BookCatalog], int]:
        """Search books with filters"""
        query = select(BookCatalog).where(BookCatalog.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    BookCatalog.title.ilike(search_term),
                    BookCatalog.author.ilike(search_term),
                    BookCatalog.isbn.ilike(search_term)
                )
            )
        
        if category:
            query = query.where(BookCatalog.category == category)
        
        if author:
            query = query.where(BookCatalog.author.ilike(f"%{author}%"))
        
        if isbn:
            query = query.where(BookCatalog.isbn == isbn)
        
        if available_only:
            query = query.where(BookCatalog.available_copies > 0)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(BookCatalog.title)
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        books = result.scalars().all()
        
        return list(books), total
    
    async def create_book(self, data: BookCreate) -> BookCatalog:
        """Create new book"""
        # Check for duplicate ISBN
        existing = await self.get_book_by_isbn(data.isbn)
        if existing:
            raise ValueError(f"Book with ISBN '{data.isbn}' already exists")
        
        book = BookCatalog(
            id=uuid.uuid4(),
            isbn=data.isbn,
            title=data.title,
            author=data.author,
            publisher=data.publisher,
            publication_year=data.publication_year,
            edition=data.edition,
            category=data.category,
            total_copies=data.total_copies,
            available_copies=data.total_copies,
            shelf_location=data.shelf_location,
            DeweyDecimal=data.DeweyDecimal,
            pages=data.pages,
            language=data.language,
            cost=data.cost,
            acquisition_date=date.today(),
            description=data.description,
            cover_image_url=data.cover_image_url
        )
        
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        
        return book
    
    async def update_book(
        self, 
        book_id: str, 
        data: BookUpdate
    ) -> Optional[BookCatalog]:
        """Update book"""
        book = await self.get_book_by_id(book_id)
        if not book:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(book, field, value)
        
        await self.db.commit()
        await self.db.refresh(book)
        
        return book
    
    async def delete_book(self, book_id: str) -> bool:
        """Soft delete book"""
        book = await self.get_book_by_id(book_id)
        if not book:
            return False
        
        # Check if book has active transactions
        active_transactions = await self.db.execute(
            select(func.count()).select_from(
                select(BookTransaction.id).where(and_(
                    BookTransaction.book_id == uuid.UUID(book_id),
                    BookTransaction.status.in_([
                        TransactionStatus.ISSUED,
                        TransactionStatus.OVERDUE
                    ])
                )).subquery()
            )
        )
        
        if (active_transactions.scalar() or 0) > 0:
            raise ValueError("Cannot delete book with active transactions")
        
        book.is_active = False
        await self.db.commit()
        
        return True
    
    # ==================== Book Copies ====================
    
    async def add_book_copy(self, book_id: str, barcode: str, **kwargs) -> BookCopy:
        """Add a physical copy of a book"""
        book = await self.get_book_by_id(book_id)
        if not book:
            raise ValueError(f"Book '{book_id}' not found")
        
        # Check for duplicate barcode
        result = await self.db.execute(
            select(BookCopy).where(BookCopy.barcode == barcode)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Book copy with barcode '{barcode}' already exists")
        
        copy = BookCopy(
            id=uuid.uuid4(),
            book_id=uuid.UUID(book_id),
            barcode=barcode,
            shelf_location=kwargs.get("shelf_location") or book.shelf_location,
            condition=kwargs.get("condition", "GOOD")
        )
        
        # Update book counts
        book.total_copies += 1
        book.available_copies += 1
        
        self.db.add(copy)
        await self.db.commit()
        await self.db.refresh(copy)
        
        return copy
    
    # ==================== Library Members ====================
    
    async def get_member_by_id(self, member_id: str) -> Optional[LibraryMember]:
        """Get library member by ID"""
        result = await self.db.execute(
            select(LibraryMember)
            .options(selectinload(LibraryMember.user))
            .where(LibraryMember.id == uuid.UUID(member_id))
        )
        return result.scalar_one_or_none()
    
    async def get_member_by_user_id(self, user_id: int) -> Optional[LibraryMember]:
        """Get library member by user ID"""
        result = await self.db.execute(
            select(LibraryMember).where(LibraryMember.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_member_by_card(self, card_number: str) -> Optional[LibraryMember]:
        """Get library member by card number"""
        result = await self.db.execute(
            select(LibraryMember).where(LibraryMember.card_number == card_number)
        )
        return result.scalar_one_or_none()
    
    async def create_member(self, user_id: int, member_type: MemberType) -> LibraryMember:
        """Create library member"""
        # Check if user is already a member
        existing = await self.get_member_by_user_id(user_id)
        if existing:
            raise ValueError(f"User is already a library member")
        
        # Get default limits
        max_books, max_days = await self._get_member_limits(member_type)
        
        # Generate card number
        card_number = await self._generate_card_number()
        
        member = LibraryMember(
            id=uuid.uuid4(),
            user_id=user_id,
            member_type=member_type,
            card_number=card_number,
            max_books=max_books,
            max_days=max_days
        )
        
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        
        return member
    
    async def _generate_card_number(self) -> str:
        """Generate unique card number"""
        # Format: LIB-YYYY-XXXX
        year = datetime.utcnow().year
        prefix = f"LIB-{year}-"
        
        result = await self.db.execute(
            select(func.count()).select_from(LibraryMember)
            .where(LibraryMember.card_number.like(f"{prefix}%"))
        )
        count = (result.scalar() or 0) + 1
        
        return f"{prefix}{count:05d}"
    
    # ==================== Book Circulation ====================
    
    async def issue_book(self, request: BookIssueRequest, issued_by_id: Optional[int] = None) -> Tuple[BookTransaction, IssueReceipt]:
        """Issue a book to a member"""
        # Get book
        book = await self.get_book_by_id(request.book_id)
        if not book:
            raise ValueError(f"Book '{request.book_id}' not found")
        
        # Check availability
        if book.available_copies <= 0:
            raise ValueError(f"Book '{book.title}' is not available")
        
        # Get member
        member = await self.get_member_by_id(request.member_id)
        if not member:
            raise ValueError(f"Library member '{request.member_id}' not found")
        
        # Check member status
        if not member.can_borrow:
            if member.suspension_end_date and member.suspension_end_date >= date.today():
                raise ValueError(f"Member is suspended until {member.suspension_end_date}")
            raise ValueError(f"Member has reached maximum book limit ({member.max_books})")
        
        # Check for existing reservation queue
        reservation = await self._check_reservation_queue(request.book_id, request.member_id)
        if reservation is None:
            # Check if someone else has a reservation
            next_reservation = await self._get_next_reservation(request.book_id)
            if next_reservation and next_reservation.member_id != uuid.UUID(request.member_id):
                raise ValueError("This book is reserved by another member")
        
        # Calculate due date
        days = request.days or member.max_days
        due_date = datetime.utcnow() + timedelta(days=days)
        
        # Get book copy if specified
        copy = None
        if request.copy_id:
            result = await self.db.execute(
                select(BookCopy).where(BookCopy.id == uuid.UUID(request.copy_id))
            )
            copy = result.scalar_one_or_none()
        
        # Create transaction
        transaction = BookTransaction(
            id=uuid.uuid4(),
            book_id=uuid.UUID(request.book_id),
            copy_id=uuid.UUID(request.copy_id) if request.copy_id else None,
            member_id=uuid.UUID(request.member_id),
            issue_date=datetime.utcnow(),
            due_date=due_date,
            status=TransactionStatus.ISSUED,
            issued_by_id=issued_by_id,
            issue_notes=request.notes
        )
        
        # Update book and member
        book.available_copies -= 1
        member.current_issues += 1
        
        # Fulfill reservation if exists
        if reservation:
            reservation.status = ReservationStatus.FULFILLED
            reservation.fulfilled_date = datetime.utcnow()
        
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        receipt = IssueReceipt(
            transaction_id=str(transaction.id),
            book_title=book.title,
            book_isbn=book.isbn,
            member_name=member.user.first_name + " " + member.user.last_name if member.user else "Unknown",
            member_card=member.card_number,
            issue_date=transaction.issue_date,
            due_date=transaction.due_date,
            days_allowed=days,
            renewal_count=0,
            max_renewals=transaction.max_renewals
        )
        
        return transaction, receipt
    
    async def return_book(self, request: BookReturnRequest, received_by_id: Optional[int] = None) -> Tuple[BookTransaction, ReturnReceipt]:
        """Return a book"""
        # Get transaction
        result = await self.db.execute(
            select(BookTransaction)
            .options(
                selectinload(BookTransaction.book),
                selectinload(BookTransaction.member).selectinload(LibraryMember.user)
            )
            .where(BookTransaction.id == uuid.UUID(request.transaction_id))
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise ValueError(f"Transaction '{request.transaction_id}' not found")
        
        if transaction.status in [TransactionStatus.RETURNED, TransactionStatus.LOST]:
            raise ValueError(f"Book has already been returned")
        
        # Update transaction
        transaction.return_date = datetime.utcnow()
        transaction.actual_return_date = datetime.utcnow()
        transaction.status = TransactionStatus.RETURNED
        transaction.received_by_id = received_by_id
        transaction.return_notes = request.condition_notes
        transaction.condition_on_return = request.condition
        
        # Calculate fine if overdue
        if transaction.is_overdue:
            transaction.fine_amount = transaction.calculate_fine()
            transaction.status = TransactionStatus.OVERDUE
        else:
            transaction.fine_amount = Decimal("0.00")
        
        # Update book and member
        book = transaction.book
        member = transaction.member
        
        book.available_copies += 1
        member.current_issues -= 1
        
        # Check for next reservation
        next_reservation = await self._get_next_reservation(str(book.id))
        if next_reservation:
            # Notify next person (in production, this would send SMS/email)
            logger.info(f"Book {book.title} reserved by member {next_reservation.member_id}")
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        receipt = ReturnReceipt(
            transaction_id=str(transaction.id),
            book_title=book.title,
            book_isbn=book.isbn,
            member_name=member.user.first_name + " " + member.user.last_name if member.user else "Unknown",
            member_card=member.card_number,
            issued_date=transaction.issue_date,
            due_date=transaction.due_date,
            returned_date=transaction.actual_return_date,
            overdue_days=transaction.overdue_days,
            fine_amount=transaction.fine_amount,
            fine_paid=transaction.fine_paid,
            fine_status=transaction.fine_status
        )
        
        return transaction, receipt
    
    async def renew_book(self, request: BookRenewRequest) -> BookTransaction:
        """Renew a book"""
        result = await self.db.execute(
            select(BookTransaction)
            .options(selectinload(BookTransaction.book))
            .where(BookTransaction.id == uuid.UUID(request.transaction_id))
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise ValueError(f"Transaction '{request.transaction_id}' not found")
        
        if transaction.status == TransactionStatus.RETURNED:
            raise ValueError("Cannot renew a returned book")
        
        if transaction.status == TransactionStatus.LOST:
            raise ValueError("Cannot renew a lost book")
        
        if transaction.renewal_count >= transaction.max_renewals:
            raise ValueError(f"Maximum renewals ({transaction.max_renewals}) reached")
        
        if transaction.is_overdue:
            raise ValueError("Cannot renew overdue book. Please return and pay fine.")
        
        # Check for reservation queue
        next_reservation = await self._get_next_reservation(str(transaction.book_id))
        if next_reservation and next_reservation.member_id != transaction.member_id:
            raise ValueError("Cannot renew: book reserved by another member")
        
        # Renew
        settings = await self.get_settings()
        transaction.due_date = transaction.due_date + timedelta(days=settings.renewal_extends_days)
        transaction.status = TransactionStatus.RENEWED
        transaction.renewal_count += 1
        transaction.issue_notes = request.notes or transaction.issue_notes
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def mark_as_lost(self, transaction_id: str) -> BookTransaction:
        """Mark a book as lost"""
        result = await self.db.execute(
            select(BookTransaction)
            .options(selectinload(BookTransaction.member))
            .where(BookTransaction.id == uuid.UUID(transaction_id))
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise ValueError(f"Transaction '{transaction_id}' not found")
        
        transaction.status = TransactionStatus.LOST
        transaction.fine_amount = transaction.book.cost or Decimal("50.00")  # Use book cost or default
        
        # Update member fine
        member = transaction.member
        member.unpaid_fines += transaction.fine_amount
        member.current_issues -= 1
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    # ==================== Reservations ====================
    
    async def create_reservation(self, request: ReservationCreate) -> BookReservation:
        """Create a book reservation"""
        # Get book
        book = await self.get_book_by_id(request.book_id)
        if not book:
            raise ValueError(f"Book '{request.book_id}' not found")
        
        # Check if book is available
        if book.available_copies > 0:
            raise ValueError("Book is available. Please issue directly instead of reserving.")
        
        # Get member
        member = await self.get_member_by_id(request.member_id)
        if not member:
            raise ValueError(f"Library member '{request.member_id}' not found")
        
        if not member.can_borrow:
            raise ValueError("Member cannot borrow books")
        
        # Check for existing active reservation
        existing = await self.db.execute(
            select(BookReservation).where(and_(
                BookReservation.book_id == uuid.UUID(request.book_id),
                BookReservation.member_id == uuid.UUID(request.member_id),
                BookReservation.status == ReservationStatus.ACTIVE
            ))
        )
        if existing.scalar_one_or_none():
            raise ValueError("Member already has an active reservation for this book")
        
        # Check reservation limit
        settings = await self.get_settings()
        reservation_count = await self.db.execute(
            select(func.count()).select_from(BookReservation)
            .where(and_(
                BookReservation.member_id == uuid.UUID(request.member_id),
                BookReservation.status == ReservationStatus.ACTIVE
            ))
        )
        if (reservation_count.scalar() or 0) >= settings.max_reservations_per_member:
            raise ValueError(f"Maximum reservations ({settings.max_reservations_per_member}) reached")
        
        # Calculate expiry
        settings = await self.get_settings()
        expiry_date = datetime.utcnow() + timedelta(days=settings.reservation_expiry_days)
        
        reservation = BookReservation(
            id=uuid.uuid4(),
            book_id=uuid.UUID(request.book_id),
            member_id=uuid.UUID(request.member_id),
            expiry_date=expiry_date,
            notes=request.notes
        )
        
        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)
        
        return reservation
    
    async def cancel_reservation(self, reservation_id: str) -> BookReservation:
        """Cancel a reservation"""
        result = await self.db.execute(
            select(BookReservation).where(BookReservation.id == uuid.UUID(reservation_id))
        )
        reservation = result.scalar_one_or_none()
        
        if not reservation:
            raise ValueError(f"Reservation '{reservation_id}' not found")
        
        if reservation.status != ReservationStatus.ACTIVE:
            raise ValueError(f"Cannot cancel reservation with status: {reservation.status}")
        
        reservation.status = ReservationStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(reservation)
        
        return reservation
    
    async def _check_reservation_queue(self, book_id: str, member_id: str) -> Optional[BookReservation]:
        """Check if member is first in reservation queue"""
        result = await self.db.execute(
            select(BookReservation)
            .where(and_(
                BookReservation.book_id == uuid.UUID(book_id),
                BookReservation.member_id == uuid.UUID(member_id),
                BookReservation.status == ReservationStatus.ACTIVE
            ))
            .order_by(BookReservation.reservation_date)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def _get_next_reservation(self, book_id: str) -> Optional[BookReservation]:
        """Get next active reservation for a book"""
        result = await self.db.execute(
            select(BookReservation)
            .options(selectinload(BookReservation.member))
            .where(and_(
                BookReservation.book_id == uuid.UUID(book_id),
                BookReservation.status == ReservationStatus.ACTIVE,
                BookReservation.expiry_date > datetime.utcnow()
            ))
            .order_by(BookReservation.reservation_date)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    # ==================== Fines ====================
    
    async def pay_fine(self, request: FinePaymentRequest) -> FineRecord:
        """Pay a fine"""
        result = await self.db.execute(
            select(FineRecord)
            .options(selectinload(FineRecord.member))
            .where(FineRecord.id == uuid.UUID(request.fine_id))
        )
        fine = result.scalar_one_or_none()
        
        if not fine:
            raise ValueError(f"Fine '{request.fine_id}' not found")
        
        if fine.status in ["PAID", "WAIVED"]:
            raise ValueError(f"Fine already {fine.status.lower()}")
        
        fine.paid_amount += request.amount
        fine.status = "PAID" if fine.paid_amount >= fine.amount else "PARTIAL"
        fine.paid_date = datetime.utcnow()
        fine.payment_method = request.payment_method
        fine.reference_number = request.reference_number
        
        # Update member
        member = fine.member
        member.unpaid_fines -= min(request.amount, fine.amount - fine.paid_amount)
        
        await self.db.commit()
        await self.db.refresh(fine)
        
        return fine
    
    async def waive_fine(self, request: FineWaiveRequest, waived_by_id: int) -> FineRecord:
        """Waive a fine"""
        result = await self.db.execute(
            select(FineRecord)
            .options(selectinload(FineRecord.member))
            .where(FineRecord.id == uuid.UUID(request.fine_id))
        )
        fine = result.scalar_one_or_none()
        
        if not fine:
            raise ValueError(f"Fine '{request.fine_id}' not found")
        
        if fine.status == "PAID":
            raise ValueError("Cannot waive already paid fine")
        
        fine.status = "WAIVED"
        fine.waived_by_id = waived_by_id
        fine.waiver_reason = request.reason
        fine.waived_date = datetime.utcnow()
        
        # Update member
        member = fine.member
        member.unpaid_fines -= fine.amount
        
        await self.db.commit()
        await self.db.refresh(fine)
        
        return fine
    
    # ==================== Reports ====================
    
    async def get_overdue_report(self) -> List[OverdueItem]:
        """Get all overdue items"""
        result = await self.db.execute(
            select(BookTransaction)
            .options(
                selectinload(BookTransaction.book),
                selectinload(BookTransaction.member).selectinload(LibraryMember.user)
            )
            .where(BookTransaction.status.in_([TransactionStatus.ISSUED, TransactionStatus.OVERDUE]))
            .order_by(BookTransaction.due_date)
        )
        transactions = result.scalars().all()
        
        overdue_items = []
        for tx in transactions:
            if tx.is_overdue:
                overdue_items.append(OverdueItem(
                    transaction_id=str(tx.id),
                    book_id=str(tx.book_id),
                    book_title=tx.book.title,
                    book_isbn=tx.book.isbn,
                    member_id=str(tx.member_id),
                    member_card=tx.member.card_number,
                    member_name=tx.member.user.first_name + " " + tx.member.user.last_name if tx.member.user else "Unknown",
                    due_date=tx.due_date,
                    overdue_days=tx.overdue_days,
                    fine_amount=tx.fine_amount,
                    status=tx.status.value
                ))
        
        return overdue_items
    
    async def get_stats(self) -> dict:
        """Get library statistics"""
        # Book stats
        books_result = await self.db.execute(
            select(
                func.count(BookCatalog.id),
                func.sum(BookCatalog.total_copies),
                func.sum(BookCatalog.available_copies)
            ).where(BookCatalog.is_active == True)
        )
        books_row = books_result.first()
        
        # Member stats
        members_result = await self.db.execute(
            select(
                func.count(LibraryMember.id),
                func.count().where(LibraryMember.status == MemberStatus.ACTIVE)
            )
        )
        members_row = members_result.first()
        
        # Transaction stats
        tx_result = await self.db.execute(
            select(
                func.count(BookTransaction.id),
                func.count().where(BookTransaction.status.in_([
                    TransactionStatus.ISSUED, TransactionStatus.OVERDUE
                ]))
            )
        )
        tx_row = tx_result.first()
        
        # Overdue and fines
        overdue_result = await self.db.execute(
            select(
                func.count().where(BookTransaction.status == TransactionStatus.OVERDUE),
                func.sum(BookTransaction.fine_amount - BookTransaction.fine_paid)
                .where(BookTransaction.fine_status.in_(["PENDING", "PARTIAL"]))
            )
        )
        overdue_row = overdue_result.first()
        
        return {
            "total_books": books_row[0] or 0,
            "total_copies": books_row[1] or 0,
            "available_copies": books_row[2] or 0,
            "total_members": members_row[0] or 0,
            "active_members": members_row[1] or 0,
            "total_transactions": tx_row[0] or 0,
            "active_transactions": tx_row[1] or 0,
            "overdue_count": overdue_row[0] or 0,
            "total_fines_pending": overdue_row[1] or Decimal("0.00")
        }
