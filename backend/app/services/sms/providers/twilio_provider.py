"""
Twilio SMS Provider - Paid SMS Gateway

Twilio is a popular SMS gateway with:
- Pay-as-you-go pricing (no monthly fees)
- Free test credentials available
- Reliable delivery worldwide
- Webhook support for status updates

Budget: ~$0.0079 per SMS (varies by country)
Free tier: Yes (test mode only)

Setup:
1. Create account at https://www.twilio.com
2. Get Account SID, Auth Token, and Phone Number
3. Add to .env file
"""

from datetime import datetime
from typing import List, Dict, Optional, Any

from app.config import settings
from app.services.sms.base import SMSProviderBase, SMSResult, ProviderConfig


class TwilioSMSProvider(SMSProviderBase):
    """
    Twilio SMS provider for reliable delivery.
    
    Features:
    - Pay-as-you-go pricing
    - High deliverability
    - Delivery webhooks
    - Message status tracking
    
    Required Configuration:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_PHONE_NUMBER
    """
    
    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig(
            provider_name="twilio",
            is_active=True,
            sender_id="SCHOOL",
            country_code="91",
            config={
                "account_sid": settings.TWILIO_ACCOUNT_SID if hasattr(settings, 'TWILIO_ACCOUNT_SID') else "",
                "auth_token": settings.TWILIO_AUTH_TOKEN if hasattr(settings, 'TWILIO_AUTH_TOKEN') else "",
                "phone_number": settings.TWILIO_PHONE_NUMBER if hasattr(settings, 'TWILIO_PHONE_NUMBER') else "",
            }
        )
        
        self._cfg = self.config.config or {}
        self._client = None
    
    @property
    def provider_name(self) -> str:
        return "twilio"
    
    @property
    def is_available(self) -> bool:
        """Check if Twilio is configured"""
        return bool(
            self._cfg.get("account_sid") and 
            self._cfg.get("auth_token") and 
            self._cfg.get("phone_number")
        )
    
    def _get_client(self):
        """Get or create Twilio client"""
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(
                    self._cfg["account_sid"],
                    self._cfg["auth_token"]
                )
            except ImportError:
                raise ImportError("Twilio library not installed. Run: pip install twilio")
        return self._client
    
    async def send(
        self,
        phone_number: str,
        message: str,
        **kwargs
    ) -> SMSResult:
        """
        Send SMS via Twilio API.
        """
        if not self.is_available:
            return SMSResult(
                success=False,
                error="Twilio not configured. Set TWILIO credentials in .env"
            )
        
        try:
            client = self._get_client()
            
            # Ensure phone number is in E.164 format
            formatted_number = self._format_phone(phone_number)
            
            # Send message (sync call in thread pool)
            import asyncio
            loop = asyncio.get_event_loop()
            
            def send_sync():
                return client.messages.create(
                    body=message,
                    from_=self._cfg["phone_number"],
                    to=formatted_number,
                    status_callback=f"{settings.API_BASE_URL}/api/v1/sms/webhook/twilio" if hasattr(settings, 'API_BASE_URL') else None
                )
            
            twilio_msg = await loop.run_in_executor(None, send_sync)
            
            return SMSResult(
                success=True,
                message_id=twilio_msg.sid,
                status=twilio_msg.status,
                message="SMS sent via Twilio",
                provider_data={
                    "sid": twilio_msg.sid,
                    "status": twilio_msg.status,
                    "price": str(twilio_msg.price) if twilio_msg.price else None,
                    "price_unit": twilio_msg.price_unit if twilio_msg.price_unit else None,
                    "date_created": str(twilio_msg.date_created)
                },
                cost=float(twilio_msg.price) if twilio_msg.price else 0.0
            )
            
        except Exception as e:
            return SMSResult(
                success=False,
                error=str(e)
            )
    
    async def send_bulk(
        self,
        phone_numbers: List[str],
        message: str,
        **kwargs
    ) -> List[SMSResult]:
        """
        Send bulk SMS via Twilio.
        
        Note: Twilio has rate limits. For large batches,
        consider using their Bulk API or implementing delays.
        """
        results = []
        client = self._get_client()
        
        for phone in phone_numbers:
            result = await self.send(phone, message, **kwargs)
            results.append(result)
            
            # Respect rate limits (66 messages/second for Twilio)
            await asyncio.sleep(0.1)
        
        return results
    
    async def get_balance(self) -> float:
        """
        Get remaining Twilio balance.
        """
        try:
            client = self._get_client()
            
            import asyncio
            loop = asyncio.get_event_loop()
            
            def fetch_balance():
                return client.balance.fetch()
            
            balance = await loop.run_in_executor(None, fetch_balance)
            return float(balance.balance)
            
        except Exception:
            return -1.0
    
    async def get_delivery_status(self, message_id: str) -> str:
        """
        Get delivery status from Twilio.
        """
        try:
            client = self._get_client()
            
            import asyncio
            loop = asyncio.get_event_loop()
            
            def fetch_message():
                return client.messages(message_id).fetch()
            
            msg = await loop.run_in_executor(None, fetch_message)
            return msg.status
            
        except Exception:
            return "unknown"
    
    def _format_phone(self, phone: str) -> str:
        """
        Format phone number to E.164 format.
        """
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, phone))
        
        # If starts with country code, add +
        if len(digits) > 10:
            return f"+{digits}"
        elif len(digits) == 10:
            # Add default country code (91 for India)
            return f"+{self.config.country_code}{digits}"
        else:
            return f"+{digits}"
    
    async def verify_phone_number(self, phone: str) -> Dict[str, Any]:
        """
        Verify a phone number using Twilio Lookup API.
        
        Returns carrier and other info if available.
        """
        try:
            from twilio.rest import Client
            
            client = self._get_client()
            
            import asyncio
            loop = asyncio.get_event_loop()
            
            def lookup():
                return client.lookups.v2.phone_numbers(phone).fetch()
            
            result = await loop.run_in_executor(None, lookup)
            
            return {
                "valid": result.valid,
                "phone_number": result.phone_number,
                "country_code": result.country_code,
                "carrier": result.carrier.name if result.carrier else None,
                "carrier_type": result.carrier.type if result.carrier else None
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
