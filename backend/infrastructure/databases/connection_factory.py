"""
Database Connection Factory
Manages both system database (env) and user dynamic databases
"""

import logging
from typing import Optional, Dict
from core.interfaces.database import IDatabaseConnection
from infrastructure.databases.system_database import SystemDatabaseConnection
from infrastructure.databases.user_database import UserDatabaseConnection

logger = logging.getLogger(__name__)


class DatabaseConnectionFactory:
    """
    Factory for creating and managing database connections
    
    Manages:
    - System database (singleton from environment)
    - User databases (created on-demand from connection strings)
    
    Following SOLID:
    - SRP: Single responsibility - database connection management
    - OCP: Can add new database types without modification
    - DIP: Returns IDatabaseConnection interface
    """
    
    def __init__(
        self,
        system_db: SystemDatabaseConnection,
        user_db_factory
    ):
        """
        Initialize connection factory
        
        Args:
            system_db: System database connection (singleton)
            user_db_factory: Factory for creating user database connections
        """
        self._system_db = system_db
        self._user_db_factory = user_db_factory
        
        # Cache for user database connections (by connection string)
        self._user_db_cache: Dict[str, UserDatabaseConnection] = {}
        
        logger.info("Database Connection Factory initialized")
    
    def get_system_database(self) -> IDatabaseConnection:
        """
        Get system database connection
        
        Returns:
            System database connection (from environment)
        """
        return self._system_db
    
    def get_user_database(self, connection_string: str) -> IDatabaseConnection:
        """
        Get user database connection (creates if not cached)
        
        Args:
            connection_string: User's database connection string
            
        Returns:
            User database connection
            
        Note:
            Connections are cached by connection string for efficiency
        """
        # Check cache first
        if connection_string in self._user_db_cache:
            logger.debug(f"Returning cached user database connection")
            return self._user_db_cache[connection_string]
        
        # Create new connection
        logger.info(f"Creating new user database connection")
        user_db = self._user_db_factory(connection_string=connection_string)
        
        # Cache for future use
        self._user_db_cache[connection_string] = user_db
        
        return user_db
    
    def get_database(
        self,
        connection_string: Optional[str] = None,
        use_system: bool = False
    ) -> IDatabaseConnection:
        """
        Get database connection (system or user)
        
        Args:
            connection_string: Optional user connection string
            use_system: Force use of system database
            
        Returns:
            Database connection (system or user)
            
        Note:
            If connection_string is None and use_system is False,
            returns system database by default
        """
        if use_system or connection_string is None:
            return self.get_system_database()
        else:
            return self.get_user_database(connection_string)
    
    async def test_connection(self, connection_string: str) -> bool:
        """
        Test a connection string without caching
        
        Args:
            connection_string: Connection string to test
            
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Create temporary connection (don't cache)
            temp_db = self._user_db_factory(connection_string=connection_string)
            result = await temp_db.health_check()
            logger.info(f"Connection test result: {result}")
            return result
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def clear_cache(self):
        """Clear user database connection cache"""
        logger.info(f"Clearing user database cache ({len(self._user_db_cache)} connections)")
        self._user_db_cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached user connections"""
        return len(self._user_db_cache)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all connections
        
        Returns:
            Dictionary with health status of system and cached user databases
        """
        results = {}
        
        # Check system database
        try:
            results['system'] = await self._system_db.health_check()
        except Exception as e:
            logger.error(f"System database health check failed: {e}")
            results['system'] = False
        
        # Check cached user databases
        for i, (conn_str, user_db) in enumerate(self._user_db_cache.items()):
            try:
                key = f"user_{i+1}"
                results[key] = await user_db.health_check()
            except Exception as e:
                logger.error(f"User database {i+1} health check failed: {e}")
                results[f"user_{i+1}"] = False
        
        return results

