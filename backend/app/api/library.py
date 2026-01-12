"""
Library API Routes
Endpoints for library management and book circulation
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user, require_roles
from app.schema.library_schema import (
    BookCreate, BookUpdate, BookResponse, BookListResponse,
    MemberCreate, MemberUpdate, MemberResponse, MemberListResponse,
    BookIssueRequest, BookReturnRequest, BookRenewRequest,
    TransactionResponse, TransactionListResponse,
    ReservationCreate, ReservationResponse, ReservationListResponse,
    FineResponse, FineListResponse, FinePaymentRequest, FineWaiveRequest,
    OverdueReport, LibrarySettingsResponse, LibraryStatsResponse,
    IssueReceipt, ReturnReceipt, MessageResponse
)
from app.services.library_service import LibraryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["Library"])


# ==================== Book Catalog Endpoints ====================

@router.get("/books", response_model=BookListResponse)
async def list_books(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    isbn: Optional[str] = Query(None),
    available_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List books with search and filters"""
    from app.schema.library_schema import BookCategory
    
    service = LibraryService(db)
    books, total = await service.search_books(
        search=search,
        category=BookCategory(category) if category else None,
        author=author,
        isbn=isbn,
        available_only=available_only,
        page=page,
        per_page=per_page
    )
    
    return BookListResponse(
        books=[
            BookResponse(
                id=str(book.id),
                isbn=book.isbn,
                title=book.title,
                author=book.author,
                publisher=book.publisher,
                publication_year=book.publication_year,
                edition=book.edition,
                category=book.category.value,
                total_copies=book.total_copies,
                available_copies=book.available_copies,
                shelf_location=book.shelf_location,
                DeweyDecimal=book.DeweyDecimal,
                pages=book.pages,
                language=book.language,
                cost=book.cost,
                description=book.description,
                cover_image_url=book.cover_image_url,
                is_active=book.is_active,
                is_available=book.available_copies > 0,
                created_at=book.created_at,
                updated_at=book.updated_at
            )
            for book in books
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get book by ID"""
    service = LibraryService(db)
    book = await service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book '{book_id}' not found"
        )
    
    return BookResponse(
        id=str(book.id),
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        publication_year=book.publication_year,
        edition=book.edition,
        category=book.category.value,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        shelf_location=book.shelf_location,
        DeweyDecimal=book.DeweyDecimal,
        pages=book.pages,
        language=book.language,
        cost=book.cost,
        description=book.description,
        cover_image_url=book.cover_image_url,
        is_active=book.is_active,
        is_available=book.available_copies > 0,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Create new book"""
    try:
        service = LibraryService(db)
        book = await service.create_book(data)
        
        return BookResponse(
            id=str(book.id),
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            publication_year=book.publication_year,
            edition=book.edition,
            category=book.category.value,
            total_copies=book.total_copies,
            available_copies=book.available_copies,
            shelf_location=book.shelf_location,
            DeweyDecimal=book.DeweyDecimal,
            pages=book.pages,
            language=book.language,
            cost=book.cost,
            description=book.description,
            cover_image_url=book.cover_image_url,
            is_active=book.is_active,
            is_available=book.available_copies > 0,
            created_at=book.created_at,
            updated_at=book.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Update book"""
    service = LibraryService(db)
    book = await service.update_book(book_id, data)
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book '{book_id}' not found"
        )
    
    return BookResponse(
        id=str(book.id),
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        publication_year=book.publication_year,
        edition=book.edition,
        category=book.category.value,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        shelf_location=book.shelf_location,
        DeweyDecimal=book.DeweyDecimal,
        pages=book.pages,
        language=book.language,
        cost=book.cost,
        description=book.description,
        cover_image_url=book.cover_image_url,
        is_active=book.is_active,
        is_available=book.available_copies > 0,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


@router.delete("/books/{book_id}", response_model=MessageResponse)
async def delete_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Delete (deactivate) book"""
    try:
        service = LibraryService(db)
        success = await service.delete_book(book_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Book '{book_id}' not found"
            )
        
        return MessageResponse(message="Book deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Member Endpoints ====================

@router.get("/members", response_model=MemberListResponse)
async def list_members(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List library members"""
    from app.schema.library_schema import MemberStatus
    
    service = LibraryService(db)
    
    # Get all members (simplified - in production would filter by search)
    result = await service.db.execute(
        select(LibraryMember)
        .options(selectinload(LibraryMember.user))
        .where(LibraryMember.is_active == True)
        .order_by(LibraryMember.created_at.desc())
    )
    members = result.scalars().all()
    
    total = len(members)
    
    return MemberListResponse(
        members=[
            MemberResponse(
                id=str(member.id),
                user_id=member.user_id,
                member_type=member.member_type.value,
                card_number=member.card_number,
                registration_date=member.registration_date,
                expiry_date=member.expiry_date,
                max_books=member.max_books,
                max_days=member.max_days,
                current_issues=member.current_issues,
                total_fines=member.total_fines,
                unpaid_fines=member.unpaid_fines,
                status=member.status.value,
                can_borrow=member.can_borrow,
                remaining_books=member.max_books - member.current_issues,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at
            )
            for member in members
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get member by ID"""
    service = LibraryService(db)
    member = await service.get_member_by_id(member_id)
    
    if not member:
        raise HTTPException(
            status_code=404,
            detail=f"Member '{member_id}' not found"
        )
    
    return MemberResponse(
        id=str(member.id),
        user_id=member.user_id,
        member_type=member.member_type.value,
        card_number=member.card_number,
        registration_date=member.registration_date,
        expiry_date=member.expiry_date,
        max_books=member.max_books,
        max_days=member.max_days,
        current_issues=member.current_issues,
        total_fines=member.total_fines,
        unpaid_fines=member.unpaid_fines,
        status=member.status.value,
        can_borrow=member.can_borrow,
        remaining_books=member.max_books - member.current_issues,
        is_active=member.is_active,
        created_at=member.created_at,
        updated_at=member.updated_at
    )


@router.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    user_id: int,
    member_type: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Create library member"""
    from app.schema.library_schema import MemberType
    
    try:
        member_type_enum = MemberType(member_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid member type. Must be STUDENT or STAFF"
        )
    
    try:
        service = LibraryService(db)
        member = await service.create_member(user_id, member_type_enum)
        
        return MemberResponse(
            id=str(member.id),
            user_id=member.user_id,
            member_type=member.member_type.value,
            card_number=member.card_number,
            registration_date=member.registration_date,
            expiry_date=member.expiry_date,
            max_books=member.max_books,
            max_days=member.max_days,
            current_issues=member.current_issues,
            total_fines=member.total_fines,
            unpaid_fines=member.unpaid_fines,
            status=member.status.value,
            can_borrow=member.can_borrow,
            remaining_books=member.max_books - member.current_issues,
            is_active=member.is_active,
            created_at=member.created_at,
            updated_at=member.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Circulation Endpoints ====================

@router.post("/issue", response_model=IssueReceipt)
async def issue_book(
    request: BookIssueRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Issue a book to a member"""
    try:
        service = LibraryService(db)
        transaction, receipt = await service.issue_book(
            request=request,
            issued_by_id=current_user.id if current_user else None
        )
        return receipt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/return", response_model=ReturnReceipt)
async def return_book(
    request: BookReturnRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Return a book"""
    try:
        service = LibraryService(db)
        transaction, receipt = await service.return_book(
            request=request,
            received_by_id=current_user.id if current_user else None
        )
        return receipt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/renew", response_model=TransactionResponse)
async def renew_book(
    request: BookRenewRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian", "member"]))
):
    """Renew a book"""
    try:
        service = LibraryService(db)
        transaction = await service.renew_book(request)
        
        return TransactionResponse(
            id=str(transaction.id),
            book_id=str(transaction.book_id),
            member_id=str(transaction.member_id),
            copy_id=str(transaction.copy_id) if transaction.copy_id else None,
            issue_date=transaction.issue_date,
            due_date=transaction.due_date,
            return_date=transaction.return_date,
            actual_return_date=transaction.actual_return_date,
            status=transaction.status.value,
            renewal_count=transaction.renewal_count,
            fine_amount=transaction.fine_amount,
            fine_paid=transaction.fine_paid,
            fine_status=transaction.fine_status,
            is_overdue=transaction.is_overdue,
            overdue_days=transaction.overdue_days,
            current_fine=transaction.calculate_fine(),
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mark-lost/{transaction_id}", response_model=TransactionResponse)
async def mark_as_lost(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Mark a book as lost"""
    try:
        service = LibraryService(db)
        transaction = await service.mark_as_lost(transaction_id)
        
        return TransactionResponse(
            id=str(transaction.id),
            book_id=str(transaction.book_id),
            member_id=str(transaction.member_id),
            copy_id=str(transaction.copy_id) if transaction.copy_id else None,
            issue_date=transaction.issue_date,
            due_date=transaction.due_date,
            return_date=transaction.return_date,
            actual_return_date=transaction.actual_return_date,
            status=transaction.status.value,
            renewal_count=transaction.renewal_count,
            fine_amount=transaction.fine_amount,
            fine_paid=transaction.fine_paid,
            fine_status=transaction.fine_status,
            is_overdue=transaction.is_overdue,
            overdue_days=transaction.overdue_days,
            current_fine=transaction.calculate_fine(),
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    member_id: Optional[str] = Query(None),
    book_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List transactions"""
    from app.schema.library_schema import TransactionStatus
    
    service = LibraryService(db)
    
    query = select(BookTransaction).order_by(BookTransaction.created_at.desc())
    
    if status_filter:
        try:
            status_enum = TransactionStatus(status_filter)
            query = query.where(BookTransaction.status == status_enum)
        except ValueError:
            pass
    
    if member_id:
        query = query.where(BookTransaction.member_id == uuid.UUID(member_id))
    
    if book_id:
        query = query.where(BookTransaction.book_id == uuid.UUID(book_id))
    
    # Get total count
    count_result = await service.db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await service.db.execute(query)
    transactions = result.scalars().all()
    
    return TransactionListResponse(
        transactions=[
            TransactionResponse(
                id=str(tx.id),
                book_id=str(tx.book_id),
                member_id=str(tx.member_id),
                copy_id=str(tx.copy_id) if tx.copy_id else None,
                issue_date=tx.issue_date,
                due_date=tx.due_date,
                return_date=tx.return_date,
                actual_return_date=tx.actual_return_date,
                status=tx.status.value,
                renewal_count=tx.renewal_count,
                fine_amount=tx.fine_amount,
                fine_paid=tx.fine_paid,
                fine_status=tx.fine_status,
                is_overdue=tx.is_overdue,
                overdue_days=tx.overdue_days,
                current_fine=tx.calculate_fine(),
                created_at=tx.created_at,
                updated_at=tx.updated_at
            )
            for tx in transactions
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


# ==================== Reservation Endpoints ====================

@router.post("/reserve", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    request: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a book reservation"""
    try:
        service = LibraryService(db)
        reservation = await service.create_reservation(request)
        
        return ReservationResponse(
            id=str(reservation.id),
            book_id=str(reservation.book_id),
            member_id=str(reservation.member_id),
            reservation_date=reservation.reservation_date,
            expiry_date=reservation.expiry_date,
            status=reservation.status.value,
            notification_sent=reservation.notification_sent,
            notification_date=reservation.notification_date,
            fulfilled_date=reservation.fulfilled_date,
            days_waited=reservation.days_waited,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel a reservation"""
    try:
        service = LibraryService(db)
        reservation = await service.cancel_reservation(reservation_id)
        
        return ReservationResponse(
            id=str(reservation.id),
            book_id=str(reservation.book_id),
            member_id=str(reservation.member_id),
            reservation_date=reservation.reservation_date,
            expiry_date=reservation.expiry_date,
            status=reservation.status.value,
            notification_sent=reservation.notification_sent,
            notification_date=reservation.notification_date,
            fulfilled_date=reservation.fulfilled_date,
            days_waited=reservation.days_waited,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Fine Endpoints ====================

@router.post("/fines/{fine_id}/pay", response_model=FineResponse)
async def pay_fine(
    fine_id: str,
    request: FinePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "accountant"]))
):
    """Pay a fine"""
    try:
        service = LibraryService(db)
        fine = await service.pay_fine(request)
        
        return FineResponse(
            id=str(fine.id),
            transaction_id=str(fine.transaction_id),
            member_id=str(fine.member_id),
            fine_type=fine.fine_type,
            amount=fine.amount,
            paid_amount=fine.paid_amount,
            status=fine.status,
            waived_date=fine.waived_date,
            paid_date=fine.paid_date,
            created_at=fine.created_at,
            updated_at=fine.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fines/{fine_id}/waive", response_model=FineResponse)
async def waive_fine(
    fine_id: str,
    request: FineWaiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Waive a fine"""
    try:
        service = LibraryService(db)
        fine = await service.waive_fine(request, current_user.id if current_user else None)
        
        return FineResponse(
            id=str(fine.id),
            transaction_id=str(fine.transaction_id),
            member_id=str(fine.member_id),
            fine_type=fine.fine_type,
            amount=fine.amount,
            paid_amount=fine.paid_amount,
            status=fine.status,
            waived_date=fine.waived_date,
            paid_date=fine.paid_date,
            created_at=fine.created_at,
            updated_at=fine.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Reports and Statistics ====================

@router.get("/reports/overdue", response_model=List[OverdueItem])
async def get_overdue_report(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "librarian"]))
):
    """Get overdue items report"""
    service = LibraryService(db)
    return await service.get_overdue_report()


@router.get("/stats/summary", response_model=LibraryStatsResponse)
async def get_library_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get library statistics"""
    service = LibraryService(db)
    stats = await service.get_stats()
    
    return LibraryStatsResponse(
        total_books=stats["total_books"],
        total_copies=stats["total_copies"],
        available_copies=stats["available_copies"],
        total_members=stats["total_members"],
        active_members=stats["active_members"],
        total_transactions=stats["total_transactions"],
        active_transactions=stats["active_transactions"],
        overdue_count=stats["overdue_count"],
        total_fines_pending=stats["total_fines_pending"],
        most_popular_books=[],
        most_active_members=[]
    )


@router.get("/settings", response_model=LibrarySettingsResponse)
async def get_library_settings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get library settings"""
    service = LibraryService(db)
    settings = await service.get_settings()
    
    return LibrarySettingsResponse(
        student_max_books=settings.student_max_books,
        student_max_days=settings.student_max_days,
        staff_max_books=settings.staff_max_books,
        staff_max_days=settings.staff_max_days,
        max_renewals=settings.max_renewals,
        renewal_extends_days=settings.renewal_extends_days,
        fine_per_day=settings.fine_per_day,
        max_fine_cap=settings.max_fine_cap,
        reservation_expiry_days=settings.reservation_expiry_days,
        max_reservations_per_member=settings.max_reservations_per_member
    )
