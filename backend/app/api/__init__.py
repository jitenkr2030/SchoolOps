"""
API Routes Package
"""

from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.fees import router as fees_router
from app.api.payments import router as payments_router
from app.api.sms import router as sms_router
from app.api.staff import router as staff_router
from app.api.academics import router as academics_router
from app.api.attendance import router as attendance_router
from app.api.ai import router as ai_router
from app.api.inventory import router as inventory_router
from app.api.assets import router as assets_router
from app.api.suppliers import router as suppliers_router
from app.api.library import router as library_router
from app.api.transport import router as transport_router
from app.api.hostel import router as hostel_router
from app.api.communication import router as communication_router
from app.api.reports import router as reports_router

__all__ = [
    "auth_router", 
    "students_router", 
    "fees_router", 
    "payments_router", 
    "sms_router",
    "staff_router",
    "academics_router",
    "attendance_router",
    "ai_router",
    "inventory_router",
    "assets_router",
    "suppliers_router",
    "library_router",
    "transport_router",
    "hostel_router",
    "communication_router",
    "reports_router"
]
