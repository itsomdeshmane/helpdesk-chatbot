"""
Pytest Configuration and Fixtures

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import core modules
from core.config import DatabaseConfig, OpenAIConfig, Settings
from core.models.query import Query, QueryContext
from core.models.response import DataSourceResponse, ChatResponse
from core.interfaces.llm_provider import ILLMProvider
from core.interfaces.embedding_service import IEmbeddingService
from core.interfaces.vector_store import IVectorStore
from core.interfaces.database import IDatabaseConnection


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_db_config():
    """Mock database configuration"""
    return DatabaseConfig(
        host="localhost",
        port=3306,
        user="test_user",
        password="test_password",
        database="test_db"
    )


@pytest.fixture
def mock_openai_config():
    """Mock OpenAI configuration"""
    return OpenAIConfig(
        api_key="sk-test-key",
        model="gpt-4",
        embedding_model="text-embedding-3-small",
        max_tokens=500,
        temperature=0.7
    )


@pytest.fixture
def mock_settings(mock_db_config, mock_openai_config):
    """Mock application settings"""
    return Settings(
        system_database=mock_db_config,
        openai=mock_openai_config
    )


# ============================================================================
# Domain Model Fixtures
# ============================================================================

@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return Query(
        text="How do I create a work order?",
        source_preference="auto",
        context=QueryContext(
            session_id="test_session_123",
            tenant_id="test_tenant",
            user_id="test_user"
        )
    )


@pytest.fixture
def sample_query_context():
    """Sample query context"""
    return QueryContext(
        session_id="test_session",
        tenant_id="test_tenant",
        user_id="test_user"
    )


@pytest.fixture
def sample_data_source_response():
    """Sample data source response"""
    return DataSourceResponse(
        success=True,
        results=["Result 1", "Result 2"],
        source="documents",
        metadata={"score": 0.95}
    )


@pytest.fixture
def sample_chat_response():
    """Sample chat response"""
    return ChatResponse(
        success=True,
        message="Here's how to create a work order...",
        source="documents",
        session_id="test_session",
        confidence_score=0.95
    )


# ============================================================================
# Mock Interface Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider"""
    mock = AsyncMock(spec=ILLMProvider)
    mock.get_provider_name.return_value = "mock_llm"
    mock.get_model.return_value = "gpt-4"
    mock.generate_completion.return_value = "This is a test response"
    mock.count_tokens.return_value = 10
    
    # Mock streaming
    async def mock_stream():
        yield "This "
        yield "is "
        yield "a "
        yield "stream"
    
    mock.generate_streaming.return_value = mock_stream()
    
    return mock


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service"""
    mock = AsyncMock(spec=IEmbeddingService)
    mock.get_provider_name.return_value = "mock_embeddings"
    mock.get_embedding_dimension.return_value = 1536
    mock.create_embedding.return_value = [0.1] * 1536
    mock.create_embeddings.return_value = [[0.1] * 1536, [0.2] * 1536]
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    mock = AsyncMock(spec=IVectorStore)
    mock.is_healthy.return_value = True
    mock.search.return_value = [
        {
            "id": "doc1",
            "text": "Test document 1",
            "score": 0.95,
            "metadata": {}
        },
        {
            "id": "doc2",
            "text": "Test document 2",
            "score": 0.85,
            "metadata": {}
        }
    ]
    mock.get_stats.return_value = {
        "total_vectors": 100,
        "dimensions": 1536
    }
    return mock


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock = AsyncMock(spec=IDatabaseConnection)
    mock.get_connection_type.return_value = "mysql"
    mock.health_check.return_value = True
    mock.execute_query.return_value = [
        {"id": 1, "name": "Test 1"},
        {"id": 2, "name": "Test 2"}
    ]
    mock.get_schema.return_value = {
        "tables": [
            {
                "name": "customers",
                "columns": [
                    {"name": "id", "type": "int"},
                    {"name": "name", "type": "varchar"}
                ]
            }
        ]
    }
    return mock


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def mock_source_selector():
    """Mock source selector"""
    from application.services.source_selector import SourceSelector
    mock = AsyncMock(spec=SourceSelector)
    mock.select_sources.return_value = ["vector", "sql"]
    mock.should_use_vector.return_value = True
    mock.should_use_database.return_value = False
    return mock


@pytest.fixture
def mock_query_processor():
    """Mock query processor"""
    from application.services.query_processor import QueryProcessor
    mock = AsyncMock(spec=QueryProcessor)
    mock.preprocess.return_value = Query(text="Preprocessed query")
    mock.extract_intent.return_value = "information_retrieval"
    mock.extract_entities.return_value = {"entity": "work order"}
    return mock


@pytest.fixture
def mock_response_formatter():
    """Mock response formatter"""
    from application.services.response_formatter import ResponseFormatter
    mock = Mock(spec=ResponseFormatter)
    mock.format_response.return_value = ChatResponse(
        success=True,
        message="Formatted response",
        source="test"
    )
    return mock


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def sample_messages():
    """Sample message history for LLM"""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How do I create a work order?"}
    ]


@pytest.fixture
def sample_embedding():
    """Sample embedding vector"""
    return [0.1] * 1536


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "doc1",
            "text": "To create a work order, go to...",
            "metadata": {"source": "manual", "page": 1}
        },
        {
            "id": "doc2",
            "text": "Work orders can be created by...",
            "metadata": {"source": "manual", "page": 2}
        }
    ]


# ============================================================================
# Test Helpers
# ============================================================================

def assert_implements_interface(instance, interface):
    """
    Assert that an instance implements an interface
    
    Args:
        instance: The instance to check
        interface: The interface class
    """
    assert isinstance(instance, interface), \
        f"{instance.__class__.__name__} does not implement {interface.__name__}"


def assert_async_method(obj, method_name):
    """
    Assert that a method is async
    
    Args:
        obj: Object with the method
        method_name: Name of the method
    """
    import inspect
    method = getattr(obj, method_name)
    assert inspect.iscoroutinefunction(method), \
        f"{method_name} should be an async method"


@pytest.fixture
def assert_interface():
    """Fixture for interface assertion helper"""
    return assert_implements_interface


@pytest.fixture
def assert_async():
    """Fixture for async method assertion helper"""
    return assert_async_method


# ============================================================================
# Async Helpers
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mocks(mock_llm_provider, mock_embedding_service, 
                mock_vector_store, mock_database_connection):
    """Reset all mocks after each test"""
    yield
    mock_llm_provider.reset_mock()
    mock_embedding_service.reset_mock()
    mock_vector_store.reset_mock()
    mock_database_connection.reset_mock()

