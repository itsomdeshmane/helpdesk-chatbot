"""
User Database Connection - Dynamic MySQL connections from user settings
Parses connection strings and creates database connections on-demand
"""

import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import pymysql
from pymysql.cursors import DictCursor
from core.interfaces.database import IDatabaseConnection

logger = logging.getLogger(__name__)


class UserDatabaseConnection(IDatabaseConnection):
    """
    User dynamic database connection
    
    Parses connection strings from user settings and creates connections
    Following SOLID:
    - SRP: Single responsibility - user database operations
    - OCP: Implements IDatabaseConnection interface
    - LSP: Substitutable for any IDatabaseConnection
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize user database connection
        
        Args:
            connection_string: Connection string format:
                "host=x;port=p;database=d;user=u;password=pw"
        """
        self._connection_string = connection_string
        self._connection_params = self._parse_connection_string(connection_string)
        
        logger.info(
            f"User Database initialized: "
            f"{self._connection_params['host']}:"
            f"{self._connection_params['port']}/"
            f"{self._connection_params['database']}"
        )
    
    def _parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """
        Parse connection string into parameters
        
        Args:
            connection_string: Connection string
            
        Returns:
            Dictionary of connection parameters
        """
        params = {
            'host': 'localhost',
            'port': 3306,
            'database': '',
            'user': 'root',
            'password': ''
        }
        
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Map alternative keys
                if key in ['server']:
                    key = 'host'
                elif key in ['db', 'database_name']:
                    key = 'database'
                elif key in ['username']:
                    key = 'user'
                elif key in ['pwd']:
                    key = 'password'
                
                # Convert port to int
                if key == 'port':
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Invalid port value: {value}, using default 3306")
                        value = 3306
                
                params[key] = value
        
        return params
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get database connection as async context manager
        
        Yields:
            Database connection wrapper
        """
        connection = None
        try:
            # Create connection
            connection = pymysql.connect(
                host=self._connection_params['host'],
                port=self._connection_params['port'],
                user=self._connection_params['user'],
                password=self._connection_params['password'],
                database=self._connection_params['database'],
                cursorclass=DictCursor,
                charset='utf8mb4',
                autocommit=False
            )
            
            yield connection
            
        except pymysql.Error as e:
            if connection:
                connection.rollback()
            logger.error(f"User database error: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
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
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
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
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
    
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
            WHERE TABLE_SCHEMA = %s
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
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        
        db_name = self._connection_params['database']
        tables = await self.execute_query(tables_query, (db_name,))
        columns = await self.execute_query(columns_query, (db_name,))
        
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
        return "user"
    
    def get_database_type(self) -> str:
        """Return database type"""
        return "mysql"
    
    def get_connection_string(self) -> str:
        """Get the connection string (for logging/debugging)"""
        # Return sanitized version (hide password)
        sanitized = self._connection_string
        if 'password=' in sanitized:
            parts = sanitized.split('password=')
            if len(parts) > 1:
                after_pwd = parts[1].split(';', 1)
                sanitized = parts[0] + 'password=***' + (';' + after_pwd[1] if len(after_pwd) > 1 else '')
        return sanitized
    
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

