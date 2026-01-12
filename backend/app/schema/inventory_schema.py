"""
Inventory and Asset Management Schemas
Pydantic models for inventory, assets, and supplier operations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==================== Enums ====================

class SupplierCategory(str, Enum):
    """Supplier category classification"""
    IT = "IT"
    FURNITURE = "FURNITURE"
    STATIONERY = "STATIONERY"
    GENERAL = "GENERAL"
    MAINTENANCE = "MAINTENANCE"
    CLEANING = "CLEANING"


class ItemType(str, Enum):
    """Item type classification"""
    ASSET = "ASSET"
    INVENTORY = "INVENTORY"


class AssetStatus(str, Enum):
    """Asset lifecycle status"""
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    BROKEN = "BROKEN"
    UNDER_REPAIR = "UNDER_REPAIR"
    DISPOSED = "DISPOSED"
    LOST = "LOST"


class TransactionType(str, Enum):
    """Inventory transaction types"""
    PURCHASE = "PURCHASE"
    CONSUMPTION = "CONSUMPTION"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    TRANSFER = "TRANSFER"
    WRITE_OFF = "WRITE_OFF"


class PurchaseOrderStatus(str, Enum):
    """Purchase order status"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ORDERED = "ORDERED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


# ==================== Supplier Schemas ====================

class SupplierBase(BaseModel):
    """Base supplier schema"""
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    category: SupplierCategory = SupplierCategory.GENERAL
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    category: Optional[SupplierCategory] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Schema for supplier response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    assets_count: int = 0
    inventory_count: int = 0


class SupplierListResponse(BaseModel):
    """Paginated supplier list response"""
    suppliers: List[SupplierResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Item Category Schemas ====================

class ItemCategoryBase(BaseModel):
    """Base item category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    item_type: ItemType
    description: Optional[str] = None


class ItemCategoryCreate(ItemCategoryBase):
    """Schema for creating an item category"""
    parent_id: Optional[str] = None


class ItemCategoryUpdate(BaseModel):
    """Schema for updating an item category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ItemCategoryResponse(ItemCategoryBase):
    """Schema for item category response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    parent_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==================== Asset Schemas ====================

class AssetBase(BaseModel):
    """Base asset schema"""
    name: str = Field(..., min_length=1, max_length=200)
    asset_tag: str = Field(..., min_length=1, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=100)
    
    # Categorization
    category_id: str
    supplier_id: Optional[str] = None
    
    # Financial information
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = Field(None, ge=0)
    depreciation_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Status and tracking
    status: AssetStatus = AssetStatus.AVAILABLE
    location: Optional[str] = Field(None, max_length=200)
    
    # Additional details
    description: Optional[str] = None
    specifications: Optional[str] = None
    warranty_expiry: Optional[date] = None


class AssetCreate(AssetBase):
    """Schema for creating an asset"""
    pass
    
    @field_validator('purchase_cost')
    @classmethod
    def validate_purchase_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Purchase cost must be non-negative')
        return v


class AssetUpdate(BaseModel):
    """Schema for updating an asset"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    specifications: Optional[str] = None
    status: Optional[AssetStatus] = None
    current_value: Optional[Decimal] = Field(None, ge=0)


class AssetAssignment(BaseModel):
    """Schema for assigning an asset to a user or location"""
    assigned_to_id: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class AssetUnassignment(BaseModel):
    """Schema for unassigning an asset"""
    notes: Optional[str] = None


class AssetResponse(AssetBase):
    """Schema for asset response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    current_value: Optional[Decimal]
    assigned_to_id: Optional[str]
    assigned_date: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None


class AssetListResponse(BaseModel):
    """Paginated asset list response"""
    assets: List[AssetResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AssetStatsResponse(BaseModel):
    """Asset statistics response"""
    total_assets: int
    available: int
    in_use: int
    broken: int
    under_repair: int
    disposed: int
    total_value: Decimal
    by_category: Dict[str, int]


# ==================== Asset Maintenance Schemas ====================

class AssetMaintenanceBase(BaseModel):
    """Base asset maintenance schema"""
    maintenance_type: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    cost: Optional[Decimal] = Field(None, ge=0)
    start_date: date
    end_date: Optional[date] = None
    performed_by: Optional[str] = None
    notes: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    """Schema for creating maintenance record"""
    asset_id: str


class AssetMaintenanceResponse(AssetMaintenanceBase):
    """Schema for maintenance response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    asset_id: str
    status: str
    created_at: datetime
    updated_at: datetime


# ==================== Inventory Schemas ====================

class InventoryBase(BaseModel):
    """Base inventory item schema"""
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    
    # Categorization
    category_id: str
    supplier_id: Optional[str] = None
    
    # Stock information
    quantity_on_hand: int = Field(default=0, ge=0)
    unit_of_measure: str = Field(default="Unit", max_length=50)
    reorder_level: int = Field(default=10, ge=0)
    reorder_quantity: int = Field(default=50, ge=1)
    
    # Financial information
    cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    
    # Location
    storage_location: Optional[str] = Field(None, max_length=200)
    
    # Additional details
    description: Optional[str] = None
    specifications: Optional[str] = None
    barcode: Optional[str] = Field(None, max_length=100)


class InventoryCreate(InventoryBase):
    """Schema for creating an inventory item"""
    pass


class InventoryUpdate(BaseModel):
    """Schema for updating an inventory item"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    reorder_level: Optional[int] = Field(None, ge=0)
    reorder_quantity: Optional[int] = Field(None, ge=1)
    cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    storage_location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    specifications: Optional[str] = None
    track_expiry: Optional[bool] = None
    expiry_date: Optional[date] = None


class StockAdjustment(BaseModel):
    """Schema for stock adjustment"""
    transaction_type: TransactionType
    quantity: int = Field(..., ne=0)  # Non-zero quantity
    notes: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


class StockAdjustmentResult(BaseModel):
    """Schema for stock adjustment result"""
    success: bool
    item_id: str
    item_name: str
    transaction_type: TransactionType
    quantity_before: int
    quantity_after: int
    transaction_id: str
    timestamp: datetime


class InventoryResponse(InventoryBase):
    """Schema for inventory item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    is_active: bool
    track_expiry: bool
    expiry_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_low_stock: bool
    needs_reorder: bool
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None


class InventoryListResponse(BaseModel):
    """Paginated inventory list response"""
    items: List[InventoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class LowStockAlert(BaseModel):
    """Low stock alert schema"""
    item_id: str
    item_name: str
    sku: str
    category_name: str
    quantity_on_hand: int
    reorder_level: int
    supplier_id: Optional[str]
    supplier_name: Optional[str]
    suggested_order_qty: int


class InventoryStatsResponse(BaseModel):
    """Inventory statistics response"""
    total_items: int
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    category_breakdown: Dict[str, int]


# ==================== Stock Transaction Schemas ====================

class StockTransactionResponse(BaseModel):
    """Schema for stock transaction response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    item_id: str
    transaction_type: TransactionType
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reference_type: Optional[str]
    reference_id: Optional[str]
    performed_by_id: Optional[str]
    performed_by_name: Optional[str]
    notes: Optional[str]
    timestamp: datetime


class StockTransactionListResponse(BaseModel):
    """Paginated transaction list response"""
    transactions: List[StockTransactionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Purchase Order Schemas ====================

class PurchaseOrderDetailBase(BaseModel):
    """Base purchase order detail schema"""
    item_id: str
    quantity_ordered: int = Field(..., ge=1)
    unit_price: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class PurchaseOrderCreate(BaseModel):
    """Schema for creating a purchase order"""
    supplier_id: str
    order_date: date
    expected_delivery: Optional[date] = None
    notes: Optional[str] = None
    details: List[PurchaseOrderDetailBase]


class PurchaseOrderUpdateStatus(BaseModel):
    """Schema for updating purchase order status"""
    status: PurchaseOrderStatus
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    """Schema for purchase order response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    order_number: str
    supplier_id: str
    status: PurchaseOrderStatus
    order_date: date
    expected_delivery: Optional[date]
    actual_delivery: Optional[date]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: Optional[str]
    created_by_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    supplier_name: Optional[str] = None


class PurchaseOrderListResponse(BaseModel):
    """Paginated purchase order list response"""
    orders: List[PurchaseOrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# ==================== Common Schemas ====================

class IdResponse(BaseModel):
    """Standard ID response"""
    id: str
    message: Optional[str] = None


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class DateRangeParams(BaseModel):
    """Date range parameters"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SupplierItemsResponse(BaseModel):
    """Response for supplier items"""
    supplier_id: str
    supplier_name: str
    assets: List[AssetResponse]
    inventory_items: List[InventoryResponse]
    total_assets: int
    total_inventory: int
