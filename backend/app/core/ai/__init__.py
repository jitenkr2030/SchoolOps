"""
AI Core Package
Self-hosted AI provider implementations
"""

from app.core.ai.provider import (
    AIProvider,
    AIProviderType,
    AIResponse,
    OllamaProvider,
    MockAIProvider,
    get_ai_provider,
    get_ai_service
)

__all__ = [
    "AIProvider",
    "AIProviderType",
    "AIResponse",
    "OllamaProvider",
    "MockAIProvider",
    "get_ai_provider",
    "get_ai_service"
]
