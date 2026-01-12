"""
Transport Pydantic Schemas
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class VehicleStatusEnum(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class TransportStatusEnum(str, Enum):
    ALLOCATED = "allocated"
    PENDING = "pending"
    CANCELLED = "cancelled"


# ==================== Vehicle Schemas ====================

class VehicleBase(BaseModel):
    """Base schema for vehicle data"""
    registration_number: str = Field(..., min_length=3, max_length=50)
    vehicle_number: str = Field(..., min_length=3, max_length=50)
    vehicle_type: str = Field(..., min_length=2, max_length=50)
    capacity: int = Field(..., gt=0, le=100)
    description: Optional[str] = None


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle"""
    driver_id: Optional[int] = None
    helper_id: Optional[int] = None
    status: VehicleStatusEnum = VehicleStatusEnum.ACTIVE


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    registration_number: Optional[str] = Field(None, min_length=3, max_length=50)
    vehicle_number: Optional[str] = Field(None, min_length=3, max_length=50)
    vehicle_type: Optional[str] = Field(None, min_length=2, max_length=50)
    capacity: Optional[int] = Field(None, gt=0, le=100)
    driver_id: Optional[int] = None
    helper_id: Optional[int] = None
    status: Optional[VehicleStatusEnum] = None
    description: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    last_gps_update: Optional[datetime] = None
    driver_id: Optional[int] = None
    helper_id: Optional[int] = None
    status: VehicleStatusEnum
    insurance_expiry: Optional[datetime] = None
    fitness_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class VehicleWithDetailsResponse(VehicleResponse):
    """Schema for vehicle with relationships"""
    driver_name: Optional[str] = None
    helper_name: Optional[str] = None
    active_routes_count: int = 0
    current_allocations_count: int = 0


# ==================== GPS Update Schema ====================

class GPSUpdate(BaseModel):
    """Schema for GPS location update"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = None


class GPSUpdateResponse(BaseModel):
    """Response for GPS update"""
    vehicle_id: int
    latitude: float
    longitude: float
    updated_at: datetime
    message: str = "Location updated successfully"


# ==================== Route Schemas ====================

class RouteStopBase(BaseModel):
    """Base schema for route stop"""
    stop_name: str = Field(..., min_length=1, max_length=100)
    stop_address: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    pickup_time: Optional[time] = None
    drop_time: Optional[time] = None
    distance_from_start: Optional[float] = Field(None, ge=0)


class RouteStopCreate(RouteStopBase):
    """Schema for creating a route stop"""
    pass


class RouteStopResponse(RouteStopBase):
    """Schema for route stop response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    route_id: int
    created_at: datetime
    updated_at: datetime


class RouteBase(BaseModel):
    """Base schema for route"""
    name: str = Field(..., min_length=1, max_length=100)
    route_code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    distance_km: Optional[float] = Field(None, ge=0)
    estimated_time_minutes: Optional[int] = Field(None, ge=0)
    morning_pickup_time: Optional[time] = None
    evening_drop_time: Optional[time] = None


class RouteCreate(RouteBase):
    """Schema for creating a route"""
    vehicle_id: Optional[int] = None
    stops: Optional[List[RouteStopCreate]] = None


class RouteUpdate(BaseModel):
    """Schema for updating a route"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    route_code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    vehicle_id: Optional[int] = None
    distance_km: Optional[float] = Field(None, ge=0)
    estimated_time_minutes: Optional[int] = Field(None, ge=0)
    morning_pickup_time: Optional[time] = None
    evening_drop_time: Optional[time] = None
    is_active: Optional[bool] = None


class RouteResponse(RouteBase):
    """Schema for route response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    vehicle_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RouteWithStopsResponse(RouteResponse):
    """Schema for route with stops"""
    stops: List[RouteStopResponse] = []
    vehicle_details: Optional[VehicleResponse] = None
    total_allocations: int = 0


# ==================== Transport Allocation Schemas ====================

class TransportAllocationBase(BaseModel):
    """Base schema for transport allocation"""
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    notes: Optional[str] = None


class TransportAllocationCreate(TransportAllocationBase):
    """Schema for creating transport allocation"""
    student_id: int
    route_id: int
    vehicle_id: Optional[int] = None
    pickup_stop_id: Optional[int] = None
    dropoff_stop_id: Optional[int] = None
    pickup_time: Optional[time] = None
    dropoff_time: Optional[time] = None
    transport_fee: Optional[float] = 0.0


class TransportAllocationUpdate(BaseModel):
    """Schema for updating transport allocation"""
    route_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    pickup_stop_id: Optional[int] = None
    dropoff_stop_id: Optional[int] = None
    pickup_time: Optional[time] = None
    dropoff_time: Optional[time] = None
    status: Optional[TransportStatusEnum] = None
    transport_fee: Optional[float] = None
    notes: Optional[str] = None


class TransportAllocationResponse(TransportAllocationBase):
    """Schema for transport allocation response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    student_id: int
    route_id: int
    vehicle_id: Optional[int] = None
    pickup_stop_id: Optional[int] = None
    dropoff_stop_id: Optional[int] = None
    status: TransportStatusEnum
    fee_status: str
    created_at: datetime
    updated_at: datetime


class TransportAllocationWithDetailsResponse(TransportAllocationResponse):
    """Schema for allocation with full details"""
    student_name: Optional[str] = None
    route_name: Optional[str] = None
    vehicle_registration: Optional[str] = None
    pickup_stop_name: Optional[str] = None
    dropoff_stop_name: Optional[str] = None


# ==================== Transport Fee Schemas ====================

class TransportFeeBase(BaseModel):
    """Base schema for transport fee"""
    fee_type: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class TransportFeeCreate(TransportFeeBase):
    """Schema for creating transport fee"""
    route_id: int


class TransportFeeUpdate(BaseModel):
    """Schema for updating transport fee"""
    fee_type: Optional[str] = Field(None, min_length=1, max_length=50)
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TransportFeeResponse(TransportFeeBase):
    """Schema for transport fee response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    route_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== Payment Schemas ====================

class TransportFeePaymentCreate(BaseModel):
    """Schema for creating transport fee payment"""
    allocation_id: int
    transport_fee_id: int
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class TransportFeePaymentResponse(BaseModel):
    """Schema for transport fee payment response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    allocation_id: int
    transport_fee_id: int
    amount: float
    payment_date: datetime
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    receipt_number: Optional[str] = None


# ==================== List/Pagination Schemas ====================

class VehicleListResponse(BaseModel):
    """Schema for vehicle list response"""
    vehicles: List[VehicleResponse]
    total: int
    page: int
    page_size: int


class RouteListResponse(BaseModel):
    """Schema for route list response"""
    routes: List[RouteResponse]
    total: int
    page: int
    page_size: int


class TransportAllocationListResponse(BaseModel):
    """Schema for allocation list response"""
    allocations: List[TransportAllocationResponse]
    total: int
    page: int
    page_size: int


# ==================== Analytics Schemas ====================

class TransportUtilizationResponse(BaseModel):
    """Schema for transport utilization report"""
    vehicle_id: int
    vehicle_registration: str
    total_capacity: int
    current_allocations: int
    utilization_percentage: float
    available_seats: int


class TransportSummaryResponse(BaseModel):
    """Schema for transport summary"""
    total_vehicles: int
    active_vehicles: int
    vehicles_in_maintenance: int
    total_routes: int
    active_routes: int
    total_allocations: int
    active_allocations: int
    total_revenue_collected: float
    pending_fee_amount: float
