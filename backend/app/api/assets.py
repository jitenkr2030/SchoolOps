"""
Asset API Routes
Endpoints for asset management and tracking
"""

import logging
from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user, require_roles
from app.schema.inventory_schema import (
    AssetCreate, AssetUpdate, AssetAssignment, AssetUnassignment,
    AssetResponse, AssetListResponse, AssetStatsResponse,
    AssetMaintenanceCreate, AssetMaintenanceResponse,
    MessageResponse, PaginationParams
)
from app.services.asset_service import AssetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assets", tags=["Assets"])


# ==================== CRUD Endpoints ====================

@router.get("", response_model=AssetListResponse)
async def list_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    supplier_id: Optional[str] = Query(None),
    assigned_to_id: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List assets with pagination and filtering
    
    Supports filtering by status, category, supplier, assigned user, and location.
    Search by name, asset tag, serial number, or description.
    """
    from app.schema.inventory_schema import AssetStatus
    
    service = AssetService(db)
    
    asset_status = AssetStatus(status) if status else None
    
    assets, total = await service.list_assets(
        page=page,
        per_page=per_page,
        status=asset_status,
        category_id=category_id,
        supplier_id=supplier_id,
        assigned_to_id=assigned_to_id,
        location=location,
        search=search
    )
    
    return AssetListResponse(
        assets=[AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        ) for asset in assets],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get asset by ID"""
    service = AssetService(db)
    asset = await service.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{asset_id}' not found"
        )
    
    return AssetResponse(
        id=str(asset.id),
        name=asset.name,
        asset_tag=asset.asset_tag,
        serial_number=asset.serial_number,
        category_id=str(asset.category_id),
        supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
        purchase_date=asset.purchase_date,
        purchase_cost=asset.purchase_cost,
        depreciation_rate=asset.depreciation_rate,
        current_value=asset.current_value,
        status=asset.status.value,
        location=asset.location,
        assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
        assigned_date=asset.assigned_date,
        description=asset.description,
        specifications=asset.specifications,
        warranty_expiry=asset.warranty_expiry,
        is_active=asset.is_active,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        category_name=asset.category.name if asset.category else None,
        supplier_name=asset.supplier.name if asset.supplier else None
    )


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Create new asset"""
    try:
        service = AssetService(db)
        asset = await service.create(data)
        
        return AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Update asset"""
    service = AssetService(db)
    asset = await service.update(asset_id, data)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{asset_id}' not found"
        )
    
    return AssetResponse(
        id=str(asset.id),
        name=asset.name,
        asset_tag=asset.asset_tag,
        serial_number=asset.serial_number,
        category_id=str(asset.category_id),
        supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
        purchase_date=asset.purchase_date,
        purchase_cost=asset.purchase_cost,
        depreciation_rate=asset.depreciation_rate,
        current_value=asset.current_value,
        status=asset.status.value,
        location=asset.location,
        assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
        assigned_date=asset.assigned_date,
        description=asset.description,
        specifications=asset.specifications,
        warranty_expiry=asset.warranty_expiry,
        is_active=asset.is_active,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        category_name=asset.category.name if asset.category else None,
        supplier_name=asset.supplier.name if asset.supplier else None
    )


@router.delete("/{asset_id}", response_model=MessageResponse)
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """Delete (deactivate) asset"""
    service = AssetService(db)
    success = await service.delete(asset_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{asset_id}' not found"
        )
    
    return MessageResponse(message="Asset deleted successfully")


# ==================== Assignment Endpoints ====================

@router.post("/{asset_id}/assign", response_model=AssetResponse)
async def assign_asset(
    asset_id: str,
    assignment: AssetAssignment,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Assign asset to user or location"""
    try:
        service = AssetService(db)
        asset = await service.assign(
            asset_id=asset_id,
            assignment=assignment,
            performed_by_id=str(current_user.id) if current_user else None
        )
        
        if not asset:
            raise HTTPException(
                status_code=404,
                detail=f"Asset '{asset_id}' not found"
            )
        
        return AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{asset_id}/unassign", response_model=AssetResponse)
async def unassign_asset(
    asset_id: str,
    unassignment: AssetUnassignment,
    release_to_location: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Unassign asset from current user/location"""
    try:
        service = AssetService(db)
        asset = await service.unassign(
            asset_id=asset_id,
            unassignment=unassignment,
            release_to_location=release_to_location,
            performed_by_id=str(current_user.id) if current_user else None
        )
        
        if not asset:
            raise HTTPException(
                status_code=404,
                detail=f"Asset '{asset_id}' not found"
            )
        
        return AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{asset_id}/status", response_model=AssetResponse)
async def update_asset_status(
    asset_id: str,
    new_status: str,
    notes: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Update asset status"""
    from app.schema.inventory_schema import AssetStatus
    
    try:
        status_enum = AssetStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: AVAILABLE, IN_USE, BROKEN, UNDER_REPAIR, DISPOSED, LOST"
        )
    
    service = AssetService(db)
    asset = await service.update_status(
        asset_id=asset_id,
        new_status=status_enum,
        notes=notes
    )
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{asset_id}' not found"
        )
    
    return AssetResponse(
        id=str(asset.id),
        name=asset.name,
        asset_tag=asset.asset_tag,
        serial_number=asset.serial_number,
        category_id=str(asset.category_id),
        supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
        purchase_date=asset.purchase_date,
        purchase_cost=asset.purchase_cost,
        depreciation_rate=asset.depreciation_rate,
        current_value=asset.current_value,
        status=asset.status.value,
        location=asset.location,
        assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
        assigned_date=asset.assigned_date,
        description=asset.description,
        specifications=asset.specifications,
        warranty_expiry=asset.warranty_expiry,
        is_active=asset.is_active,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        category_name=asset.category.name if asset.category else None,
        supplier_name=asset.supplier.name if asset.supplier else None
    )


# ==================== Maintenance Endpoints ====================

@router.post("/{asset_id}/maintenance", response_model=AssetMaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def add_maintenance_record(
    asset_id: str,
    data: AssetMaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff", "maintenance"]))
):
    """Add maintenance record for asset"""
    try:
        service = AssetService(db)
        maintenance = await service.add_maintenance_record(
            data=data,
            performed_by_id=str(current_user.id) if current_user else None
        )
        
        return {
            "id": str(maintenance.id),
            "asset_id": str(maintenance.asset_id),
            "maintenance_type": maintenance.maintenance_type,
            "description": maintenance.description,
            "cost": maintenance.cost,
            "start_date": maintenance.start_date,
            "end_date": maintenance.end_date,
            "status": maintenance.status,
            "performed_by": maintenance.performed_by,
            "notes": maintenance.notes,
            "created_at": maintenance.created_at,
            "updated_at": maintenance.updated_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/maintenance/{maintenance_id}/complete", response_model=AssetMaintenanceResponse)
async def complete_maintenance(
    maintenance_id: str,
    notes: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff", "maintenance"]))
):
    """Mark maintenance as completed"""
    service = AssetService(db)
    maintenance = await service.complete_maintenance(
        maintenance_id=maintenance_id,
        notes=notes
    )
    
    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail=f"Maintenance record '{maintenance_id}' not found"
        )
    
    return {
        "id": str(maintenance.id),
        "asset_id": str(maintenance.asset_id),
        "maintenance_type": maintenance.maintenance_type,
        "description": maintenance.description,
        "cost": maintenance.cost,
        "start_date": maintenance.start_date,
        "end_date": maintenance.end_date,
        "status": maintenance.status,
        "performed_by": maintenance.performed_by,
        "notes": maintenance.notes,
        "created_at": maintenance.created_at,
        "updated_at": maintenance.updated_at
    }


@router.get("/{asset_id}/maintenance", response_model=dict)
async def get_maintenance_history(
    asset_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get maintenance history for an asset"""
    service = AssetService(db)
    records, total = await service.get_maintenance_history(
        asset_id=asset_id,
        page=page,
        per_page=per_page
    )
    
    return {
        "records": [
            {
                "id": str(r.id),
                "asset_id": str(r.asset_id),
                "maintenance_type": r.maintenance_type,
                "description": r.description,
                "cost": r.cost,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "status": r.status,
                "performed_by": r.performed_by,
                "notes": r.notes,
                "created_at": r.created_at,
                "updated_at": r.updated_at
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


# ==================== Reports and Statistics ====================

@router.get("/stats/summary", response_model=AssetStatsResponse)
async def get_asset_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get asset statistics"""
    service = AssetService(db)
    return await service.get_stats()


@router.get("/location/{location}", response_model=List[AssetResponse])
async def get_assets_by_location(
    location: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assets at a specific location"""
    service = AssetService(db)
    assets = await service.get_assets_by_location(location)
    
    return [
        AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
        for asset in assets
    ]


@router.get("/user/{user_id}", response_model=List[AssetResponse])
async def get_assets_by_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assets assigned to a user"""
    service = AssetService(db)
    assets = await service.get_assets_by_user(user_id)
    
    return [
        AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
        for asset in assets
    ]


@router.get("/warranty/expiring", response_model=List[AssetResponse])
async def get_warranty_expiring(
    days_ahead: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get assets with warranty expiring within specified days"""
    service = AssetService(db)
    assets = await service.get_warranty_expiring(days_ahead=days_ahead)
    
    return [
        AssetResponse(
            id=str(asset.id),
            name=asset.name,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            category_id=str(asset.category_id),
            supplier_id=str(asset.supplier_id) if asset.supplier_id else None,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            depreciation_rate=asset.depreciation_rate,
            current_value=asset.current_value,
            status=asset.status.value,
            location=asset.location,
            assigned_to_id=str(asset.assigned_to_id) if asset.assigned_to_id else None,
            assigned_date=asset.assigned_date,
            description=asset.description,
            specifications=asset.specifications,
            warranty_expiry=asset.warranty_expiry,
            is_active=asset.is_active,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            category_name=asset.category.name if asset.category else None,
            supplier_name=asset.supplier.name if asset.supplier else None
        )
        for asset in assets
    ]


@router.get("/generate-tag")
async def generate_asset_tag(
    category_prefix: str = Query("AST", max_length=10),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Generate unique asset tag"""
    service = AssetService(db)
    tag = await service.generate_asset_tag(category_prefix=category_prefix)
    return {"asset_tag": tag}
