"""
SMS Provider Factory

Factory pattern for instantiating the appropriate SMS provider
based on environment configuration.

Supports:
- Mock (testing)
- Email (free email-to-SMS)
- Twilio (paid international)
- Msg91 (paid, popular in India)
"""

from typing import Optional
from app.config import settings
from app.services.sms.base import SMSProviderBase, ProviderConfig
from app.services.sms.providers.mock_provider import MockSMSProvider
from app.services.sms.providers.email_sms_provider import EmailToSMSProvider
from app.services.sms.providers.twilio_provider import TwilioSMSProvider


class SMSProviderFactory:
    """
    Factory for creating SMS provider instances.
    
    Usage:
        provider = SMSProviderFactory.get_provider()
        result = await provider.send("1234567890", "Hello!")
    """
    
    _providers = {
        "mock": MockSMSProvider,
        "email": EmailToSMSProvider,
        "twilio": TwilioSMSProvider,
        # "msg91": Msg91SMSProvider,  # TODO: Implement
    }
    
    @classmethod
    def get_provider(cls, provider_name: Optional[str] = None) -> SMSProviderBase:
        """
        Get the configured SMS provider.
        
        Args:
            provider_name: Optional specific provider name
            
        Returns:
            SMSProviderBase instance
        """
        # Use provided name or get from settings
        provider = provider_name or getattr(settings, 'SMS_PROVIDER', 'mock')
        provider = provider.lower()
        
        # Get provider class
        provider_class = cls._providers.get(provider)
        
        if not provider_class:
            # Unknown provider, use mock as fallback
            provider_class = MockSMSProvider
        
        # Create instance with default config
        return provider_class()
    
    @classmethod
    def get_provider_with_config(
        cls, 
        provider_name: str, 
        config: ProviderConfig
    ) -> SMSProviderBase:
        """
        Get provider with custom configuration.
        
        Args:
            provider_name: Name of the provider
            config: ProviderConfig instance
            
        Returns:
            SMSProviderBase instance
        """
        provider_class = cls._providers.get(provider_name.lower())
        
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get list of available provider names.
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """
        Check if a provider is configured and available.
        """
        provider = cls.get_provider(provider_name)
        return provider.is_available


# Convenience function
def get_sms_provider(provider_name: Optional[str] = None) -> SMSProviderBase:
    """
    Get the configured SMS provider.
    
    Usage:
        from app.services.sms import get_sms_provider
        
        provider = get_sms_provider()
        result = await provider.send("1234567890", "Hello!")
    """
    return SMSProviderFactory.get_provider(provider_name)
