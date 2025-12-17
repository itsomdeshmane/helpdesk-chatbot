"""
In-Memory Vector Store Implementation
Fallback vector store using in-memory storage and simple similarity search
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from core.interfaces.vector_store import IVectorStore

logger = logging.getLogger(__name__)


class InMemoryVectorStore(IVectorStore):
    """
    In-memory vector store implementation
    
    Uses:
    - In-memory storage (Python list)
    - Cosine similarity for search
    - Simple filtering
    
    Following SOLID:
    - SRP: Single responsibility - in-memory vector operations
    - OCP: Implements IVectorStore interface
    - LSP: Substitutable for any IVectorStore
    
    Note:
        This is a fallback/development solution.
        For production with large datasets, use Pinecone or similar.
    """
    
    def __init__(self):
        """Initialize in-memory vector store"""
        self._vectors: List[Dict[str, Any]] = []
        logger.info("In-Memory Vector Store initialized")
    
    async def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Insert or update vectors in memory
        
        Args:
            vectors: List of vector objects with id, values, metadata
            namespace: Optional namespace (stored in metadata)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for vec in vectors:
                # Add namespace to metadata if provided
                if namespace:
                    if 'metadata' not in vec:
                        vec['metadata'] = {}
                    vec['metadata']['namespace'] = namespace
                
                # Check if vector with this ID exists
                existing_idx = None
                for idx, stored_vec in enumerate(self._vectors):
                    if stored_vec['id'] == vec['id']:
                        existing_idx = idx
                        break
                
                # Update or insert
                if existing_idx is not None:
                    self._vectors[existing_idx] = vec
                else:
                    self._vectors.append(vec)
            
            logger.debug(f"Upserted {len(vectors)} vectors (total: {len(self._vectors)})")
            return True
            
        except Exception as e:
            logger.error(f"In-memory upsert failed: {e}")
            return False
    
    async def search(
        self,
        embedding: List[float],
        tenant_id: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity
        
        Args:
            embedding: Query embedding vector
            tenant_id: Tenant ID for filtering
            top_k: Number of results
            filter: Optional metadata filters
            
        Returns:
            List of matching results with id, score, metadata
        """
        try:
            if not self._vectors:
                logger.debug("No vectors in store")
                return []
            
            # Convert query embedding to numpy array
            query_vec = np.array(embedding)
            
            # Calculate similarities
            results = []
            for vec in self._vectors:
                metadata = vec.get('metadata', {})
                
                # Apply filters
                if metadata.get('tenant_id') != tenant_id:
                    continue
                
                if filter:
                    if not all(metadata.get(k) == v for k, v in filter.items()):
                        continue
                
                # Calculate cosine similarity
                stored_vec = np.array(vec['values'])
                similarity = self._cosine_similarity(query_vec, stored_vec)
                
                results.append({
                    'id': vec['id'],
                    'score': float(similarity),
                    'metadata': metadata
                })
            
            # Sort by score (descending) and take top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:top_k]
            
            logger.debug(f"In-memory search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"In-memory search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete vectors from memory
        
        Args:
            ids: Optional list of vector IDs to delete
            filter: Optional metadata filter for deletion
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ids:
                # Delete by IDs
                self._vectors = [v for v in self._vectors if v['id'] not in ids]
                logger.debug(f"Deleted vectors by ID (remaining: {len(self._vectors)})")
            elif filter:
                # Delete by filter
                self._vectors = [
                    v for v in self._vectors
                    if not all(v.get('metadata', {}).get(k) == val for k, val in filter.items())
                ]
                logger.debug(f"Deleted vectors by filter (remaining: {len(self._vectors)})")
            else:
                logger.warning("No IDs or filter provided for delete")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"In-memory delete failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get in-memory store statistics
        
        Returns:
            Dictionary with stats
        """
        try:
            # Get dimension from first vector
            dimension = 0
            if self._vectors:
                dimension = len(self._vectors[0].get('values', []))
            
            # Get namespaces
            namespaces = set()
            for vec in self._vectors:
                ns = vec.get('metadata', {}).get('namespace')
                if ns:
                    namespaces.add(ns)
            
            return {
                'store_type': 'in_memory',
                'total_vectors': len(self._vectors),
                'dimension': dimension,
                'namespaces': list(namespaces)
            }
            
        except Exception as e:
            logger.error(f"Failed to get in-memory stats: {e}")
            return {
                'store_type': 'in_memory',
                'error': str(e)
            }
    
    def get_store_type(self) -> str:
        """Return store type"""
        return "in_memory"
    
    async def is_healthy(self) -> bool:
        """
        Check if in-memory store is operational
        
        Returns:
            True (always operational)
        """
        return True
    
    def clear(self):
        """Clear all vectors (for testing/development)"""
        count = len(self._vectors)
        self._vectors.clear()
        logger.info(f"Cleared {count} vectors from memory")
    
    def get_vector_count(self) -> int:
        """Get total number of vectors stored"""
        return len(self._vectors)

