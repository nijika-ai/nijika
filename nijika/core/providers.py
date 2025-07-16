"""
AI Provider management for the Nijika AI Agent Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json


class ProviderType(Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    provider_type: ProviderType
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 100
    additional_config: Dict[str, Any] = None


class BaseProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.logger = logging.getLogger(f"nijika.provider.{config.name}")
        self.request_count = 0
        self.error_count = 0
    
    @abstractmethod
    async def complete(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a completion from the provider"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings from the provider"""
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """Get available models from the provider"""
        pass
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        try:
            await self.complete("Hello", {"timeout": 5})
            return True
        except Exception:
            return False


class OpenAIProvider(BaseProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_url or "https://api.openai.com/v1"
        self.model = config.model or "gpt-3.5-turbo"
    
    async def complete(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate completion using OpenAI API"""
        try:
            self.request_count += 1
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "content": result["choices"][0]["message"]["content"],
                            "tokens_used": result["usage"]["total_tokens"],
                            "model": self.model,
                            "provider": "openai"
                        }
                    else:
                        self.error_count += 1
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
        
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"OpenAI completion failed: {str(e)}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "text-embedding-ada-002",
                "input": text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["data"][0]["embedding"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI embedding error: {response.status} - {error_text}")
        
        except Exception as e:
            self.logger.error(f"OpenAI embedding failed: {str(e)}")
            raise
    
    def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_url or "https://api.anthropic.com/v1"
        self.model = config.model or "claude-3-sonnet-20240229"
    
    async def complete(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate completion using Anthropic API"""
        try:
            self.request_count += 1
            
            headers = {
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "content": result["content"][0]["text"],
                            "tokens_used": result["usage"]["input_tokens"] + result["usage"]["output_tokens"],
                            "model": self.model,
                            "provider": "anthropic"
                        }
                    else:
                        self.error_count += 1
                        error_text = await response.text()
                        raise Exception(f"Anthropic API error: {response.status} - {error_text}")
        
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Anthropic completion failed: {str(e)}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """Anthropic doesn't provide embeddings, raise not implemented"""
        raise NotImplementedError("Anthropic does not provide embedding endpoints")
    
    def get_models(self) -> List[str]:
        """Get available Anthropic models"""
        return ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"]


class GoogleProvider(BaseProvider):
    """Google AI provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_url or "https://generativelanguage.googleapis.com/v1beta"
        self.model = config.model or "gemini-pro"
    
    async def complete(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate completion using Google AI API"""
        try:
            self.request_count += 1
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/models/{self.model}:generateContent?key={self.config.api_key}",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "content": result["candidates"][0]["content"]["parts"][0]["text"],
                            "tokens_used": result.get("usageMetadata", {}).get("totalTokenCount", 0),
                            "model": self.model,
                            "provider": "google"
                        }
                    else:
                        self.error_count += 1
                        error_text = await response.text()
                        raise Exception(f"Google AI API error: {response.status} - {error_text}")
        
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Google AI completion failed: {str(e)}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Google AI API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "models/embedding-001",
                "content": {
                    "parts": [{"text": text}]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/models/embedding-001:embedContent?key={self.config.api_key}",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["embedding"]["values"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Google AI embedding error: {response.status} - {error_text}")
        
        except Exception as e:
            self.logger.error(f"Google AI embedding failed: {str(e)}")
            raise
    
    def get_models(self) -> List[str]:
        """Get available Google AI models"""
        return ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]


class ProviderManager:
    """
    Manager for multiple AI providers
    """
    
    def __init__(self, provider_configs: List[Union[ProviderConfig, Dict[str, Any]]]):
        self.providers: Dict[str, BaseProvider] = {}
        self.logger = logging.getLogger("nijika.provider_manager")
        self.load_balancer_index = 0
        
        # Initialize providers
        for config in provider_configs:
            if isinstance(config, dict):
                config = ProviderConfig(**config)
            
            provider = self._create_provider(config)
            self.providers[config.name] = provider
        
        self.logger.info(f"Initialized {len(self.providers)} providers")
    
    def _create_provider(self, config: ProviderConfig) -> BaseProvider:
        """Create a provider instance based on type"""
        if config.provider_type == ProviderType.OPENAI:
            return OpenAIProvider(config)
        elif config.provider_type == ProviderType.ANTHROPIC:
            return AnthropicProvider(config)
        elif config.provider_type == ProviderType.GOOGLE:
            return GoogleProvider(config)
        else:
            raise ValueError(f"Unsupported provider type: {config.provider_type}")
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get a provider by name"""
        return self.providers.get(name)
    
    def get_provider_by_type(self, provider_type: ProviderType) -> Optional[BaseProvider]:
        """Get first provider by type"""
        for provider in self.providers.values():
            if provider.config.provider_type == provider_type:
                return provider
        return None
    
    def list_providers(self) -> List[str]:
        """List all provider names"""
        return list(self.providers.keys())
    
    async def complete_with_fallback(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete with automatic fallback to other providers
        """
        providers = list(self.providers.values())
        
        for provider in providers:
            try:
                result = await provider.complete(prompt, context)
                return result
            except Exception as e:
                self.logger.warning(f"Provider {provider.config.name} failed: {str(e)}")
                continue
        
        raise Exception("All providers failed")
    
    async def complete_with_load_balancing(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete with round-robin load balancing
        """
        if not self.providers:
            raise Exception("No providers available")
        
        providers = list(self.providers.values())
        provider = providers[self.load_balancer_index % len(providers)]
        self.load_balancer_index += 1
        
        try:
            return await provider.complete(prompt, context)
        except Exception as e:
            self.logger.warning(f"Load balanced provider {provider.config.name} failed: {str(e)}")
            # Fallback to other providers
            return await self.complete_with_fallback(prompt, context)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        
        for name, provider in self.providers.items():
            try:
                health_status[name] = await provider.health_check()
            except Exception:
                health_status[name] = False
        
        return health_status
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all providers"""
        stats = {}
        
        for name, provider in self.providers.items():
            stats[name] = {
                "request_count": provider.request_count,
                "error_count": provider.error_count,
                "error_rate": provider.error_count / max(provider.request_count, 1),
                "model": provider.config.model,
                "provider_type": provider.config.provider_type.value
            }
        
        return stats 