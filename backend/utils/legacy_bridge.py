"""
Legacy Bridge Module

This module provides compatibility between old (global state) and new (DI) code.

Purpose:
- Allow gradual migration from global state to dependency injection
- Maintain backward compatibility during transition
- Enable old and new code to coexist

IMPORTANT: This is a TEMPORARY module for migration only.
Once all code is migrated to use DI, this module can be removed.
"""

import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class LegacyBridge:
    """
    Bridge between legacy global state and new DI architecture
    
    This class provides access to DI-managed instances for legacy code
    that still expects global singletons.
    
    Usage in legacy code:
        # Old way:
        from llm.rag import in_memory_docs
        
        # Migration path:
        from utils.legacy_bridge import get_vector_store
        vector_store = get_vector_store()
    """
    
    _container = None  # Will be set by app.py at startup
    
    @classmethod
    def set_container(cls, container):
        """
        Set the DI container
        
        Called once at application startup
        
        Args:
            container: The AppContainer instance
        """
        cls._container = container
        logger.info("✅ Legacy bridge connected to DI container")
    
    @classmethod
    def get_container(cls):
        """Get the DI container"""
        if cls._container is None:
            logger.warning("⚠️  DI container not set, legacy bridge inactive")
        return cls._container
    
    @classmethod
    def get_llm_provider(cls):
        """Get LLM provider from DI container"""
        container = cls.get_container()
        if container:
            return container.llm_provider()
        return None
    
    @classmethod
    def get_embedding_service(cls):
        """Get embedding service from DI container"""
        container = cls.get_container()
        if container:
            return container.embedding_service()
        return None
    
    @classmethod
    def get_vector_store(cls):
        """Get vector store from DI container"""
        container = cls.get_container()
        if container:
            # Return in-memory store for backward compatibility
            return container.in_memory_vector_store()
        return None
    
    @classmethod
    def get_system_database(cls):
        """Get system database from DI container"""
        container = cls.get_container()
        if container:
            return container.system_database()
        return None
    
    @classmethod
    def get_chat_orchestrator(cls):
        """Get chat orchestrator from DI container"""
        container = cls.get_container()
        if container:
            return container.chat_orchestrator()
        return None


# Convenience functions for legacy code migration

def get_llm_provider():
    """
    Get LLM provider (for legacy code migration)
    
    Usage:
        # Instead of: from config import GPT_MODEL
        # Use:
        from utils.legacy_bridge import get_llm_provider
        llm = get_llm_provider()
        response = await llm.generate_completion(messages)
    """
    return LegacyBridge.get_llm_provider()


def get_embedding_service():
    """
    Get embedding service (for legacy code migration)
    
    Usage:
        # Instead of: import openai; openai.Embedding.create()
        # Use:
        from utils.legacy_bridge import get_embedding_service
        embeddings = get_embedding_service()
        vector = await embeddings.create_embedding("text")
    """
    return LegacyBridge.get_embedding_service()


def get_vector_store():
    """
    Get vector store (for legacy code migration)
    
    Usage:
        # Instead of: from llm.rag import in_memory_docs
        # Use:
        from utils.legacy_bridge import get_vector_store
        store = get_vector_store()
        results = await store.search(embedding, "tenant", 5)
    """
    return LegacyBridge.get_vector_store()


def get_system_database():
    """
    Get system database (for legacy code migration)
    
    Usage:
        # Instead of: from database.db_manager import db_manager
        # Use:
        from utils.legacy_bridge import get_system_database
        db = get_system_database()
        results = await db.execute_query("SELECT ...")
    """
    return LegacyBridge.get_system_database()


def get_chat_orchestrator():
    """
    Get chat orchestrator (for legacy code migration)
    
    Usage:
        from utils.legacy_bridge import get_chat_orchestrator
        orchestrator = get_chat_orchestrator()
        response = await orchestrator.process_query(query)
    """
    return LegacyBridge.get_chat_orchestrator()


# Global state wrapper for in_memory_docs
class InMemoryDocsWrapper:
    """
    Wrapper for legacy in_memory_docs global variable
    
    This provides backward compatibility for code that uses:
        from llm.rag import in_memory_docs
    
    Usage in legacy code:
        # Old way (still works):
        from llm.rag import in_memory_docs
        docs = in_memory_docs.get("tenant_id", [])
        
        # New way (preferred):
        from utils.legacy_bridge import get_vector_store
        store = get_vector_store()
    """
    
    def __init__(self):
        self._docs: Dict[str, list] = {}
    
    def get(self, tenant_id: str, default=None):
        """Get documents for tenant"""
        return self._docs.get(tenant_id, default if default is not None else [])
    
    def set(self, tenant_id: str, docs: list):
        """Set documents for tenant"""
        self._docs[tenant_id] = docs
    
    def clear(self, tenant_id: Optional[str] = None):
        """Clear documents"""
        if tenant_id:
            self._docs.pop(tenant_id, None)
        else:
            self._docs.clear()
    
    def __len__(self):
        """Total number of documents across all tenants"""
        return sum(len(docs) for docs in self._docs.values())
    
    def __getitem__(self, tenant_id: str):
        """Dict-like access"""
        return self._docs.get(tenant_id, [])
    
    def __setitem__(self, tenant_id: str, docs: list):
        """Dict-like setting"""
        self._docs[tenant_id] = docs


# Create singleton instance for backward compatibility
_in_memory_docs_wrapper = InMemoryDocsWrapper()


def get_in_memory_docs():
    """
    Get the in-memory docs wrapper
    
    This maintains backward compatibility with code that uses:
        from llm.rag import in_memory_docs
    """
    return _in_memory_docs_wrapper


# Migration helpers

def is_new_architecture_available() -> bool:
    """
    Check if new SOLID architecture is available
    
    Returns:
        True if DI container is set up and ready
    """
    return LegacyBridge.get_container() is not None


def log_migration_warning(component: str, old_way: str, new_way: str):
    """
    Log a migration warning for deprecated usage
    
    Args:
        component: Component name
        old_way: Old code pattern
        new_way: New code pattern
    """
    logger.warning(
        f"⚠️  MIGRATION: {component} is using legacy pattern.\n"
        f"   Old: {old_way}\n"
        f"   New: {new_way}\n"
        f"   Please migrate to new SOLID architecture."
    )


# Export public API
__all__ = [
    'LegacyBridge',
    'get_llm_provider',
    'get_embedding_service',
    'get_vector_store',
    'get_system_database',
    'get_chat_orchestrator',
    'get_in_memory_docs',
    'InMemoryDocsWrapper',
    'is_new_architecture_available',
    'log_migration_warning'
]

