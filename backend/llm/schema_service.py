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


def get_column_metadata_service():
    """Import and get metadata service (lazy import to avoid circular dependencies)"""
    from llm.column_metadata_service import get_column_metadata_service as get_meta_svc
    return get_meta_svc()


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
    
    def get_schema_context(
        self, 
        schema: Dict[str, Any],
        tenant_id: Optional[str] = None,
        database_name: Optional[str] = None,
        include_descriptions: bool = True
    ) -> str:
        """
        Convert schema to string format for LLM context with enriched metadata
        
        Args:
            schema: Schema dictionary from get_database_schema
            tenant_id: Tenant ID for metadata lookup
            database_name: Database name for metadata lookup
            include_descriptions: Whether to include column descriptions
        
        Returns:
            Formatted schema string with descriptions
        """
        # Enrich schema with metadata if requested
        if include_descriptions and tenant_id and database_name:
            try:
                metadata_service = get_column_metadata_service()
                schema = metadata_service.enrich_schema(schema, tenant_id, database_name)
            except Exception as e:
                logger.warning(f"Could not enrich schema with metadata: {e}")
        
        context_lines = ["=== DATABASE SCHEMA ===\n"]
        
        for table in schema.get("tables", []):
            table_name = table['table_name']
            context_lines.append(f"\n📊 TABLE: {table_name}")
            
            if table.get('description'):
                context_lines.append(f"   Description: {table['description']}")
            
            if table.get('row_count'):
                context_lines.append(f"   Estimated Rows: {table['row_count']:,}")
            
            context_lines.append("   Columns:")
            
            for col in table.get('columns', []):
                col_name = col['column_name']
                col_type = col['data_type']
                nullable = col['is_nullable']
                key = col.get('column_key', '')
                col_desc = col.get('description', '')
                
                # Build column line with better formatting
                key_str = ""
                if key == 'PRI':
                    key_str = " 🔑 PRIMARY KEY"
                elif key == 'MUL':
                    key_str = " 🔗 INDEXED"
                elif key == 'UNI':
                    key_str = " ⭐ UNIQUE"
                
                null_str = "" if nullable == 'YES' else " NOT NULL"
                
                col_line = f"     • {col_name} ({col_type}){key_str}{null_str}"
                
                # Add description if available
                if col_desc:
                    col_line += f"\n       ℹ️  {col_desc}"
                
                context_lines.append(col_line)
            
            context_lines.append("")  # Blank line between tables
        
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



