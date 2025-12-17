"""
ILLMProvider Interface - Following Dependency Inversion Principle (DIP)
Allows swapping LLM providers (OpenAI, Anthropic, local models) without code changes
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator


class ILLMProvider(ABC):
    """
    Interface for Large Language Model providers
    
    Supports:
    - Standard completion (synchronous)
    - Streaming completion (asynchronous)
    - Multiple providers (OpenAI, Anthropic, Gemini, local models)
    
    Following SOLID:
    - SRP: Single responsibility - LLM text generation
    - OCP: Can add new providers without modifying existing code
    - DIP: Application layer depends on this interface, not concrete providers
    """
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        """
        Generate text completion from LLM
        
        Args:
            messages: List of messages in chat format
                      [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            Generated text response
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "What is SOLID?"}
            ... ]
            >>> response = await provider.generate_completion(messages)
        """
        pass
    
    @abstractmethod
    async def generate_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming text completion from LLM
        
        Args:
            messages: List of messages in chat format
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Yields:
            Text chunks as they are generated
            
        Example:
            >>> async for chunk in provider.generate_streaming(messages):
            ...     print(chunk, end='', flush=True)
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the name of the LLM provider
        
        Returns:
            Provider identifier (e.g., 'openai', 'anthropic', 'local')
        """
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (provider-specific tokenization)
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass

