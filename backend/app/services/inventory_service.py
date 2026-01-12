"""
Inventory Service
Business logic for inventory management and stock control
"""

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    InventoryItem, StockTransaction, Supplier, ItemCategory, 
    TransactionType, PurchaseOrder, PurchaseOrderDetail
)
from app.schema.inventory_schema import (
    InventoryCreate, InventoryUpdate, StockAdjustment,
    StockAdjustmentResult, LowStockAlert, InventoryStatsResponse,
    PurchaseOrderCreate, PurchaseOrderDetailBase
)

logger = logging.getLogger(__name__)


class InventoryService:
    """
    Service for managing inventory items and stock levels
    
    Provides business logic for inventory CRUD operations,
    stock adjustments, and low stock monitoring.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CRUD Operations ====================
    
    async def get_by_id(self, item_id: str) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        result = await self.db.execute(
            select(InventoryItem)
            .options(
                selectinload(InventoryItem.category),
                selectinload(InventoryItem.supplier)
            )
            .where(InventoryItem.id == uuid.UUID(item_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU"""
        result = await self.db.execute(
            select(InventoryItem)
            .where(InventoryItem.sku == sku)
        )
        return result.scalar_one_or_none()
    
    async def list_items(
        self,
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[str] = None,
        supplier_id: Optional[str] = None,
        low_stock_only: bool = False,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryItem], int]:
        """
        List inventory items with pagination and filtering
        
        Returns tuple of (items, total_count)
        """
        query = select(InventoryItem).options(
            selectinload(InventoryItem.category),
            selectinload(InventoryItem.supplier)
        ).where(InventoryItem.is_active == True)
        
        # Apply filters
        if category_id:
            query = query.where(InventoryItem.category_id == uuid.UUID(category_id))
        
        if supplier_id:
            query = query.where(InventoryItem.supplier_id == uuid.UUID(supplier_id))
        
        if low_stock_only:
            query = query.where(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    InventoryItem.name.ilike(search_term),
                    InventoryItem.sku.ilike(search_term),
                    InventoryItem.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(InventoryItem.name)
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def create(self, data: InventoryCreate) -> InventoryItem:
        """Create new inventory item"""
        # Check for duplicate SKU
        existing = await self.get_by_sku(data.sku)
        if existing:
            raise ValueError(f"Inventory item with SKU '{data.sku}' already exists")
        
        item = InventoryItem(
            id=uuid.uuid4(),
            name=data.name,
            sku=data.sku,
            category_id=uuid.UUID(data.category_id),
            supplier_id=uuid.UUID(data.supplier_id) if data.supplier_id else None,
            quantity_on_hand=data.quantity_on_hand,
            unit_of_measure=data.unit_of_measure,
            reorder_level=data.reorder_level,
            reorder_quantity=data.reorder_quantity,
            cost_per_unit=data.cost_per_unit,
            storage_location=data.storage_location,
            description=data.description,
            specifications=data.specifications,
            barcode=data.barcode
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        # Log initial stock if quantity > 0
        if item.quantity_on_hand > 0:
            await self._create_transaction(
                item_id=str(item.id),
                transaction_type=TransactionType.ADJUSTMENT,
                quantity=item.quantity_on_hand,
                quantity_before=0,
                quantity_after=item.quantity_on_hand,
                notes="Initial stock on creation",
                performed_by_name="System"
            )
        
        return item
    
    async def update(
        self, 
        item_id: str, 
        data: InventoryUpdate
    ) -> Optional[InventoryItem]:
        """Update inventory item"""
        item = await self.get_by_id(item_id)
        if not item:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(item, field, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def delete(self, item_id: str) -> bool:
        """Soft delete inventory item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        item.is_active = False
        await self.db.commit()
        
        return True
    
    # ==================== Stock Management ====================
    
    async def adjust_stock(
        self,
        item_id: str,
        adjustment: StockAdjustment,
        performed_by_id: Optional[str] = None,
        performed_by_name: Optional[str] = None
    ) -> StockAdjustmentResult:
        """
        Adjust inventory stock level
        
        Creates a transaction record and updates the quantity atomically.
        Prevents negative stock levels.
        """
        item = await self.get_by_id(item_id)
        if not item:
            raise ValueError(f"Inventory item '{item_id}' not found")
        
        quantity_before = item.quantity_on_hand
        quantity_change = adjustment.quantity
        quantity_after = quantity_before + quantity_change
        
        # Prevent negative stock
        if quantity_after < 0:
            raise ValueError(
                f"Cannot reduce stock by {abs(quantity_change)}. "
                f"Current stock: {quantity_before}, Requested: {quantity_change}"
            )
        
        # Update stock level
        item.quantity_on_hand = quantity_after
        item.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = await self._create_transaction(
            item_id=item_id,
            transaction_type=adjustment.transaction_type,
            quantity=abs(quantity_change),
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            notes=adjustment.notes,
            reference_type=adjustment.reference_type,
            reference_id=adjustment.reference_id,
            performed_by_id=performed_by_id,
            performed_by_name=performed_by_name
        )
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return StockAdjustmentResult(
            success=True,
            item_id=item_id,
            item_name=item.name,
            transaction_type=adjustment.transaction_type,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            transaction_id=str(transaction.id),
            timestamp=transaction.timestamp
        )
    
    async def consume_stock(
        self,
        item_id: str,
        quantity: int,
        notes: Optional[str] = None,
        performed_by_id: Optional[str] = None,
        performed_by_name: Optional[str] = None
    ) -> StockAdjustmentResult:
        """Consume inventory items (for internal use)"""
        return await self.adjust_stock(
            item_id=item_id,
            adjustment=StockAdjustment(
                transaction_type=TransactionType.CONSUMPTION,
                quantity=-abs(quantity),
                notes=notes
            ),
            performed_by_id=performed_by_id,
            performed_by_name=performed_by_name
        )
    
    async def receive_stock(
        self,
        item_id: str,
        quantity: int,
        notes: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        performed_by_id: Optional[str] = None,
        performed_by_name: Optional[str] = None
    ) -> StockAdjustmentResult:
        """Receive inventory items (from purchase)"""
        return await self.adjust_stock(
            item_id=item_id,
            adjustment=StockAdjustment(
                transaction_type=TransactionType.PURCHASE,
                quantity=abs(quantity),
                notes=notes,
                reference_type=reference_type,
                reference_id=reference_id
            ),
            performed_by_id=performed_by_id,
            performed_by_name=performed_by_name
        )
    
    # ==================== Transaction History ====================
    
    async def get_transactions(
        self,
        item_id: str,
        page: int = 1,
        per_page: int = 50,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[StockTransaction], int]:
        """Get transaction history for an item"""
        query = select(StockTransaction).where(
            StockTransaction.item_id == uuid.UUID(item_id)
        )
        
        if transaction_type:
            query = query.where(StockTransaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.where(StockTransaction.timestamp >= start_date)
        
        if end_date:
            query = query.where(StockTransaction.timestamp <= end_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(StockTransaction.timestamp.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total
    
    # ==================== Alerts and Reports ====================
    
    async def get_low_stock_alerts(self) -> List[LowStockAlert]:
        """Get all items below reorder level"""
        result = await self.db.execute(
            select(InventoryItem)
            .options(
                selectinload(InventoryItem.category),
                selectinload(InventoryItem.supplier)
            )
            .where(and_(
                InventoryItem.is_active == True,
                InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
            ))
            .order_by(InventoryItem.quantity_on_hand)
        )
        
        items = result.scalars().all()
        
        alerts = []
        for item in items:
            alerts.append(LowStockAlert(
                item_id=str(item.id),
                item_name=item.name,
                sku=item.sku,
                category_name=item.category.name if item.category else "Unknown",
                quantity_on_hand=item.quantity_on_hand,
                reorder_level=item.reorder_level,
                supplier_id=str(item.supplier_id) if item.supplier_id else None,
                supplier_name=item.supplier.name if item.supplier else None,
                suggested_order_qty=item.reorder_quantity
            ))
        
        return alerts
    
    async def get_out_of_stock_items(self) -> List[InventoryItem]:
        """Get items with zero stock"""
        result = await self.db.execute(
            select(InventoryItem)
            .where(and_(
                InventoryItem.is_active == True,
                InventoryItem.quantity_on_hand == 0
            ))
        )
        return list(result.scalars().all())
    
    async def get_stats(self) -> InventoryStatsResponse:
        """Get inventory statistics"""
        # Total items
        total_query = select(func.count()).select_from(
            select(InventoryItem.id).where(InventoryItem.is_active == True).subquery()
        )
        total_result = await self.db.execute(total_query)
        total_items = total_result.scalar() or 0
        
        # Total value
        value_query = select(func.sum(
            InventoryItem.quantity_on_hand * InventoryItem.cost_per_unit
        )).where(InventoryItem.is_active == True)
        value_result = await self.db.execute(value_query)
        total_value = value_result.scalar() or Decimal("0")
        
        # Low stock count
        low_stock_query = select(func.count()).select_from(
            select(InventoryItem.id).where(and_(
                InventoryItem.is_active == True,
                InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
            )).subquery()
        )
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock_count = low_stock_result.scalar() or 0
        
        # Out of stock count
        out_of_stock_query = select(func.count()).select_from(
            select(InventoryItem.id).where(and_(
                InventoryItem.is_active == True,
                InventoryItem.quantity_on_hand == 0
            )).subquery()
        )
        out_of_stock_result = await self.db.execute(out_of_stock_query)
        out_of_stock_count = out_of_stock_result.scalar() or 0
        
        # Category breakdown
        category_query = select(
            ItemCategory.name,
            func.count(InventoryItem.id)
        ).join(
            InventoryItem, 
            InventoryItem.category_id == ItemCategory.id
        ).where(and_(
            InventoryItem.is_active == True,
            ItemCategory.is_active == True
        )).group_by(ItemCategory.name)
        
        category_result = await self.db.execute(category_query)
        category_breakdown = dict(category_result.all())
        
        return InventoryStatsResponse(
            total_items=total_items,
            total_value=total_value,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            category_breakdown=category_breakdown
        )
    
    # ==================== Purchase Orders ====================
    
    async def create_purchase_order(
        self,
        data: PurchaseOrderCreate,
        created_by_id: Optional[str] = None
    ) -> PurchaseOrder:
        """Create a purchase order"""
        # Generate order number
        order_number = await self._generate_order_number()
        
        # Calculate totals
        subtotal = Decimal("0")
        details = []
        
        for detail_data in data.details:
            total = detail_data.unit_price * detail_data.quantity_ordered
            subtotal += total
            
            detail = PurchaseOrderDetail(
                id=uuid.uuid4(),
                item_id=uuid.UUID(detail_data.item_id),
                quantity_ordered=detail_data.quantity_ordered,
                quantity_received=0,
                unit_price=detail_data.unit_price,
                total_price=total,
                notes=detail_data.notes
            )
            details.append(detail)
        
        tax_amount = subtotal * Decimal("0.10")  # 10% tax example
        total_amount = subtotal + tax_amount
        
        order = PurchaseOrder(
            id=uuid.uuid4(),
            order_number=order_number,
            supplier_id=uuid.UUID(data.supplier_id),
            order_date=data.order_date,
            expected_delivery=data.expected_delivery,
            notes=data.notes,
            created_by_id=uuid.UUID(created_by_id) if created_by_id else None,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            details=details
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def receive_purchase_order(
        self,
        order_id: str,
        received_by_id: Optional[str] = None,
        received_by_name: Optional[str] = None
    ) -> PurchaseOrder:
        """Receive a purchase order and update inventory"""
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.details).selectinload(PurchaseOrderDetail.item),
                selectinload(PurchaseOrder.supplier)
            )
            .where(PurchaseOrder.id == uuid.UUID(order_id))
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Purchase order '{order_id}' not found")
        
        if order.status not in [PurchaseOrderStatus.ORDERED, PurchaseOrderStatus.PENDING]:
            raise ValueError(f"Purchase order cannot be received. Current status: {order.status}")
        
        # Process each item
        for detail in order.details:
            if detail.quantity_received < detail.quantity_ordered:
                remaining = detail.quantity_ordered - detail.quantity_received
                
                # Update inventory
                await self.receive_stock(
                    item_id=str(detail.item_id),
                    quantity=remaining,
                    reference_type="PURCHASE_ORDER",
                    reference_id=str(order.id),
                    performed_by_id=received_by_id,
                    performed_by_name=received_by_name
                )
                
                detail.quantity_received = detail.quantity_ordered
        
        order.status = PurchaseOrderStatus.RECEIVED
        order.actual_delivery = datetime.utcnow().date()
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    # ==================== Helper Methods ====================
    
    async def _create_transaction(
        self,
        item_id: str,
        transaction_type: TransactionType,
        quantity: int,
        quantity_before: int,
        quantity_after: int,
        notes: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        performed_by_id: Optional[str] = None,
        performed_by_name: Optional[str] = None
    ) -> StockTransaction:
        """Create a stock transaction record"""
        transaction = StockTransaction(
            id=uuid.uuid4(),
            item_id=uuid.UUID(item_id),
            transaction_type=transaction_type,
            quantity_change=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_type=reference_type,
            reference_id=reference_id,
            performed_by_id=uuid.UUID(performed_by_id) if performed_by_id else None,
            performed_by_name=performed_by_name,
            notes=notes
        )
        
        self.db.add(transaction)
        return transaction
    
    async def _generate_order_number(self) -> str:
        """Generate a unique order number"""
        # Format: PO-YYYYMMDD-XXXX
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of orders today
        result = await self.db.execute(
            select(func.count()).select_from(PurchaseOrder)
            .where(PurchaseOrder.order_number.like(f"PO-{date_str}%"))
        )
        count = (result.scalar() or 0) + 1
        
        return f"PO-{date_str}-{count:04d}"
