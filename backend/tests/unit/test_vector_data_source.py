"""
Unit tests for Vector Data Source

Tests the document/RAG data source implementation.
"""

import pytest
from unittest.mock import AsyncMock
from infrastructure.data_sources.vector_data_source import VectorDataSource
from core.models.query import Query


@pytest.mark.unit
class TestVectorDataSource:
    """Test suite for Vector Data Source"""
    
    def test_init(self, mock_vector_store, mock_embedding_service):
        """Test data source initialization"""
        source = VectorDataSource(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service
        )
        
        assert source is not None
        assert source.get_source_type() == "documents"
    
    @pytest.mark.asyncio
    async def test_can_handle_document_query(
        self,
        mock_vector_store,
        mock_embedding_service
    ):
        """Test can_handle for document queries"""
        source = VectorDataSource(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service
        )
        
        # Document-like query
        query = Query(text="How do I create a work order?")
        can_handle = await source.can_handle(query)
        
        # Should be able to handle
        assert can_handle is True
    
    @pytest.mark.asyncio
    async def test_search_success(
        self,
        mock_vector_store,
        mock_embedding_service,
        sample_query
    ):
        """Test successful search"""
        source = VectorDataSource(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service
        )
        
        # Setup mock responses
        mock_embedding_service.create_embedding.return_value = [0.1] * 1536
        mock_vector_store.search.return_value = [
            {
                "id": "doc1",
                "text": "Result 1",
                "score": 0.95,
                "metadata": {}
            }
        ]
        
        # Execute
        response = await source.search(
            query=sample_query,
            tenant_id="test_tenant",
            limit=5
        )
        
        # Assert
        assert response is not None
        assert response.success is True
        assert response.source == "documents"
        assert len(response.results) > 0
        
        # Verify mocks called
        mock_embedding_service.create_embedding.assert_called_once()
        mock_vector_store.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(
        self,
        mock_vector_store,
        mock_embedding_service
    ):
        """Test health check"""
        source = VectorDataSource(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service
        )
        
        mock_vector_store.is_healthy.return_value = True
        
        # Execute
        healthy = await source.health_check()
        
        # Assert
        assert healthy is True
        mock_vector_store.is_healthy.assert_called_once()

