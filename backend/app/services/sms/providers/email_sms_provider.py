"""
Email-to-SMS Provider - Free SMS Gateway

This provider sends SMS via carrier email gateways.
Most carriers provide email-to-SMS services for free.

Budget-friendly: $0 per message
Supported carriers: Major Indian and international carriers

How it works:
1. Map phone number to carrier email gateway
2. Send email to: number@gateway.carrier.com
3. Carrier delivers as SMS to the phone

Example: 9876543210@vtext.com (Verizon)

Note: Requires carrier information for each phone number.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from app.config import settings
from app.services.sms.base import SMSProviderBase, SMSResult, ProviderConfig
from app.schema.sms_schema import get_carrier_gateway


class EmailToSMSProvider(SMSProviderBase):
    """
    Email-to-SMS provider using SMTP.
    
    Sends SMS by emailing carrier gateways.
    Free but requires SMTP configuration.
    
    Setup:
    1. Configure SMTP settings in .env
    2. Optionally specify carrier for each number
    3. Falls back to default gateway if carrier unknown
    """
    
    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig(
            provider_name="email",
            is_active=True,
            sender_id="SCHOOL",
            country_code="91",
            config={
                "smtp_host": settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else "smtp.gmail.com",
                "smtp_port": settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587,
                "smtp_user": settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else "",
                "smtp_password": settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else "",
                "from_email": settings.SMS_FROM_EMAIL if hasattr(settings, 'SMS_FROM_EMAIL') else "",
                "from_name": settings.SMS_FROM_NAME if hasattr(settings, 'SMS_FROM_NAME') else "SchoolOps"
            }
        )
        
        self._smtp_config = self.config.config or {}
    
    @property
    def provider_name(self) -> str:
        return "email"
    
    @property
    def is_available(self) -> bool:
        """Check if SMTP is configured"""
        return bool(self._smtp_config.get("smtp_user") and 
                   self._smtp_config.get("smtp_password"))
    
    def _get_gateway_email(self, phone_number: str, carrier: Optional[str] = None) -> str:
        """
        Get the email address for a phone number's carrier gateway.
        
        Args:
            phone_number: Phone number (will be cleaned)
            carrier: Optional carrier name (if known)
            
        Returns:
            Email address for the carrier's SMS gateway
        """
        # Clean phone number - remove non-digits
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # If carrier specified, use its gateway
        if carrier:
            gateway = get_carrier_gateway(carrier)
            return gateway.replace("number", clean_number)
        
        # Return default gateway (you might want to implement number-to-carrier lookup)
        gateway = get_carrier_gateway("default")
        return gateway.replace("number", clean_number)
    
    async def send(
        self,
        phone_number: str,
        message: str,
        carrier: Optional[str] = None,
        subject: str = "SchoolOps Notification",
        **kwargs
    ) -> SMSResult:
        """
        Send SMS via email to carrier gateway.
        """
        if not self.is_available:
            return SMSResult(
                success=False,
                error="Email-to-SMS not configured. Set SMTP credentials in .env"
            )
        
        try:
            # Get carrier gateway email
            gateway_email = self._get_gateway_email(phone_number, carrier)
            
            # Create email message
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = f"{self._smtp_config['from_name']} <{self._smtp_config['from_email']}>"
            msg['To'] = gateway_email
            
            # Send email (blocking, so run in thread pool)
            loop = asyncio.get_event_loop()
            
            def send_sync():
                server = smtplib.SMTP(
                    self._smtp_config['smtp_host'],
                    self._smtp_config['smtp_port']
                )
                server.starttls()
                server.login(
                    self._smtp_config['smtp_user'],
                    self._smtp_config['smtp_password']
                )
                server.send_message(msg)
                server.quit()
            
            await loop.run_in_executor(None, send_sync)
            
            # Generate message ID
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            message_id = f"EMAIL-{timestamp}-{hash(phone_number) % 10000:04d}"
            
            return SMSResult(
                success=True,
                message_id=message_id,
                status="sent",
                message="SMS sent via email gateway",
                provider_data={
                    "gateway_email": gateway_email,
                    "carrier": carrier or "unknown",
                    "sent_at": datetime.now().isoformat()
                },
                cost=0.0  # Free!
            )
            
        except smtplib.SMTPException as e:
            return SMSResult(
                success=False,
                error=f"SMTP error: {str(e)}"
            )
        except Exception as e:
            return SMSResult(
                success=False,
                error=f"Failed to send email SMS: {str(e)}"
            )
    
    async def send_bulk(
        self,
        phone_numbers: List[str],
        message: str,
        carriers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> List[SMSResult]:
        """
        Send bulk SMS via email.
        
        Note: Rate limits apply based on SMTP server.
        """
        results = []
        carriers = carriers or {}
        
        for phone in phone_numbers:
            carrier = carriers.get(phone)
            result = await self.send(phone, message, carrier=carrier, **kwargs)
            results.append(result)
            
            # Small delay to avoid triggering spam filters
            await asyncio.sleep(0.1)
        
        return results
    
    async def get_balance(self) -> float:
        """
        Email-to-SMS has no per-message cost.
        Returns infinite to indicate unlimited usage.
        """
        return float('inf')
    
    async def get_delivery_status(self, message_id: str) -> str:
        """
        Email-to-SMS doesn't provide delivery status.
        Returns 'sent' as we can't verify delivery.
        """
        if message_id.startswith("EMAIL-"):
            return "sent"
        return "unknown"
    
    async def check_smtp_connection(self) -> bool:
        """
        Verify SMTP connection is working.
        """
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((
                self._smtp_config['smtp_host'],
                self._smtp_config['smtp_port']
            ))
            sock.close()
            return result == 0
        except:
            return False
