"""
System Database Connection - MySQL from environment variables
Wraps existing database/db_manager.py for backward compatibility
"""

import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import mysql.connector
from mysql.connector import Error, pooling
from core.interfaces.database import IDatabaseConnection

logger = logging.getLogger(__name__)


class SystemDatabaseConnection(IDatabaseConnection):
    """
    System database connection (MySQL from environment)
    
    Wraps the existing DatabaseManager for backward compatibility
    Following SOLID:
    - SRP: Single responsibility - system database operations
    - OCP: Implements IDatabaseConnection interface
    - DIP: Application layer depends on interface, not this class
    """
    
    def __init__(self, config):
        """
        Initialize system database connection
        
        Args:
            config: Database configuration object (from core.config)
        """
        self._config = config
        self._connection_pool = None
        self._initialize_pool()
        
        logger.info(f"System Database initialized: {config.host}:{config.port}/{config.database}")
    
    def _initialize_pool(self):
        """Initialize MySQL connection pool"""
        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name="system_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self._config.host,
                port=self._config.port,
                user=self._config.user,
                password=self._config.password,
                database=self._config.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            logger.info("System database connection pool initialized")
        except Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get database connection as async context manager
        
        Yields:
            Database connection wrapper
        """
        connection = None
        try:
            if self._connection_pool is None:
                raise Error("Connection pool not initialized")
            
            connection = self._connection_pool.get_connection()
            
            # Wrap connection to provide dict-like cursor
            yield self._wrap_connection(connection)
            
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def _wrap_connection(self, conn):
        """Wrap connection to provide dict-like results"""
        class ConnectionWrapper:
            def __init__(self, connection):
                self._conn = connection
            
            def execute(self, query, params=None):
                cursor = self._conn.cursor()
                cursor.execute(query, params or ())
                return self._dict_cursor(cursor)
            
            def _dict_cursor(self, cursor):
                class DictCursor:
                    def __init__(self, cur):
                        self._cursor = cur
                    
                    def fetchone(self):
                        row = self._cursor.fetchone()
                        if row:
                            columns = [desc[0] for desc in self._cursor.description]
                            return dict(zip(columns, row))
                        return None
                    
                    def fetchall(self):
                        rows = self._cursor.fetchall()
                        if rows:
                            columns = [desc[0] for desc in self._cursor.description]
                            return [dict(zip(columns, row)) for row in rows]
                        return []
                
                return DictCursor(cursor)
            
            def commit(self):
                self._conn.commit()
            
            def rollback(self):
                self._conn.rollback()
        
        return ConnectionWrapper(conn)
    
    async def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as dictionaries
        
        Args:
            query: SQL query string (parameterized)
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        async with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
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
        async with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor._cursor.rowcount
    
    async def get_schema(self) -> Dict[str, Any]:
        """
        Get database schema information
        
        Returns:
            Dictionary with tables and columns
        """
        tables_query = """
            SELECT 
                TABLE_NAME as table_name,
                TABLE_TYPE as table_type,
                TABLE_ROWS as row_count,
                TABLE_COMMENT as description
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        
        columns_query = """
            SELECT 
                TABLE_NAME as table_name,
                COLUMN_NAME as column_name,
                DATA_TYPE as data_type,
                IS_NULLABLE as nullable,
                COLUMN_COMMENT as description
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        
        tables = await self.execute_query(tables_query)
        columns = await self.execute_query(columns_query)
        
        # Organize columns by table
        schema = {"tables": []}
        table_columns = {}
        
        for col in columns:
            table_name = col['table_name']
            if table_name not in table_columns:
                table_columns[table_name] = []
            table_columns[table_name].append({
                "name": col['column_name'],
                "type": col['data_type'],
                "nullable": col['nullable'] == 'YES',
                "description": col.get('description', '')
            })
        
        for table in tables:
            table_name = table['table_name']
            schema["tables"].append({
                "name": table_name,
                "type": table.get('table_type', 'BASE TABLE'),
                "row_count": table.get('row_count', 0),
                "description": table.get('description', ''),
                "columns": table_columns.get(table_name, [])
            })
        
        return schema
    
    def get_connection_type(self) -> str:
        """Return connection type"""
        return "system"
    
    def get_database_type(self) -> str:
        """Return database type"""
        return "mysql"
    
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy
        
        Returns:
            True if connection is operational, False otherwise
        """
        try:
            await self.execute_query("SELECT 1")
            return True
        except:
            return False

