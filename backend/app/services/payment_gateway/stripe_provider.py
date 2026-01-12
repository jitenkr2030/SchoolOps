"""
Stripe Payment Provider Integration

Stripe payment gateway integration with test mode support.
Stripe offers a generous free tier - no monthly fees, pay-as-you-go.

Budget: 2.9% + ₹3 per successful card transaction (Industry standard)
Free for test mode transactions
"""

import stripe
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any

from app.config import settings
from app.services.payment_gateway.base import (
    PaymentProviderBase,
    PaymentProviderType,
    PaymentResult,
    ProviderConfig
)


class StripePaymentProvider(PaymentProviderBase):
    """
    Stripe payment provider for online card payments and UPI.
    
    Setup Instructions:
    1. Create account at https://stripe.com
    2. Get API keys from Dashboard → Developers → API keys
    3. Add STRIPE_SECRET_KEY to .env file
    4. Use test keys for development, live keys for production
    
    Features:
    - Card payments (Visa, Mastercard, RuPay)
    - UPI payments
    - Automatic payment verification
    - Webhook support for real-time updates
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or ProviderConfig(
            provider_type=PaymentProviderType.STRIPE,
            is_active=True,
            currency="INR",
            min_amount=Decimal("1.00"),
            max_amount=Decimal("1000000.00"),  # 10L limit per transaction
            config={
                "api_key": settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None,
                "webhook_secret": settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else None
            }
        )
        
        # Initialize Stripe with API key
        if self.config.config.get("api_key"):
            stripe.api_key = self.config.config["api_key"]
    
    @property
    def provider_type(self) -> PaymentProviderType:
        return PaymentProviderType.STRIPE
    
    async def process_payment(
        self,
        amount: Decimal,
        currency: str,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Process a payment via Stripe PaymentIntent API.
        
        For production use, you would typically:
        1. Create a PaymentIntent on the server
        2. Confirm it from the client using Stripe.js
        3. Verify the webhook for completion
        
        This method handles the server-side portion.
        """
        # Validate Stripe is configured
        if not stripe.api_key:
            return PaymentResult(
                success=False,
                message="Stripe is not configured. Add STRIPE_SECRET_KEY to .env",
                error_code="STRIPE_NOT_CONFIGURED"
            )
        
        # Validate amount
        if amount < self.config.min_amount:
            return PaymentResult(
                success=False,
                message=f"Amount must be at least {self.config.min_amount}",
                error_code="INVALID_AMOUNT"
            )
        
        if self.config.max_amount and amount > self.config.max_amount:
            return PaymentResult(
                success=False,
                message=f"Amount exceeds maximum limit of {self.config.max_amount}",
                error_code="AMOUNT_TOO_HIGH"
            )
        
        try:
            # Convert amount to smallest currency unit (paise for INR)
            amount_in_smallest_unit = int(amount * 100)
            
            # Create PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_smallest_unit,
                currency=currency.lower(),
                description=reference,
                metadata={
                    **(metadata or {}),
                    "schoolops_reference": reference,
                    "created_at": datetime.now().isoformat()
                },
                automatic_payment_methods={
                    "enabled": True,
                }
            )
            
            return PaymentResult(
                success=True,
                transaction_id=payment_intent.id,
                status="pending",
                message="Payment intent created. Complete payment from client.",
                provider_data={
                    "client_secret": payment_intent.client_secret,
                    "amount": float(amount),
                    "currency": currency,
                    "status": payment_intent.status
                }
            )
            
        except stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                message=f"Card declined: {e.user_message}",
                error_code="CARD_DECLINED",
                provider_data={"stripe_error_code": e.code}
            )
        except stripe.error.InvalidRequestError as e:
            return PaymentResult(
                success=False,
                message="Invalid payment request",
                error_code="INVALID_REQUEST",
                provider_data={"error": str(e)}
            )
        except stripe.error.AuthenticationError:
            return PaymentResult(
                success=False,
                message="Stripe authentication failed. Check API keys.",
                error_code="AUTH_FAILED"
            )
        except Exception as e:
            return PaymentResult(
                success=False,
                message=f"Payment processing error: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """Process a refund via Stripe"""
        if not stripe.api_key:
            return PaymentResult(
                success=False,
                message="Stripe not configured",
                error_code="STRIPE_NOT_CONFIGURED"
            )
        
        try:
            # Create refund parameters
            refund_params = {
                "payment_intent": transaction_id,
                "reason": "requested_by_customer"
            }
            
            # Add amount if specified (partial refund)
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return PaymentResult(
                success=True,
                transaction_id=refund.id,
                status="refunded",
                message="Refund processed successfully",
                provider_data={
                    "original_transaction": transaction_id,
                    "refund_amount": float(amount) if amount else "full",
                    "status": refund.status
                }
            )
            
        except stripe.error.InvalidRequestError as e:
            return PaymentResult(
                success=False,
                message=f"Refund failed: {str(e)}",
                error_code="REFUND_FAILED"
            )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verify Stripe payment status"""
        if not stripe.api_key:
            return PaymentResult(
                success=False,
                message="Stripe not configured",
                error_code="STRIPE_NOT_CONFIGURED"
            )
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            # Map Stripe status to our status
            status_map = {
                "succeeded": "completed",
                "processing": "pending",
                "requires_payment_method": "pending",
                "requires_confirmation": "pending",
                "requires_action": "pending",
                "canceled": "cancelled",
            }
            
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                status=status_map.get(payment_intent.status, payment_intent.status),
                message=f"Payment status: {payment_intent.status}",
                provider_data={
                    "amount": payment_intent.amount / 100,
                    "currency": payment_intent.currency,
                    "status": payment_intent.status,
                    "created": datetime.fromtimestamp(payment_intent.created).isoformat()
                }
            )
            
        except stripe.error.InvalidRequestError:
            return PaymentResult(
                success=False,
                message="Transaction not found",
                error_code="TRANSACTION_NOT_FOUND"
            )
    
    def is_available(self) -> bool:
        """Check if Stripe is configured"""
        return stripe.api_key is not None
    
    async def create_checkout_session(
        self,
        amount: Decimal,
        currency: str,
        product_name: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Create a Stripe Checkout session for hosted payment page.
        
        This provides a pre-built payment page hosted by Stripe.
        """
        if not stripe.api_key:
            return PaymentResult(
                success=False,
                message="Stripe not configured",
                error_code="STRIPE_NOT_CONFIGURED"
            )
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card", "upi"],
                line_items=[{
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            
            return PaymentResult(
                success=True,
                transaction_id=session.id,
                status="pending",
                message="Checkout session created",
                provider_data={
                    "session_url": session.url,
                    "session_id": session.id
                }
            )
            
        except Exception as e:
            return PaymentResult(
                success=False,
                message=f"Failed to create checkout session: {str(e)}",
                error_code="CHECKOUT_ERROR"
            )
