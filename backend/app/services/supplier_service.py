"""
Supplier Service
Business logic for supplier management
"""

import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Supplier, Asset, InventoryItem, ItemCategory
from app.schema.inventory_schema import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierListResponse, SupplierItemsResponse
)

logger = logging.getLogger(__name__)


class SupplierService:
    """
    Service for managing suppliers
    
    Provides business logic for supplier CRUD operations
    and related item management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CRUD Operations ====================
    
    async def get_by_id(self, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID"""
        result = await self.db.execute(
            select(Supplier)
            .options(selectinload(Supplier.assets), selectinload(Supplier.inventory_items))
            .where(Supplier.id == uuid.UUID(supplier_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Supplier]:
        """Get supplier by name"""
        result = await self.db.execute(
            select(Supplier).where(Supplier.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_suppliers(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[Supplier], int]:
        """
        List suppliers with pagination and filtering
        
        Returns tuple of (suppliers, total_count)
        """
        query = select(Supplier)
        
        if active_only:
            query = query.where(Supplier.is_active == True)
        
        if category:
            query = query.where(Supplier.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.contact_person.ilike(search_term),
                    Supplier.email.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(Supplier.name)
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        suppliers = result.scalars().all()
        
        return list(suppliers), total
    
    async def create(self, data: SupplierCreate) -> Supplier:
        """Create new supplier"""
        # Check for duplicate name
        existing = await self.get_by_name(data.name)
        if existing:
            raise ValueError(f"Supplier with name '{data.name}' already exists")
        
        supplier = Supplier(
            id=uuid.uuid4(),
            name=data.name,
            contact_person=data.contact_person,
            email=data.email,
            phone=data.phone,
            address=data.address,
            category=data.category,
            notes=data.notes
        )
        
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        
        return supplier
    
    async def update(
        self, 
        supplier_id: str, 
        data: SupplierUpdate
    ) -> Optional[Supplier]:
        """Update supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return None
        
        # Check for duplicate name if name is being changed
        if data.name and data.name != supplier.name:
            existing = await self.get_by_name(data.name)
            if existing:
                raise ValueError(f"Supplier with name '{data.name}' already exists")
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(supplier, field, value)
        
        await self.db.commit()
        await self.db.refresh(supplier)
        
        return supplier
    
    async def delete(self, supplier_id: str) -> Tuple[bool, str]:
        """
        Delete supplier
        
        Returns tuple of (success, message)
        Prevents deletion if supplier has linked items.
        """
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return False, "Supplier not found"
        
        # Check for linked items
        assets_count = await self.db.execute(
            select(func.count()).select_from(
                select(Asset.id).where(and_(
                    Asset.supplier_id == supplier.id,
                    Asset.is_active == True
                )).subquery()
            )
        )
        assets_linked = (assets_count.scalar() or 0) > 0
        
        inventory_count = await self.db.execute(
            select(func.count()).select_from(
                select(InventoryItem.id).where(and_(
                    InventoryItem.supplier_id == supplier.id,
                    InventoryItem.is_active == True
                )).subquery()
            )
        )
        inventory_linked = (inventory_count.scalar() or 0) > 0
        
        if assets_linked or inventory_linked:
            return False, (
                f"Cannot delete supplier. Linked items: "
                f"{assets_count.scalar() or 0} assets, "
                f"{inventory_count.scalar() or 0} inventory items"
            )
        
        # Soft delete
        supplier.is_active = False
        await self.db.commit()
        
        return True, "Supplier deleted successfully"
    
    async def deactivate(self, supplier_id: str) -> Optional[Supplier]:
        """Deactivate supplier (soft delete)"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return None
        
        supplier.is_active = False
        await self.db.commit()
        await self.db.refresh(supplier)
        
        return supplier
    
    async def activate(self, supplier_id: str) -> Optional[Supplier]:
        """Activate previously deactivated supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return None
        
        supplier.is_active = True
        await self.db.commit()
        await self.db.refresh(supplier)
        
        return supplier
    
    # ==================== Related Items ====================
    
    async def get_supplier_items(
        self,
        supplier_id: str
    ) -> Optional[SupplierItemsResponse]:
        """Get all assets and inventory items from a supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return None
        
        # Get assets
        assets_result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.category))
            .where(and_(
                Asset.supplier_id == supplier.id,
                Asset.is_active == True
            ))
        )
        assets = list(assets_result.scalars().all())
        
        # Get inventory items
        inventory_result = await self.db.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.category))
            .where(and_(
                InventoryItem.supplier_id == supplier.id,
                InventoryItem.is_active == True
            ))
        )
        inventory_items = list(inventory_result.scalars().all())
        
        return SupplierItemsResponse(
            supplier_id=str(supplier.id),
            supplier_name=supplier.name,
            assets=assets,
            inventory_items=inventory_items,
            total_assets=len(assets),
            total_inventory=len(inventory_items)
        )
    
    async def get_items_count(self, supplier_id: str) -> dict:
        """Get count of items linked to supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return {"assets": 0, "inventory": 0}
        
        assets_result = await self.db.execute(
            select(func.count()).select_from(Asset)
            .where(and_(
                Asset.supplier_id == supplier.id,
                Asset.is_active == True
            ))
        )
        
        inventory_result = await self.db.execute(
            select(func.count()).select_from(InventoryItem)
            .where(and_(
                InventoryItem.supplier_id == supplier.id,
                InventoryItem.is_active == True
            ))
        )
        
        return {
            "assets": assets_result.scalar() or 0,
            "inventory": inventory_result.scalar() or 0
        }
    
    # ==================== Statistics ====================
    
    async def get_stats(self) -> dict:
        """Get supplier statistics"""
        total_result = await self.db.execute(
            select(func.count()).select_from(Supplier)
        )
        total = total_result.scalar() or 0
        
        active_result = await self.db.execute(
            select(func.count()).select_from(Supplier).where(Supplier.is_active == True)
        )
        active = active_result.scalar() or 0
        
        # By category
        category_result = await self.db.execute(
            select(
                Supplier.category,
                func.count(Supplier.id)
            ).where(Supplier.is_active == True).group_by(Supplier.category)
        )
        by_category = dict(category_result.all())
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_category": by_category
        }
    
    # ==================== Categories ====================
    
    async def list_categories(self) -> List[str]:
        """List all available supplier categories"""
        return [cat.value for cat in list(SupplierCategory)]
    
    async def get_suppliers_by_category(self, category: str) -> List[Supplier]:
        """Get all active suppliers in a category"""
        result = await self.db.execute(
            select(Supplier)
            .where(and_(
                Supplier.category == category,
                Supplier.is_active == True
            ))
            .order_by(Supplier.name)
        )
        return list(result.scalars().all())
