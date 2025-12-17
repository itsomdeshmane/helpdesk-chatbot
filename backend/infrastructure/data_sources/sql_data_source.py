"""
SQL Data Source Implementation
Handles database queries using natural language to SQL conversion
Wraps existing database_query_service functionality
"""

import logging
import time
from typing import List, Optional
from core.interfaces.data_source import IDataSource
from core.interfaces.llm_provider import ILLMProvider
from core.interfaces.database import IDatabaseConnection
from core.models.query import Query
from core.models.response import DataSourceResponse

logger = logging.getLogger(__name__)


class SQLDataSource(IDataSource):
    """
    SQL Database data source
    
    Converts natural language queries to SQL and executes them
    
    Following SOLID:
    - SRP: Single responsibility - SQL query execution
    - OCP: Implements IDataSource interface
    - DIP: Depends on IDatabaseConnection and ILLMProvider abstractions
    
    This wraps the existing database_query_service functionality
    """
    
    # Keywords that indicate database/data queries
    DATABASE_KEYWORDS = [
        'show', 'list', 'get', 'find', 'fetch', 'display',
        'how many', 'count', 'total', 'sum', 'average',
        'max', 'maximum', 'min', 'minimum',
        'between', 'from', 'to', 'where',
        'sales', 'customers', 'orders', 'items', 'products',
        'data', 'records', 'rows', 'entries', 'results',
        'report', 'analytics', 'dashboard', 'metrics'
    ]
    
    def __init__(
        self,
        llm_provider: ILLMProvider,
        connection_factory
    ):
        """
        Initialize SQL data source
        
        Args:
            llm_provider: LLM for SQL generation
            connection_factory: Factory for database connections
        """
        self._llm = llm_provider
        self._connection_factory = connection_factory
        self._source_type = "database"
        
        logger.info("SQL Data Source initialized")
    
    async def can_handle(self, query: Query) -> bool:
        """
        Determine if this data source can handle the query
        
        Args:
            query: The user query
            
        Returns:
            True if query seems to be asking for database data
        """
        query_lower = query.text.lower()
        
        # Check for database-related keywords
        return any(keyword in query_lower for keyword in self.DATABASE_KEYWORDS)
    
    async def search(
        self,
        query: Query,
        tenant_id: str,
        limit: int = 100
    ) -> DataSourceResponse:
        """
        Execute SQL query against database
        
        Args:
            query: The user query
            tenant_id: Tenant identifier
            limit: Maximum number of rows to return
            
        Returns:
            DataSourceResponse with query results
        """
        start_time = time.time()
        
        try:
            logger.info(f"SQL search: '{query.text[:50]}...' (tenant: {tenant_id})")
            
            # Step 1: Get database connection
            # Check if user has custom connection, otherwise use system
            connection_string = query.metadata.get('connection_string')
            db = self._connection_factory.get_database(connection_string)
            
            # Step 2: Get database schema
            schema = await db.get_schema()
            
            # Step 3: Generate SQL using LLM
            sql_query = await self._generate_sql(
                query.text,
                schema,
                query.context.get_recent_history() if query.context else []
            )
            
            if not sql_query or sql_query.upper().startswith('SELECT'):
                logger.warning(f"Invalid SQL generated: {sql_query}")
                return DataSourceResponse(
                    success=False,
                    source_type=self._source_type,
                    error="Could not generate valid SQL query",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Step 4: Execute SQL query
            results = await db.execute_query(sql_query)
            
            # Step 5: Extract column names
            columns = []
            if results and len(results) > 0:
                columns = list(results[0].keys())
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"SQL executed successfully: {len(results)} rows returned")
            
            return DataSourceResponse(
                success=True,
                source_type=self._source_type,
                data=results,
                sql_query=sql_query,
                metadata={
                    'row_count': len(results),
                    'columns': columns,
                    'database_type': db.get_database_type(),
                    'connection_type': db.get_connection_type()
                },
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"SQL search failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return DataSourceResponse(
                success=False,
                source_type=self._source_type,
                error=f"Database query error: {str(e)}",
                execution_time_ms=execution_time
            )
    
    async def _generate_sql(
        self,
        natural_language_query: str,
        schema: dict,
        conversation_history: List[dict]
    ) -> str:
        """
        Generate SQL from natural language using LLM
        
        Args:
            natural_language_query: User's question
            schema: Database schema
            conversation_history: Previous conversation
            
        Returns:
            Generated SQL query
        """
        try:
            # Build schema context string
            schema_context = self._build_schema_context(schema)
            
            # Build prompt for LLM
            messages = [
                {
                    "role": "system",
                    "content": """You are a SQL expert. Convert natural language queries to MySQL SQL.
                    
CRITICAL: Return ONLY the SQL query. NO explanations, NO comments, NO markdown.
If you cannot understand the query, return: SELECT 'query_unclear' as message

Rules:
1. Return ONLY the SQL query
2. Use proper MySQL syntax
3. Use appropriate WHERE clauses for filters
4. Use JOINs when querying multiple tables
5. Use LIMIT 100 by default
6. Handle date ranges properly
7. For names/text fields, use LIKE with wildcards
8. Use GROUP BY and HAVING for aggregations
9. Use COUNT(*), SUM(), AVG(), MAX(), MIN() for statistics
"""
                },
                {
                    "role": "user",
                    "content": f"""Database Schema:
{schema_context}

Question: {natural_language_query}

Generate the SQL query:"""
                }
            ]
            
            # Generate SQL using LLM
            sql_query = await self._llm.generate_completion(
                messages=messages,
                temperature=0.0,  # Use deterministic generation
                max_tokens=500
            )
            
            # Clean up the response
            sql_query = sql_query.strip()
            
            # Remove markdown code blocks if present
            if sql_query.startswith('```'):
                lines = sql_query.split('\n')
                sql_query = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql_query
            
            sql_query = sql_query.strip()
            
            logger.debug(f"Generated SQL: {sql_query}")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise
    
    def _build_schema_context(self, schema: dict) -> str:
        """
        Build schema context string from schema dict
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Formatted schema string
        """
        context_parts = []
        
        tables = schema.get('tables', [])
        for table in tables[:20]:  # Limit to 20 tables to avoid token limit
            table_name = table['name']
            columns = table.get('columns', [])
            
            col_strs = []
            for col in columns:
                col_str = f"  - {col['name']} ({col['type']})"
                if not col.get('nullable', True):
                    col_str += " NOT NULL"
                col_strs.append(col_str)
            
            context_parts.append(
                f"Table: {table_name}\n" + "\n".join(col_strs)
            )
        
        return "\n\n".join(context_parts)
    
    def get_source_type(self) -> str:
        """Return source type"""
        return self._source_type
    
    async def health_check(self) -> bool:
        """
        Check if database is operational
        
        Returns:
            True if database is healthy
        """
        try:
            # Check system database
            db = self._connection_factory.get_system_database()
            return await db.health_check()
        except:
            return False

