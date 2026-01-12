"""
Asset Service
Business logic for asset management and tracking
"""

import logging
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Asset, AssetMaintenance, Supplier, ItemCategory, AssetStatus
)
from app.schema.inventory_schema import (
    AssetCreate, AssetUpdate, AssetAssignment, AssetUnassignment,
    AssetResponse, AssetStatsResponse, AssetMaintenanceCreate
)

logger = logging.getLogger(__name__)


class AssetService:
    """
    Service for managing school assets
    
    Provides business logic for asset lifecycle management,
    assignment tracking, and maintenance records.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CRUD Operations ====================
    
    async def get_by_id(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        result = await self.db.execute(
            select(Asset)
            .options(
                selectinload(Asset.category),
                selectinload(Asset.supplier),
                selectinload(Asset.maintenance_records)
            )
            .where(Asset.id == uuid.UUID(asset_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_asset_tag(self, asset_tag: str) -> Optional[Asset]:
        """Get asset by asset tag"""
        result = await self.db.execute(
            select(Asset)
            .where(Asset.asset_tag == asset_tag)
        )
        return result.scalar_one_or_none()
    
    async def list_assets(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[AssetStatus] = None,
        category_id: Optional[str] = None,
        supplier_id: Optional[str] = None,
        assigned_to_id: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Asset], int]:
        """
        List assets with pagination and filtering
        
        Returns tuple of (assets, total_count)
        """
        query = select(Asset).options(
            selectinload(Asset.category),
            selectinload(Asset.supplier)
        ).where(Asset.is_active == True)
        
        # Apply filters
        if status:
            query = query.where(Asset.status == status)
        
        if category_id:
            query = query.where(Asset.category_id == uuid.UUID(category_id))
        
        if supplier_id:
            query = query.where(Asset.supplier_id == uuid.UUID(supplier_id))
        
        if assigned_to_id:
            query = query.where(Asset.assigned_to_id == uuid.UUID(assigned_to_id))
        
        if location:
            query = query.where(Asset.location.ilike(f"%{location}%"))
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Asset.name.ilike(search_term),
                    Asset.asset_tag.ilike(search_term),
                    Asset.serial_number.ilike(search_term),
                    Asset.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(Asset.name)
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        assets = result.scalars().all()
        
        return list(assets), total
    
    async def create(self, data: AssetCreate) -> Asset:
        """Create new asset"""
        # Check for duplicate asset tag
        existing = await self.get_by_asset_tag(data.asset_tag)
        if existing:
            raise ValueError(f"Asset with tag '{data.asset_tag}' already exists")
        
        # Check category exists and is of type ASSET
        result = await self.db.execute(
            select(ItemCategory).where(ItemCategory.id == uuid.UUID(data.category_id))
        )
        category = result.scalar_one_or_none()
        if not category:
            raise ValueError(f"Category '{data.category_id}' not found")
        
        asset = Asset(
            id=uuid.uuid4(),
            name=data.name,
            asset_tag=data.asset_tag,
            serial_number=data.serial_number,
            category_id=uuid.UUID(data.category_id),
            supplier_id=uuid.UUID(data.supplier_id) if data.supplier_id else None,
            purchase_date=data.purchase_date,
            purchase_cost=data.purchase_cost,
            depreciation_rate=data.depreciation_rate or Decimal("10.00"),
            current_value=data.purchase_cost,
            status=data.status,
            location=data.location,
            description=data.description,
            specifications=data.specifications,
            warranty_expiry=data.warranty_expiry
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def update(
        self, 
        asset_id: str, 
        data: AssetUpdate
    ) -> Optional[Asset]:
        """Update asset"""
        asset = await self.get_by_id(asset_id)
        if not asset:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(asset, field, value)
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def delete(self, asset_id: str) -> bool:
        """Soft delete asset"""
        asset = await self.get_by_id(asset_id)
        if not asset:
            return False
        
        asset.is_active = False
        await self.db.commit()
        
        return True
    
    # ==================== Assignment Management ====================
    
    async def assign(
        self,
        asset_id: str,
        assignment: AssetAssignment,
        performed_by_id: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Assign asset to a user or location
        
        Updates status to IN_USE and records assignment details.
        """
        asset = await self.get_by_id(asset_id)
        if not asset:
            return None
        
        # Validation: If status is IN_USE, must have assignment details
        if assignment.assigned_to_id is None and assignment.location is None:
            raise ValueError("Assignment must include either assigned_to_id or location")
        
        # Update assignment fields
        asset.assigned_to_id = uuid.UUID(assignment.assigned_to_id) if assignment.assigned_to_id else None
        asset.location = assignment.location or asset.location
        asset.assigned_date = date.today()
        asset.status = AssetStatus.IN_USE
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        logger.info(
            f"Asset {asset.asset_tag} assigned to {assignment.assigned_to_id or 'location: ' + str(assignment.location)}"
        )
        
        return asset
    
    async def unassign(
        self,
        asset_id: str,
        unassignment: AssetUnassignment,
        release_to_location: Optional[str] = None,
        performed_by_id: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Unassign asset from current user/location
        
        Returns asset to available pool or new location.
        """
        asset = await self.get_by_id(asset_id)
        if not asset:
            return None
        
        if asset.status != AssetStatus.IN_USE:
            raise ValueError(f"Asset is not currently assigned. Status: {asset.status}")
        
        # Update fields
        asset.assigned_to_id = None
        asset.assigned_date = None
        asset.status = AssetStatus.AVAILABLE
        
        # Optionally move to new location
        if release_to_location:
            asset.location = release_to_location
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        logger.info(f"Asset {asset.asset_tag} unassigned")
        
        return asset
    
    async def update_status(
        self,
        asset_id: str,
        new_status: AssetStatus,
        notes: Optional[str] = None
    ) -> Optional[Asset]:
        """Update asset status"""
        asset = await self.get_by_id(asset_id)
        if not asset:
            return None
        
        old_status = asset.status
        asset.status = new_status
        
        # If marking as under repair, unassign
        if new_status == AssetStatus.UNDER_REPAIR and asset.status == AssetStatus.IN_USE:
            asset.assigned_to_id = None
            asset.assigned_date = None
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        logger.info(f"Asset {asset.asset_tag} status changed: {old_status} -> {new_status}")
        
        return asset
    
    # ==================== Maintenance Management ====================
    
    async def add_maintenance_record(
        self,
        data: AssetMaintenanceCreate,
        performed_by_id: Optional[str] = None
    ) -> AssetMaintenance:
        """Add maintenance record for asset"""
        # Verify asset exists
        asset = await self.get_by_id(data.asset_id)
        if not asset:
            raise ValueError(f"Asset '{data.asset_id}' not found")
        
        maintenance = AssetMaintenance(
            id=uuid.uuid4(),
            asset_id=uuid.UUID(data.asset_id),
            maintenance_type=data.maintenance_type,
            description=data.description,
            cost=data.cost,
            start_date=data.start_date,
            end_date=data.end_date,
            performed_by=data.performed_by,
            notes=data.notes
        )
        
        # Update asset status if under repair
        if data.maintenance_type in ["REPAIR", "INSPECTION"]:
            asset.status = AssetStatus.UNDER_REPAIR
        
        self.db.add(maintenance)
        await self.db.commit()
        await self.db.refresh(maintenance)
        
        return maintenance
    
    async def complete_maintenance(
        self,
        maintenance_id: str,
        notes: Optional[str] = None
    ) -> Optional[AssetMaintenance]:
        """Mark maintenance as completed"""
        result = await self.db.execute(
            select(AssetMaintenance).where(
                AssetMaintenance.id == uuid.UUID(maintenance_id)
            )
        )
        maintenance = result.scalar_one_or_none()
        
        if not maintenance:
            return None
        
        maintenance.end_date = date.today()
        maintenance.status = "COMPLETED"
        maintenance.notes = notes or maintenance.notes
        
        # Update asset status back to available or in use
        asset = await self.get_by_id(str(maintenance.asset_id))
        if asset:
            asset.status = AssetStatus.AVAILABLE
        
        await self.db.commit()
        await self.db.refresh(maintenance)
        
        return maintenance
    
    async def get_maintenance_history(
        self,
        asset_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[AssetMaintenance], int]:
        """Get maintenance history for an asset"""
        query = select(AssetMaintenance).where(
            AssetMaintenance.asset_id == uuid.UUID(asset_id)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(AssetMaintenance.start_date.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return list(records), total
    
    # ==================== Statistics and Reports ====================
    
    async def get_stats(self) -> AssetStatsResponse:
        """Get asset statistics"""
        # Total assets
        total_query = select(func.count()).select_from(
            select(Asset.id).where(Asset.is_active == True).subquery()
        )
        total_result = await self.db.execute(total_query)
        total_assets = total_result.scalar() or 0
        
        # Count by status
        status_counts = {}
        for status in AssetStatus:
            result = await self.db.execute(
                select(func.count()).select_from(
                    select(Asset.id).where(and_(
                        Asset.is_active == True,
                        Asset.status == status
                    )).subquery()
                )
            )
            status_counts[status.value] = result.scalar() or 0
        
        # Total value
        value_result = await self.db.execute(
            select(func.sum(Asset.current_value)).where(Asset.is_active == True)
        )
        total_value = value_result.scalar() or Decimal("0")
        
        # By category
        category_result = await self.db.execute(
            select(
                ItemCategory.name,
                func.count(Asset.id)
            ).join(
                Asset, 
                Asset.category_id == ItemCategory.id
            ).where(and_(
                Asset.is_active == True,
                ItemCategory.is_active == True
            )).group_by(ItemCategory.name)
        )
        by_category = dict(category_result.all())
        
        return AssetStatsResponse(
            total_assets=total_assets,
            available=status_counts.get(AssetStatus.AVAILABLE.value, 0),
            in_use=status_counts.get(AssetStatus.IN_USE.value, 0),
            broken=status_counts.get(AssetStatus.BROKEN.value, 0),
            under_repair=status_counts.get(AssetStatus.UNDER_REPAIR.value, 0),
            disposed=status_counts.get(AssetStatus.DISPOSED.value, 0),
            total_value=total_value,
            by_category=by_category
        )
    
    async def get_assets_by_location(self, location: str) -> List[Asset]:
        """Get all assets at a specific location"""
        result = await self.db.execute(
            select(Asset)
            .options(
                selectinload(Asset.category),
                selectinload(Asset.supplier)
            )
            .where(and_(
                Asset.is_active == True,
                Asset.location.ilike(f"%{location}%")
            ))
            .order_by(Asset.location, Asset.name)
        )
        return list(result.scalars().all())
    
    async def get_assets_by_user(self, user_id: str) -> List[Asset]:
        """Get all assets assigned to a user"""
        result = await self.db.execute(
            select(Asset)
            .options(
                selectinload(Asset.category),
                selectinload(Asset.supplier)
            )
            .where(and_(
                Asset.is_active == True,
                Asset.assigned_to_id == uuid.UUID(user_id)
            ))
            .order_by(Asset.name)
        )
        return list(result.scalars().all())
    
    async def get_warranty_expiring(
        self,
        days_ahead: int = 30
    ) -> List[Asset]:
        """Get assets with warranty expiring within specified days"""
        from datetime import timedelta
        
        expiry_date = date.today() + timedelta(days=days_ahead)
        
        result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.category))
            .where(and_(
                Asset.is_active == True,
                Asset.warranty_expiry != None,
                Asset.warranty_expiry <= expiry_date,
                Asset.warranty_expiry >= date.today()
            ))
            .order_by(Asset.warranty_expiry)
        )
        
        return list(result.scalars().all())
    
    # ==================== Bulk Operations ====================
    
    async def bulk_update_status(
        self,
        asset_ids: List[str],
        new_status: AssetStatus,
        performed_by_id: Optional[str] = None
    ) -> int:
        """Update status for multiple assets"""
        result = await self.db.execute(
            select(Asset).where(Asset.id.in_([
                uuid.UUID(aid) for aid in asset_ids
            ]))
        )
        assets = result.scalars().all()
        
        updated_count = 0
        for asset in assets:
            old_status = asset.status
            asset.status = new_status
            updated_count += 1
            logger.info(
                f"Bulk update: Asset {asset.asset_tag} status {old_status} -> {new_status}"
            )
        
        await self.db.commit()
        
        return updated_count
    
    async def generate_asset_tag(self, category_prefix: str = "AST") -> str:
        """Generate unique asset tag"""
        # Format: PREFIX-YYYY-XXXXXX
        year = datetime.utcnow().year
        prefix = f"{category_prefix}-{year}-"
        
        # Get count for this year
        result = await self.db.execute(
            select(func.count()).select_from(Asset)
            .where(Asset.asset_tag.like(f"{prefix}%"))
        )
        count = (result.scalar() or 0) + 1
        
        return f"{prefix}{count:06d}"
