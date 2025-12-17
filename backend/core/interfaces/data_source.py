"""
IDataSource Interface - Following Open-Closed Principle (OCP)
Allows adding new data sources without modifying existing code
"""

from abc import ABC, abstractmethod
from typing import Optional
from core.models.query import Query
from core.models.response import DataSourceResponse


class IDataSource(ABC):
    """
    Interface for data sources (documents, databases, APIs, etc.)
    
    Following SOLID Principles:
    - SRP: Single responsibility - handle one type of data source
    - OCP: Open for extension (new sources), closed for modification
    - LSP: All implementations must be substitutable
    - ISP: Interface segregation - only essential methods
    - DIP: High-level modules depend on this abstraction
    """
    
    @abstractmethod
    async def can_handle(self, query: Query) -> bool:
        """
        Determine if this data source can handle the query
        
        Args:
            query: The user query to evaluate
            
        Returns:
            True if this source is appropriate for the query, False otherwise
            
        Example:
            VectorDataSource returns True for "How do I create a work order?"
            SQLDataSource returns True for "Show me all customers"
        """
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: Query,
        tenant_id: str,
        limit: int = 5
    ) -> DataSourceResponse:
        """
        Search this data source for relevant information
        
        Args:
            query: The user query
            tenant_id: Tenant identifier for multi-tenancy
            limit: Maximum number of results to return
            
        Returns:
            DataSourceResponse with results and metadata
            
        Raises:
            Should not raise exceptions - return error in DataSourceResponse
        """
        pass
    
    @abstractmethod
    def get_source_type(self) -> str:
        """
        Return the type of data source
        
        Returns:
            String identifier (e.g., 'documents', 'database', 'api')
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if data source is available and healthy
        
        Returns:
            True if data source is operational, False otherwise
        """
        pass

