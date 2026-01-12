"""
Database Models Package
Re-exports all database models for easy importing
"""

# Import from main models file
from app.models.models import (
    # Enums
    UserRole, Gender, AttendanceStatus, FeeStatus,
    
    # User & Auth
    User, UserProfile,
    
    # School & Admin
    School, SchoolUser, AcademicYear, Term,
    
    # Student & Guardian
    Student, Guardian, StudentGuardian, StudentClass,
    
    # Staff
    Staff, StaffSubject,
    
    # Academics
    Department, Class, Subject, ClassSubject, Timetable, TimetableSlot,
    Grade, GradeComponent,
    
    # Attendance
    Attendance, AttendanceSummary,
    
    # Finance
    FeeStructure, FeeCategory, Invoice, InvoiceLine, Payment,
    PaymentMethod, Receipt,
    
    # Transport
    Vehicle, Route, Stop, RouteStop, VehicleAssignment,
    
    # Notifications
    NotificationTemplate, Notification, NotificationLog,
    
    # AI & Analytics
    AIInsight, LearningPath,
    
    # Audit & Compliance
    AuditLog, DataRetentionPolicy
)

# Import from inventory models (Phase 6)
from app.db.models.inventory import (
    # Enums
    SupplierCategory, ItemType, AssetStatus, TransactionType,
    
    # Models
    Supplier, ItemCategory, Asset, AssetMaintenance,
    InventoryItem, StockTransaction, PurchaseOrder, PurchaseOrderDetail
)

# Import from library models (Phase 7)
from app.db.models.library import (
    # Enums
    BookCategory, MemberType, MemberStatus, TransactionStatus, ReservationStatus,
    
    # Models
    BookCatalog, BookCopy, LibraryMember, BookTransaction,
    BookReservation, FineRecord, LibrarySettings
)

__all__ = [
    # Enums
    "UserRole", "Gender", "AttendanceStatus", "FeeStatus",
    "SupplierCategory", "ItemType", "AssetStatus", "TransactionType",
    "BookCategory", "MemberType", "MemberStatus", "TransactionStatus", "ReservationStatus",
    
    # User & Auth
    "User", "UserProfile",
    
    # School & Admin
    "School", "SchoolUser", "AcademicYear", "Term",
    
    # Student & Guardian
    "Student", "Guardian", "StudentGuardian", "StudentClass",
    
    # Staff
    "Staff", "StaffSubject",
    
    # Academics
    "Department", "Class", "Subject", "ClassSubject", "Timetable", "TimetableSlot",
    "Grade", "GradeComponent",
    
    # Attendance
    "Attendance", "AttendanceSummary",
    
    # Finance
    "FeeStructure", "FeeCategory", "Invoice", "InvoiceLine", "Payment",
    "PaymentMethod", "Receipt",
    
    # Transport
    "Vehicle", "Route", "Stop", "RouteStop", "VehicleAssignment",
    
    # Inventory (Phase 6)
    "Supplier", "ItemCategory", "Asset", "AssetMaintenance",
    "InventoryItem", "StockTransaction", "PurchaseOrder", "PurchaseOrderDetail",
    
    # Library (Phase 7)
    "BookCatalog", "BookCopy", "LibraryMember", "BookTransaction",
    "BookReservation", "FineRecord", "LibrarySettings",
    
    # Notifications
    "NotificationTemplate", "Notification", "NotificationLog",
    
    # AI & Analytics
    "AIInsight", "LearningPath",
    
    # Audit & Compliance
    "AuditLog", "DataRetentionPolicy"
]
