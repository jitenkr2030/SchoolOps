"""
Supplier API Routes
Endpoints for supplier management
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user, require_roles
from app.schema.inventory_schema import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierListResponse, SupplierItemsResponse, MessageResponse
)
from app.services.supplier_service import SupplierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


# ==================== CRUD Endpoints ====================

@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List suppliers with pagination and filtering
    
    Supports filtering by category and search by name, contact person, or email.
    """
    service = SupplierService(db)
    suppliers, total = await service.list_suppliers(
        page=page,
        per_page=per_page,
        category=category,
        search=search,
        active_only=active_only
    )
    
    return SupplierListResponse(
        suppliers=[SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            category=supplier.category.value,
            is_active=supplier.is_active,
            notes=supplier.notes,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
            assets_count=supplier.assets.count() if supplier.assets else 0,
            inventory_count=supplier.inventory_items.count() if supplier.inventory_items else 0
        ) for supplier in suppliers],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supplier by ID"""
    service = SupplierService(db)
    supplier = await service.get_by_id(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier '{supplier_id}' not found"
        )
    
    # Get counts
    items_count = await service.get_items_count(supplier_id)
    
    return SupplierResponse(
        id=str(supplier.id),
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        category=supplier.category.value,
        is_active=supplier.is_active,
        notes=supplier.notes,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
        assets_count=items_count["assets"],
        inventory_count=items_count["inventory"]
    )


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Create new supplier"""
    try:
        service = SupplierService(db)
        supplier = await service.create(data)
        
        return SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            category=supplier.category.value,
            is_active=supplier.is_active,
            notes=supplier.notes,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
            assets_count=0,
            inventory_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Update supplier"""
    try:
        service = SupplierService(db)
        supplier = await service.update(supplier_id, data)
        
        if not supplier:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier '{supplier_id}' not found"
            )
        
        items_count = await service.get_items_count(supplier_id)
        
        return SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            category=supplier.category.value,
            is_active=supplier.is_active,
            notes=supplier.notes,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
            assets_count=items_count["assets"],
            inventory_count=items_count["inventory"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{supplier_id}", response_model=MessageResponse)
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """Delete (deactivate) supplier"""
    service = SupplierService(db)
    success, message = await service.delete(supplier_id)
    
    if not success:
        raise HTTPException(status_code=409, detail=message)
    
    return MessageResponse(message=message)


@router.post("/{supplier_id}/deactivate", response_model=MessageResponse)
async def deactivate_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """Deactivate supplier"""
    service = SupplierService(db)
    supplier = await service.deactivate(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier '{supplier_id}' not found"
        )
    
    return MessageResponse(message="Supplier deactivated successfully")


@router.post("/{supplier_id}/activate", response_model=MessageResponse)
async def activate_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """Activate previously deactivated supplier"""
    service = SupplierService(db)
    supplier = await service.activate(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier '{supplier_id}' not found"
        )
    
    return MessageResponse(message="Supplier activated successfully")


# ==================== Related Items Endpoints ====================

@router.get("/{supplier_id}/items", response_model=dict)
async def get_supplier_items(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assets and inventory items from a supplier"""
    from app.schema.inventory_schema import AssetResponse, InventoryResponse
    from app.db.models import AssetStatus, TransactionType
    
    service = SupplierService(db)
    result = await service.get_supplier_items(supplier_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier '{supplier_id}' not found"
        )
    
    assets = [
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
            supplier_name=result.supplier_name
        )
        for asset in result.assets
    ]
    
    inventory_items = [
        InventoryResponse(
            id=str(item.id),
            name=item.name,
            sku=item.sku,
            category_id=str(item.category_id),
            supplier_id=str(item.supplier_id) if item.supplier_id else None,
            quantity_on_hand=item.quantity_on_hand,
            unit_of_measure=item.unit_of_measure,
            reorder_level=item.reorder_level,
            reorder_quantity=item.reorder_quantity,
            cost_per_unit=item.cost_per_unit,
            storage_location=item.storage_location,
            description=item.description,
            specifications=item.specifications,
            barcode=item.barcode,
            is_active=item.is_active,
            track_expiry=item.track_expiry,
            expiry_date=item.expiry_date,
            created_at=item.created_at,
            updated_at=item.updated_at,
            is_low_stock=item.is_low_stock,
            needs_reorder=item.needs_reorder,
            category_name=item.category.name if item.category else None,
            supplier_name=result.supplier_name
        )
        for item in result.inventory_items
    ]
    
    return {
        "supplier_id": result.supplier_id,
        "supplier_name": result.supplier_name,
        "assets": assets,
        "inventory_items": inventory_items,
        "total_assets": result.total_assets,
        "total_inventory": result.total_inventory
    }


# ==================== Categories Endpoint ====================

@router.get("/categories/list", response_model=List[str])
async def list_supplier_categories(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all available supplier categories"""
    service = SupplierService(db)
    return await service.list_categories()


@router.get("/by-category/{category}", response_model=List[SupplierResponse])
async def get_suppliers_by_category(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all active suppliers in a category"""
    from app.schema.inventory_schema import SupplierCategory
    
    try:
        category_enum = SupplierCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: IT, FURNITURE, STATIONERY, GENERAL, MAINTENANCE, CLEANING"
        )
    
    service = SupplierService(db)
    suppliers = await service.get_suppliers_by_category(category)
    
    return [
        SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            category=supplier.category.value,
            is_active=supplier.is_active,
            notes=supplier.notes,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
            assets_count=supplier.assets.count() if supplier.assets else 0,
            inventory_count=supplier.inventory_items.count() if supplier.inventory_items else 0
        )
        for supplier in suppliers
    ]


# ==================== Statistics Endpoint ====================

@router.get("/stats/summary", response_model=dict)
async def get_supplier_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supplier statistics"""
    service = SupplierService(db)
    return await service.get_stats()
