"""
IRepository Interface - Data access abstraction
Repository pattern for database operations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic

# Generic type for entities
T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Generic repository interface for data access
    
    Following Repository Pattern:
    - Abstracts data access logic
    - Separates business logic from data access
    - Makes code more testable
    
    Following SOLID:
    - SRP: Single responsibility - data access for one entity
    - OCP: Can add new repositories without changes
    - DIP: Services depend on this interface
    """
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        Get all entities matching filter
        
        Args:
            filter: Optional filter criteria
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Add new entity
        
        Args:
            entity: Entity to add
            
        Returns:
            Added entity with generated ID
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> bool:
        """
        Update existing entity
        
        Args:
            entity: Entity to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """
        Delete entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists(self, id: Any) -> bool:
        """
        Check if entity exists
        
        Args:
            id: Entity identifier
            
        Returns:
            True if exists, False otherwise
        """
        pass

