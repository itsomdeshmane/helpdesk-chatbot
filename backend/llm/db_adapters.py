"""
Database Adapters - Support for multiple database types
Supports: MySQL, PostgreSQL, SQL Server

Provides a unified interface for different database systems
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters"""
    
    @abstractmethod
    def get_connection_module(self):
        """Get the database connection module (pymysql, psycopg2, etc.)"""
        pass
    
    @abstractmethod
    def create_connection(self, config: Dict[str, Any]):
        """Create a database connection"""
        pass
    
    @abstractmethod
    def get_connection_string_format(self) -> str:
        """Get connection string format for this database"""
        pass
    
    @abstractmethod
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse connection string to config dict"""
        pass
    
    @abstractmethod
    def adapt_sql_query(self, sql_query: str) -> str:
        """Adapt SQL query for this database (handle dialect differences)"""
        pass
    
    @abstractmethod
    def get_schema_query(self, database: str) -> str:
        """Get query to fetch database schema"""
        pass
    
    @abstractmethod
    def get_limit_syntax(self, limit: int) -> str:
        """Get LIMIT clause syntax for this database"""
        pass
    
    @abstractmethod
    def get_error_code(self, exception) -> Optional[int]:
        """Extract error code from database exception"""
        pass


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter"""
    
    def __init__(self):
        self.db_type = DatabaseType.MYSQL
        logger.info("✅ MySQL adapter initialized")
    
    def get_connection_module(self):
        """Get pymysql module"""
        try:
            import pymysql
            return pymysql
        except ImportError:
            logger.error("pymysql not installed. Install: pip install pymysql")
            raise
    
    def create_connection(self, config: Dict[str, Any]):
        """Create MySQL connection"""
        pymysql = self.get_connection_module()
        from pymysql.cursors import DictCursor
        
        return pymysql.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            user=config.get('user', 'root'),
            password=config.get('password', ''),
            database=config.get('database', ''),
            cursorclass=DictCursor,
            charset='utf8mb4'
        )
    
    def get_connection_string_format(self) -> str:
        """MySQL connection string format"""
        return "host=<host>;port=<port>;database=<database>;user=<user>;password=<password>"
    
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse MySQL connection string"""
        params = {}
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip().lower()] = value.strip()
        
        return {
            'host': params.get('host', params.get('server', 'localhost')),
            'port': int(params.get('port', 3306)),
            'database': params.get('database', params.get('db', '')),
            'user': params.get('user', 'root'),
            'password': params.get('password', '')
        }
    
    def adapt_sql_query(self, sql_query: str) -> str:
        """MySQL uses standard SQL (no adaptation needed)"""
        return sql_query
    
    def get_schema_query(self, database: str) -> str:
        """MySQL schema query"""
        return f"""
        SELECT 
            t.TABLE_NAME as table_name,
            c.COLUMN_NAME as column_name,
            c.DATA_TYPE as data_type,
            c.IS_NULLABLE as is_nullable,
            c.COLUMN_KEY as column_key
        FROM 
            INFORMATION_SCHEMA.TABLES t
            INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
                ON t.TABLE_NAME = c.TABLE_NAME
        WHERE 
            t.TABLE_SCHEMA = '{database}'
            AND t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY 
            t.TABLE_NAME, c.ORDINAL_POSITION
        """
    
    def get_limit_syntax(self, limit: int) -> str:
        """MySQL LIMIT syntax"""
        return f"LIMIT {limit}"
    
    def get_error_code(self, exception) -> Optional[int]:
        """Extract MySQL error code"""
        if hasattr(exception, 'args') and len(exception.args) > 0:
            return exception.args[0]
        return None


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""
    
    def __init__(self):
        self.db_type = DatabaseType.POSTGRESQL
        logger.info("✅ PostgreSQL adapter initialized")
    
    def get_connection_module(self):
        """Get psycopg2 module"""
        try:
            import psycopg2
            import psycopg2.extras
            return psycopg2
        except ImportError:
            logger.error("psycopg2 not installed. Install: pip install psycopg2-binary")
            raise
    
    def create_connection(self, config: Dict[str, Any]):
        """Create PostgreSQL connection"""
        psycopg2 = self.get_connection_module()
        
        return psycopg2.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            user=config.get('user', 'postgres'),
            password=config.get('password', ''),
            database=config.get('database', 'postgres')
        )
    
    def get_connection_string_format(self) -> str:
        """PostgreSQL connection string format"""
        return "host=<host>;port=<port>;database=<database>;user=<user>;password=<password>"
    
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse PostgreSQL connection string"""
        params = {}
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip().lower()] = value.strip()
        
        return {
            'host': params.get('host', params.get('server', 'localhost')),
            'port': int(params.get('port', 5432)),
            'database': params.get('database', params.get('db', 'postgres')),
            'user': params.get('user', 'postgres'),
            'password': params.get('password', '')
        }
    
    def adapt_sql_query(self, sql_query: str) -> str:
        """
        Adapt SQL for PostgreSQL
        - LIMIT syntax is the same
        - String concatenation uses || instead of CONCAT
        """
        # PostgreSQL uses || for concatenation, but also supports CONCAT
        # Most standard SQL should work as-is
        return sql_query
    
    def get_schema_query(self, database: str) -> str:
        """PostgreSQL schema query"""
        return """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            CASE 
                WHEN pk.column_name IS NOT NULL THEN 'PRI'
                ELSE ''
            END as column_key
        FROM 
            information_schema.tables t
            INNER JOIN information_schema.columns c 
                ON t.table_name = c.table_name
            LEFT JOIN (
                SELECT ku.table_name, ku.column_name
                FROM information_schema.table_constraints tc
                INNER JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.table_name = pk.table_name 
                AND c.column_name = pk.column_name
        WHERE 
            t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
        ORDER BY 
            t.table_name, c.ordinal_position
        """
    
    def get_limit_syntax(self, limit: int) -> str:
        """PostgreSQL LIMIT syntax"""
        return f"LIMIT {limit}"
    
    def get_error_code(self, exception) -> Optional[int]:
        """Extract PostgreSQL error code"""
        if hasattr(exception, 'pgcode'):
            # Convert pgcode to integer (e.g., '42P01' -> 42)
            try:
                return int(exception.pgcode[:2])
            except:
                return None
        return None


class SQLServerAdapter(DatabaseAdapter):
    """SQL Server database adapter"""
    
    def __init__(self):
        self.db_type = DatabaseType.SQLSERVER
        logger.info("✅ SQL Server adapter initialized")
    
    def get_connection_module(self):
        """Get pyodbc module"""
        try:
            import pyodbc
            return pyodbc
        except ImportError:
            logger.error("pyodbc not installed. Install: pip install pyodbc")
            raise
    
    def create_connection(self, config: Dict[str, Any]):
        """Create SQL Server connection"""
        pyodbc = self.get_connection_module()
        
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.get('host', 'localhost')};"
            f"DATABASE={config.get('database', 'master')};"
            f"UID={config.get('user', 'sa')};"
            f"PWD={config.get('password', '')}"
        )
        
        if config.get('port'):
            conn_str = conn_str.replace(
                f"SERVER={config['host']}",
                f"SERVER={config['host']},{config['port']}"
            )
        
        return pyodbc.connect(conn_str)
    
    def get_connection_string_format(self) -> str:
        """SQL Server connection string format"""
        return "host=<host>;port=<port>;database=<database>;user=<user>;password=<password>"
    
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse SQL Server connection string"""
        params = {}
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip().lower()] = value.strip()
        
        return {
            'host': params.get('host', params.get('server', 'localhost')),
            'port': int(params.get('port', 1433)) if params.get('port') else None,
            'database': params.get('database', params.get('db', 'master')),
            'user': params.get('user', params.get('uid', 'sa')),
            'password': params.get('password', params.get('pwd', ''))
        }
    
    def adapt_sql_query(self, sql_query: str) -> str:
        """
        Adapt SQL for SQL Server
        - LIMIT -> TOP
        - CONCAT works the same
        """
        # Replace LIMIT with TOP (more complex transformation needed)
        import re
        
        # Pattern: SELECT ... LIMIT N
        # Replace with: SELECT TOP N ...
        pattern = r'SELECT\s+(.*?)\s+LIMIT\s+(\d+)'
        
        def replace_limit(match):
            select_clause = match.group(1)
            limit_value = match.group(2)
            return f"SELECT TOP {limit_value} {select_clause}"
        
        adapted = re.sub(pattern, replace_limit, sql_query, flags=re.IGNORECASE)
        
        return adapted
    
    def get_schema_query(self, database: str) -> str:
        """SQL Server schema query"""
        return f"""
        SELECT 
            t.TABLE_NAME as table_name,
            c.COLUMN_NAME as column_name,
            c.DATA_TYPE as data_type,
            c.IS_NULLABLE as is_nullable,
            CASE 
                WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PRI'
                ELSE ''
            END as column_key
        FROM 
            [{database}].INFORMATION_SCHEMA.TABLES t
            INNER JOIN [{database}].INFORMATION_SCHEMA.COLUMNS c 
                ON t.TABLE_NAME = c.TABLE_NAME
            LEFT JOIN (
                SELECT ku.TABLE_NAME, ku.COLUMN_NAME
                FROM [{database}].INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                INNER JOIN [{database}].INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                    ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ) pk ON c.TABLE_NAME = pk.TABLE_NAME 
                AND c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE 
            t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY 
            t.TABLE_NAME, c.ORDINAL_POSITION
        """
    
    def get_limit_syntax(self, limit: int) -> str:
        """SQL Server uses TOP instead of LIMIT"""
        return f"TOP {limit}"
    
    def get_error_code(self, exception) -> Optional[int]:
        """Extract SQL Server error code"""
        # pyodbc exceptions have args[0] as error tuple
        if hasattr(exception, 'args') and len(exception.args) > 0:
            # Error format: ('error_code', 'message')
            if isinstance(exception.args[0], tuple):
                return exception.args[0][0]
        return None


class DatabaseAdapterFactory:
    """Factory for creating database adapters"""
    
    _adapters = {
        DatabaseType.MYSQL: MySQLAdapter,
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
        DatabaseType.SQLSERVER: SQLServerAdapter
    }
    
    @classmethod
    def get_adapter(cls, db_type: str) -> DatabaseAdapter:
        """
        Get database adapter for the specified type
        
        Args:
            db_type: Database type ('mysql', 'postgresql', 'sqlserver')
            
        Returns:
            DatabaseAdapter instance
        """
        try:
            db_type_enum = DatabaseType(db_type.lower())
        except ValueError:
            supported = [t.value for t in DatabaseType]
            raise ValueError(f"Unsupported database type: {db_type}. Supported: {supported}")
        
        adapter_class = cls._adapters.get(db_type_enum)
        if not adapter_class:
            raise ValueError(f"No adapter found for database type: {db_type}")
        
        return adapter_class()
    
    @classmethod
    def get_supported_databases(cls) -> List[str]:
        """Get list of supported database types"""
        return [db_type.value for db_type in DatabaseType]
    
    @classmethod
    def get_default_ports(cls) -> Dict[str, int]:
        """Get default ports for each database type"""
        return {
            DatabaseType.MYSQL.value: 3306,
            DatabaseType.POSTGRESQL.value: 5432,
            DatabaseType.SQLSERVER.value: 1433
        }


def get_database_adapter(db_type: str) -> DatabaseAdapter:
    """
    Get database adapter (convenience function)
    
    Args:
        db_type: Database type string
        
    Returns:
        DatabaseAdapter instance
    """
    return DatabaseAdapterFactory.get_adapter(db_type)

