"""
Unit tests for ChatOrchestrator

Tests the main business logic coordinator in isolation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from application.services.chat_orchestrator import ChatOrchestrator
from core.models.query import Query, QueryContext
from core.models.response import DataSourceResponse, ChatResponse


@pytest.mark.unit
class TestChatOrchestrator:
    """Test suite for ChatOrchestrator"""
    
    def test_init(
        self,
        mock_llm_provider,
        mock_embedding_service,
        mock_source_selector,
        mock_query_processor,
        mock_response_formatter
    ):
        """Test orchestrator initialization"""
        orchestrator = ChatOrchestrator(
            data_sources=[],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            source_selector=mock_source_selector,
            query_processor=mock_query_processor,
            response_formatter=mock_response_formatter
        )
        
        assert orchestrator is not None
        assert orchestrator.llm_provider == mock_llm_provider
        assert orchestrator.embedding_service == mock_embedding_service
    
    @pytest.mark.asyncio
    async def test_process_query_success(
        self,
        sample_query,
        mock_llm_provider,
        mock_embedding_service,
        mock_source_selector,
        mock_query_processor,
        mock_response_formatter
    ):
        """Test successful query processing"""
        # Setup mocks
        mock_data_source = AsyncMock()
        mock_data_source.can_handle.return_value = True
        mock_data_source.search.return_value = DataSourceResponse(
            success=True,
            results=["Result 1", "Result 2"],
            source="documents"
        )
        mock_data_source.get_source_type.return_value = "documents"
        
        mock_source_selector.select_sources.return_value = ["documents"]
        mock_query_processor.preprocess.return_value = sample_query
        mock_response_formatter.format_response.return_value = ChatResponse(
            success=True,
            message="Test response",
            source="documents"
        )
        
        # Create orchestrator
        orchestrator = ChatOrchestrator(
            data_sources=[mock_data_source],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            source_selector=mock_source_selector,
            query_processor=mock_query_processor,
            response_formatter=mock_response_formatter
        )
        
        # Execute
        response = await orchestrator.process_query(
            query=sample_query,
            tenant_id="test_tenant"
        )
        
        # Assert
        assert response is not None
        assert response.success is True
        assert response.source == "documents"
        
        # Verify mocks called
        mock_source_selector.select_sources.assert_called_once()
        mock_query_processor.preprocess.assert_called_once()
        mock_data_source.can_handle.assert_called_once()
        mock_data_source.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_no_sources(
        self,
        sample_query,
        mock_llm_provider,
        mock_embedding_service,
        mock_source_selector,
        mock_query_processor,
        mock_response_formatter
    ):
        """Test query processing when no data sources available"""
        # Setup: no data sources
        orchestrator = ChatOrchestrator(
            data_sources=[],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            source_selector=mock_source_selector,
            query_processor=mock_query_processor,
            response_formatter=mock_response_formatter
        )
        
        mock_source_selector.select_sources.return_value = []
        mock_query_processor.preprocess.return_value = sample_query
        mock_response_formatter.format_response.return_value = ChatResponse(
            success=False,
            message="No data sources available",
            source="none"
        )
        
        # Execute
        response = await orchestrator.process_query(
            query=sample_query,
            tenant_id="test_tenant"
        )
        
        # Assert
        assert response is not None
        # Should still return a response (formatted error)
        mock_response_formatter.format_response.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_query_with_session(
        self,
        sample_query,
        mock_llm_provider,
        mock_embedding_service,
        mock_source_selector,
        mock_query_processor,
        mock_response_formatter
    ):
        """Test query processing with session ID"""
        mock_data_source = AsyncMock()
        mock_data_source.can_handle.return_value = True
        mock_data_source.search.return_value = DataSourceResponse(
            success=True,
            results=["Result"],
            source="test"
        )
        mock_data_source.get_source_type.return_value = "test"
        
        mock_source_selector.select_sources.return_value = ["test"]
        mock_query_processor.preprocess.return_value = sample_query
        mock_response_formatter.format_response.return_value = ChatResponse(
            success=True,
            message="Response",
            source="test",
            session_id="test_session_123"
        )
        
        orchestrator = ChatOrchestrator(
            data_sources=[mock_data_source],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            source_selector=mock_source_selector,
            query_processor=mock_query_processor,
            response_formatter=mock_response_formatter
        )
        
        # Execute with session
        response = await orchestrator.process_query(
            query=sample_query,
            tenant_id="test_tenant",
            session_id="test_session_123"
        )
        
        # Assert session preserved
        assert response.session_id == "test_session_123"
    
    @pytest.mark.asyncio
    async def test_streaming_query(
        self,
        sample_query,
        mock_llm_provider,
        mock_embedding_service,
        mock_source_selector,
        mock_query_processor,
        mock_response_formatter
    ):
        """Test streaming query processing"""
        orchestrator = ChatOrchestrator(
            data_sources=[],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            source_selector=mock_source_selector,
            query_processor=mock_query_processor,
            response_formatter=mock_response_formatter
        )
        
        mock_query_processor.preprocess.return_value = sample_query
        
        # Setup streaming mock
        async def mock_stream():
            yield {"type": "chunk", "content": "Test"}
            yield {"type": "chunk", "content": " chunk"}
            yield {"type": "done"}
        
        # Execute streaming
        stream = orchestrator.process_streaming_query(
            query=sample_query,
            tenant_id="test_tenant"
        )
        
        # Collect chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        # Assert we got chunks
        assert len(chunks) > 0

