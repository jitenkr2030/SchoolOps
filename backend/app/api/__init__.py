"""
API Routes Package
"""

from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.fees import router as fees_router
from app.api.payments import router as payments_router
from app.api.sms import router as sms_router

__all__ = ["auth_router", "students_router", "fees_router", "payments_router", "sms_router"]
