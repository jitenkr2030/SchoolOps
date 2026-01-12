"""
Mock SMS Provider - Free Testing Provider

This provider simulates SMS sending for development and testing.
No actual messages are sent - logs are created for verification.

Budget-friendly: $0 per message
Use case: Development, testing, CI/CD pipelines
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from app.services.sms.base import SMSProviderBase, SMSResult, ProviderConfig


class MockSMSProvider(SMSProviderBase):
    """
    Mock SMS provider for testing environments.
    
    Features:
    - No SMS cost
    - Simulates sending delays
    - Generates realistic message IDs
    - Stores "sent" messages in memory for verification
    
    Usage:
    Set SMS_PROVIDER=mock in environment variables
    """
    
    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig(
            provider_name="mock",
            is_active=True,
            sender_id="SCHOOL",
            country_code="91"
        )
        # In-memory storage for testing (use database in production)
        self._sent_messages: List[Dict] = []
        self._delay_seconds = 0.1  # Simulated delay
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    @property
    def is_available(self) -> bool:
        return True
    
    async def send(
        self,
        phone_number: str,
        message: str,
        **kwargs
    ) -> SMSResult:
        """
        Simulate sending an SMS.
        
        In production, this would actually send via a paid provider.
        For testing, we simulate the process.
        """
        # Simulate network delay
        import asyncio
        await asyncio.sleep(self._delay_seconds)
        
        # Generate mock message ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message_id = f"MOCK-{timestamp}-{uuid.uuid4().hex[:8].upper()}"
        
        # Store message for verification
        sent_message = {
            "message_id": message_id,
            "phone_number": phone_number,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "provider": "mock",
            "status": "delivered",
            "kwargs": kwargs
        }
        self._sent_messages.append(sent_message)
        
        return SMSResult(
            success=True,
            message_id=message_id,
            status="delivered",
            message="Mock SMS sent successfully",
            provider_data={"sent_at": sent_message["sent_at"]},
            cost=0.0
        )
    
    async def send_bulk(
        self,
        phone_numbers: List[str],
        message: str,
        **kwargs
    ) -> List[SMSResult]:
        """
        Simulate sending bulk SMS.
        
        Returns a list of results for each recipient.
        """
        results = []
        for phone in phone_numbers:
            result = await self.send(phone, message, **kwargs)
            results.append(result)
        return results
    
    async def get_balance(self) -> float:
        """
        Mock balance - always unlimited for testing.
        """
        return float('inf')
    
    async def get_delivery_status(self, message_id: str) -> str:
        """
        Mock delivery status check.
        """
        # Verify message exists
        for msg in self._sent_messages:
            if msg["message_id"] == message_id:
                return "delivered"
        
        return "unknown"
    
    def get_sent_messages(self) -> List[Dict]:
        """
        Get all sent messages (for testing verification).
        """
        return self._sent_messages
    
    def clear_sent_messages(self):
        """
        Clear sent message history (for testing).
        """
        self._sent_messages = []
    
    def set_delay(self, seconds: float):
        """
        Set simulated delay for testing rate limiting.
        """
        self._delay_seconds = seconds
