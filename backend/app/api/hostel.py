"""
Hostel API Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.hostel_service import HostelService
from app.schema.hostel_schema import (
    HostelBlockCreate, HostelBlockUpdate, HostelBlockResponse, HostelBlockWithDetailsResponse,
    RoomCreate, RoomUpdate, RoomResponse, RoomWithDetailsResponse,
    BedCreate, BedResponse,
    HostelAllocationCreate, HostelAllocationUpdate, HostelAllocationResponse,
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceRequestResponse,
    HostelFeeCreate, HostelFeeResponse,
    HostelFeePaymentCreate, HostelFeePaymentResponse,
    HostelBlockListResponse, RoomListResponse, MaintenanceRequestListResponse,
    RoomAvailabilityResponse, BlockAvailabilityResponse,
    HostelSummaryResponse
)
from app.core.security import get_current_user
from app.db.models.models import User


router = APIRouter(prefix="/hostel", tags=["Hostel"])


# ==================== Block Endpoints ====================

@router.post("/blocks", response_model=HostelBlockResponse)
async def create_block(
    block: HostelBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new hostel block"""
    service = HostelService(db)
    return await service.create_block(block)


@router.get("/blocks", response_model=HostelBlockListResponse)
async def get_blocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_type: Optional[str] = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all hostel blocks"""
    service = HostelService(db)
    from app.db.models.hostel import BlockType
    block_type_enum = BlockType(block_type) if block_type else None
    blocks = await service.get_all_blocks(skip, limit, block_type_enum, active_only)
    total = len(blocks)
    return {"blocks": blocks, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/blocks/{block_id}", response_model=HostelBlockWithDetailsResponse)
async def get_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get block by ID with details"""
    service = HostelService(db)
    block = await service.get_block(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    availability = await service.get_block_availability(block_id)
    return {
        **block.__dict__,
        **availability
    }


@router.put("/blocks/{block_id}", response_model=HostelBlockResponse)
async def update_block(
    block_id: int,
    block_update: HostelBlockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update block information"""
    service = HostelService(db)
    block = await service.update_block(block_id, block_update)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


@router.delete("/blocks/{block_id}")
async def delete_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a block"""
    service = HostelService(db)
    success = await service.delete_block(block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Block deleted successfully"}


@router.get("/blocks/{block_id}/availability", response_model=BlockAvailabilityResponse)
async def get_block_availability(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get block availability summary"""
    service = HostelService(db)
    availability = await service.get_block_availability(block_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Block not found")
    return availability


# ==================== Room Endpoints ====================

@router.post("/rooms", response_model=RoomResponse)
async def create_room(
    room: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room"""
    service = HostelService(db)
    return await service.create_room(room)


@router.get("/rooms", response_model=RoomListResponse)
async def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_id: Optional[int] = None,
    room_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all rooms"""
    service = HostelService(db)
    from app.db.models.hostel import RoomType
    room_type_enum = RoomType(room_type) if room_type else None
    rooms = await service.get_all_rooms(skip, limit, block_id, room_type_enum, status)
    total = len(rooms)
    return {"rooms": rooms, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/rooms/available")
async def get_available_rooms(
    block_id: Optional[int] = None,
    block_type: Optional[str] = None,
    room_type: Optional[str] = None,
    min_beds: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available rooms with available beds"""
    service = HostelService(db)
    from app.db.models.hostel import BlockType
    block_type_enum = BlockType(block_type) if block_type else None
    from app.db.models.hostel import RoomType
    room_type_enum = RoomType(room_type) if room_type else None
    rooms = await service.get_available_rooms(block_id, block_type_enum, room_type_enum, min_beds)
    return rooms


@router.get("/rooms/{room_id}", response_model=RoomWithDetailsResponse)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get room by ID with bed details"""
    service = HostelService(db)
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get available beds
    available_beds = await service.get_available_beds(room_id)
    return {
        **room.__dict__,
        "beds": available_beds,
        "available_beds": len(available_beds)
    }


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update room information"""
    service = HostelService(db)
    room = await service.update_room(room_id, room_update)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a room"""
    service = HostelService(db)
    success = await service.delete_room(room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}


@router.post("/rooms/{room_id}/beds", response_model=BedResponse)
async def add_bed_to_room(
    room_id: int,
    bed: BedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a bed to a room"""
    service = HostelService(db)
    try:
        return await service.add_bed_to_room(room_id, bed.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rooms/{room_id}/beds/available")
async def get_room_available_beds(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available beds in a room"""
    service = HostelService(db)
    beds = await service.get_available_beds(room_id)
    return beds


# ==================== Hostel Allocation Endpoints ====================

@router.post("/allocations", response_model=HostelAllocationResponse)
async def create_allocation(
    allocation: HostelAllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create hostel allocation for a student"""
    service = HostelService(db)
    try:
        return await service.create_allocation(allocation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/allocations")
async def get_allocations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_id: Optional[int] = None,
    room_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all allocations"""
    service = HostelService(db)
    from app.db.models.hostel import AllocationStatus
    status_enum = AllocationStatus(status) if status else None
    allocations = await service.get_all_allocations(skip, limit, block_id, room_id, status_enum)
    return {"allocations": allocations, "total": len(allocations), "page": skip // limit + 1, "page_size": limit}


@router.get("/allocations/student/{student_id}", response_model=HostelAllocationResponse)
async def get_student_allocation(
    student_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get allocation for a specific student"""
    service = HostelService(db)
    allocation = await service.get_allocation_by_student(student_id, active_only)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.put("/allocations/{allocation_id}", response_model=HostelAllocationResponse)
async def update_allocation(
    allocation_id: int,
    allocation_update: HostelAllocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update allocation information"""
    service = HostelService(db)
    allocation = await service.update_allocation(allocation_id, allocation_update)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.post("/allocations/{allocation_id}/vacate")
async def vacate_allocation(
    allocation_id: int,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vacate student from hostel"""
    service = HostelService(db)
    allocation = await service.vacate_allocation(allocation_id, reason)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return {"message": "Student vacated successfully", "allocation": allocation}


@router.post("/allocations/{allocation_id}/transfer")
async def transfer_allocation(
    allocation_id: int,
    new_room_id: int,
    new_bed_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer student to new room"""
    service = HostelService(db)
    try:
        allocation = await service.transfer_allocation(allocation_id, new_room_id, new_bed_id)
        return {"message": "Transfer successful", "allocation": allocation}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Maintenance Endpoints ====================

@router.post("/maintenance", response_model=MaintenanceRequestResponse)
async def create_maintenance_request(
    request: MaintenanceRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create maintenance request"""
    service = HostelService(db)
    return await service.create_maintenance_request(request, current_user.id)


@router.get("/maintenance", response_model=MaintenanceRequestListResponse)
async def get_maintenance_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    room_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all maintenance requests"""
    service = HostelService(db)
    from app.db.models.hostel import MaintenanceStatus
    status_enum = MaintenanceStatus(status) if status else None
    requests = await service.get_all_maintenance_requests(skip, limit, room_id, status_enum, priority)
    return {"requests": requests, "total": len(requests), "page": skip // limit + 1, "page_size": limit}


@router.get("/maintenance/{request_id}")
async def get_maintenance_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance request by ID"""
    service = HostelService(db)
    request = await service.get_maintenance_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return request


@router.put("/maintenance/{request_id}", response_model=MaintenanceRequestResponse)
async def update_maintenance_request(
    request_id: int,
    request_update: MaintenanceRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance request"""
    service = HostelService(db)
    request = await service.update_maintenance_request(request_id, request_update)
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return request


# ==================== Hostel Fee Endpoints ====================

@router.post("/fees", response_model=HostelFeeResponse)
async def create_hostel_fee(
    fee: HostelFeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create hostel fee structure"""
    service = HostelService(db)
    return await service.create_hostel_fee(fee)


@router.get("/fees/block/{block_id}")
async def get_block_fees(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all fees for a block"""
    service = HostelService(db)
    return await service.get_hostel_fees_by_block(block_id)


@router.post("/payments")
async def create_hostel_fee_payment(
    payment: HostelFeePaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record hostel fee payment"""
    service = HostelService(db)
    return await service.create_hostel_fee_payment(
        allocation_id=payment.allocation_id,
        fee_id=payment.hostel_fee_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        notes=payment.notes
    )


# ==================== Analytics Endpoints ====================

@router.get("/summary", response_model=HostelSummaryResponse)
async def get_hostel_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hostel summary statistics"""
    service = HostelService(db)
    return await service.get_hostel_summary()


@router.get("/maintenance/pending/count")
async def get_pending_maintenance_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of pending maintenance requests"""
    service = HostelService(db)
    count = await service.get_pending_maintenance_count()
    return {"pending_count": count}
