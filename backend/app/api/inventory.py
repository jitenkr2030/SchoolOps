"""
Inventory API Routes
Endpoints for inventory management and stock control
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user, require_roles
from app.schema.inventory_schema import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    InventoryListResponse, StockAdjustment, StockAdjustmentResult,
    LowStockAlert, InventoryStatsResponse, StockTransactionListResponse,
    PurchaseOrderCreate, PurchaseOrderResponse, PurchaseOrderListResponse,
    MessageResponse
)
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ==================== CRUD Endpoints ====================

@router.get("", response_model=InventoryListResponse)
async def list_inventory(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),
    supplier_id: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List inventory items with pagination and filtering
    
    Supports filtering by category, supplier, and low stock status.
    Search by name, SKU, or description.
    """
    service = InventoryService(db)
    items, total = await service.list_items(
        page=page,
        per_page=per_page,
        category_id=category_id,
        supplier_id=supplier_id,
        low_stock_only=low_stock_only,
        search=search
    )
    
    return InventoryListResponse(
        items=[InventoryResponse(
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
            supplier_name=item.supplier.name if item.supplier else None
        ) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory item by ID"""
    service = InventoryService(db)
    item = await service.get_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory item '{item_id}' not found"
        )
    
    return InventoryResponse(
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
        supplier_name=item.supplier.name if item.supplier else None
    )


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    data: InventoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Create new inventory item"""
    try:
        service = InventoryService(db)
        item = await service.create(data)
        
        return InventoryResponse(
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
            supplier_name=item.supplier.name if item.supplier else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: str,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Update inventory item"""
    service = InventoryService(db)
    item = await service.update(item_id, data)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory item '{item_id}' not found"
        )
    
    return InventoryResponse(
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
        supplier_name=item.supplier.name if item.supplier else None
    )


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_inventory_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """Delete (deactivate) inventory item"""
    service = InventoryService(db)
    success = await service.delete(item_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory item '{item_id}' not found"
        )
    
    return MessageResponse(message="Inventory item deleted successfully")


# ==================== Stock Management Endpoints ====================

@router.post("/{item_id}/adjust", response_model=StockAdjustmentResult)
async def adjust_stock(
    item_id: str,
    adjustment: StockAdjustment,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """
    Adjust inventory stock level
    
    Creates a transaction record and updates the quantity.
    Prevents negative stock levels.
    """
    try:
        service = InventoryService(db)
        result = await service.adjust_stock(
            item_id=item_id,
            adjustment=adjustment,
            performed_by_id=str(current_user.id) if current_user else None,
            performed_by_name=getattr(current_user, 'full_name', None) or current_user.email
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}/transactions", response_model=StockTransactionListResponse)
async def get_item_transactions(
    item_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get transaction history for an inventory item"""
    from app.schema.inventory_schema import TransactionType
    
    service = InventoryService(db)
    
    tx_type = TransactionType(transaction_type) if transaction_type else None
    
    transactions, total = await service.get_transactions(
        item_id=item_id,
        page=page,
        per_page=per_page,
        transaction_type=tx_type,
        start_date=start_date,
        end_date=end_date
    )
    
    return StockTransactionListResponse(
        transactions=[
            {
                "id": str(tx.id),
                "item_id": str(tx.item_id),
                "transaction_type": tx.transaction_type.value,
                "quantity_change": tx.quantity_change,
                "quantity_before": tx.quantity_before,
                "quantity_after": tx.quantity_after,
                "reference_type": tx.reference_type,
                "reference_id": tx.reference_id,
                "performed_by_id": str(tx.performed_by_id) if tx.performed_by_id else None,
                "performed_by_name": tx.performed_by_name,
                "notes": tx.notes,
                "timestamp": tx.timestamp
            }
            for tx in transactions
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


# ==================== Alerts and Reports ====================

@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
async def get_low_stock_alerts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all items below reorder level"""
    service = InventoryService(db)
    alerts = await service.get_low_stock_alerts()
    return alerts


@router.get("/alerts/out-of-stock", response_model=List[InventoryResponse])
async def get_out_of_stock_items(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get items with zero stock"""
    service = InventoryService(db)
    items = await service.get_out_of_stock_items()
    
    return [
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
            supplier_name=item.supplier.name if item.supplier else None
        )
        for item in items
    ]


@router.get("/stats/summary", response_model=InventoryStatsResponse)
async def get_inventory_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory statistics"""
    service = InventoryService(db)
    return await service.get_stats()


# ==================== Purchase Order Endpoints ====================

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Create purchase order for inventory restocking"""
    service = InventoryService(db)
    order = await service.create_purchase_order(
        data=data,
        created_by_id=str(current_user.id) if current_user else None
    )
    
    return PurchaseOrderResponse(
        id=str(order.id),
        order_number=order.order_number,
        supplier_id=str(order.supplier_id),
        status=order.status.value,
        order_date=order.order_date,
        expected_delivery=order.expected_delivery,
        actual_delivery=order.actual_delivery,
        subtotal=order.subtotal,
        tax_amount=order.tax_amount,
        total_amount=order.total_amount,
        notes=order.notes,
        created_by_id=str(order.created_by_id) if order.created_by_id else None,
        created_at=order.created_at,
        updated_at=order.updated_at,
        supplier_name=order.supplier.name if order.supplier else None
    )


@router.post("/purchase-orders/{order_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "staff"]))
):
    """Receive purchase order and update inventory"""
    try:
        service = InventoryService(db)
        order = await service.receive_purchase_order(
            order_id=order_id,
            received_by_id=str(current_user.id) if current_user else None,
            received_by_name=getattr(current_user, 'full_name', None) or current_user.email
        )
        
        return PurchaseOrderResponse(
            id=str(order.id),
            order_number=order.order_number,
            supplier_id=str(order.supplier_id),
            status=order.status.value,
            order_date=order.order_date,
            expected_delivery=order.expected_delivery,
            actual_delivery=order.actual_delivery,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total_amount=order.total_amount,
            notes=order.notes,
            created_by_id=str(order.created_by_id) if order.created_by_id else None,
            created_at=order.created_at,
            updated_at=order.updated_at,
            supplier_name=order.supplier.name if order.supplier else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
