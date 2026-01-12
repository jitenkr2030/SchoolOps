"""
Hostel Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class BlockTypeEnum(str, Enum):
    BOYS = "boys"
    GIRLS = "girls"
    MIXED = "mixed"


class RoomTypeEnum(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    DORMITORY = "dormitory"


class AllocationStatusEnum(str, Enum):
    ACTIVE = "active"
    TEMPORARY = "temporary"
    VACATED = "vacated"
    TRANSFERRED = "transferred"


class MaintenanceStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MaintenancePriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


# ==================== Hostel Block Schemas ====================

class HostelBlockBase(BaseModel):
    """Base schema for hostel block"""
    name: str = Field(..., min_length=1, max_length=100)
    block_code: Optional[str] = Field(None, min_length=1, max_length=20)
    block_type: BlockTypeEnum
    contact_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    description: Optional[str] = None


class HostelBlockCreate(HostelBlockBase):
    """Schema for creating hostel block"""
    warden_id: Optional[int] = None
    assistant_warden_id: Optional[int] = None


class HostelBlockUpdate(BaseModel):
    """Schema for updating hostel block"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    block_code: Optional[str] = Field(None, min_length=1, max_length=20)
    block_type: Optional[BlockTypeEnum] = None
    warden_id: Optional[int] = None
    assistant_warden_id: Optional[int] = None
    contact_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class HostelBlockResponse(HostelBlockBase):
    """Schema for hostel block response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    total_rooms: int
    total_capacity: int
    warden_id: Optional[int] = None
    assistant_warden_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class HostelBlockWithDetailsResponse(HostelBlockResponse):
    """Schema for block with additional details"""
    warden_name: Optional[str] = None
    assistant_warden_name: Optional[str] = None
    current_occupancy: int = 0
    available_beds: int = 0
    occupancy_percentage: float = 0.0
    rooms_count: int = 0


# ==================== Room Schemas ====================

class RoomBase(BaseModel):
    """Base schema for room"""
    room_number: str = Field(..., min_length=1, max_length=20)
    floor: int = Field(default=1, ge=1)
    room_type: RoomTypeEnum
    capacity: int = Field(..., gt=0)
    bed_count: Optional[int] = None
    is_ac_available: bool = False
    is_attached_bathroom: bool = False
    amenities: Optional[str] = None
    description: Optional[str] = None


class RoomCreate(RoomBase):
    """Schema for creating room"""
    block_id: int


class RoomUpdate(BaseModel):
    """Schema for updating room"""
    room_number: Optional[str] = Field(None, min_length=1, max_length=20)
    floor: Optional[int] = Field(None, ge=1)
    room_type: Optional[RoomTypeEnum] = None
    capacity: Optional[int] = Field(None, gt=0)
    bed_count: Optional[int] = None
    is_ac_available: Optional[bool] = None
    is_attached_bathroom: Optional[bool] = None
    amenities: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RoomResponse(RoomBase):
    """Schema for room response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    block_id: int
    current_occupancy: int
    status: str
    created_at: datetime
    updated_at: datetime


class RoomWithDetailsResponse(RoomResponse):
    """Schema for room with bed details"""
    block_name: Optional[str] = None
    block_type: BlockTypeEnum
    beds: List[BedResponse] = []
    available_beds: int = 0


# ==================== Bed Schemas ====================

class BedBase(BaseModel):
    """Base schema for bed"""
    bed_number: str = Field(..., min_length=1, max_length=20)
    bed_position: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class BedCreate(BedBase):
    """Schema for creating bed"""
    room_id: int


class BedResponse(BedBase):
    """Schema for bed response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    is_occupied: bool


# ==================== Hostel Allocation Schemas ====================

class HostelAllocationBase(BaseModel):
    """Base schema for hostel allocation"""
    allocation_type: str = Field(default="regular")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reason_for_leaving: Optional[str] = None
    notes: Optional[str] = None


class HostelAllocationCreate(HostelAllocationBase):
    """Schema for creating hostel allocation"""
    student_id: int
    room_id: int
    bed_id: Optional[int] = None
    parent_consent: bool = False


class HostelAllocationUpdate(BaseModel):
    """Schema for updating hostel allocation"""
    room_id: Optional[int] = None
    bed_id: Optional[int] = None
    allocation_type: Optional[str] = None
    status: Optional[AllocationStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reason_for_leaving: Optional[str] = None
    notes: Optional[str] = None


class HostelAllocationResponse(HostelAllocationBase):
    """Schema for hostel allocation response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    student_id: int
    room_id: int
    bed_id: Optional[int] = None
    status: AllocationStatusEnum
    parent_consent: bool
    consent_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class HostelAllocationWithDetailsResponse(HostelAllocationResponse):
    """Schema for allocation with full details"""
    student_name: Optional[str] = None
    room_number: Optional[str] = None
    bed_number: Optional[str] = None
    block_name: Optional[str] = None
    block_type: BlockTypeEnum


# ==================== Maintenance Request Schemas ====================

class MaintenanceRequestBase(BaseModel):
    """Base schema for maintenance request"""
    category: str = Field(..., min_length=1, max_length=50)
    priority: MaintenancePriorityEnum = MaintenancePriorityEnum.MEDIUM
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    images: Optional[str] = None


class MaintenanceRequestCreate(MaintenanceRequestBase):
    """Schema for creating maintenance request"""
    room_id: int


class MaintenanceRequestUpdate(BaseModel):
    """Schema for updating maintenance request"""
    priority: Optional[MaintenancePriorityEnum] = None
    status: Optional[MaintenanceStatusEnum] = None
    assigned_to_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None


class MaintenanceRequestResponse(MaintenanceRequestBase):
    """Schema for maintenance request response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    requested_by_id: int
    assigned_to_id: Optional[int] = None
    status: MaintenanceStatusEnum
    assigned_date: Optional[datetime] = None
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class MaintenanceRequestWithDetailsResponse(MaintenanceRequestResponse):
    """Schema for request with additional details"""
    room_number: Optional[str] = None
    block_name: Optional[str] = None
    requested_by_name: Optional[str] = None
    assigned_to_name: Optional[str] = None


# ==================== Hostel Fee Schemas ====================

class HostelFeeBase(BaseModel):
    """Base schema for hostel fee"""
    room_type: RoomTypeEnum
    fee_type: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    mess_charge: float = 0.0
    description: Optional[str] = None


class HostelFeeCreate(HostelFeeBase):
    """Schema for creating hostel fee"""
    block_id: int


class HostelFeeUpdate(BaseModel):
    """Schema for updating hostel fee"""
    room_type: Optional[RoomTypeEnum] = None
    fee_type: Optional[str] = Field(None, min_length=1, max_length=50)
    amount: Optional[float] = Field(None, gt=0)
    mess_charge: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class HostelFeeResponse(HostelFeeBase):
    """Schema for hostel fee response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    block_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== Hostel Payment Schemas ====================

class HostelFeePaymentCreate(BaseModel):
    """Schema for creating hostel fee payment"""
    allocation_id: int
    hostel_fee_id: int
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class HostelFeePaymentResponse(BaseModel):
    """Schema for hostel fee payment response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    allocation_id: int
    hostel_fee_id: int
    amount: float
    payment_date: datetime
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    receipt_number: Optional[str] = None


# ==================== List/Pagination Schemas ====================

class HostelBlockListResponse(BaseModel):
    """Schema for block list response"""
    blocks: List[HostelBlockResponse]
    total: int
    page: int
    page_size: int


class RoomListResponse(BaseModel):
    """Schema for room list response"""
    rooms: List[RoomResponse]
    total: int
    page: int
    page_size: int


class MaintenanceRequestListResponse(BaseModel):
    """Schema for maintenance request list"""
    requests: List[MaintenanceRequestResponse]
    total: int
    page: int
    page_size: int


# ==================== Availability Schemas ====================

class RoomAvailabilityResponse(BaseModel):
    """Schema for room availability"""
    room_id: int
    room_number: str
    block_id: int
    block_name: str
    block_type: BlockTypeEnum
    floor: int
    room_type: RoomTypeEnum
    capacity: int
    current_occupancy: int
    available_beds: int
    is_ac_available: bool
    amenities: Optional[str] = None


class BlockAvailabilityResponse(BaseModel):
    """Schema for block availability summary"""
    block_id: int
    block_name: str
    block_type: BlockTypeEnum
    total_rooms: int
    total_capacity: int
    current_occupancy: int
    available_beds: int
    occupancy_percentage: float
    rooms: List[RoomAvailabilityResponse]


# ==================== Analytics Schemas ====================

class HostelSummaryResponse(BaseModel):
    """Schema for hostel summary"""
    total_blocks: int
    active_blocks: int
    total_rooms: int
    total_capacity: int
    total_occupancy: int
    overall_occupancy_percentage: float
    total_boys_occupancy: int
    total_girls_occupancy: int
    pending_maintenance_requests: int
    available_beds: int
