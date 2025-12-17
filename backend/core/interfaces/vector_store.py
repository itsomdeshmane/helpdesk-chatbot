"""
IVectorStore Interface - Vector database abstraction
Supports Pinecone, in-memory, and future vector databases
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IVectorStore(ABC):
    """
    Interface for vector database/store
    
    Supports:
    - Pinecone (cloud vector database)
    - In-memory vector store (fallback/development)
    - Future: Weaviate, Qdrant, Milvus, etc.
    
    Following SOLID:
    - SRP: Single responsibility - vector storage and search
    - OCP: Can add new vector stores without changes
    - DIP: Data sources depend on this interface
    """
    
    @abstractmethod
    async def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Insert or update vectors in the store
        
        Args:
            vectors: List of vector objects with:
                - id: Unique identifier
                - values: Embedding vector (list of floats)
                - metadata: Optional metadata dict
            namespace: Optional namespace for organization
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> vectors = [
            ...     {
            ...         "id": "doc-1",
            ...         "values": [0.1, 0.2, ...],
            ...         "metadata": {"text": "...", "tenant_id": "test"}
            ...     }
            ... ]
            >>> await store.upsert(vectors)
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        embedding: List[float],
        tenant_id: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            embedding: Query embedding vector
            tenant_id: Tenant ID for filtering
            top_k: Number of results to return
            filter: Optional metadata filters
            
        Returns:
            List of matching results with:
                - id: Vector ID
                - score: Similarity score
                - metadata: Associated metadata
                
        Example:
            >>> results = await store.search(
            ...     embedding=[0.1, 0.2, ...],
            ...     tenant_id="test",
            ...     top_k=5
            ... )
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete vectors by IDs or filter
        
        Args:
            ids: Optional list of vector IDs to delete
            filter: Optional metadata filter for deletion
            
        Returns:
            True if successful, False otherwise
            
        Note:
            Either ids or filter must be provided
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with stats like:
                - total_vectors: Total number of vectors
                - dimension: Vector dimension
                - namespaces: List of namespaces
        """
        pass
    
    @abstractmethod
    def get_store_type(self) -> str:
        """
        Return store type
        
        Returns:
            Store identifier (e.g., 'pinecone', 'in_memory', 'weaviate')
        """
        pass
    
    @abstractmethod
    async def is_healthy(self) -> bool:
        """
        Check if vector store is available and healthy
        
        Returns:
            True if operational, False otherwise
        """
        pass

