"""
Vector Data Source Implementation
Handles document/knowledge base search using vector similarity
Wraps existing RAG functionality
"""

import logging
import time
from typing import List
from core.interfaces.data_source import IDataSource
from core.interfaces.embedding_service import IEmbeddingService
from core.interfaces.vector_store import IVectorStore
from core.models.query import Query
from core.models.response import DataSourceResponse

logger = logging.getLogger(__name__)


class VectorDataSource(IDataSource):
    """
    Document/Knowledge Base data source using vector search
    
    Following SOLID:
    - SRP: Single responsibility - document search
    - OCP: Implements IDataSource interface
    - DIP: Depends on IVectorStore and IEmbeddingService abstractions
    
    This wraps the existing RAG functionality from llm/rag.py
    """
    
    # Keywords that indicate document/knowledge base queries
    DOCUMENT_KEYWORDS = [
        'how', 'what', 'why', 'when', 'where', 'who',
        'explain', 'describe', 'define', 'tell me',
        'guide', 'steps', 'process', 'procedure',
        'tutorial', 'documentation', 'help',
        'feature', 'functionality', 'capability',
        'setup', 'configure', 'install',
        'troubleshoot', 'fix', 'solve', 'error'
    ]
    
    def __init__(
        self,
        vector_store: IVectorStore,
        embedding_service: IEmbeddingService
    ):
        """
        Initialize vector data source
        
        Args:
            vector_store: Vector database (Pinecone or in-memory)
            embedding_service: Embedding generation service
        """
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._source_type = "documents"
        
        logger.info(f"Vector Data Source initialized with {vector_store.get_store_type()} store")
    
    async def can_handle(self, query: Query) -> bool:
        """
        Determine if this data source can handle the query
        
        Args:
            query: The user query
            
        Returns:
            True if query seems to be asking for documentation/knowledge
        """
        query_lower = query.text.lower()
        
        # Check for document-related keywords
        return any(keyword in query_lower for keyword in self.DOCUMENT_KEYWORDS)
    
    async def search(
        self,
        query: Query,
        tenant_id: str,
        limit: int = 5
    ) -> DataSourceResponse:
        """
        Search vector database for relevant documents
        
        Args:
            query: The user query
            tenant_id: Tenant identifier
            limit: Maximum number of results
            
        Returns:
            DataSourceResponse with document chunks
        """
        start_time = time.time()
        
        try:
            logger.info(f"Vector search: '{query.text[:50]}...' (tenant: {tenant_id})")
            
            # Step 1: Generate embedding for query
            embedding = await self._embedding_service.create_embedding(query.text)
            
            # Step 2: Search vector store
            results = await self._vector_store.search(
                embedding=embedding,
                tenant_id=tenant_id,
                top_k=limit
            )
            
            # Step 3: Extract text from results
            documents = []
            for result in results:
                metadata = result.get('metadata', {})
                text = metadata.get('text', '')
                if text:
                    documents.append({
                        'text': text,
                        'score': result.get('score', 0),
                        'source': metadata.get('filename', 'unknown'),
                        'page': metadata.get('page', None)
                    })
            
            execution_time = (time.time() - start_time) * 1000
            
            if documents:
                logger.info(f"Found {len(documents)} documents (score: {documents[0]['score']:.3f})")
                
                return DataSourceResponse(
                    success=True,
                    source_type=self._source_type,
                    data=documents,
                    metadata={
                        'count': len(documents),
                        'top_score': documents[0]['score'] if documents else 0,
                        'vector_store': self._vector_store.get_store_type()
                    },
                    execution_time_ms=execution_time
                )
            else:
                logger.warning("No documents found in vector search")
                
                return DataSourceResponse(
                    success=False,
                    source_type=self._source_type,
                    error="No relevant documents found in knowledge base",
                    execution_time_ms=execution_time
                )
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return DataSourceResponse(
                success=False,
                source_type=self._source_type,
                error=f"Vector search error: {str(e)}",
                execution_time_ms=execution_time
            )
    
    def get_source_type(self) -> str:
        """Return source type"""
        return self._source_type
    
    async def health_check(self) -> bool:
        """
        Check if vector store is operational
        
        Returns:
            True if vector store is healthy
        """
        try:
            return await self._vector_store.is_healthy()
        except:
            return False
    
    async def get_stats(self) -> dict:
        """Get vector store statistics"""
        try:
            return await self._vector_store.get_stats()
        except Exception as e:
            logger.error(f"Failed to get vector store stats: {e}")
            return {"error": str(e)}

