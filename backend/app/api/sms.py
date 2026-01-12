"""
SMS API endpoints
SMS sending, template management, and notification handling
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.schema.sms_schema import (
    SMSRequest, SMSResponse, BulkSMSResponse, SMSTemplateCreate,
    SMSTemplateResponse, SMSTemplateUpdate, SMSLogResponse, SMSLogFilter,
    SMSPaginatedResponse, SMSApiResponse, NotificationType, SMSStatus
)
from app.services.sms.notification_service import SMSNotificationService, initialize_default_templates
from app.services.sms.factory import get_sms_provider
from app.core.security import get_current_user, require_admin, require_staff


router = APIRouter(prefix="/sms", tags=["SMS Notifications"])


# ==================== SMS Sending ====================

@router.post("/send", response_model=SMSResponse)
async def send_sms(
    request: SMSRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send a single SMS message.
    
    Requires authentication.
    Admins and staff can send to any number.
    """
    service = SMSNotificationService(db)
    
    return await service.send_sms(
        phone_number=request.phone_number,
        message=request.message,
        notification_type=request.notification_type if hasattr(request, 'notification_type') else None
    )


@router.post("/send/template", response_model=SMSResponse)
async def send_sms_from_template(
    phone_number: str,
    template_slug: str,
    variables: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send SMS using a template.
    
    Args:
        phone_number: Recipient phone number
        template_slug: Template identifier
        variables: Template variable values
    """
    service = SMSNotificationService(db)
    
    return await service.send_from_template(
        phone_number=phone_number,
        template_slug=template_slug,
        variables=variables
    )


@router.post("/bulk", response_model=BulkSMSResponse)
async def send_bulk_sms(
    phone_numbers: List[str],
    message: Optional[str] = None,
    template_slug: Optional[str] = None,
    template_vars: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Send SMS to multiple recipients.
    
    Requires admin privileges.
    Use template or direct message (not both).
    """
    if not message and not template_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either message or template_slug required"
        )
    
    if len(phone_numbers) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 1000 recipients per bulk SMS"
        )
    
    service = SMSNotificationService(db)
    
    # Get template if specified
    if template_slug:
        template = await service.get_template(template_slug)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found: {template_slug}"
            )
        
        # Render template for each number
        rendered_message = service.render_template(template.content, template_vars or {})
    else:
        rendered_message = message
    
    return await service.send_bulk_sms(
        phone_numbers=phone_numbers,
        message=rendered_message,
        notification_type=template.notification_type if template_slug else None
    )


# ==================== Template Management ====================

@router.get("/templates", response_model=List[SMSTemplateResponse])
async def list_templates(
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff)
):
    """
    List all SMS templates.
    Requires staff privileges.
    """
    service = SMSNotificationService(db)
    templates = await service.list_templates(notification_type)
    return templates


@router.post("/templates", response_model=SMSApiResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: SMSTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new SMS template.
    Requires admin privileges.
    """
    service = SMSNotificationService(db)
    
    result = await service.create_template(
        name=template.name,
        slug=template.slug,
        content=template.content,
        notification_type=template.notification_type.value if template.notification_type else None,
        description=template.description
    )
    
    return SMSApiResponse(
        success=True,
        message="Template created successfully",
        data=result
    )


@router.put("/templates/{slug}", response_model=SMSApiResponse)
async def update_template(
    slug: str,
    update: SMSTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update an existing template.
    Requires admin privileges.
    """
    from app.models.models import SMSTemplate
    
    result = await db.execute(
        select(SMSTemplate).where(SMSTemplate.slug == slug)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    update_data = update.model_dump(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(template, key, value)
        
        await db.commit()
    
    return SMSApiResponse(
        success=True,
        message="Template updated successfully"
    )


@router.delete("/templates/{slug}", response_model=SMSApiResponse)
async def delete_template(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Deactivate a template (soft delete).
    Requires admin privileges.
    """
    from app.models.models import SMSTemplate
    
    result = await db.execute(
        select(SMSTemplate).where(SMSTemplate.slug == slug)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template.is_active = False
    await db.commit()
    
    return SMSApiResponse(
        success=True,
        message="Template deactivated"
    )


# ==================== SMS History ====================

@router.get("/history", response_model=SMSPaginatedResponse)
async def get_sms_history(
    phone_number: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff)
):
    """
    Get SMS delivery history.
    Requires staff privileges.
    """
    service = SMSNotificationService(db)
    
    return await service.get_sms_history(
        phone_number=phone_number,
        status=SMSStatus(status) if status else None,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )


@router.get("/stats", response_model=SMSApiResponse)
async def get_delivery_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_staff)
):
    """
    Get SMS delivery statistics.
    Requires staff privileges.
    """
    service = SMSNotificationService(db)
    stats = await service.get_delivery_stats()
    
    return SMSApiResponse(
        success=True,
        message="Statistics retrieved",
        data=stats
    )


# ==================== Webhooks ====================

@router.post("/webhook/twilio")
async def twilio_webhook(
    MessageSid: str = Query(...),
    MessageStatus: str = Query(...),
    To: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Receive delivery status from Twilio.
    Configure Twilio to send status callbacks to this endpoint.
    """
    from app.models.models import SMSLog, SMSStatus as DBSMSStatus
    
    # Map Twilio status to our status
    status_map = {
        "delivered": DBSMSStatus.DELIVERED,
        "sent": DBSMSStatus.SENT,
        "failed": DBSMSStatus.FAILED,
        "undelivered": DBSMSStatus.FAILED,
    }
    
    # Update log
    result = await db.execute(
        select(SMSLog).where(SMSLog.message_id == MessageSid)
    )
    log = result.scalar_one_or_none()
    
    if log:
        log.status = status_map.get(MessageStatus, DBSMSStatus.PENDING)
        if MessageStatus == "delivered":
            log.delivered_at = datetime.now()
        await db.commit()
    
    return {"received": True}


# ==================== Provider Status ====================

@router.get("/provider/status", response_model=SMSApiResponse)
async def get_provider_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Get current SMS provider status and balance.
    Requires admin privileges.
    """
    provider = get_sms_provider()
    
    balance = await provider.get_balance()
    
    return SMSApiResponse(
        success=True,
        message="Provider status",
        data={
            "provider": provider.provider_name,
            "is_available": provider.is_available,
            "balance": balance if balance != float('inf') else "unlimited"
        }
    )


# ==================== Initialize Templates ====================

@router.post("/templates/initialize", response_model=SMSApiResponse)
async def init_default_templates(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Initialize default SMS templates.
    Requires admin privileges.
    """
    await initialize_default_templates(db)
    
    return SMSApiResponse(
        success=True,
        message="Default templates initialized"
    )
