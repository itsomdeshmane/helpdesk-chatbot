"""
Pinecone Vector Store Implementation
Wraps Pinecone API following IVectorStore interface
"""

import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from core.interfaces.vector_store import IVectorStore

logger = logging.getLogger(__name__)


class PineconeVectorStore(IVectorStore):
    """
    Pinecone vector database implementation
    
    Following SOLID:
    - SRP: Single responsibility - Pinecone vector operations
    - OCP: Implements IVectorStore interface
    - LSP: Substitutable for any IVectorStore
    """
    
    def __init__(
        self,
        api_key: Optional[str],
        index_name: str,
        enabled: bool = True
    ):
        """
        Initialize Pinecone vector store
        
        Args:
            api_key: Pinecone API key
            index_name: Name of Pinecone index
            enabled: Whether Pinecone is enabled (from config)
        """
        self._api_key = api_key
        self._index_name = index_name
        self._enabled = enabled and api_key is not None
        self._index = None
        self._pc = None
        
        if self._enabled:
            self._initialize_pinecone()
        else:
            logger.info("Pinecone disabled or API key not provided")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        try:
            self._pc = Pinecone(api_key=self._api_key)
            self._index = self._pc.Index(self._index_name)
            logger.info(f"Pinecone connected to index: {self._index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self._enabled = False
            raise
    
    async def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Insert or update vectors in Pinecone
        
        Args:
            vectors: List of vector objects with id, values, metadata
            namespace: Optional namespace
            
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled or not self._index:
            logger.warning("Pinecone not enabled, skipping upsert")
            return False
        
        try:
            # Convert to Pinecone format if needed
            pinecone_vectors = []
            for vec in vectors:
                if isinstance(vec, dict):
                    pinecone_vectors.append((
                        vec['id'],
                        vec['values'],
                        vec.get('metadata', {})
                    ))
                else:
                    pinecone_vectors.append(vec)
            
            # Upsert to Pinecone
            self._index.upsert(
                vectors=pinecone_vectors,
                namespace=namespace or ""
            )
            
            logger.debug(f"Upserted {len(vectors)} vectors to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            return False
    
    async def search(
        self,
        embedding: List[float],
        tenant_id: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone
        
        Args:
            embedding: Query embedding vector
            tenant_id: Tenant ID for filtering
            top_k: Number of results
            filter: Optional metadata filters
            
        Returns:
            List of matching results with id, score, metadata
        """
        if not self._enabled or not self._index:
            logger.warning("Pinecone not enabled, returning empty results")
            return []
        
        try:
            # Build filter (always include tenant_id)
            query_filter = {"tenant_id": tenant_id}
            if filter:
                query_filter.update(filter)
            
            # Query Pinecone
            results = self._index.query(
                vector=embedding,
                filter=query_filter,
                top_k=top_k,
                include_metadata=True
            )
            
            # Convert results to standard format
            matches = []
            pinecone_matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
            
            for match in pinecone_matches:
                matches.append({
                    'id': match.id if hasattr(match, 'id') else match.get('id'),
                    'score': match.score if hasattr(match, 'score') else match.get('score', 0),
                    'metadata': match.metadata if hasattr(match, 'metadata') else match.get('metadata', {})
                })
            
            logger.debug(f"Pinecone search found {len(matches)} results")
            return matches
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete vectors from Pinecone
        
        Args:
            ids: Optional list of vector IDs to delete
            filter: Optional metadata filter for deletion
            
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled or not self._index:
            logger.warning("Pinecone not enabled, skipping delete")
            return False
        
        try:
            if ids:
                # Delete by IDs
                self._index.delete(ids=ids)
                logger.debug(f"Deleted {len(ids)} vectors by ID")
            elif filter:
                # Delete by filter
                self._index.delete(filter=filter)
                logger.debug(f"Deleted vectors by filter: {filter}")
            else:
                logger.warning("No IDs or filter provided for delete")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Pinecone delete failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Pinecone index statistics
        
        Returns:
            Dictionary with stats
        """
        if not self._enabled or not self._index:
            return {
                'enabled': False,
                'total_vectors': 0
            }
        
        try:
            stats = self._index.describe_index_stats()
            
            return {
                'enabled': True,
                'index_name': self._index_name,
                'total_vectors': stats.total_vector_count if hasattr(stats, 'total_vector_count') else stats.get('total_vector_count', 0),
                'dimension': stats.dimension if hasattr(stats, 'dimension') else stats.get('dimension', 0),
                'namespaces': stats.namespaces if hasattr(stats, 'namespaces') else stats.get('namespaces', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {
                'enabled': True,
                'error': str(e)
            }
    
    def get_store_type(self) -> str:
        """Return store type"""
        return "pinecone"
    
    async def is_healthy(self) -> bool:
        """
        Check if Pinecone is accessible
        
        Returns:
            True if operational, False otherwise
        """
        if not self._enabled or not self._index:
            return False
        
        try:
            # Try to get stats as health check
            stats = await self.get_stats()
            return 'error' not in stats
        except:
            return False
    
    def is_enabled(self) -> bool:
        """Check if Pinecone is enabled"""
        return self._enabled

