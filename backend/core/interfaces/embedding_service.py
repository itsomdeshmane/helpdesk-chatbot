"""
IEmbeddingService Interface - Text embedding generation
Allows swapping embedding providers independently from LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Union


class IEmbeddingService(ABC):
    """
    Interface for text embedding services
    
    Embeddings are vector representations of text used for:
    - Semantic search
    - Similarity calculations
    - Vector database storage
    
    Following SOLID:
    - SRP: Single responsibility - generate embeddings
    - OCP: Can add new embedding providers without changes
    - ISP: Minimal interface - only embedding generation
    """
    
    @abstractmethod
    async def create_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Input text to embed
            **kwargs: Provider-specific parameters
            
        Returns:
            List of floats representing the embedding vector
            (typically 1536 dimensions for OpenAI, varies by provider)
            
        Example:
            >>> embedding = await service.create_embedding("Hello world")
            >>> len(embedding)
            1536
        """
        pass
    
    @abstractmethod
    async def create_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch operation)
        
        Args:
            texts: List of texts to embed
            **kwargs: Provider-specific parameters
            
        Returns:
            List of embedding vectors
            
        Note:
            Batch operations are typically more efficient than individual calls
            
        Example:
            >>> texts = ["Hello", "World", "SOLID"]
            >>> embeddings = await service.create_embeddings(texts)
            >>> len(embeddings)
            3
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Return the dimension of embedding vectors
        
        Returns:
            Number of dimensions (e.g., 1536 for OpenAI text-embedding-3-small)
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the name of the embedding provider
        
        Returns:
            Provider identifier (e.g., 'openai', 'sentence-transformers')
        """
        pass

