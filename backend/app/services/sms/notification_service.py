"""
SMS Notification Service

Business logic for SMS notifications with template support.
Handles message rendering, notification triggers, and delivery tracking.

Features:
- Template-based messaging
- Variable substitution
- Notification type handling
- Delivery tracking
- Integration with payment and attendance services
"""

import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import SMSTemplate, SMSLog, Student, User, UserProfile, Guardian
from app.schema.sms_schema import (
    SMSRequest, SMSResponse, BulkSMSResponse, SMSTemplateCreate,
    SMSStatus, NotificationType
)
from app.services.sms.factory import get_sms_provider
from app.services.sms.base import SMSProviderBase


class SMSNotificationService:
    """
    SMS notification service with template and provider support.
    
    Handles:
    - Template management
    - Message rendering
    - Provider selection
    - Delivery logging
    - Notification triggers
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider: SMSProviderBase = get_sms_provider()
    
    # ==================== Template Management ====================
    
    async def create_template(
        self,
        name: str,
        slug: str,
        content: str,
        notification_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new SMS template.
        """
        template = SMSTemplate(
            name=name,
            slug=slug,
            content=content,
            notification_type=notification_type,
            description=description,
            is_active=True
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return {
            "id": template.id,
            "slug": template.slug,
            "name": template.name
        }
    
    async def get_template(self, slug: str) -> Optional[SMSTemplate]:
        """
        Get template by slug.
        """
        result = await self.db.execute(
            select(SMSTemplate).where(
                and_(
                    SMSTemplate.slug == slug,
                    SMSTemplate.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_templates(
        self,
        notification_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all active templates.
        """
        query = select(SMSTemplate).where(SMSTemplate.is_active == True)
        
        if notification_type:
            query = query.where(SMSTemplate.notification_type == notification_type)
        
        query = query.order_by(SMSTemplate.name)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "slug": t.slug,
                "content": t.content,
                "notification_type": t.notification_type
            }
            for t in templates
        ]
    
    # ==================== Message Rendering ====================
    
    def render_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render template with variable substitution.
        
        Variables are marked with {{variable_name}} syntax.
        
        Example:
            template = "Hello {{name}}, your fee of {{amount}} is due."
            variables = {"name": "John", "amount": "₹5000"}
            result = "Hello John, your fee of ₹5000 is due."
        """
        rendered = template
        
        for key, value in variables.items():
            # Replace {{key}} or {{ key }} patterns
            patterns = [
                f"{{{{{key}}}}}",
                f"{{{{ {key} }}}}",
                f"{{{{{key.lower()}}}}}",  # Case insensitive
            ]
            for pattern in patterns:
                rendered = rendered.replace(pattern, str(value))
        
        return rendered
    
    # ==================== SMS Sending ====================
    
    async def send_sms(
        self,
        phone_number: str,
        message: str,
        notification_type: Optional[str] = None,
        student_id: Optional[int] = None,
        **kwargs
    ) -> SMSResponse:
        """
        Send a single SMS.
        """
        # Log the attempt
        log = SMSLog(
            message_id=f"MSG-{uuid.uuid4().hex[:12]}",
            phone_number=phone_number,
            message_content=message[:1600],  # Truncate for DB
            provider=self.provider.provider_name,
            status=SMSStatus.QUEUED,
            notification_type=notification_type,
            sent_at=datetime.now()
        )
        self.db.add(log)
        
        # Send via provider
        result = await self.provider.send(
            phone_number=phone_number,
            message=message,
            **kwargs
        )
        
        # Update log
        log.message_id = result.message_id or log.message_id
        log.status = SMSStatus.SENT if result.success else SMSStatus.FAILED
        log.error_message = result.error
        
        if result.success:
            log.status = SMSStatus.DELIVERED if result.status == "delivered" else SMSStatus.SENT
        
        await self.db.commit()
        
        return SMSResponse(
            success=result.success,
            message_id=result.message_id,
            status=log.status,
            error=result.error
        )
    
    async def send_from_template(
        self,
        phone_number: str,
        template_slug: str,
        variables: Dict[str, Any],
        notification_type: Optional[str] = None,
        **kwargs
    ) -> SMSResponse:
        """
        Send SMS using a template.
        """
        # Get template
        template = await self.get_template(template_slug)
        
        if not template:
            return SMSResponse(
                success=False,
                error=f"Template not found: {template_slug}"
            )
        
        # Render message
        message = self.render_template(template.content, variables)
        
        # Send
        return await self.send_sms(
            phone_number=phone_number,
            message=message,
            notification_type=notification_type or template.notification_type,
            **kwargs
        )
    
    async def send_bulk_sms(
        self,
        phone_numbers: List[str],
        message: str,
        notification_type: Optional[str] = None
    ) -> BulkSMSResponse:
        """
        Send SMS to multiple recipients.
        
        Note: For large batches, consider using background tasks.
        """
        results = await self.provider.send_bulk(phone_numbers, message)
        
        # Log all messages
        for i, (phone, result) in enumerate(zip(phone_numbers, results)):
            log = SMSLog(
                message_id=result.message_id or f"BULK-{i}",
                phone_number=phone,
                message_content=message[:1600],
                provider=self.provider.provider_name,
                status=SMSStatus.SENT if result.success else SMSStatus.FAILED,
                notification_type=notification_type,
                sent_at=datetime.now(),
                error_message=result.error
            )
            self.db.add(log)
        
        await self.db.commit()
        
        sent_count = sum(1 for r in results if r.success)
        
        return BulkSMSResponse(
            success=True,
            job_id=f"JOB-{uuid.uuid4().hex[:8]}",
            total_recipients=len(phone_numbers),
            queued_count=sent_count,
            message=f"Sent {sent_count}/{len(phone_numbers)} messages"
        )
    
    # ==================== Notification Triggers ====================
    
    async def notify_fee_payment(
        self,
        student_id: int,
        amount: float,
        payment_method: str
    ) -> SMSResponse:
        """
        Send fee payment confirmation to parent.
        """
        # Get student and parent info
        result = await self.db.execute(
            select(Student)
            .options(
                selectinload(Student.user).selectinload(UserProfile),
                selectinload(Student.guardians).selectinload(Guardian.user).selectinload(UserProfile)
            )
            .where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if not student:
            return SMSResponse(success=False, error="Student not found")
        
        profile = student.user.profile
        student_name = f"{profile.first_name} {profile.last_name}" if profile else "Student"
        
        # Try to send to first guardian
        if student.guardians:
            guardian = student.guardians[0]
            guardian_profile = guardian.user.profile
            phone = guardian_profile.phone if guardian_profile else None
            
            if phone:
                return await self.send_from_template(
                    phone_number=phone,
                    template_slug="fee_payment_received",
                    variables={
                        "student_name": student_name,
                        "amount": f"₹{amount:,.2f}",
                        "date": datetime.now().strftime("%d-%m-%Y"),
                        "method": payment_method
                    }
                )
        
        return SMSResponse(success=False, error="No guardian phone number found")
    
    async def notify_attendance(
        self,
        student_id: int,
        date: datetime,
        status: str,
        period: Optional[int] = None
    ) -> Optional[SMSResponse]:
        """
        Send attendance notification to parent.
        
        Triggered when student is marked absent.
        """
        if status != "absent":
            return None  # Only notify for absences
        
        # Get student info
        result = await self.db.execute(
            select(Student)
            .options(
                selectinload(Student.user).selectinload(UserProfile),
                selectinload(Student.guardians).selectinload(Guardian.user).selectinload(UserProfile)
            )
            .where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if not student:
            return None
        
        profile = student.user.profile
        student_name = f"{profile.first_name} {profile.last_name}" if profile else "Student"
        
        # Notify parent
        if student.guardians:
            for guardian in student.guardians:
                if guardian.is_emergency_contact:
                    guardian_profile = guardian.user.profile
                    phone = guardian_profile.phone if guardian_profile else None
                    
                    if phone:
                        return await self.send_from_template(
                            phone_number=phone,
                            template_slug="attendance_absent_alert",
                            variables={
                                "student_name": student_name,
                                "date": date.strftime("%d-%m-%Y"),
                                "period": f"Period {period}" if period else "Full Day"
                            }
                        )
        
        return None
    
    # ==================== History & Logs ====================
    
    async def get_sms_history(
        self,
        phone_number: Optional[str] = None,
        status: Optional[SMSStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get SMS delivery history with filters.
        """
        query = select(SMSLog)
        
        if phone_number:
            query = query.where(SMSLog.phone_number.contains(phone_number))
        if status:
            query = query.where(SMSLog.status == status)
        if start_date:
            query = query.where(SMSLog.sent_at >= start_date)
        if end_date:
            query = query.where(SMSLog.sent_at <= end_date)
        
        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Paginate
        query = query.order_by(SMSLog.sent_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": log.id,
                    "message_id": log.message_id,
                    "phone_number": log.phone_number,
                    "message": log.message_content,
                    "provider": log.provider,
                    "status": log.status.value,
                    "sent_at": log.sent_at.isoformat() if log.sent_at else None
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    async def get_delivery_stats(self) -> Dict[str, Any]:
        """
        Get SMS delivery statistics.
        """
        result = await self.db.execute(
            select(
                func.count(SMSLog.id).label("total"),
                func.sum(func.cast(SMSLog.status == SMSStatus.DELIVERED, Integer)).label("delivered"),
                func.sum(func.cast(SMSLog.status == SMSStatus.FAILED, Integer)).label("failed")
            )
        )
        stats = result.one()
        
        return {
            "total_sent": stats.total or 0,
            "delivered": stats.delivered or 0,
            "failed": stats.failed or 0,
            "delivery_rate": (stats.delivered / stats.total * 100) if stats.total else 0
        }


# Import for type checking
from sqlalchemy.sql.expression import cast
from sqlalchemy import Integer

# Create table if not exists for SMSLog
from app.models.models import Base

# Default templates
DEFAULT_TEMPLATES = [
    {
        "slug": "fee_payment_received",
        "name": "Fee Payment Received",
        "content": "Dear Parent, We have received payment of {{amount}} for {{student_name}} on {{date}} via {{method}}. Thank you!",
        "notification_type": "fee_paid"
    },
    {
        "slug": "fee_reminder",
        "name": "Fee Payment Reminder",
        "content": "Dear Parent, This is a reminder that fee payment of {{amount}} for {{student_name}} is due on {{due_date}}. Please pay at the earliest.",
        "notification_type": "fee_reminder"
    },
    {
        "slug": "attendance_absent_alert",
        "name": "Absent Alert",
        "content": "Dear Parent, {{student_name}} was marked absent on {{date}} ({{period}}). Please contact the school if this is unexpected.",
        "notification_type": "absent_notification"
    },
    {
        "slug": "meeting_scheduled",
        "name": "Meeting Scheduled",
        "content": "Dear Parent, A meeting has been scheduled with {{teacher_name}} on {{date}} at {{time}}. {{meeting_link}}",
        "notification_type": "meeting_scheduled"
    }
]


async def initialize_default_templates(db: AsyncSession):
    """
    Initialize default SMS templates.
    Call this on app startup.
    """
    for template_data in DEFAULT_TEMPLATES:
        # Check if exists
        result = await db.execute(
            select(SMSTemplate).where(SMSTemplate.slug == template_data["slug"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            template = SMSTemplate(**template_data, is_active=True)
            db.add(template)
    
    await db.commit()
