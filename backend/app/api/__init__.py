"""
API Routes Package
"""

from app.api.auth import router as auth_router
from app.api.students import router as students_router

__all__ = ["auth_router", "students_router"]
