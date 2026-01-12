"""
Services Package
Contains business logic and external service integrations
"""

from app.services.ai_service import ai_service, SelfHostedAIService
from app.services.payment_service import PaymentService
from app.services.receipt_service import ReceiptGenerator, receipt_generator
from app.services.sms.notification_service import SMSNotificationService
from app.services.academic_service import AcademicService
from app.services.attendance_service import AttendanceService
from app.services.risk_detection_service import RiskDetectionService
from app.services.forecast_service import AcademicForecastService
from app.services.intelligent_notification_service import IntelligentNotificationService
from app.services.inventory_service import InventoryService
from app.services.asset_service import AssetService
from app.services.supplier_service import SupplierService
from app.services.library_service import LibraryService
from app.services.transport_service import TransportService
from app.services.hostel_service import HostelService
from app.services.communication_service import CommunicationService
from app.services.report_service import ReportService
from app.services.chat_manager import chat_manager, ConnectionManager

__all__ = [
    "ai_service", 
    "SelfHostedAIService", 
    "PaymentService", 
    "ReceiptGenerator", 
    "receipt_generator",
    "SMSNotificationService",
    "AcademicService",
    "AttendanceService",
    "RiskDetectionService",
    "AcademicForecastService",
    "IntelligentNotificationService",
    "InventoryService",
    "AssetService",
    "SupplierService",
    "LibraryService",
    "TransportService",
    "HostelService",
    "CommunicationService",
    "ReportService",
    "chat_manager",
    "ConnectionManager"
]
