"""
Column Metadata Service
Manages semantic descriptions for database columns to improve SQL generation accuracy
Supports both database storage (primary) and JSON file fallback
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


def get_db_manager():
    """Import DB manager (lazy import to avoid circular dependencies)"""
    from database.db_manager import DatabaseManager
    return DatabaseManager()


class ColumnMetadataService:
    """
    Service for managing column metadata and descriptions
    This helps the LLM understand what each column represents for better SQL generation
    """
    
    def __init__(self, metadata_file: Optional[str] = None, use_database: bool = True):
        """
        Initialize metadata service
        
        Args:
            metadata_file: Path to JSON file with custom column metadata (fallback)
            use_database: Whether to use database storage (default: True)
        """
        self.metadata_file = metadata_file or os.getenv('COLUMN_METADATA_FILE', 'config/column_metadata.json')
        self.use_database = use_database
        self.custom_metadata = self._load_custom_metadata()
        self._metadata_cache = {}  # Cache for database metadata
    
    def _load_custom_metadata(self) -> Dict[str, Any]:
        """
        Load custom column metadata from JSON configuration file
        
        Returns:
            Dictionary with custom metadata by table and column
        """
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    logger.info(f"✅ Loaded custom column metadata from {self.metadata_file}")
                    return metadata
            else:
                logger.info(f"📝 No custom metadata file found at {self.metadata_file}, using defaults")
                return {}
        except Exception as e:
            logger.warning(f"Could not load custom metadata: {e}")
            return {}
    
    def _load_metadata_from_database(
        self,
        tenant_id: str,
        database_name: str
    ) -> Dict[str, Any]:
        """
        Load all metadata for a database from the database
        
        Args:
            tenant_id: Tenant ID
            database_name: Name of the database
        
        Returns:
            Dictionary with metadata organized by table and column
        """
        cache_key = f"{tenant_id}:{database_name}"
        
        # Check cache first
        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]
        
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Load table metadata
                cursor.execute("""
                    SELECT table_name, description, business_purpose, primary_entity
                    FROM table_metadata
                    WHERE tenant_id = %s AND database_name = %s
                """, (tenant_id, database_name))
                
                table_rows = cursor.fetchall()
                
                # Load column metadata
                cursor.execute("""
                    SELECT table_name, column_name, description, semantic_type, examples
                    FROM column_metadata
                    WHERE tenant_id = %s AND database_name = %s
                """, (tenant_id, database_name))
                
                column_rows = cursor.fetchall()
                
                # Organize metadata
                metadata = {}
                
                # Add table metadata
                for row in table_rows:
                    table_name = row['table_name']
                    metadata[table_name] = {
                        'description': row['description'],
                        'business_purpose': row.get('business_purpose'),
                        'primary_entity': row.get('primary_entity'),
                        'columns': {}
                    }
                
                # Add column metadata
                for row in column_rows:
                    table_name = row['table_name']
                    column_name = row['column_name']
                    
                    if table_name not in metadata:
                        metadata[table_name] = {'columns': {}}
                    
                    if 'columns' not in metadata[table_name]:
                        metadata[table_name]['columns'] = {}
                    
                    metadata[table_name]['columns'][column_name] = {
                        'description': row['description'],
                        'semantic_type': row.get('semantic_type'),
                        'examples': row.get('examples')
                    }
                
                # Cache the result
                self._metadata_cache[cache_key] = metadata
                
                logger.info(f"✅ Loaded metadata from database for {tenant_id}:{database_name}")
                return metadata
                
        except Exception as e:
            logger.warning(f"Could not load metadata from database: {e}")
            return {}
    
    def save_column_metadata(
        self,
        tenant_id: str,
        database_name: str,
        table_name: str,
        column_name: str,
        description: str,
        semantic_type: Optional[str] = None,
        examples: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Save or update column metadata in database
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            table_name: Table name
            column_name: Column name
            description: Column description
            semantic_type: Semantic type (e.g., 'location', 'financial')
            examples: Example values (optional)
            user_id: User ID who created/updated this
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db_manager = get_db_manager()
            examples_json = json.dumps(examples) if examples else None
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO column_metadata 
                    (tenant_id, database_name, table_name, column_name, description, semantic_type, examples, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        description = VALUES(description),
                        semantic_type = VALUES(semantic_type),
                        examples = VALUES(examples),
                        updated_by = VALUES(updated_by),
                        updated_at = CURRENT_TIMESTAMP
                """, (tenant_id, database_name, table_name, column_name, description, 
                      semantic_type, examples_json, user_id, user_id))
                
                conn.commit()
                
                # Clear cache
                cache_key = f"{tenant_id}:{database_name}"
                if cache_key in self._metadata_cache:
                    del self._metadata_cache[cache_key]
                
                logger.info(f"✅ Saved metadata for {table_name}.{column_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save column metadata: {e}")
            return False
    
    def save_table_metadata(
        self,
        tenant_id: str,
        database_name: str,
        table_name: str,
        description: str,
        business_purpose: Optional[str] = None,
        primary_entity: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Save or update table metadata in database
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            table_name: Table name
            description: Table description
            business_purpose: Business purpose of the table
            primary_entity: Primary entity type (e.g., 'Customer', 'Order')
            user_id: User ID who created/updated this
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO table_metadata 
                    (tenant_id, database_name, table_name, description, business_purpose, primary_entity, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        description = VALUES(description),
                        business_purpose = VALUES(business_purpose),
                        primary_entity = VALUES(primary_entity),
                        updated_by = VALUES(updated_by),
                        updated_at = CURRENT_TIMESTAMP
                """, (tenant_id, database_name, table_name, description, 
                      business_purpose, primary_entity, user_id, user_id))
                
                conn.commit()
                
                # Clear cache
                cache_key = f"{tenant_id}:{database_name}"
                if cache_key in self._metadata_cache:
                    del self._metadata_cache[cache_key]
                
                logger.info(f"✅ Saved metadata for table {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save table metadata: {e}")
            return False
    
    def get_column_description(
        self,
        table_name: str,
        column_name: str,
        db_comment: Optional[str] = None,
        data_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> str:
        """
        Get description for a column from multiple sources
        
        Priority:
        1. Database metadata table (if tenant_id and database_name provided)
        2. Custom metadata from JSON file
        3. Database column comments
        4. Smart inference from column name and type
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            db_comment: Comment from database (if any)
            data_type: SQL data type
            tenant_id: Tenant ID (for database lookup)
            database_name: Database name (for database lookup)
        
        Returns:
            Description string for the column
        """
        # 1. Check database metadata (highest priority)
        if self.use_database and tenant_id and database_name:
            db_metadata = self._load_metadata_from_database(tenant_id, database_name)
            if table_name in db_metadata:
                table_meta = db_metadata[table_name]
                if 'columns' in table_meta and column_name in table_meta['columns']:
                    col_meta = table_meta['columns'][column_name]
                    if isinstance(col_meta, dict):
                        return col_meta.get('description', '')
                    else:
                        return str(col_meta)
        
        # 2. Check custom metadata from JSON file
        if table_name in self.custom_metadata:
            table_meta = self.custom_metadata[table_name]
            if 'columns' in table_meta and column_name in table_meta['columns']:
                return table_meta['columns'][column_name]
        
        # 3. Check database comment
        if db_comment and db_comment.strip():
            return db_comment.strip()
        
        # 4. Smart inference from column name and type
        return self._infer_column_description(column_name, data_type)
    
    def _infer_column_description(self, column_name: str, data_type: Optional[str] = None) -> str:
        """
        Infer column description from its name and type
        
        Args:
            column_name: Name of the column
            data_type: SQL data type
        
        Returns:
            Inferred description
        """
        col_lower = column_name.lower()
        
        # Common patterns for inference
        patterns = {
            # IDs and Keys
            'id': 'Unique identifier',
            '_id': 'Foreign key reference',
            'uuid': 'Universal unique identifier',
            
            # Names and Identifiers
            'name': 'Name',
            'title': 'Title or heading',
            'code': 'Code or identifier',
            'number': 'Reference number',
            'reference': 'Reference code',
            
            # Locations
            'country': 'Country name',
            'city': 'City name',
            'state': 'State or province',
            'address': 'Street address',
            'zip': 'Postal/ZIP code',
            'postal': 'Postal code',
            'location': 'Geographic location',
            'region': 'Geographic region',
            'latitude': 'Geographic latitude coordinate',
            'longitude': 'Geographic longitude coordinate',
            
            # Contact Information
            'email': 'Email address',
            'phone': 'Phone number',
            'mobile': 'Mobile phone number',
            'fax': 'Fax number',
            'website': 'Website URL',
            'url': 'Web address',
            
            # Dates and Times
            'created_at': 'Creation timestamp',
            'updated_at': 'Last update timestamp',
            'deleted_at': 'Deletion timestamp',
            'date': 'Date',
            'time': 'Time',
            'timestamp': 'Timestamp',
            'year': 'Year',
            'month': 'Month',
            'day': 'Day',
            
            # Status and State
            'status': 'Current status',
            'state': 'Current state',
            'active': 'Active/inactive flag',
            'enabled': 'Enabled/disabled flag',
            'is_active': 'Whether item is active',
            'is_deleted': 'Soft delete flag',
            'is_verified': 'Verification status',
            
            # Financial
            'amount': 'Monetary amount',
            'price': 'Price value',
            'cost': 'Cost value',
            'total': 'Total amount',
            'tax': 'Tax amount',
            'discount': 'Discount amount',
            'balance': 'Balance amount',
            'salary': 'Salary amount',
            'revenue': 'Revenue amount',
            'currency': 'Currency code',
            
            # Quantities
            'quantity': 'Quantity or count',
            'count': 'Count value',
            'stock': 'Stock quantity',
            'inventory': 'Inventory level',
            'capacity': 'Capacity amount',
            
            # Descriptions and Content
            'description': 'Detailed description',
            'details': 'Additional details',
            'notes': 'Notes or comments',
            'comment': 'Comment text',
            'remarks': 'Remarks or observations',
            
            # Categories and Types
            'type': 'Type or category',
            'category': 'Category classification',
            'class': 'Classification',
            'group': 'Group identifier',
            'department': 'Department name',
            
            # User/Person Related
            'username': 'Username for login',
            'password': 'Encrypted password',
            'first_name': 'First name',
            'last_name': 'Last name',
            'full_name': 'Full name',
            'age': 'Age in years',
            'gender': 'Gender',
            'birth': 'Birth date',
        }
        
        # Check for exact matches or contains patterns
        for pattern, description in patterns.items():
            if pattern in col_lower:
                # Make it more specific if possible
                if pattern.endswith('_id') and col_lower.startswith(pattern.replace('_id', '')):
                    entity = col_lower.replace('_id', '').replace('_', ' ').title()
                    return f"Reference to {entity}"
                elif col_lower == pattern:
                    return description
                elif col_lower.endswith(pattern):
                    prefix = col_lower.replace(pattern, '').replace('_', ' ').strip().title()
                    return f"{prefix} {description.lower()}" if prefix else description
        
        # If no pattern matches, create a generic description from the name
        readable_name = column_name.replace('_', ' ').title()
        return f"{readable_name}"
    
    def get_table_description(
        self, 
        table_name: str, 
        db_comment: Optional[str] = None,
        tenant_id: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> str:
        """
        Get description for a table
        
        Args:
            table_name: Name of the table
            db_comment: Comment from database (if any)
            tenant_id: Tenant ID (for database lookup)
            database_name: Database name (for database lookup)
        
        Returns:
            Description string for the table
        """
        # 1. Check database metadata
        if self.use_database and tenant_id and database_name:
            db_metadata = self._load_metadata_from_database(tenant_id, database_name)
            if table_name in db_metadata and 'description' in db_metadata[table_name]:
                return db_metadata[table_name]['description']
        
        # 2. Check custom metadata from JSON
        if table_name in self.custom_metadata:
            table_meta = self.custom_metadata[table_name]
            if 'description' in table_meta:
                return table_meta['description']
        
        # 3. Check database comment
        if db_comment and db_comment.strip():
            return db_comment.strip()
        
        # 4. Infer from table name
        return self._infer_table_description(table_name)
    
    def _infer_table_description(self, table_name: str) -> str:
        """
        Infer table description from its name
        
        Args:
            table_name: Name of the table
        
        Returns:
            Inferred description
        """
        # Common table patterns
        table_lower = table_name.lower()
        
        patterns = {
            'users': 'System users and authentication',
            'customers': 'Customer information and contacts',
            'vendors': 'Vendor/supplier information',
            'products': 'Product catalog and inventory',
            'orders': 'Order transactions and details',
            'invoices': 'Invoice records',
            'payments': 'Payment transactions',
            'employees': 'Employee records',
            'departments': 'Department information',
            'categories': 'Category classifications',
            'logs': 'System or activity logs',
            'settings': 'Configuration settings',
            'sessions': 'User session data',
            'transactions': 'Transaction records',
        }
        
        for pattern, description in patterns.items():
            if pattern in table_lower:
                return description
        
        # Generic description
        readable_name = table_name.replace('_', ' ').title()
        return f"Stores {readable_name.lower()} data"
    
    def enrich_schema(
        self, 
        schema: Dict[str, Any],
        tenant_id: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich schema with descriptions from all sources
        
        Args:
            schema: Schema dictionary from SchemaService
            tenant_id: Tenant ID (for database metadata lookup)
            database_name: Database name (for metadata lookup)
        
        Returns:
            Enriched schema with descriptions
        """
        enriched_schema = schema.copy()
        
        for table in enriched_schema.get('tables', []):
            table_name = table['table_name']
            
            # Enrich table description
            table['description'] = self.get_table_description(
                table_name,
                table.get('description'),
                tenant_id,
                database_name
            )
            
            # Enrich column descriptions
            for column in table.get('columns', []):
                column_name = column['column_name']
                column['description'] = self.get_column_description(
                    table_name,
                    column_name,
                    column.get('description'),
                    column.get('data_type'),
                    tenant_id,
                    database_name
                )
        
        return enriched_schema
    
    def auto_discover_and_save_metadata(
        self,
        tenant_id: str,
        database_name: str,
        schema: Dict[str, Any],
        user_id: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, int]:
        """
        Auto-discover and save metadata for all tables and columns in a schema
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            schema: Schema dictionary from SchemaService
            user_id: User ID
            overwrite: Whether to overwrite existing metadata
        
        Returns:
            Dictionary with counts of tables and columns processed
        """
        tables_saved = 0
        columns_saved = 0
        
        try:
            for table in schema.get('tables', []):
                table_name = table['table_name']
                
                # Generate table description
                table_desc = self._infer_table_description(table_name)
                
                # Save table metadata
                if self.save_table_metadata(
                    tenant_id,
                    database_name,
                    table_name,
                    table_desc,
                    user_id=user_id
                ):
                    tables_saved += 1
                
                # Save column metadata
                for column in table.get('columns', []):
                    column_name = column['column_name']
                    data_type = column.get('data_type')
                    
                    # Generate column description
                    col_desc = self._infer_column_description(column_name, data_type)
                    
                    # Determine semantic type
                    semantic_type = self._detect_semantic_type(column_name, data_type)
                    
                    # Save column metadata
                    if self.save_column_metadata(
                        tenant_id,
                        database_name,
                        table_name,
                        column_name,
                        col_desc,
                        semantic_type=semantic_type,
                        user_id=user_id
                    ):
                        columns_saved += 1
            
            logger.info(f"✅ Auto-discovered metadata: {tables_saved} tables, {columns_saved} columns")
            return {'tables': tables_saved, 'columns': columns_saved}
            
        except Exception as e:
            logger.error(f"Failed to auto-discover metadata: {e}")
            return {'tables': tables_saved, 'columns': columns_saved}
    
    def _detect_semantic_type(self, column_name: str, data_type: Optional[str] = None) -> Optional[str]:
        """
        Detect semantic type from column name and data type
        
        Args:
            column_name: Column name
            data_type: SQL data type
        
        Returns:
            Semantic type or None
        """
        col_lower = column_name.lower()
        
        # Map patterns to semantic types
        type_patterns = {
            'identifier': ['id', 'uuid', 'key', 'code'],
            'location': ['country', 'city', 'state', 'address', 'zip', 'postal', 'location', 'region'],
            'contact': ['email', 'phone', 'mobile', 'fax', 'website', 'url'],
            'temporal': ['date', 'time', 'timestamp', 'created_at', 'updated_at', 'deleted_at'],
            'financial': ['amount', 'price', 'cost', 'total', 'tax', 'salary', 'revenue', 'balance'],
            'quantity': ['quantity', 'count', 'stock', 'inventory', 'capacity'],
            'status': ['status', 'state', 'active', 'enabled', 'is_active', 'is_deleted'],
            'personal': ['name', 'first_name', 'last_name', 'age', 'gender', 'ssn', 'birth'],
            'description': ['description', 'details', 'notes', 'comment', 'remarks'],
            'category': ['type', 'category', 'class', 'group', 'department']
        }
        
        for semantic_type, patterns in type_patterns.items():
            for pattern in patterns:
                if pattern in col_lower:
                    return semantic_type
        
        return None
    
    def generate_sample_metadata_file(self, schema: Dict[str, Any], output_file: Optional[str] = None):
        """
        Generate a sample metadata JSON file from schema
        This helps users customize descriptions for their database
        
        Args:
            schema: Database schema
            output_file: Path to output file
        """
        output_file = output_file or self.metadata_file
        
        metadata = {
            "_readme": "This file allows you to customize column and table descriptions for better SQL generation",
            "_format": {
                "table_name": {
                    "description": "Table description",
                    "columns": {
                        "column_name": "Column description"
                    }
                }
            }
        }
        
        # Generate template for each table
        for table in schema.get('tables', []):
            table_name = table['table_name']
            
            metadata[table_name] = {
                "description": self.get_table_description(table_name, table.get('description')),
                "columns": {}
            }
            
            for column in table.get('columns', []):
                column_name = column['column_name']
                metadata[table_name]['columns'][column_name] = self.get_column_description(
                    table_name,
                    column_name,
                    column.get('description'),
                    column.get('data_type')
                )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Generated sample metadata file at {output_file}")
        return output_file


# Singleton instance
_metadata_service_instance = None

def get_column_metadata_service() -> ColumnMetadataService:
    """Get singleton instance of ColumnMetadataService"""
    global _metadata_service_instance
    if _metadata_service_instance is None:
        _metadata_service_instance = ColumnMetadataService()
    return _metadata_service_instance

