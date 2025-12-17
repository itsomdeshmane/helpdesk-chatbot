"""
Core Interfaces - Following Dependency Inversion Principle (DIP)
All high-level modules depend on these abstractions, not concrete implementations
"""

from .data_source import IDataSource
from .llm_provider import ILLMProvider
from .embedding_service import IEmbeddingService
from .database import IDatabaseConnection
from .vector_store import IVectorStore
from .repository import IRepository

__all__ = [
    "IDataSource",
    "ILLMProvider",
    "IEmbeddingService",
    "IDatabaseConnection",
    "IVectorStore",
    "IRepository",
]

