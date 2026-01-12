"""
Schema Package
"""

from app.schema.auth_schema import *
from app.schema.student_schema import *
from app.schema.payment_schema import *
from app.schema.sms_schema import *
from app.schema.academic_schema import *
from app.schema.attendance_schema import *
from app.schema.ai_schema import *
from app.schema.inventory_schema import *
from app.schema.library_schema import *
from app.schema.transport_schema import *
from app.schema.hostel_schema import *
from app.schema.communication_schema import *
from app.schema.report_schema import *

__all__ = [
    "auth_schema", 
    "student_schema", 
    "payment_schema", 
    "sms_schema",
    "academic_schema",
    "attendance_schema",
    "ai_schema",
    "inventory_schema",
    "library_schema",
    "transport_schema",
    "hostel_schema",
    "communication_schema",
    "report_schema"
]
