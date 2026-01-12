"""
Payment Gateway Base Interface

Abstract base class defining the payment provider interface.
All payment providers must implement these methods.

This follows the Strategy Pattern for extensibility.
Supports both free (manual/cash) and paid (Stripe/Razorpay) providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal
from enum import Enum


class PaymentProviderType(str, Enum):
    """Payment provider types"""
    MANUAL = "manual"      # Free - Admin records cash/cheque
    STRIPE = "stripe"      # Paid - Stripe payment processor
    RAZORPAY = "razorpay"  # Paid - Razorpay payment processor
    BANK = "bank"          # Free - Bank transfer recording


@dataclass
class PaymentResult:
    """Result from payment processing"""
    success: bool
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class PaymentProviderBase(ABC):
    """Abstract base class for all payment providers"""
    
    @property
    @abstractmethod
    def provider_type(self) -> PaymentProviderType:
        """Return the provider type identifier"""
        pass
    
    @abstractmethod
    async def process_payment(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Process a payment transaction
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., INR, USD)
            reference: Internal reference/description
            metadata: Additional metadata for the transaction
            
        Returns:
            PaymentResult with transaction details
        """
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """
        Process a refund for a previous payment
        
        Args:
            transaction_id: Original transaction ID to refund
            amount: Refund amount (full refund if None)
            reason: Reason for refund
            
        Returns:
            PaymentResult with refund details
        """
        pass
    
    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify the status of a payment
        
        Args:
            transaction_id: Transaction ID to verify
            
        Returns:
            PaymentResult with verification status
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is configured and available
        
        Returns:
            True if provider can process payments
        """
        pass


@dataclass
class ProviderConfig:
    """Configuration for a payment provider"""
    provider_type: PaymentProviderType
    is_active: bool = True
    currency: str = "INR"
    min_amount: Decimal = Decimal("1.00")
    max_amount: Optional[Decimal] = None
    config: Optional[Dict[str, Any]] = None
