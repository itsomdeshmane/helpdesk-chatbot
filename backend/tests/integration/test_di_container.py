"""
Integration tests for DI Container

Tests that the container properly wires dependencies.
"""

import pytest
from core.container import AppContainer


@pytest.mark.integration
class TestDIContainer:
    """Test dependency injection container"""
    
    def test_container_initialization(self):
        """Test container can be initialized"""
        container = AppContainer()
        assert container is not None
    
    def test_config_provider(self):
        """Test config provider"""
        container = AppContainer()
        config = container.config()
        
        assert config is not None
        assert hasattr(config, 'openai')
        assert hasattr(config, 'system_database')
    
    def test_llm_provider(self):
        """Test LLM provider can be created"""
        container = AppContainer()
        llm = container.llm_provider()
        
        assert llm is not None
        assert hasattr(llm, 'generate_completion')
        assert llm.get_provider_name() == "openai"
    
    def test_embedding_service(self):
        """Test embedding service can be created"""
        container = AppContainer()
        embeddings = container.embedding_service()
        
        assert embeddings is not None
        assert hasattr(embeddings, 'create_embedding')
        assert embeddings.get_provider_name() == "openai"
    
    def test_vector_stores(self):
        """Test vector stores can be created"""
        container = AppContainer()
        
        # In-memory store
        in_memory = container.in_memory_vector_store()
        assert in_memory is not None
        
        # Pinecone store (may be None if not configured)
        # pinecone = container.pinecone_vector_store()
        # This is okay to be None in test environment
    
    def test_data_sources(self):
        """Test data sources can be created"""
        container = AppContainer()
        
        vector_source = container.vector_data_source()
        assert vector_source is not None
        assert vector_source.get_source_type() == "documents"
    
    def test_application_services(self):
        """Test application services can be created"""
        container = AppContainer()
        
        # Source selector
        selector = container.source_selector()
        assert selector is not None
        
        # Query processor
        processor = container.query_processor()
        assert processor is not None
        
        # Response formatter
        formatter = container.response_formatter()
        assert formatter is not None
        
        # Chat orchestrator
        orchestrator = container.chat_orchestrator()
        assert orchestrator is not None
    
    def test_singleton_behavior(self):
        """Test that singletons return same instance"""
        container = AppContainer()
        
        llm1 = container.llm_provider()
        llm2 = container.llm_provider()
        
        # Should be same instance (singleton)
        assert llm1 is llm2

