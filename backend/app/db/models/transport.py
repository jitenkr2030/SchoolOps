"""
Transport Management Database Models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Enum as SQLEnum, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class TransportStatus(str, enum.Enum):
    ALLOCATED = "allocated"
    PENDING = "pending"
    CANCELLED = "cancelled"


class TransportBase(Base):
    """Abstract base class for transport models"""
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Vehicle(TransportBase):
    """Vehicle model for buses and transport vehicles"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(50), unique=True, index=True, nullable=False)
    vehicle_number = Column(String(50), unique=True, nullable=False)  # Alternate identification
    vehicle_type = Column(String(50), nullable=False)  # Bus, Van, Mini-bus
    capacity = Column(Integer, nullable=False)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_gps_update = Column(DateTime, nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    helper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(VehicleStatus), default=VehicleStatus.ACTIVE)
    insurance_expiry = Column(DateTime, nullable=True)
    fitness_expiry = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    driver = relationship("User", foreign_keys=[driver_id], back_populates="vehicles_as_driver")
    helper = relationship("User", foreign_keys=[helper_id], back_populates="vehicles_as_helper")
    routes = relationship("Route", back_populates="vehicle")
    allocations = relationship("TransportAllocation", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle {self.registration_number}>"


class Route(TransportBase):
    """Route model for transport routes"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    route_code = Column(String(20), unique=True, index=True)
    description = Column(Text, nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    distance_km = Column(Float, nullable=True)
    estimated_time_minutes = Column(Integer, nullable=True)
    morning_pickup_time = Column(Time, nullable=True)
    evening_drop_time = Column(Time, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route", order_by="RouteStop.sequence_order")
    allocations = relationship("TransportAllocation", back_populates="route")
    
    def __repr__(self):
        return f"<Route {self.name}>"


class RouteStop(TransportBase):
    """Route stop model for pickup/drop points"""
    __tablename__ = "route_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    stop_name = Column(String(100), nullable=False)
    stop_address = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    pickup_time = Column(Time, nullable=True)
    drop_time = Column(Time, nullable=True)
    distance_from_start = Column(Float, nullable=True)  # KM from route start
    
    # Relationships
    route = relationship("Route", back_populates="stops")
    pickup_allocations = relationship("TransportAllocation", foreign_keys="TransportAllocation.pickup_stop_id")
    dropoff_allocations = relationship("TransportAllocation", foreign_keys="TransportAllocation.dropoff_stop_id")
    
    def __repr__(self):
        return f"<RouteStop {self.stop_name}>"


class TransportAllocation(TransportBase):
    """Student transport allocation model"""
    __tablename__ = "transport_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    pickup_stop_id = Column(Integer, ForeignKey("route_stops.id"), nullable=True)
    dropoff_stop_id = Column(Integer, ForeignKey("route_stops.id"), nullable=True)
    pickup_time = Column(Time, nullable=True)
    dropoff_time = Column(Time, nullable=True)
    status = Column(SQLEnum(TransportStatus), default=TransportStatus.PENDING)
    transport_fee = Column(Float, default=0.0)
    fee_status = Column(String(20), default="unpaid")  # unpaid, partial, paid
    effective_from = Column(DateTime, nullable=True)
    effective_until = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="transport_allocations")
    route = relationship("Route", back_populates="allocations")
    vehicle = relationship("Vehicle", back_populates="allocations")
    pickup_stop = relationship("RouteStop", foreign_keys=[pickup_stop_id])
    dropoff_stop = relationship("RouteStop", foreign_keys=[dropoff_stop_id])
    
    def __repr__(self):
        return f"<TransportAllocation for Student {self.student_id}>"


class TransportFee(TransportBase):
    """Transport fee structure model"""
    __tablename__ = "transport_fees"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    fee_type = Column(String(50), nullable=False)  # monthly, quarterly, annually
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    route = relationship("Route")
    payments = relationship("TransportFeePayment", back_populates="transport_fee")
    
    def __repr__(self):
        return f"<TransportFee {self.amount} for Route {self.route_id}>"


class TransportFeePayment(TransportBase):
    """Transport fee payment records"""
    __tablename__ = "transport_fee_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(Integer, ForeignKey("transport_allocations.id"), nullable=False)
    transport_fee_id = Column(Integer, ForeignKey("transport_fees.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    receipt_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    allocation = relationship("TransportAllocation")
    transport_fee = relationship("TransportFee", back_populates="payments")
    
    def __repr__(self):
        return f"<TransportFeePayment {self.amount}>"
