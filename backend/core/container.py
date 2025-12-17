"""
Dependency Injection Container - Following Dependency Inversion Principle (DIP)
Central configuration for all service dependencies
"""

from dependency_injector import containers, providers
from core.config import AppConfig


class AppContainer(containers.DeclarativeContainer):
    """
    Application Dependency Injection Container
    
    Following SOLID Principles:
    - SRP: Single responsibility - wire dependencies
    - OCP: Open for extension - can add new services without modification
    - DIP: All modules depend on abstractions, wired here
    
    Usage:
        container = AppContainer()
        container.init_resources()
        
        # Get services
        llm_provider = container.llm_provider()
        chat_orchestrator = container.chat_orchestrator()
    """
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    config = providers.Singleton(AppConfig)
    
    # ========================================================================
    # LLM SERVICES
    # ========================================================================
    
    # OpenAI LLM Provider (will be implemented in infrastructure layer)
    llm_provider = providers.Singleton(
        "infrastructure.llm.openai_provider.OpenAIProvider",
        api_key=config.provided.openai.api_key,
        model=config.provided.openai.model,
        temperature=config.provided.openai.temperature,
        max_tokens=config.provided.openai.max_tokens
    )
    
    # Embedding Service
    embedding_service = providers.Singleton(
        "infrastructure.llm.openai_embedding.OpenAIEmbeddingService",
        api_key=config.provided.openai.api_key,
        model=config.provided.openai.embedding_model
    )
    
    # ========================================================================
    # DATABASE CONNECTIONS
    # ========================================================================
    
    # System Database (MySQL from environment variables)
    system_database = providers.Singleton(
        "infrastructure.databases.system_database.SystemDatabaseConnection",
        config=config.provided.system_database
    )
    
    # User Database Factory (creates connections for user-provided databases)
    user_database_factory = providers.Factory(
        "infrastructure.databases.user_database.UserDatabaseConnection"
    )
    
    # Connection Factory (manages both system and user databases)
    connection_factory = providers.Singleton(
        "infrastructure.databases.connection_factory.DatabaseConnectionFactory",
        system_db=system_database,
        user_db_factory=user_database_factory
    )
    
    # ========================================================================
    # VECTOR STORES
    # ========================================================================
    
    # Pinecone Vector Store
    pinecone_store = providers.Singleton(
        "infrastructure.vector_stores.pinecone_store.PineconeVectorStore",
        api_key=config.provided.pinecone.api_key,
        index_name=config.provided.pinecone.index_name,
        enabled=config.provided.pinecone.use_pinecone
    )
    
    # In-Memory Vector Store (fallback)
    in_memory_store = providers.Singleton(
        "infrastructure.vector_stores.in_memory_store.InMemoryVectorStore"
    )
    
    # Vector Store Selector (chooses between Pinecone and in-memory)
    vector_store = providers.Selector(
        config.provided.pinecone.use_pinecone,
        pinecone=pinecone_store,
        in_memory=in_memory_store
    )
    
    # ========================================================================
    # DATA SOURCES
    # ========================================================================
    
    # Vector Data Source (Documents/RAG)
    vector_data_source = providers.Singleton(
        "infrastructure.data_sources.vector_data_source.VectorDataSource",
        vector_store=vector_store,
        embedding_service=embedding_service
    )
    
    # SQL Data Source Factory (creates instances for user databases)
    sql_data_source_factory = providers.Factory(
        "infrastructure.data_sources.sql_data_source.SQLDataSource",
        llm_provider=llm_provider,
        connection_factory=connection_factory
    )
    
    # ========================================================================
    # REPOSITORIES
    # ========================================================================
    
    # Conversation Repository
    conversation_repository = providers.Singleton(
        "infrastructure.repositories.conversation_repository.ConversationRepository",
        db=system_database
    )
    
    # User Repository
    user_repository = providers.Singleton(
        "infrastructure.repositories.user_repository.UserRepository",
        db=system_database
    )
    
    # Metadata Repository (for metadata learning)
    metadata_repository = providers.Singleton(
        "infrastructure.repositories.metadata_repository.MetadataRepository",
        db=system_database
    )
    
    # ========================================================================
    # APPLICATION SERVICES
    # ========================================================================
    
    # Source Selector (decides which data source to use)
    source_selector = providers.Factory(
        "application.services.source_selector.SourceSelector"
    )
    
    # Response Formatter
    response_formatter = providers.Factory(
        "application.services.response_formatter.ResponseFormatter"
    )
    
    # Query Processor
    query_processor = providers.Factory(
        "application.services.query_processor.QueryProcessor",
        llm_provider=llm_provider,
        conversation_repo=conversation_repository
    )
    
    # Chat Orchestrator (main application service)
    chat_orchestrator = providers.Factory(
        "application.services.chat_orchestrator.ChatOrchestrator",
        vector_data_source=vector_data_source,
        sql_data_source_factory=sql_data_source_factory,
        llm_provider=llm_provider,
        source_selector=source_selector,
        response_formatter=response_formatter,
        query_processor=query_processor,
        conversation_repo=conversation_repository
    )
    
    # ========================================================================
    # LEGACY SUPPORT (for gradual migration)
    # ========================================================================
    
    # Legacy services are accessed directly via utils/legacy_bridge.py
    # No DI providers needed as they use direct imports from llm/ modules


# Global container instance
container = AppContainer()

