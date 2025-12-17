"""
IDatabaseConnection Interface - Database abstraction
Supports both system database (env config) and user dynamic databases
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager


class IDatabaseConnection(ABC):
    """
    Interface for database connections
    
    Supports:
    - System database (MySQL from environment variables)
    - User dynamic databases (connection string from user settings)
    - Multiple database types (MySQL, PostgreSQL, SQL Server, etc.)
    
    Following SOLID:
    - SRP: Single responsibility - database operations
    - OCP: Can add new database types without modifying code
    - DIP: Application layer depends on this interface
    """
    
    @abstractmethod
    @asynccontextmanager
    async def get_connection(self):
        """
        Get database connection as async context manager
        
        Yields:
            Database connection object
            
        Example:
            >>> async with db.get_connection() as conn:
            ...     result = await conn.execute("SELECT 1")
        """
        pass
    
    @abstractmethod
    async def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as dictionaries
        
        Args:
            query: SQL query string (parameterized)
            params: Query parameters (prevents SQL injection)
            
        Returns:
            List of rows as dictionaries
            
        Example:
            >>> results = await db.execute_query(
            ...     "SELECT * FROM users WHERE id = %s",
            ...     (user_id,)
            ... )
        """
        pass
    
    @abstractmethod
    async def execute_non_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> int:
        """
        Execute INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string (parameterized)
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """
        Get database schema information
        
        Returns:
            Dictionary with tables, columns, types, etc.
            Format:
            {
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "INT", "nullable": False},
                            ...
                        ]
                    },
                    ...
                ]
            }
        """
        pass
    
    @abstractmethod
    def get_connection_type(self) -> str:
        """
        Return connection type
        
        Returns:
            'system' for system database (env config)
            'user' for user dynamic database
        """
        pass
    
    @abstractmethod
    def get_database_type(self) -> str:
        """
        Return database type
        
        Returns:
            Database type identifier (e.g., 'mysql', 'postgresql')
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy
        
        Returns:
            True if connection is operational, False otherwise
        """
        pass

