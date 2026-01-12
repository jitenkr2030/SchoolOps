"""
Transport API Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.transport_service import TransportService
from app.schema.transport_schema import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleWithDetailsResponse,
    RouteCreate, RouteUpdate, RouteResponse, RouteWithStopsResponse,
    TransportAllocationCreate, TransportAllocationUpdate, TransportAllocationResponse,
    TransportFeeCreate, TransportFeeResponse,
    TransportFeePaymentCreate, TransportFeePaymentResponse,
    GPSUpdate, GPSUpdateResponse,
    VehicleListResponse, RouteListResponse, TransportAllocationListResponse,
    TransportUtilizationResponse, TransportSummaryResponse
)
from app.core.security import get_current_user
from app.db.models.models import User


router = APIRouter(prefix="/transport", tags=["Transport"])


# ==================== Vehicle Endpoints ====================

@router.post("/vehicles", response_model=VehicleResponse)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new vehicle"""
    service = TransportService(db)
    return await service.create_vehicle(vehicle)


@router.get("/vehicles", response_model=VehicleListResponse)
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all vehicles"""
    service = TransportService(db)
    from app.db.models.transport import VehicleStatus
    vehicle_status = VehicleStatus(status) if status else None
    vehicles = await service.get_all_vehicles(skip, limit, vehicle_status)
    total = len(vehicles)  # In production, use count query
    return {"vehicles": vehicles, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vehicle by ID"""
    service = TransportService(db)
    vehicle = await service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vehicle information"""
    service = TransportService(db)
    vehicle = await service.update_vehicle(vehicle_id, vehicle_update)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a vehicle"""
    service = TransportService(db)
    success = await service.delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}


@router.patch("/vehicles/{vehicle_id}/location", response_model=GPSUpdateResponse)
async def update_gps_location(
    vehicle_id: int,
    gps_data: GPSUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vehicle GPS location"""
    service = TransportService(db)
    vehicle = await service.update_gps_location(vehicle_id, gps_data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {
        "vehicle_id": vehicle_id,
        "latitude": gps_data.latitude,
        "longitude": gps_data.longitude,
        "updated_at": vehicle.last_gps_update
    }


# ==================== Route Endpoints ====================

@router.post("/routes", response_model=RouteResponse)
async def create_route(
    route: RouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new route"""
    service = TransportService(db)
    return await service.create_route(route)


@router.get("/routes", response_model=RouteListResponse)
async def get_routes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all routes"""
    service = TransportService(db)
    routes = await service.get_all_routes(skip, limit, active_only)
    total = len(routes)
    return {"routes": routes, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/routes/{route_id}", response_model=RouteWithStopsResponse)
async def get_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get route by ID with stops"""
    service = TransportService(db)
    route = await service.get_route(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/routes/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    route_update: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update route information"""
    service = TransportService(db)
    route = await service.update_route(route_id, route_update)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/routes/{route_id}")
async def delete_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a route"""
    service = TransportService(db)
    success = await service.delete_route(route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Route deleted successfully"}


# ==================== Transport Allocation Endpoints ====================

@router.post("/allocations", response_model=TransportAllocationResponse)
async def create_allocation(
    allocation: TransportAllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create transport allocation for a student"""
    service = TransportService(db)
    try:
        return await service.create_allocation(allocation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/allocations", response_model=TransportAllocationListResponse)
async def get_allocations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    route_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all allocations"""
    service = TransportService(db)
    from app.db.models.transport import TransportStatus
    transport_status = TransportStatus(status) if status else None
    allocations = await service.get_all_allocations(skip, limit, route_id, transport_status)
    total = len(allocations)
    return {"allocations": allocations, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/allocations/student/{student_id}", response_model=TransportAllocationResponse)
async def get_student_allocation(
    student_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get allocation for a specific student"""
    service = TransportService(db)
    allocation = await service.get_allocation_by_student(student_id, active_only)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.put("/allocations/{allocation_id}", response_model=TransportAllocationResponse)
async def update_allocation(
    allocation_id: int,
    allocation_update: TransportAllocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update allocation information"""
    service = TransportService(db)
    allocation = await service.update_allocation(allocation_id, allocation_update)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.post("/allocations/{allocation_id}/cancel")
async def cancel_allocation(
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel transport allocation"""
    service = TransportService(db)
    allocation = await service.cancel_allocation(allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return {"message": "Allocation cancelled successfully", "allocation": allocation}


# ==================== Transport Fee Endpoints ====================

@router.post("/fees", response_model=TransportFeeResponse)
async def create_transport_fee(
    fee: TransportFeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create transport fee for a route"""
    service = TransportService(db)
    return await service.create_transport_fee(fee)


@router.get("/fees/route/{route_id}")
async def get_route_fees(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all fees for a route"""
    service = TransportService(db)
    return await service.get_transport_fees_by_route(route_id)


@router.post("/payments")
async def create_fee_payment(
    payment: TransportFeePaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record transport fee payment"""
    service = TransportService(db)
    return await service.create_fee_payment(
        allocation_id=payment.allocation_id,
        fee_id=payment.transport_fee_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        notes=payment.notes
    )


@router.get("/payments/allocation/{allocation_id}")
async def get_payment_history(
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history for an allocation"""
    service = TransportService(db)
    return await service.get_payment_history(allocation_id)


# ==================== Analytics Endpoints ====================

@router.get("/utilization", response_model=List[TransportUtilizationResponse])
async def get_transport_utilization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vehicle utilization statistics"""
    service = TransportService(db)
    return await service.get_transport_utilization()


@router.get("/summary", response_model=TransportSummaryResponse)
async def get_transport_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transport summary statistics"""
    service = TransportService(db)
    return await service.get_transport_summary()


@router.get("/statistics")
async def get_vehicle_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vehicle statistics"""
    service = TransportService(db)
    return await service.get_vehicle_statistics()
