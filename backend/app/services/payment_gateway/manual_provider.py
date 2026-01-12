"""
Manual Payment Provider - Free Payment Recording

This provider allows administrators to record cash, cheque, and bank transfer payments
without any transaction fees. Ideal for schools that handle significant cash transactions.

Budget-friendly: $0 per transaction
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from app.services.payment_gateway.base import (
    PaymentProviderBase,
    PaymentProviderType,
    PaymentResult,
    ProviderConfig
)


class ManualPaymentProvider(PaymentProviderBase):
    """
    Manual payment provider for recording offline payments.
    
    Features:
    - Zero transaction fees
    - Supports cash, cheque, bank transfer
    - Automatic receipt number generation
    - Full audit trail
    
    Use cases:
    - Admin recording cash payments at school office
    - Cheque payments received
    - Bank transfer recordings
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or ProviderConfig(
            provider_type=PaymentProviderType.MANUAL,
            is_active=True,
            currency="INR",
            min_amount=Decimal("1.00")
        )
    
    @property
    def provider_type(self) -> PaymentProviderType:
        return PaymentProviderType.MANUAL
    
    async def process_payment(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Process a manual payment recording.
        
        Since this is manual recording, we generate a unique transaction ID
        and mark the payment as completed.
        """
        # Validate amount
        if amount < self.config.min_amount:
            return PaymentResult(
                success=False,
                message=f"Amount must be at least {self.config.min_amount}",
                error_code="INVALID_AMOUNT"
            )
        
        # Validate currency
        if currency.upper() != self.config.currency:
            return PaymentResult(
                success=False,
                message=f"Currency {currency} not supported. Use {self.config.currency}",
                error_code="INVALID_CURRENCY"
            )
        
        # Generate unique transaction ID
        # Format: MANUAL-YYYYMMDD-XXXXX
        timestamp = datetime.now().strftime("%Y%m%d")
        transaction_id = f"MANUAL-{timestamp}-{uuid.uuid4().hex[:8].upper()}"
        
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            status="completed",
            message="Payment recorded successfully",
            provider_data={
                "provider_type": "manual",
                "recorded_at": datetime.now().isoformat(),
                "reference": reference,
                "currency": currency,
                "amount": float(amount),
                "metadata": metadata or {}
            }
        )
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """
        Process a refund for a manual payment.
        
        Refunds for manual payments are recorded as new transactions
        with negative amounts.
        """
        # Verify this is a manual transaction
        if not transaction_id.startswith("MANUAL-"):
            return PaymentResult(
                success=False,
                message="Transaction ID does not match manual payment format",
                error_code="INVALID_TRANSACTION"
            )
        
        # Generate refund transaction ID
        timestamp = datetime.now().strftime("%Y%m%d")
        refund_id = f"REFUND-{timestamp}-{uuid.uuid4().hex[:8].upper()}"
        
        return PaymentResult(
            success=True,
            transaction_id=refund_id,
            status="refunded",
            message="Refund recorded successfully",
            provider_data={
                "original_transaction": transaction_id,
                "refund_amount": float(amount) if amount else "full",
                "refund_reason": reason,
                "refunded_at": datetime.now().isoformat()
            }
        )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify a manual payment transaction.
        
        For manual payments, we verify the format and return success
        since all recorded payments are considered valid.
        """
        # Check format
        if not transaction_id.startswith("MANUAL-"):
            return PaymentResult(
                success=False,
                message="Invalid transaction ID format",
                error_code="INVALID_FORMAT"
            )
        
        # Manual payments are always verified as they are recorded by admin
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            status="verified",
            message="Manual payment verified",
            provider_data={
                "verified_at": datetime.now().isoformat(),
                "provider_type": "manual"
            }
        )
    
    def is_available(self) -> bool:
        """
        Manual payment provider is always available.
        """
        return True


class BankTransferProvider(PaymentProviderBase):
    """
    Bank transfer payment provider for recording NEFT/RTGS/IMPS payments.
    
    Budget-friendly: $0 per transaction
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or ProviderConfig(
            provider_type=PaymentProviderType.BANK,
            is_active=True,
            currency="INR",
            min_amount=Decimal("1.00")
        )
    
    @property
    def provider_type(self) -> PaymentProviderType:
        return PaymentProviderType.BANK
    
    async def process_payment(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """Record a bank transfer payment"""
        if amount < self.config.min_amount:
            return PaymentResult(
                success=False,
                message=f"Amount must be at least {self.config.min_amount}",
                error_code="INVALID_AMOUNT"
            )
        
        # Generate transaction ID with BANK prefix
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        transaction_id = f"BANK-{timestamp}-{uuid.uuid4().hex[:6].upper()}"
        
        bank_ref = metadata.get("bank_reference", "") if metadata else ""
        
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            status="completed",
            message="Bank transfer recorded successfully",
            provider_data={
                "provider_type": "bank_transfer",
                "recorded_at": datetime.now().isoformat(),
                "reference": reference,
                "bank_reference": bank_ref,
                "currency": currency,
                "amount": float(amount)
            }
        )
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """Process bank transfer refund"""
        if not transaction_id.startswith("BANK-"):
            return PaymentResult(
                success=False,
                message="Invalid bank transaction ID",
                error_code="INVALID_TRANSACTION"
            )
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        refund_id = f"BANK-REF-{timestamp}"
        
        return PaymentResult(
            success=True,
            transaction_id=refund_id,
            status="refunded",
            message="Bank refund recorded",
            provider_data={
                "original_transaction": transaction_id,
                "refund_amount": float(amount) if amount else "full"
            }
        )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verify bank transfer"""
        if not transaction_id.startswith("BANK-"):
            return PaymentResult(
                success=False,
                error_code="INVALID_FORMAT"
            )
        
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            status="verified",
            provider_data={"verified_at": datetime.now().isoformat()}
        )
    
    def is_available(self) -> bool:
        return True
