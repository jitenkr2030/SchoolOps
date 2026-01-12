"""
SMS Provider Base Interface

Abstract base class defining the SMS provider interface.
All SMS providers must implement these methods.

Supports both free (Email-to-SMS, Mock) and paid (Twilio, Msg91) providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class SMSResult:
    """Result from SMS sending"""
    success: bool
    message_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None


class SMSProviderBase(ABC):
    """Abstract base class for all SMS providers"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        pass
    
    @abstractmethod
    async def send(
        self,
        phone_number: str,
        message: str,
        **kwargs
    ) -> SMSResult:
        """
        Send a single SMS
        
        Args:
            phone_number: Recipient phone number
            message: Message content
            **kwargs: Additional provider-specific options
            
        Returns:
            SMSResult with delivery details
        """
        pass
    
    @abstractmethod
    async def send_bulk(
        self,
        phone_numbers: list,
        message: str,
        **kwargs
    ) -> list:
        """
        Send SMS to multiple recipients
        
        Args:
            phone_numbers: List of recipient numbers
            message: Message content
            **kwargs: Additional options
            
        Returns:
            List of SMSResult for each recipient
        """
        pass
    
    @abstractmethod
    async def get_balance(self) -> float:
        """
        Get remaining credits/balance
        
        Returns:
            Available balance or -1 if not applicable
        """
        pass
    
    @abstractmethod
    async def get_delivery_status(self, message_id: str) -> str:
        """
        Check delivery status of a message
        
        Args:
            message_id: Provider's message ID
            
        Returns:
            Delivery status string
        """
        pass


@dataclass
class ProviderConfig:
    """Configuration for an SMS provider"""
    provider_name: str
    is_active: bool = True
    sender_id: str = "SCHOOL"
    country_code: str = "91"
    config: Optional[Dict[str, Any]] = None
