"""
OpenAI Embedding Service Implementation
Generates embeddings using OpenAI API
"""

import logging
from typing import List
from openai import AsyncOpenAI
from core.interfaces.embedding_service import IEmbeddingService

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(IEmbeddingService):
    """
    OpenAI embedding service implementation
    
    Following SOLID:
    - SRP: Single responsibility - embedding generation
    - OCP: Implements IEmbeddingService interface
    - LSP: Substitutable for any IEmbeddingService
    """
    
    # Model dimension mappings
    MODEL_DIMENSIONS = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072
    }
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small"
    ):
        """
        Initialize OpenAI embedding service
        
        Args:
            api_key: OpenAI API key
            model: Embedding model name
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=2
        )
        self._model = model
        self._dimension = self.MODEL_DIMENSIONS.get(model, 1536)
        
        logger.info(f"OpenAI Embedding Service initialized with model: {model} ({self._dimension} dimensions)")
    
    async def create_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Input text to embed
            **kwargs: Additional OpenAI parameters
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                # Return zero vector for empty text
                return [0.0] * self._dimension
            
            logger.debug(f"Creating embedding for text: {text[:50]}...")
            
            response = await self._client.embeddings.create(
                model=self._model,
                input=text,
                **kwargs
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Embedding created: {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    async def create_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch operation)
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional OpenAI parameters
            
        Returns:
            List of embedding vectors
            
        Note:
            Batch operations are more efficient than individual calls
        """
        try:
            if not texts:
                logger.warning("Empty text list provided for embeddings")
                return []
            
            # Filter out empty texts and keep track of indices
            valid_texts = []
            valid_indices = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text)
                    valid_indices.append(i)
            
            if not valid_texts:
                logger.warning("No valid texts in batch")
                return [[0.0] * self._dimension] * len(texts)
            
            logger.debug(f"Creating embeddings for {len(valid_texts)} texts")
            
            response = await self._client.embeddings.create(
                model=self._model,
                input=valid_texts,
                **kwargs
            )
            
            # Build result array with embeddings in correct positions
            embeddings = []
            valid_embeddings = [data.embedding for data in response.data]
            
            embedding_idx = 0
            for i in range(len(texts)):
                if i in valid_indices:
                    embeddings.append(valid_embeddings[embedding_idx])
                    embedding_idx += 1
                else:
                    # Zero vector for empty text
                    embeddings.append([0.0] * self._dimension)
            
            logger.debug(f"Created {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Return the dimension of embedding vectors"""
        return self._dimension
    
    def get_provider_name(self) -> str:
        """Return provider name"""
        return "openai"
    
    def get_model(self) -> str:
        """Get the current model name"""
        return self._model
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI Embedding API is accessible
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple test: create embedding for short text
            await self.create_embedding("test")
            return True
        except:
            return False

