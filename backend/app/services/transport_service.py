"""
Transport Service - Business Logic
"""
from typing import Optional, List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, time

from app.db.models.transport import (
    Vehicle, Route, RouteStop, TransportAllocation,
    TransportFee, TransportFeePayment, VehicleStatus, TransportStatus
)
from app.schema.transport_schema import (
    VehicleCreate, VehicleUpdate, RouteCreate, RouteUpdate,
    TransportAllocationCreate, TransportAllocationUpdate,
    TransportFeeCreate, GPSUpdate
)


class TransportService:
    """Service class for transport management operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ==================== Vehicle Operations ====================
    
    async def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        """Create a new vehicle"""
        vehicle = Vehicle(**vehicle_data.model_dump())
        self.session.add(vehicle)
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle
    
    async def get_vehicle(self, vehicle_id: int) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        result = await self.session.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_vehicles(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[VehicleStatus] = None
    ) -> List[Vehicle]:
        """Get all vehicles with optional filtering"""
        query = select(Vehicle)
        if status:
            query = query.where(Vehicle.status == status)
        query = query.offset(skip).limit(limit).order_by(Vehicle.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_vehicle(
        self, 
        vehicle_id: int, 
        vehicle_data: VehicleUpdate
    ) -> Optional[Vehicle]:
        """Update vehicle information"""
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            return None
        
        update_data = vehicle_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle
    
    async def delete_vehicle(self, vehicle_id: int) -> bool:
        """Delete a vehicle"""
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            return False
        
        await self.session.delete(vehicle)
        await self.session.commit()
        return True
    
    async def update_gps_location(
        self, 
        vehicle_id: int, 
        gps_data: GPSUpdate
    ) -> Optional[Vehicle]:
        """Update vehicle GPS location"""
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            return None
        
        vehicle.current_latitude = gps_data.latitude
        vehicle.current_longitude = gps_data.longitude
        vehicle.last_gps_update = gps_data.timestamp or datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle
    
    async def get_vehicle_statistics(self) -> dict:
        """Get vehicle statistics"""
        result = await self.session.execute(
            select(
                func.count(Vehicle.id).label('total'),
                func.sum(Vehicle.status == VehicleStatus.ACTIVE).label('active'),
                func.sum(Vehicle.status == VehicleStatus.MAINTENANCE).label('maintenance')
            ).select_from(Vehicle)
        )
        row = result.one()
        return {
            'total_vehicles': row.total or 0,
            'active_vehicles': row.active or 0,
            'vehicles_in_maintenance': row.maintenance or 0
        }
    
    # ==================== Route Operations ====================
    
    async def create_route(self, route_data: RouteCreate) -> Route:
        """Create a new route with stops"""
        route_dict = route_data.model_dump(exclude={'stops'})
        route = Route(**route_dict)
        self.session.add(route)
        await self.session.flush()  # Get the route ID
        
        # Add stops if provided
        if route_data.stops:
            for stop_data in route_data.stops:
                stop = RouteStop(**stop_data.model_dump(), route_id=route.id)
                self.session.add(stop)
        
        await self.session.commit()
        await self.session.refresh(route)
        return route
    
    async def get_route(self, route_id: int) -> Optional[Route]:
        """Get route by ID with stops"""
        result = await self.session.execute(
            select(Route)
            .options(selectinload(Route.stops))
            .where(Route.id == route_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_routes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> List[Route]:
        """Get all routes"""
        query = select(Route)
        if active_only:
            query = query.where(Route.is_active == True)
        query = query.offset(skip).limit(limit).order_by(Route.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_routes_by_vehicle(self, vehicle_id: int) -> List[Route]:
        """Get all routes for a vehicle"""
        result = await self.session.execute(
            select(Route)
            .options(selectinload(Route.stops))
            .where(Route.vehicle_id == vehicle_id)
            .order_by(Route.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_route(
        self, 
        route_id: int, 
        route_data: RouteUpdate
    ) -> Optional[Route]:
        """Update route information"""
        route = await self.get_route(route_id)
        if not route:
            return None
        
        update_data = route_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(route, field, value)
        
        await self.session.commit()
        await self.session.refresh(route)
        return route
    
    async def delete_route(self, route_id: int) -> bool:
        """Delete a route"""
        route = await self.get_route(route_id)
        if not route:
            return False
        
        await self.session.delete(route)
        await self.session.commit()
        return True
    
    async def add_stop_to_route(
        self, 
        route_id: int, 
        stop_data: dict
    ) -> Optional[RouteStop]:
        """Add a stop to existing route"""
        route = await self.get_route(route_id)
        if not route:
            return None
        
        # Get current max sequence order
        result = await self.session.execute(
            select(func.max(RouteStop.sequence_order))
            .where(RouteStop.route_id == route_id)
        )
        max_order = result.scalar() or 0
        
        stop = RouteStop(**stop_data, route_id=route_id, sequence_order=max_order + 1)
        self.session.add(stop)
        await self.session.commit()
        await self.session.refresh(stop)
        return stop
    
    # ==================== Transport Allocation Operations ====================
    
    async def create_allocation(
        self, 
        allocation_data: TransportAllocationCreate
    ) -> TransportAllocation:
        """Create transport allocation for a student"""
        # Check vehicle capacity if vehicle is specified
        if allocation_data.vehicle_id:
            vehicle = await self.get_vehicle(allocation_data.vehicle_id)
            if vehicle:
                current_count = await self.get_vehicle_allocation_count(allocation_data.vehicle_id)
                if current_count >= vehicle.capacity:
                    raise ValueError("Vehicle has reached maximum capacity")
        
        allocation = TransportAllocation(**allocation_data.model_dump())
        self.session.add(allocation)
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    async def get_allocation(self, allocation_id: int) -> Optional[TransportAllocation]:
        """Get allocation by ID"""
        result = await self.session.execute(
            select(TransportAllocation)
            .where(TransportAllocation.id == allocation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_allocation_by_student(
        self, 
        student_id: int,
        active_only: bool = True
    ) -> Optional[TransportAllocation]:
        """Get active allocation for a student"""
        query = select(TransportAllocation).where(
            TransportAllocation.student_id == student_id
        )
        if active_only:
            query = query.where(TransportAllocation.status == TransportStatus.ALLOCATED)
        query = query.order_by(TransportAllocation.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_allocations(
        self,
        skip: int = 0,
        limit: int = 100,
        route_id: Optional[int] = None,
        status: Optional[TransportStatus] = None
    ) -> List[TransportAllocation]:
        """Get all allocations with filtering"""
        query = select(TransportAllocation)
        
        if route_id:
            query = query.where(TransportAllocation.route_id == route_id)
        if status:
            query = query.where(TransportAllocation.status == status)
        
        query = query.offset(skip).limit(limit).order_by(TransportAllocation.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_allocation(
        self,
        allocation_id: int,
        allocation_data: TransportAllocationUpdate
    ) -> Optional[TransportAllocation]:
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
    
    async def cancel_allocation(self, allocation_id: int) -> Optional[TransportAllocation]:
        """Cancel transport allocation"""
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            return None
        
        allocation.status = TransportStatus.CANCELLED
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation
    
    async def get_vehicle_allocation_count(self, vehicle_id: int) -> int:
        """Get count of active allocations for a vehicle"""
        result = await self.session.execute(
            select(func.count(TransportAllocation.id))
            .where(
                and_(
                    TransportAllocation.vehicle_id == vehicle_id,
                    TransportAllocation.status == TransportStatus.ALLOCATED
                )
            )
        )
        return result.scalar() or 0
    
    async def get_route_allocation_count(self, route_id: int) -> int:
        """Get count of active allocations for a route"""
        result = await self.session.execute(
            select(func.count(TransportAllocation.id))
            .where(
                and_(
                    TransportAllocation.route_id == route_id,
                    TransportAllocation.status == TransportStatus.ALLOCATED
                )
            )
        )
        return result.scalar() or 0
    
    # ==================== Transport Fee Operations ====================
    
    async def create_transport_fee(self, fee_data: TransportFeeCreate) -> TransportFee:
        """Create transport fee for a route"""
        fee = TransportFee(**fee_data.model_dump())
        self.session.add(fee)
        await self.session.commit()
        await self.session.refresh(fee)
        return fee
    
    async def get_transport_fees_by_route(self, route_id: int) -> List[TransportFee]:
        """Get all fees for a route"""
        result = await self.session.execute(
            select(TransportFee)
            .where(TransportFee.route_id == route_id)
            .order_by(TransportFee.created_at.desc())
        )
        return list(result.scalars().all())
    
    # ==================== Transport Fee Payment Operations ====================
    
    async def create_fee_payment(
        self,
        allocation_id: int,
        fee_id: int,
        amount: float,
        payment_method: Optional[str] = None,
        transaction_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> TransportFeePayment:
        """Record transport fee payment"""
        payment = TransportFeePayment(
            allocation_id=allocation_id,
            transport_fee_id=fee_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            notes=notes
        )
        self.session.add(payment)
        
        # Update allocation fee status
        allocation = await self.get_allocation(allocation_id)
        if allocation:
            allocation.fee_status = "paid"
        
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def get_payment_history(self, allocation_id: int) -> List[TransportFeePayment]:
        """Get payment history for an allocation"""
        result = await self.session.execute(
            select(TransportFeePayment)
            .where(TransportFeePayment.allocation_id == allocation_id)
            .order_by(TransportFeePayment.payment_date.desc())
        )
        return list(result.scalars().all())
    
    # ==================== Analytics Operations ====================
    
    async def get_transport_utilization(self) -> List[dict]:
        """Get vehicle utilization statistics"""
        result = await self.session.execute(
            select(Vehicle).options(selectinload(Vehicle.allocations))
        )
        vehicles = result.scalars().all()
        
        utilization = []
        for vehicle in vehicles:
            active_allocations = len([
                a for a in vehicle.allocations 
                if a.status == TransportStatus.ALLOCATED
            ])
            utilization.append({
                'vehicle_id': vehicle.id,
                'vehicle_registration': vehicle.registration_number,
                'total_capacity': vehicle.capacity,
                'current_allocations': active_allocations,
                'utilization_percentage': round(
                    (active_allocations / vehicle.capacity * 100) 
                    if vehicle.capacity > 0 else 0, 2
                ),
                'available_seats': vehicle.capacity - active_allocations
            })
        
        return utilization
    
    async def get_transport_summary(self) -> dict:
        """Get transport summary statistics"""
        vehicle_stats = await self.get_vehicle_statistics()
        
        result = await self.session.execute(
            select(
                func.count(Route.id).label('total_routes'),
                func.sum(Route.is_active == True).label('active_routes'),
                func.count(TransportAllocation.id).label('total_allocations'),
                func.sum(TransportAllocation.status == TransportStatus.ALLOCATED).label('active_allocations')
            )
        )
        row = result.one()
        
        # Calculate financial summary
        payments_result = await self.session.execute(
            select(func.sum(TransportFeePayment.amount))
        )
        total_revenue = payments_result.scalar() or 0
        
        # Pending fees calculation
        pending_result = await self.session.execute(
            select(func.sum(TransportAllocation.transport_fee))
            .where(
                and_(
                    TransportAllocation.status == TransportStatus.ALLOCATED,
                    or_(
                        TransportAllocation.fee_status == "unpaid",
                        TransportAllocation.fee_status == "partial"
                    )
                )
            )
        )
        pending_amount = pending_result.scalar() or 0
        
        return {
            **vehicle_stats,
            'total_routes': row.total_routes or 0,
            'active_routes': row.active_routes or 0,
            'total_allocations': row.total_allocations or 0,
            'active_allocations': row.active_allocations or 0,
            'total_revenue_collected': total_revenue,
            'pending_fee_amount': pending_amount
        }
