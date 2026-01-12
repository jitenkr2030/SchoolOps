"""
Hostel Management Database Models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class BlockType(str, enum.Enum):
    BOYS = "boys"
    GIRLS = "girls"
    MIXED = "mixed"


class RoomType(str, enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    DORMITORY = "dormitory"


class AllocationStatus(str, enum.Enum):
    ACTIVE = "active"
    TEMPORARY = "temporary"
    VACATED = "vacated"
    TRANSFERRED = "transferred"


class MaintenanceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MaintenancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class HostelBase(Base):
    """Abstract base class for hostel models"""
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HostelBlock(HostelBase):
    """Hostel building/block model"""
    __tablename__ = "hostel_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    block_code = Column(String(20), unique=True, index=True)
    block_type = Column(SQLEnum(BlockType), nullable=False)
    total_rooms = Column(Integer, default=0)
    total_capacity = Column(Integer, default=0)
    warden_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assistant_warden_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contact_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    warden = relationship("User", foreign_keys=[warden_id], back_populates="warden_of_blocks")
    assistant_warden = relationship("User", foreign_keys=[assistant_warden_id])
    rooms = relationship("Room", back_populates="block")
    
    def __repr__(self):
        return f"<HostelBlock {self.name}>"


class Room(HostelBase):
    """Room model within hostel blocks"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("hostel_blocks.id"), nullable=False)
    room_number = Column(String(20), nullable=False)
    floor = Column(Integer, default=1)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    bed_count = Column(Integer, default=0)
    is_ac_available = Column(Boolean, default=False)
    is_attached_bathroom = Column(Boolean, default=False)
    amenities = Column(Text, nullable=True)  # JSON string of amenities
    status = Column(String(20), default="available")  # available, full, maintenance
    description = Column(Text, nullable=True)
    
    # Relationships
    block = relationship("HostelBlock", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")
    allocations = relationship("HostelAllocation", back_populates="room")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="room")
    
    def __repr__(self):
        return f"<Room {self.room_number} in {self.block_id}>"


class Bed(HostelBase):
    """Individual bed model within rooms"""
    __tablename__ = "beds"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    bed_number = Column(String(20), nullable=False)
    bed_position = Column(String(50), nullable=True)  # window, door, corner
    is_occupied = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    room = relationship("Room", back_populates="beds")
    allocations = relationship("HostelAllocation", back_populates="bed")
    
    def __repr__(self):
        return f"<Bed {self.bed_number}>"


class HostelAllocation(HostelBase):
    """Student hostel allocation model"""
    __tablename__ = "hostel_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    allocation_type = Column(String(20), default="regular")  # regular, temporary, emergency
    status = Column(SQLEnum(AllocationStatus), default=AllocationStatus.ACTIVE)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    reason_for_leaving = Column(Text, nullable=True)
    parent_consent = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="hostel_allocations")
    room = relationship("Room", back_populates="allocations")
    bed = relationship("Bed", back_populates="allocations")
    
    def __repr__(self):
        return f"<HostelAllocation for Student {self.student_id}>"


class MaintenanceRequest(HostelBase):
    """Hostel maintenance request model"""
    __tablename__ = "maintenance_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # electrical, plumbing, furniture, cleaning
    priority = Column(SQLEnum(MaintenancePriority), default=MaintainmentPriority.MEDIUM)
    status = Column(SQLEnum(MaintenanceStatus), default=MaintainmentStatus.PENDING)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    images = Column(Text, nullable=True)  # JSON array of image paths
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    started_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Relationships
    room = relationship("Room", back_populates="maintenance_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f"<MaintenanceRequest {self.title}>"


class HostelFee(HostelBase):
    """Hostel fee structure model"""
    __tablename__ = "hostel_fees"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("hostel_blocks.id"), nullable=False)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    fee_type = Column(String(50), nullable=False)  # monthly, quarterly, annually
    amount = Column(Float, nullable=False)
    mess_charge = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    block = relationship("HostelBlock")
    payments = relationship("HostelFeePayment", back_populates="hostel_fee")
    
    def __repr__(self):
        return f"<HostelFee {self.amount}>"


class HostelFeePayment(HostelBase):
    """Hostel fee payment records"""
    __tablename__ = "hostel_fee_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(Integer, ForeignKey("hostel_allocations.id"), nullable=False)
    hostel_fee_id = Column(Integer, ForeignKey("hostel_fees.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    receipt_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    allocation = relationship("HostelAllocation")
    hostel_fee = relationship("HostelFee", back_populates="payments")
    
    def __repr__(self):
        return f"<HostelFeePayment {self.amount}>"
