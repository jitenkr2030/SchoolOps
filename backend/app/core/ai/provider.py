"""
AI Provider Interface and Ollama Implementation
Self-hosted AI integration for SchoolOps using local LLM models
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
import json
import logging

import httpx
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProviderType(str, Enum):
    """Supported AI Provider types"""
    OLLAMA = "ollama"
    LOCALAI = "localai"
    MOCK = "mock"


class AIResponse(BaseModel):
    """Standardized AI response wrapper"""
    content: str
    model: str
    provider: AIProviderType
    response_time_ms: int
    tokens_used: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """Generate text from the AI model"""
        pass
    
    @abstractmethod
    async def analyze_json(
        self, 
        prompt: str, 
        context_data: Dict[str, Any],
        response_schema: type[BaseModel]
    ) -> AIResponse:
        """Analyze data and return structured JSON output"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the AI provider is available"""
        pass


class OllamaProvider(AIProvider):
    """
    Ollama local LLM provider implementation
    
    This provider connects to a locally running Ollama instance,
    avoiding external API costs while providing powerful AI capabilities.
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0
    ):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate text using Ollama's chat completion API
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system instruction for the model
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            AIResponse with generated content
        """
        import time
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("message", {}).get("content", "")
            response_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Ollama response received in {response_time}ms")
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=response_time,
                success=True
            )
            
        except httpx.TimeoutException as e:
            logger.error(f"Ollama timeout: {e}")
            return AIResponse(
                content="",
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message="Request timed out"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            return AIResponse(
                content="",
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Ollama unexpected error: {e}")
            return AIResponse(
                content="",
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e)
            )
    
    async def analyze_json(
        self, 
        prompt: str, 
        context_data: Dict[str, Any],
        response_schema: type[BaseModel]
    ) -> AIResponse:
        """
        Analyze data and return structured JSON output
        
        This method constructs a comprehensive prompt with context data
        and requests JSON output that conforms to the provided schema.
        
        Args:
            prompt: Analysis instructions
            context_data: Data to analyze
            response_schema: Pydantic schema for expected output
            
        Returns:
            AIResponse with parsed JSON content
        """
        import time
        start_time = time.time()
        
        # Construct comprehensive prompt
        schema_json = response_schema.model_json_schema()
        
        full_prompt = f"""{prompt}

## CONTEXT DATA (JSON):
```json
{json.dumps(context_data, indent=2, default=str)}
```

## REQUIRED OUTPUT FORMAT:
```json
{json.dumps(schema_json, indent=2)}
```

## INSTRUCTIONS:
1. Analyze the context data carefully
2. Output ONLY valid JSON matching the required format
3. Do not include any explanatory text or markdown formatting
4. Ensure all required fields are populated

Output your analysis as valid JSON:"""
        
        system_prompt = """You are a structured data analysis assistant.
Your task is to analyze student data and output valid JSON only.
Never include markdown formatting, code blocks, or explanatory text.
Always output raw, valid JSON that conforms to the specified schema."""
        
        result = await self.generate_text(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2048
        )
        
        if not result.success:
            return result
        
        # Parse and validate JSON response
        try:
            # Clean up potential markdown formatting
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            parsed_data = json.loads(content)
            
            # Validate against schema
            validated = response_schema.model_validate(parsed_data)
            
            result.content = validated.model_dump_json(indent=2)
            result.tokens_used = None  # Ollama doesn't always return this
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            logger.error(f"Raw content: {result.content}")
            return AIResponse(
                content=result.content,
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=f"Failed to parse JSON response: {e}"
            )
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return AIResponse(
                content=result.content,
                model=self.model,
                provider=AIProviderType.OLLAMA,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=f"Schema validation failed: {e}"
            )
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is running and the model is available
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            client = await self._get_client()
            
            # Check if server is responsive
            response = await client.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                return False
            
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            
            # Check if our model is available
            model_available = any(
                self.model in name or name.startswith(self.model)
                for name in models
            )
            
            if not model_available:
                logger.warning(
                    f"Model {self.model} not found in Ollama. "
                    f"Available models: {models}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False


class MockAIProvider(AIProvider):
    """
    Mock AI provider for testing and development
    
    Returns predefined responses without calling an actual LLM.
    Useful for testing the API structure without running Ollama.
    """
    
    def __init__(self, latency_ms: int = 100):
        self.latency_ms = latency_ms
        self.call_count = 0
    
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """Return mock text response"""
        import asyncio
        await asyncio.sleep(self.latency_ms / 1000)
        
        self.call_count += 1
        
        return AIResponse(
            content=f"Mock response for: {prompt[:50]}...",
            model="mock-model",
            provider=AIProviderType.MOCK,
            response_time_ms=self.latency_ms,
            tokens_used=10,
            success=True
        )
    
    async def analyze_json(
        self, 
        prompt: str, 
        context_data: Dict[str, Any],
        response_schema: type[BaseModel]
    ) -> AIResponse:
        """Return mock JSON analysis"""
        import asyncio
        await asyncio.sleep(self.latency_ms / 1000)
        
        self.call_count += 1
        
        # Return a mock valid response
        mock_content = '{"mock": true, "analysis": "mock result"}'
        
        return AIResponse(
            content=mock_content,
            model="mock-model",
            provider=AIProviderType.MOCK,
            response_time_ms=self.latency_ms,
            success=True
        )
    
    async def health_check(self) -> bool:
        """Mock always returns healthy"""
        return True


# Provider factory function
async def get_ai_provider(
    provider_type: Optional[AIProviderType] = None
) -> AIProvider:
    """
    Factory function to get the appropriate AI provider
    
    Args:
        provider_type: Type of provider to use (defaults to config setting)
        
    Returns:
        Configured AI provider instance
    """
    if provider_type is None:
        provider_type = AIProviderType(settings.AI_PROVIDER)
    
    if provider_type == AIProviderType.OLLAMA:
        return OllamaProvider()
    elif provider_type == AIProviderType.MOCK:
        return MockAIProvider()
    else:
        raise ValueError(f"Unknown AI provider type: {provider_type}")


# Singleton instance for dependency injection
_ai_provider: Optional[AIProvider] = None


async def get_ai_service() -> AIProvider:
    """Get the singleton AI provider instance"""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = await get_ai_provider()
    return _ai_provider
