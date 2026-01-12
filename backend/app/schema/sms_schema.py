"""
Pydantic schemas for SMS operations
Comprehensive schemas for SMS notifications and messaging
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SMSProviderType(str, Enum):
    """SMS provider types"""
    MOCK = "mock"           # Free - Testing only
    EMAIL = "email"         # Free - Email to SMS gateway
    TWILIO = "twilio"       # Paid - International
    MSG91 = "msg91"         # Paid - Popular in India
    AWS_SNS = "aws_sns"     # Paid - AWS service
    BULK_SMS = "bulk_sms"   # Paid - Regional


class SMSStatus(str, Enum):
    """SMS delivery status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    PENDING = "pending"


class NotificationType(str, Enum):
    """Types of notifications"""
    FEE_REMINDER = "fee_reminder"
    FEE_PAID = "fee_paid"
    ATTENDANCE_ALERT = "attendance_alert"
    ABSENT_NOTIFICATION = "absent_notification"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_REMINDER = "meeting_reminder"
    GENERAL_ANNOUNCEMENT = "general_announcement"
    HOMEWORK_UPDATE = "homework_update"
    EXAM_SCHEDULE = "exam_schedule"
    RESULT_DECLARED = "result_declared"
    CUSTOM = "custom"


# ==================== SMS Request Schemas ====================

class SMSBase(BaseModel):
    """Base SMS schema"""
    phone_number: str = Field(..., min_length=10, max_length=15, description="Recipient phone number")
    message: str = Field(..., min_length=1, max_length=1600, description="Message content")


class SMSRequest(SMSBase):
    """Schema for sending single SMS"""
    provider: Optional[SMSProviderType] = Field(None, description="Specific provider (auto if not set)")
    is_promotional: bool = Field(False, description="Promotional vs transactional SMS")
    priority: int = Field(1, ge=1, le=5, description="Message priority")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule for later delivery")


class BulkSMSRequest(BaseModel):
    """Schema for bulk SMS sending"""
    phone_numbers: List[str] = Field(..., min_length=1, max_length=1000, description="Recipients")
    template_slug: Optional[str] = Field(None, description="Use template instead of message")
    template_vars: Optional[Dict[str, Any]] = Field(None, description="Template variables")
    message: Optional[str] = Field(None, description="Direct message (if no template)")
    provider: Optional[SMSProviderType] = None
    scheduled_at: Optional[datetime] = None


class SMSResponse(BaseModel):
    """Schema for SMS send response"""
    success: bool
    message_id: Optional[str] = None
    status: Optional[SMSStatus] = None
    error: Optional[str] = None


class BulkSMSResponse(BaseModel):
    """Schema for bulk SMS response"""
    success: bool
    job_id: str
    total_recipients: int
    queued_count: int
    message: str


# ==================== Template Schemas ====================

class SMSTemplateBase(BaseModel):
    """Base SMS template schema"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, description="Unique template identifier")
    content: str = Field(..., min_length=1, max_length=1600)


class SMSTemplateCreate(SMSTemplateBase):
    """Schema for creating template"""
    notification_type: Optional[NotificationType] = None
    description: Optional[str] = None
    is_active: bool = True


class SMSTemplateUpdate(BaseModel):
    """Schema for updating template"""
    name: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, max_length=1600)
    is_active: Optional[bool] = None


class SMSTemplateResponse(SMSTemplateBase):
    """Schema for template response"""
    id: int
    notification_type: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SMS Log Schemas ====================

class SMSLogResponse(BaseModel):
    """Schema for SMS log entry"""
    id: int
    message_id: str
    phone_number: str
    message_content: str
    provider: str
    status: SMSStatus
    notification_type: Optional[str]
    sent_at: datetime
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class SMSLogFilter(BaseModel):
    """Schema for filtering SMS logs"""
    phone_number: Optional[str] = None
    provider: Optional[SMSProviderType] = None
    status: Optional[SMSStatus] = None
    notification_type: Optional[NotificationType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


# ==================== Notification Schemas ====================

class FeeNotificationRequest(BaseModel):
    """Schema for fee-related notifications"""
    student_id: int
    notification_type: NotificationType  # fee_reminder, fee_paid
    fee_record_id: Optional[int] = None
    custom_message: Optional[str] = None


class AttendanceNotificationRequest(BaseModel):
    """Schema for attendance notifications"""
    student_id: int
    notification_type: NotificationType  # attendance_alert, absent_notification
    date: datetime
    period: Optional[int] = None
    notify_both_parents: bool = True


class MeetingNotificationRequest(BaseModel):
    """Schema for meeting notifications"""
    student_id: int
    parent_phone: str
    notification_type: NotificationType  # meeting_scheduled, meeting_reminder
    meeting_date: datetime
    teacher_name: str
    meeting_link: Optional[str] = None
    custom_message: Optional[str] = None


# ==================== Carrier Schemas ====================

class CarrierInfo(BaseModel):
    """Carrier information for email-to-SMS"""
    name: str
    email_gateway: str  # e.g., "number@txt.att.net"


# Pre-defined carrier gateways (India + International)
CARRIER_GATEWAYS = {
    # India
    "airtel": "number@airtelmail.com",
    "jio": "number@jiosms.com",
    "vi": "number@vodafone.in",
    "bsnl": "number@bsnl.co.in",
    # US
    "att": "number@txt.att.net",
    "verizon": "number@vtext.com",
    "tmobile": "number@tmomail.net",
    "sprint": "number@messaging.sprintpcs.com",
    # UK
    "vodafone_uk": "number@vodafone.co.uk",
    "o2_uk": "number@mmail.co.uk",
    "ee": "number@ee.co.uk",
    # Generic
    "default": "number@email2sms.com"
}


def get_carrier_gateway(carrier_name: str) -> str:
    """Get email gateway for a carrier"""
    return CARRIER_GATEWAYS.get(carrier_name.lower(), CARRIER_GATEWAYS["default"])


# ==================== API Response Schemas ====================

class SMSPaginatedResponse(BaseModel):
    """Paginated SMS log response"""
    success: bool
    message: str
    data: List[SMSLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class SMSApiResponse(BaseModel):
    """Generic SMS API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
