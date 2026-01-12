"""
Hostel Service - Business Logic
"""
from typing import Optional, List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.db.models.hostel import (
    HostelBlock, Room, Bed, HostelAllocation,
    HostelFee, HostelFeePayment, MaintenanceRequest,
    BlockType, RoomType, AllocationStatus, MaintenanceStatus
)
from app.schema.hostel_schema import (
    HostelBlockCreate, HostelBlockUpdate, RoomCreate, RoomUpdate,
    HostelAllocationCreate, HostelAllocationUpdate,
    MaintenanceRequestCreate, MaintenanceRequestUpdate,
    HostelFeeCreate
)


class HostelService:
    """Service class for hostel management operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ==================== Block Operations ====================
    
    async def create_block(self, block_data: HostelBlockCreate) -> HostelBlock:
        """Create a new hostel block"""
        block = HostelBlock(**block_data.model_dump())
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh(block)
        return block
    
    async def get_block(self, block_id: int) -> Optional[HostelBlock]:
        """Get block by ID"""
        result = await self.session.execute(
            select(HostelBlock).where(HostelBlock.id == block_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_blocks(
        self,
        skip: int = 0,
        limit: int = 100,
        block_type: Optional[BlockType] = None,
        active_only: bool = False
    ) -> List[HostelBlock]:
        """Get all blocks with optional filtering"""
        query = select(HostelBlock)
        if block_type:
            query = query.where(HostelBlock.block_type == block_type)
        if active_only:
            query = query.where(HostelBlock.is_active == True)
        query = query.offset(skip).limit(limit).order_by(HostelBlock.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_block(
        self,
        block_id: int,
        block_data: HostelBlockUpdate
    ) -> Optional[HostelBlock]:
        """Update block information"""
        block = await self.get_block(block_id)
        if not block:
            return None
        
        update_data = block_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(block, field, value)
        
        await self.session.commit()
        await self.session.refresh(block)
        return block
    
    async def delete_block(self, block_id: int) -> bool:
        """Delete a block"""
        block = await self.get_block(block_id)
        if not block:
            return False
        
        await self.session.delete(block)
        await self.session.commit()
        return True
    
    async def get_block_availability(self, block_id: int) -> dict:
        """Get block availability statistics"""
        block = await self.get_block(block_id)
        if not block:
            return None
        
        # Count rooms and occupancy
        rooms_result = await self.session.execute(
            select(
                func.count(Room.id).label('total_rooms'),
                func.sum(Room.capacity).label('total_capacity'),
                func.sum(Room.current_occupancy).label('total_occupancy')
            ).where(Room.block_id == block_id)
        )
        rooms_data = rooms_result.one()
        
        return {
            'block_id': block.id,
            'block_name': block.name,
            'block_type': block.block_type,
            'total_rooms': rooms_data.total_rooms or 0,
            'total_capacity': rooms_data.total_capacity or 0,
            'current_occupancy': rooms_data.total_occupancy or 0,
            'available_beds': (rooms_data.total_capacity or 0) - (rooms_data.total_occupancy or 0),
            'occupancy_percentage': round(
                ((rooms_data.total_occupancy or 0) / (rooms_data.total_capacity or 1)) * 100, 2
            )
        }
    
    # ==================== Room Operations ====================
    
    async def create_room(self, room_data: RoomCreate) -> Room:
        """Create a new room"""
        room = Room(**room_data.model_dump())
        self.session.add(room)
        await self.session.flush()
        
        # Auto-create beds based on bed_count or capacity
        bed_count = room_data.bed_count or room_data.capacity
        for i in range(1, bed_count + 1):
            bed = Bed(room_id=room.id, bed_number=str(i))
            self.session.add(bed)
        
        room.bed_count = bed_count
        
        await self.session.commit()
        await self.session.refresh(room)
        return room
    
    async def get_room(self, room_id: int) -> Optional[Room]:
        """Get room by ID"""
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.beds))
            .where(Room.id == room_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_rooms(
        self,
        skip: int = 0,
        limit: int = 100,
        block_id: Optional[int] = None,
        room_type: Optional[RoomType] = None,
        status: Optional[str] = None
    ) -> List[Room]:
        """Get all rooms with filtering"""
        query = select(Room)
        if block_id:
            query = query.where(Room.block_id == block_id)
        if room_type:
            query = query.where(Room.room_type == room_type)
        if status:
            query = query.where(Room.status == status)
        query = query.offset(skip).limit(limit).order_by(Room.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_available_rooms(
        self,
        block_id: Optional[int] = None,
        block_type: Optional[BlockType] = None,
        room_type: Optional[RoomType] = None,
        min_beds: int = 1
    ) -> List[Room]:
        """Get available rooms with available beds"""
        query = select(Room).where(Room.current_occupancy < Room.capacity)
        
        if block_id:
            query = query.where(Room.block_id == block_id)
        if room_type:
            query = query.where(Room.room_type == room_type)
        
        query = query.order_by(Room.current_occupancy.asc())
        result = await self.session.execute(query)
        rooms = result.scalars().all()
        
        # Filter by block type if needed
        if block_type:
            rooms = [r for r in rooms if r.block.block_type == block_type]
        
        return rooms
    
    async def update_room(
        self,
        room_id: int,
        room_data: RoomUpdate
    ) -> Optional[Room]:
        """Update room information"""
        room = await self.get_room(room_id)
        if not room:
            return None
        
        update_data = room_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        await self.session.commit()
        await self.session.refresh(room)
        return room
    
    async def delete_room(self, room_id: int) -> bool:
        """Delete a room"""
        room = await self.get_room(room_id)
        if not room:
            return False
        
        await self.session.delete(room)
        await self.session.commit()
        return True
    
    async def add_bed_to_room(self, room_id: int, bed_data: dict) -> Optional[Bed]:
        """Add a bed to existing room"""
        room = await self.get_room(room_id)
        if not room:
            return None
        
        if room.current_occupancy >= room.capacity:
            raise ValueError("Room has reached maximum capacity")
        
        # Get next bed number
        result = await self.session.execute(
            select(func.max(Bed.id)).where(Bed.room_id == room_id)
        )
        max_id = result.scalar() or 0
        
        bed = Bed(room_id=room_id, bed_number=str(max_id + 1), **bed_data)
        self.session.add(bed)
        
        # Update room bed count and occupancy
        room.bed_count = (room.bed_count or 0) + 1
        
        await self.session.commit()
        await self.session.refresh(bed)
        return bed
    
    # ==================== Bed Operations ====================
    
    async def get_bed(self, bed_id: int) -> Optional[Bed]:
        """Get bed by ID"""
        result = await self.session.execute(
            select(Bed).where(Bed.id == bed_id)
        )
        return result.scalar_one_or_none()
    
    async def get_available_beds(self, room_id: int) -> List[Bed]:
        """Get available beds in a room"""
        result = await self.session.execute(
            select(Bed).where(
                and_(Bed.room_id == room_id, Bed.is_occupied == False)
            )
        )
        return list(result.scalars().all())
    
    # ==================== Hostel Allocation Operations ====================
    
    async def create_allocation(self, allocation_data: HostelAllocationCreate) -> HostelAllocation:
        """Create hostel allocation for a student"""
        # Get room and validate capacity
        room = await self.get_room(allocation_data.room_id)
        if not room:
            raise ValueError("Room not found")
        
        if room.current_occupancy >= room.capacity:
            raise ValueError("Room is full")
        
        # Validate block type with student gender
        if allocation_data.student_id and room.block.block_type != BlockType.MIXED:
            # Would need to check student gender here
            pass  # Student gender check would go here
        
        allocation = HostelAllocation(**allocation_data.model_dump())
        self.session.add(allocation)
        await self.session.flush()
        
        # Update room occupancy
        room.current_occupancy += 1
        if room.current_occupancy >= room.capacity:
            room.status = "full"
        
        # Update bed if specified
        if allocation_data.bed_id:
            bed = await self.get_bed(allocation_data.bed_id)
            if bed:
                bed.is_occupied = True
        
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    async def get_allocation(self, allocation_id: int) -> Optional[HostelAllocation]:
        """Get allocation by ID"""
        result = await self.session.execute(
            select(HostelAllocation)
            .options(selectinload(HostelAllocation.room))
            .where(HostelAllocation.id == allocation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_allocation_by_student(
        self,
        student_id: int,
        active_only: bool = True
    ) -> Optional[HostelAllocation]:
        """Get active allocation for a student"""
        query = select(HostelAllocation).where(
            HostelAllocation.student_id == student_id
        )
        if active_only:
            query = query.where(
                HostelAllocation.status.in_([
                    AllocationStatus.ACTIVE,
                    AllocationStatus.TEMPORARY
                ])
            )
        query = query.order_by(HostelAllocation.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_allocations(
        self,
        skip: int = 0,
        limit: int = 100,
        block_id: Optional[int] = None,
        room_id: Optional[int] = None,
        status: Optional[AllocationStatus] = None
    ) -> List[HostelAllocation]:
        """Get all allocations with filtering"""
        query = select(HostelAllocation)
        
        if block_id:
            query = query.join(Room).where(Room.block_id == block_id)
        if room_id:
            query = query.where(HostelAllocation.room_id == room_id)
        if status:
            query = query.where(HostelAllocation.status == status)
        
        query = query.offset(skip).limit(limit).order_by(HostelAllocation.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_allocation(
        self,
        allocation_id: int,
        allocation_data: HostelAllocationUpdate
    ) -> Optional[HostelAllocation]:
        """Update allocation information"""
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            return None
        
        update_data = allocation_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(allocation, field, value)
        
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    async def vacate_allocation(
        self,
        allocation_id: int,
        reason: Optional[str] = None
    ) -> Optional[HostelAllocation]:
        """Vacate a student from hostel"""
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            return None
        
        allocation.status = AllocationStatus.VACATED
        allocation.end_date = datetime.utcnow()
        allocation.reason_for_leaving = reason
        
        # Update room occupancy
        room = await self.get_room(allocation.room_id)
        if room:
            room.current_occupancy = max(0, room.current_occupancy - 1)
            if room.status == "full":
                room.status = "available"
        
        # Free up bed
        if allocation.bed_id:
            bed = await self.get_bed(allocation.bed_id)
            if bed:
                bed.is_occupied = False
        
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    async def transfer_allocation(
        self,
        allocation_id: int,
        new_room_id: int,
        new_bed_id: Optional[int] = None
    ) -> Optional[HostelAllocation]:
        """Transfer student to new room"""
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            return None
        
        # Vacate current room
        old_room = await self.get_room(allocation.room_id)
        if old_room:
            old_room.current_occupancy = max(0, old_room.current_occupancy - 1)
            if old_room.status == "full":
                old_room.status = "available"
        
        if allocation.bed_id:
            old_bed = await self.get_bed(allocation.bed_id)
            if old_bed:
                old_bed.is_occupied = False
        
        # Allocate new room
        new_room = await self.get_room(new_room_id)
        if not new_room:
            raise ValueError("New room not found")
        
        if new_room.current_occupancy >= new_room.capacity:
            raise ValueError("New room is full")
        
        allocation.room_id = new_room_id
        allocation.bed_id = new_bed_id
        allocation.status = AllocationStatus.TRANSFERRED
        
        new_room.current_occupancy += 1
        if new_room.current_occupancy >= new_room.capacity:
            new_room.status = "full"
        
        if new_bed_id:
            new_bed = await self.get_bed(new_bed_id)
            if new_bed:
                new_bed.is_occupied = True
        
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    # ==================== Maintenance Request Operations ====================
    
    async def create_maintenance_request(
        self,
        request_data: MaintenanceRequestCreate,
        requested_by_id: int
    ) -> MaintenanceRequest:
        """Create maintenance request"""
        request = MaintenanceRequest(
            **request_data.model_dump(),
            requested_by_id=requested_by_id
        )
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request
    
    async def get_maintenance_request(self, request_id: int) -> Optional[MaintenanceRequest]:
        """Get maintenance request by ID"""
        result = await self.session.execute(
            select(MaintenanceRequest)
            .where(MaintenanceRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_maintenance_requests(
        self,
        skip: int = 0,
        limit: int = 100,
        room_id: Optional[int] = None,
        status: Optional[MaintenanceStatus] = None,
        priority: Optional[str] = None
    ) -> List[MaintenanceRequest]:
        """Get all maintenance requests"""
        query = select(MaintenanceRequest)
        
        if room_id:
            query = query.where(MaintenanceRequest.room_id == room_id)
        if status:
            query = query.where(MaintenanceRequest.status == status)
        if priority:
            query = query.where(MaintenanceRequest.priority == priority)
        
        query = query.offset(skip).limit(limit).order_by(
            MaintenanceRequest.priority == "emergency",
            MaintenanceRequest.created_at.desc()
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_maintenance_request(
        self,
        request_id: int,
        request_data: MaintenanceRequestUpdate
    ) -> Optional[MaintenanceRequest]:
        """Update maintenance request"""
        request = await self.get_maintenance_request(request_id)
        if not request:
            return None
        
        update_data = request_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)
        
        # Update timestamps based on status changes
        if request.status == MaintenanceStatus.IN_PROGRESS and not request.started_date:
            request.started_date = datetime.utcnow()
        if request.status == MaintenanceStatus.RESOLVED and not request.completed_date:
            request.completed_date = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(request)
        return request
    
    async def get_pending_maintenance_count(self) -> int:
        """Get count of pending maintenance requests"""
        result = await self.session.execute(
            select(func.count(MaintenanceRequest.id))
            .where(MaintenanceRequest.status == MaintenanceStatus.PENDING)
        )
        return result.scalar() or 0
    
    # ==================== Hostel Fee Operations ====================
    
    async def create_hostel_fee(self, fee_data: HostelFeeCreate) -> HostelFee:
        """Create hostel fee structure"""
        fee = HostelFee(**fee_data.model_dump())
        self.session.add(fee)
        await self.session.commit()
        await self.session.refresh(fee)
        return fee
    
    async def get_hostel_fees_by_block(self, block_id: int) -> List[HostelFee]:
        """Get all fees for a block"""
        result = await self.session.execute(
            select(HostelFee)
            .where(HostelFee.block_id == block_id)
            .order_by(HostelFee.created_at.desc())
        )
        return list(result.scalars().all())
    
    # ==================== Hostel Payment Operations ====================
    
    async def create_hostel_fee_payment(
        self,
        allocation_id: int,
        fee_id: int,
        amount: float,
        payment_method: Optional[str] = None,
        transaction_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> HostelFeePayment:
        """Record hostel fee payment"""
        payment = HostelFeePayment(
            allocation_id=allocation_id,
            hostel_fee_id=fee_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            notes=notes
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    # ==================== Analytics Operations ====================
    
    async def get_hostel_summary(self) -> dict:
        """Get hostel summary statistics"""
        # Block statistics
        blocks_result = await self.session.execute(
            select(
                func.count(HostelBlock.id).label('total_blocks'),
                func.sum(HostelBlock.is_active == True).label('active_blocks')
            )
        )
        blocks_data = blocks_result.one()
        
        # Room and occupancy statistics
        rooms_result = await self.session.execute(
            select(
                func.count(Room.id).label('total_rooms'),
                func.sum(Room.capacity).label('total_capacity'),
                func.sum(Room.current_occupancy).label('total_occupancy')
            )
        )
        rooms_data = rooms_result.one()
        
        # Block type specific occupancy
        boys_result = await self.session.execute(
            select(func.sum(Room.current_occupancy))
            .join(HostelBlock)
            .where(HostelBlock.block_type == BlockType.BOYS)
        )
        girls_result = await self.session.execute(
            select(func.sum(Room.current_occupancy))
            .join(HostelBlock)
            .where(HostelBlock.block_type == BlockType.GIRLS)
        )
        
        pending_maintenance = await self.get_pending_maintenance_count()
        
        total_capacity = rooms_data.total_capacity or 0
        total_occupancy = rooms_data.total_occupancy or 0
        
        return {
            'total_blocks': blocks_data.total_blocks or 0,
            'active_blocks': blocks_data.active_blocks or 0,
            'total_rooms': rooms_data.total_rooms or 0,
            'total_capacity': total_capacity,
            'total_occupancy': total_occupancy,
            'overall_occupancy_percentage': round(
                (total_occupancy / total_capacity * 100) if total_capacity > 0 else 0, 2
            ),
            'total_boys_occupancy': boys_result.scalar() or 0,
            'total_girls_occupancy': girls_result.scalar() or 0,
            'pending_maintenance_requests': pending_maintenance,
            'available_beds': total_capacity - total_occupancy
        }
    
    async def get_block_occupancy_trends(self, days: int = 30) -> List[dict]:
        """Get occupancy trends (placeholder for historical data)"""
        # This would require a separate occupancy tracking table
        # For now, return current state
        summary = await self.get_hostel_summary()
        return [summary]
