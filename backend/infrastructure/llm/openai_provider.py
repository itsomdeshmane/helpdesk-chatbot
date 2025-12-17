"""
OpenAI LLM Provider Implementation
Wraps OpenAI API following ILLMProvider interface
"""

import logging
from typing import List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI
import tiktoken
from core.interfaces.llm_provider import ILLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(ILLMProvider):
    """
    OpenAI LLM implementation
    
    Following SOLID:
    - SRP: Single responsibility - OpenAI API interaction
    - OCP: Implements ILLMProvider interface
    - LSP: Substitutable for any ILLMProvider
    - DIP: Depends on abstract OpenAI client
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            temperature: Default sampling temperature
            max_tokens: Default max tokens in response
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=2
        )
        self._model = model
        self._default_temperature = temperature
        self._default_max_tokens = max_tokens
        
        # Initialize tokenizer for token counting
        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding (used by gpt-4)
            self._encoding = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"OpenAI Provider initialized with model: {model}")
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from OpenAI
        
        Args:
            messages: Chat messages format
            temperature: Sampling temperature (uses default if None)
            max_tokens: Max tokens (uses default if None)
            **kwargs: Additional OpenAI parameters
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            logger.debug(f"Generating completion with {len(messages)} messages")
            
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._default_temperature,
                max_tokens=max_tokens or self._default_max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Completion generated: {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise
    
    async def generate_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming text completion from OpenAI
        
        Args:
            messages: Chat messages format
            temperature: Sampling temperature (uses default if None)
            max_tokens: Max tokens (uses default if None)
            **kwargs: Additional OpenAI parameters
            
        Yields:
            Text chunks as they are generated
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            logger.debug(f"Starting streaming completion with {len(messages)} messages")
            
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._default_temperature,
                max_tokens=max_tokens or self._default_max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        """Return provider name"""
        return "openai"
    
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using OpenAI tokenizer
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            tokens = self._encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using approximation")
            # Fallback: rough approximation (1 token ≈ 4 characters)
            return len(text) // 4
    
    def get_model(self) -> str:
        """Get the current model name"""
        return self._model
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple test: count tokens
            await self.count_tokens("health check")
            return True
        except:
            return False

