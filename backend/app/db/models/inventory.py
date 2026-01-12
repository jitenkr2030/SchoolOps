"""
Inventory and Asset Database Models
SQLAlchemy models for inventory, assets, and supplier management
"""

import uuid
from decimal import Decimal
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Decimal, DateTime, Text, 
    ForeignKey, Enum, Boolean, Date, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class SupplierCategory(str, PyEnum):
    """Supplier category classification"""
    IT = "IT"
    FURNITURE = "FURNITURE"
    STATIONERY = "STATIONERY"
    GENERAL = "GENERAL"
    MAINTENANCE = "MAINTENANCE"
    CLEANING = "CLEANING"


class ItemType(str, PyEnum):
    """Item type classification"""
    ASSET = "ASSET"  # Individually tracked items
    INVENTORY = "INVENTORY"  # Bulk tracked items


class AssetStatus(str, PyEnum):
    """Asset lifecycle status"""
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    BROKEN = "BROKEN"
    UNDER_REPAIR = "UNDER_REPAIR"
    DISPOSED = "DISPOSED"
    LOST = "LOST"


class TransactionType(str, PyEnum):
    """Inventory transaction types"""
    PURCHASE = "PURCHASE"
    CONSUMPTION = "CONSUMPTION"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    TRANSFER = "TRANSFER"
    WRITE_OFF = "WRITE_OFF"


class Supplier(Base):
    """
    Supplier model for vendor management
    
    Stores information about suppliers who provide goods
    and services to the school.
    """
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    category = Column(Enum(SupplierCategory), default=SupplierCategory.GENERAL)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    assets = relationship("Asset", back_populates="supplier", lazy="dynamic")
    inventory_items = relationship("InventoryItem", back_populates="supplier", lazy="dynamic")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class ItemCategory(Base):
    """
    Item category model for organizing inventory and assets
    
    Groups items by type (IT equipment, furniture, stationery, etc.)
    and classification (asset vs inventory).
    """
    __tablename__ = "item_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("item_categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Self-referential relationship for subcategories
    parent = relationship("ItemCategory", remote_side=[id], backref="subcategories")
    
    # Relationships
    assets = relationship("Asset", back_populates="category", lazy="dynamic")
    inventory_items = relationship("InventoryItem", back_populates="category", lazy="dynamic")
    
    def __repr__(self):
        return f"<ItemCategory(id={self.id}, name='{self.name}', type={self.item_type})>"


class Asset(Base):
    """
    Asset model for individually tracked school property
    
    Tracks high-value items like laptops, furniture, and equipment
    that require individual identification and assignment tracking.
    """
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    asset_tag = Column(String(50), nullable=False, unique=True)
    serial_number = Column(String(100), nullable=True)
    
    # Categorization
    category_id = Column(UUID(as_uuid=True), ForeignKey("item_categories.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    
    # Financial information
    purchase_date = Column(Date, nullable=True)
    purchase_cost = Column(Decimal(12, 2), nullable=True)
    current_value = Column(Decimal(12, 2), nullable=True)  # Depreciated value
    depreciation_rate = Column(Decimal(5, 2), default=Decimal("10.00"))  # Annual %
    
    # Status and tracking
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE)
    location = Column(String(200), nullable=True)  # Room or location description
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True)  # User ID
    assigned_date = Column(Date, nullable=True)
    
    # Additional details
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)  # JSON or detailed specs
    warranty_expiry = Column(Date, nullable=True)
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("ItemCategory", back_populates="assets")
    supplier = relationship("Supplier", back_populates="assets")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset", lazy="dynamic")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, tag='{self.asset_tag}', name='{self.name}')>"


class AssetMaintenance(Base):
    """
    Asset maintenance and repair tracking
    
    Records maintenance activities and repairs for assets.
    """
    __tablename__ = "asset_maintenance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    
    maintenance_type = Column(String(50), nullable=False)  # REPAIR, SERVICE, INSPECTION
    description = Column(Text, nullable=False)
    cost = Column(Decimal(12, 2), nullable=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, CANCELLED
    
    performed_by = Column(String(200), nullable=True)  # Vendor or internal staff
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    
    def __repr__(self):
        return f"<AssetMaintenance(id={self.id}, asset_id={self.asset_id})>"


class InventoryItem(Base):
    """
    Inventory item model for bulk-tracked supplies
    
    Manages consumable items like stationery, cleaning supplies,
    and other materials that are tracked by quantity.
    """
    __tablename__ = "inventory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    sku = Column(String(50), nullable=False, unique=True)
    
    # Categorization
    category_id = Column(UUID(as_uuid=True), ForeignKey("item_categories.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    
    # Stock information
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    unit_of_measure = Column(String(50), default="Unit")  # Box, Pack, Unit, Kg, etc.
    reorder_level = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    
    # Financial information
    cost_per_unit = Column(Decimal(12, 2), nullable=True)
    last_purchase_price = Column(Decimal(12, 2), nullable=True)
    
    # Location
    storage_location = Column(String(200), nullable=True)
    
    # Additional details
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    barcode = Column(String(100), nullable=True)
    
    # Tracking
    is_active = Column(Boolean, default=True)
    track_expiry = Column(Boolean, default=False)
    expiry_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("ItemCategory", back_populates="inventory_items")
    supplier = relationship("Supplier", back_populates="inventory_items")
    transactions = relationship("StockTransaction", back_populates="item", lazy="dynamic")
    
    @property
    def is_low_stock(self) -> bool:
        """Check if item is below reorder level"""
        return self.quantity_on_hand <= self.reorder_level
    
    @property
    def needs_reorder(self) -> bool:
        """Check if item needs to be reordered"""
        return self.quantity_on_hand <= self.reorder_level and self.supplier_id is not None
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class StockTransaction(Base):
    """
    Stock transaction audit trail
    
    Records all changes to inventory quantities for audit
    and traceability purposes.
    """
    __tablename__ = "stock_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)  # Positive or negative
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    
    # Reference information
    reference_type = Column(String(50), nullable=True)  # PURCHASE_ORDER, CONSUMPTION, etc.
    reference_id = Column(String(100), nullable=True)  # External reference
    
    # User tracking
    performed_by_id = Column(UUID(as_uuid=True), nullable=True)
    performed_by_name = Column(String(100), nullable=True)
    
    # Details
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")
    
    def __repr__(self):
        return f"<StockTransaction(id={self.id}, type={self.transaction_type}, qty={self.quantity_change})>"


class PurchaseOrder(Base):
    """
    Purchase order for inventory replenishment
    
    Tracks purchase orders to suppliers for inventory restocking.
    """
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), nullable=False, unique=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    
    status = Column(String(20), default="DRAFT")  # DRAFT, PENDING, APPROVED, ORDERED, RECEIVED, CANCELLED
    
    order_date = Column(Date, nullable=False)
    expected_delivery = Column(Date, nullable=True)
    actual_delivery = Column(Date, nullable=True)
    
    # Financial
    subtotal = Column(Decimal(12, 2), default=Decimal("0.00"))
    tax_amount = Column(Decimal(12, 2), default=Decimal("0.00"))
    total_amount = Column(Decimal(12, 2), default=Decimal("0.00"))
    
    # Details
    notes = Column(Text, nullable=True)
    created_by_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier")
    details = relationship("PurchaseOrderDetail", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, order_number='{self.order_number}')>"


class PurchaseOrderDetail(Base):
    """
    Purchase order line items
    
    Individual items within a purchase order.
    """
    __tablename__ = "purchase_order_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0)
    
    unit_price = Column(Decimal(12, 2), nullable=False)
    total_price = Column(Decimal(12, 2), nullable=False)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship("PurchaseOrder", back_populates="details")
    item = relationship("InventoryItem")
    
    def __repr__(self):
        return f"<PurchaseOrderDetail(id={self.id}, item_id={self.item_id}, qty={self.quantity_ordered})>"
