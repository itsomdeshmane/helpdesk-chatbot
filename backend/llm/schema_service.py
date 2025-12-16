"""
Database Schema Service
Equivalent to GenericSchemaService from .NET implementation
"""
import logging
from typing import List, Dict, Any, Optional
import pymysql
from pymysql.cursors import DictCursor
import os

logger = logging.getLogger(__name__)


class SchemaService:
    """Service for database schema extraction and management"""
    
    def __init__(self):
        """Initialize schema service"""
        pass
    
    def get_db_connection(self, connection_string: Optional[str] = None):
        """
        Create MySQL database connection
        
        Args:
            connection_string: Optional connection string
        
        Returns:
            MySQL connection object
        """
        if connection_string:
            # Parse connection string
            params = {}
            for param in connection_string.split(';'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key.strip().lower()] = value.strip()
            
            return pymysql.connect(
                host=params.get('host', params.get('server', 'localhost')),
                database=params.get('database', params.get('db', '')),
                user=params.get('user', 'root'),
                password=params.get('password', ''),
                port=int(params.get('port', 3306)),
                cursorclass=DictCursor
            )
        else:
            # Use environment variables
            return pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'test'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                port=int(os.getenv('DB_PORT', 3306)),
                cursorclass=DictCursor
            )
    
    async def get_all_tables(
        self,
        connection_string: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all tables from database
        
        Args:
            connection_string: Optional database connection string
        
        Returns:
            List of table information dictionaries
        """
        try:
            connection = self.get_db_connection(connection_string)
            
            with connection.cursor() as cursor:
                query = """
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
                
                cursor.execute(query)
                tables = cursor.fetchall()
                
                logger.info(f"Found {len(tables)} tables in database")
                return tables
                
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()
    
    async def get_table_columns(
        self,
        table_name: str,
        connection_string: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get columns for a specific table
        
        Args:
            table_name: Name of the table
            connection_string: Optional database connection string
        
        Returns:
            List of column information dictionaries
        """
        try:
            connection = self.get_db_connection(connection_string)
            
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_KEY as column_key,
                        COLUMN_COMMENT as description
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """
                
                cursor.execute(query, (table_name,))
                columns = cursor.fetchall()
                
                return columns
                
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()
    
    async def get_database_schema(
        self,
        connection_string: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete database schema with tables and columns
        
        Args:
            connection_string: Optional database connection string
        
        Returns:
            Dictionary with complete schema metadata
        """
        try:
            tables = await self.get_all_tables(connection_string)
            
            schema = {
                "tables": [],
                "table_count": len(tables)
            }
            
            for table in tables:
                table_name = table['table_name']
                columns = await self.get_table_columns(table_name, connection_string)
                
                schema["tables"].append({
                    "table_name": table_name,
                    "row_count": table.get('row_count', 0),
                    "description": table.get('description', ''),
                    "columns": columns
                })
            
            logger.info(f"Retrieved schema for {len(schema['tables'])} tables")
            return schema
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {"tables": [], "table_count": 0}
    
    def get_schema_dict(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert schema to dictionary format for SQL builder
        
        Args:
            schema: Schema dictionary from get_database_schema
        
        Returns:
            Schema dictionary keyed by table name
        """
        schema_dict = {}
        
        for table in schema.get("tables", []):
            table_name = table['table_name']
            schema_dict[table_name] = {
                'columns': []
            }
            
            for col in table.get('columns', []):
                schema_dict[table_name]['columns'].append({
                    'name': col['column_name'],
                    'type': col['data_type'],
                    'is_nullable': col['is_nullable'],
                    'is_primary': col.get('column_key') == 'PRI'
                })
        
        return schema_dict
    
    def get_schema_context(self, schema: Dict[str, Any]) -> str:
        """
        Convert schema to string format for LLM context
        
        Args:
            schema: Schema dictionary from get_database_schema
        
        Returns:
            Formatted schema string
        """
        context_lines = ["Database Schema:\n"]
        
        for table in schema.get("tables", []):
            table_name = table['table_name']
            context_lines.append(f"\nTable: {table_name}")
            
            if table.get('description'):
                context_lines.append(f"  Description: {table['description']}")
            
            context_lines.append("  Columns:")
            
            for col in table.get('columns', []):
                col_name = col['column_name']
                col_type = col['data_type']
                nullable = col['is_nullable']
                key = col.get('column_key', '')
                
                key_str = f" [{key}]" if key else ""
                null_str = " NULL" if nullable == 'YES' else " NOT NULL"
                
                context_lines.append(f"    - {col_name} ({col_type}){key_str}{null_str}")
        
        return "\n".join(context_lines)
    
    def extract_table_name_from_query(
        self,
        query: str,
        available_tables: List[str]
    ) -> Optional[str]:
        """
        Extract table name from natural language query
        
        Args:
            query: Natural language query
            available_tables: List of available table names
        
        Returns:
            Detected table name or None
        """
        query_lower = query.lower()
        
        # Exact match
        for table in available_tables:
            if table.lower() in query_lower:
                return table
        
        # Singular/plural variations
        for table in available_tables:
            singular = table.rstrip('s')
            plural = table + 's'
            
            if singular.lower() in query_lower or plural.lower() in query_lower:
                return table
        
        return None


# Singleton instance
_schema_service_instance = None

def get_schema_service() -> SchemaService:
    """Get singleton instance of SchemaService"""
    global _schema_service_instance
    if _schema_service_instance is None:
        _schema_service_instance = SchemaService()
    return _schema_service_instance

