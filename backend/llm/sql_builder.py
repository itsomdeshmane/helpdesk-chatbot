"""
SQL Builder - Generic SQL query construction
Builds SQL queries from classified intents and database schema
"""
import logging
from typing import Dict, List, Any, Optional
from llm.query_classifier import QueryIntent
from llm.intelligent_entity_matcher import get_intelligent_matcher

logger = logging.getLogger(__name__)


class SQLBuilder:
    """Builds SQL queries from classified intents and schema"""
    
    def __init__(self):
        """Initialize the SQL builder"""
        pass
    
    def build_query(
        self,
        intent: QueryIntent,
        schema: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build SQL query from classified intent and schema
        
        Args:
            intent: Classified query intent
            schema: Database schema information
            conversation_history: Optional conversation context
            
        Returns:
            Generated SQL query string
        """
        logger.info(f"Building SQL for intent: {intent.intent_type}, operation: {intent.operation}")
        
        # Get entities
        entities = intent.entities
        tables = entities.get('tables', [])
        
        if not tables:
            logger.warning("No tables identified in intent - attempting fallback")
            # Try to infer table from schema keys
            if schema and len(schema) > 0:
                # Use the first available table as fallback
                first_table = list(schema.keys())[0]
                logger.info(f"Using fallback table: {first_table}")
                tables = [first_table]
                entities['tables'] = tables
            else:
                logger.error("No tables in intent and no schema available")
                return ""
        
        # Get the primary table
        table_name = self._resolve_table_name(tables[0], schema)
        if not table_name:
            logger.warning(f"Could not resolve table: {tables[0]}")
            return ""
        
        # Get table schema
        table_schema = self._get_table_schema(table_name, schema)
        if not table_schema:
            logger.warning(f"No schema found for table: {table_name}")
            return ""
        
        # 🎯 INTELLIGENT ENTITY EXTRACTION
        # Use intelligent matcher to automatically detect entities and create conditions
        query_text = entities.get('query', '')
        if query_text and not entities.get('conditions'):
            logger.info("🔍 Using intelligent entity matcher to detect filters...")
            matcher = get_intelligent_matcher()
            auto_conditions = matcher.create_filter_conditions(query_text, table_schema)
            
            if auto_conditions:
                logger.info(f"✅ Automatically detected {len(auto_conditions)} filter conditions")
                # Merge with existing conditions
                existing_conditions = entities.get('conditions', [])
                entities['conditions'] = existing_conditions + auto_conditions
            else:
                logger.info("ℹ️ No additional filters detected by intelligent matcher")
        
        # Build query based on intent type
        if intent.intent_type == 'aggregate_group':
            return self._build_aggregate_group_query(intent, table_name, table_schema)
        
        elif intent.intent_type == 'count':
            return self._build_count_query(intent, table_name, table_schema)
        
        elif intent.intent_type == 'aggregate':
            return self._build_aggregate_query(intent, table_name, table_schema)
        
        elif intent.intent_type == 'list':
            return self._build_list_query(intent, table_name, table_schema)
        
        elif intent.intent_type == 'filter':
            return self._build_filter_query(intent, table_name, table_schema)
        
        else:
            logger.warning(f"Unknown intent type: {intent.intent_type}")
            return ""
    
    def _build_aggregate_group_query(
        self,
        intent: QueryIntent,
        table_name: str,
        table_schema: Dict[str, Any]
    ) -> str:
        """Build GROUP BY query with aggregation and HAVING clause"""
        entities = intent.entities
        
        # Get group by column
        group_by_cols = entities.get('group_by', [])
        if not group_by_cols:
            logger.warning("No group by columns specified")
            return ""
        
        group_col = self._resolve_column_name(group_by_cols[0], table_schema)
        if not group_col:
            logger.warning(f"Could not resolve column: {group_by_cols[0]}")
            return ""
        
        # Build SELECT clause
        aggregate_type = entities.get('aggregate', 'count')
        if aggregate_type == 'count':
            select_clause = f"SELECT {group_col}, COUNT(*) as count"
        else:
            # For sum, avg, etc., we'd need to identify the value column
            select_clause = f"SELECT {group_col}, COUNT(*) as count"
        
        # Build FROM clause
        from_clause = f"FROM {table_name}"
        
        # Build WHERE clause (if any conditions)
        where_clause = self._build_where_clause(entities.get('conditions', []), table_schema)
        
        # Build GROUP BY clause
        group_by_clause = f"GROUP BY {group_col}"
        
        # Build HAVING clause
        having_conditions = entities.get('having', [])
        having_clause = ""
        if having_conditions:
            having_parts = []
            for condition in having_conditions:
                cond_type = condition.get('type', 'count')
                operator = condition.get('operator', '>')
                value = condition.get('value', 0)
                
                if cond_type == 'count':
                    having_parts.append(f"COUNT(*) {operator} {value}")
                else:
                    having_parts.append(f"{cond_type.upper()}(*) {operator} {value}")
            
            if having_parts:
                having_clause = f"HAVING {' AND '.join(having_parts)}"
        
        # Build ORDER BY clause (order by count descending by default)
        order_by_clause = "ORDER BY count DESC"
        
        # Build LIMIT clause
        limit = entities.get('limit', 100)
        limit_clause = f"LIMIT {limit}"
        
        # Combine all parts
        query_parts = [
            select_clause,
            from_clause,
            where_clause,
            group_by_clause,
            having_clause,
            order_by_clause,
            limit_clause
        ]
        
        sql = ' '.join([part for part in query_parts if part])
        logger.info(f"Built aggregate group query: {sql}")
        return sql
    
    def _build_count_query(
        self,
        intent: QueryIntent,
        table_name: str,
        table_schema: Dict[str, Any]
    ) -> str:
        """Build simple COUNT query"""
        entities = intent.entities
        
        # Build WHERE clause
        where_clause = self._build_where_clause(entities.get('conditions', []), table_schema)
        
        # Build query
        sql = f"SELECT COUNT(*) as total FROM {table_name}"
        if where_clause:
            sql += f" {where_clause}"
        
        logger.info(f"Built count query: {sql}")
        return sql
    
    def _build_aggregate_query(
        self,
        intent: QueryIntent,
        table_name: str,
        table_schema: Dict[str, Any]
    ) -> str:
        """Build aggregate query (SUM, AVG, MAX, MIN) - GENERIC"""
        entities = intent.entities
        aggregate = entities.get('aggregate', 'count').upper()
        
        # Try to find the best numeric column for aggregation (GENERIC)
        # Check if user specified column hints
        column_hints = entities.get('columns', [])
        numeric_col = None
        
        if column_hints:
            # Try to find column matching hints
            for hint in column_hints:
                col = self._resolve_column_name(hint, table_schema)
                if col:
                    numeric_col = col
                    logger.info(f"Found numeric column from hint '{hint}': {col}")
                    break
        
        # Fallback: auto-detect numeric column
        if not numeric_col:
            numeric_col = self._find_numeric_column(table_schema)
        
        if aggregate == 'COUNT':
            select_clause = f"SELECT COUNT(*) as total"
        elif numeric_col:
            select_clause = f"SELECT {aggregate}({numeric_col}) as result"
        else:
            # No numeric column found - fallback to COUNT
            logger.warning(f"No numeric column found for {aggregate}, using COUNT instead")
            select_clause = f"SELECT COUNT(*) as total"
        
        where_clause = self._build_where_clause(entities.get('conditions', []), table_schema)
        
        sql = f"{select_clause} FROM {table_name}"
        if where_clause:
            sql += f" {where_clause}"
        
        logger.info(f"Built aggregate query: {sql}")
        return sql
    
    def _build_list_query(
        self,
        intent: QueryIntent,
        table_name: str,
        table_schema: Dict[str, Any]
    ) -> str:
        """Build simple SELECT query"""
        entities = intent.entities
        
        # Select specific columns or all
        columns = entities.get('columns', [])
        if columns:
            resolved_cols = [self._resolve_column_name(col, table_schema) for col in columns]
            resolved_cols = [col for col in resolved_cols if col]
            select_clause = f"SELECT {', '.join(resolved_cols) if resolved_cols else '*'}"
        else:
            select_clause = "SELECT *"
        
        where_clause = self._build_where_clause(entities.get('conditions', []), table_schema)
        
        limit = entities.get('limit', 100)
        
        sql = f"{select_clause} FROM {table_name}"
        if where_clause:
            sql += f" {where_clause}"
        sql += f" LIMIT {limit}"
        
        logger.info(f"Built list query: {sql}")
        return sql
    
    def _build_filter_query(
        self,
        intent: QueryIntent,
        table_name: str,
        table_schema: Dict[str, Any]
    ) -> str:
        """Build filtered SELECT query"""
        entities = intent.entities
        
        # Get columns to select
        columns = entities.get('columns', [])
        resolved_cols = []
        
        if columns:
            logger.info(f"Resolving columns: {columns}")
            for col_hint in columns:
                col = self._resolve_column_name(col_hint, table_schema)
                if col:
                    resolved_cols.append(col)
                    logger.info(f"  ✓ Resolved '{col_hint}' → {col}")
                else:
                    logger.warning(f"  ✗ Could not resolve column: {col_hint}")
        
        # Build SELECT clause
        if resolved_cols:
            select_clause = f"SELECT {', '.join(resolved_cols)}"
        else:
            select_clause = "SELECT *"
        
        # Build WHERE clause
        where_clause = self._build_where_clause(entities.get('conditions', []), table_schema)
        
        # Build query
        sql = f"{select_clause} FROM {table_name}"
        if where_clause:
            sql += f" {where_clause}"
        
        # Add LIMIT
        limit = entities.get('limit', 10)  # Default to 10 for filtered queries
        sql += f" LIMIT {limit}"
        
        logger.info(f"Built filter query: {sql}")
        return sql
    
    def _build_where_clause(
        self,
        conditions: List[Dict[str, Any]],
        table_schema: Dict[str, Any]
    ) -> str:
        """Build WHERE clause from conditions - INTELLIGENT matching for ALL entity types"""
        if not conditions:
            return ""
        
        where_parts = []
        
        for condition in conditions:
            cond_type = condition.get('type')
            
            # Handle text filters (location, status, priority, type, category, etc.)
            if cond_type == 'text_filter':
                column = condition.get('column')
                value = condition.get('value', '').strip()
                operator = condition.get('operator', 'LIKE')
                
                if column and value:
                    if operator == 'LIKE':
                        # Capitalize first letter for better matching
                        value_formatted = value.title()
                        where_parts.append(
                            f"({column} = '{value_formatted}' OR {column} LIKE '%{value}%')"
                        )
                    else:
                        where_parts.append(f"{column} = '{value}'")
                    
                    logger.info(f"✓ Added text filter: {column} {operator} '{value}'")
            
            # Handle numeric filters (amount, value, etc.)
            elif cond_type == 'numeric_filter':
                column = condition.get('column')
                value = condition.get('value')
                operator = condition.get('operator', '=')
                
                if column and value is not None:
                    where_parts.append(f"{column} {operator} {value}")
                    logger.info(f"✓ Added numeric filter: {column} {operator} {value}")
            
            # Handle date filters
            elif cond_type == 'date_filter':
                column = condition.get('column')
                value = condition.get('value')
                operator = condition.get('operator', '=')
                
                if column and value:
                    where_parts.append(f"{column} {operator} '{value}'")
                    logger.info(f"✓ Added date filter: {column} {operator} '{value}'")
            
            # Legacy support: location_filter (backward compatibility)
            elif cond_type == 'location_filter':
                # Handle location filter - "in India", "from USA", "around Mumbai"
                value = condition.get('value', '').strip()
                
                if value:
                    # Use intelligent location column finder (ZERO HARDCODED)
                    location_col = self._find_location_column(table_schema)
                    
                    if location_col:
                        # Capitalize first letter of location for better matching
                        value_capitalized = value.title()
                        # Use both exact match and LIKE for flexibility
                        where_parts.append(
                            f"({location_col} = '{value_capitalized}' OR {location_col} LIKE '%{value}%')"
                        )
                        logger.info(f"✓ Added location filter: {location_col} matching '{value_capitalized}'")
                    else:
                        logger.warning(f"✗ Could not find location column for filter: {value}")
            
            elif cond_type == 'date_range':
                # Handle date range
                date_col = self._find_date_column(table_schema)
                if date_col:
                    match = condition.get('match')
                    if match and len(match) >= 4:
                        # Convert month names to numbers
                        start_month = self._month_to_number(match[0])
                        start_year = match[1]
                        end_month = self._month_to_number(match[2])
                        end_year = match[3]
                        
                        where_parts.append(
                            f"{date_col} BETWEEN '{start_year}-{start_month:02d}-01' "
                            f"AND '{end_year}-{end_month:02d}-31'"
                        )
            
            elif cond_type == 'entity_filter':
                # Handle entity name filters - ZERO HARDCODED, finds name columns dynamically
                value = condition.get('value', '')
                
                if value:
                    # Find ANY name column in the table (no hardcoded hints)
                    name_col = self._find_name_column(table_schema)
                    
                    if name_col:
                        # Use LIKE for flexible matching
                        where_parts.append(f"{name_col} LIKE '%{value}%'")
                        logger.info(f"Added entity filter: {name_col} LIKE '%{value}%'")
                    else:
                        logger.warning(f"Could not find name column for filter: {value}")
            
            elif cond_type == 'text_filter':
                # Handle generic text filter
                value = condition.get('value', '')
                text_col = self._find_text_column(table_schema, ['name', 'title', 'description'])
                if text_col:
                    where_parts.append(f"{text_col} LIKE '%{value}%'")
        
        if where_parts:
            return f"WHERE {' AND '.join(where_parts)}"
        return ""
    
    def _resolve_table_name(self, table_hint: str, schema: Dict[str, Any]) -> Optional[str]:
        """Resolve table name from hint using schema"""
        table_hint_lower = table_hint.lower().strip()
        
        # Direct match
        if table_hint in schema:
            return table_hint
        
        # Case-insensitive match
        for table_name in schema.keys():
            if table_name.lower() == table_hint_lower:
                return table_name
        
        # Fuzzy match (singular/plural, substring)
        for table_name in schema.keys():
            table_name_lower = table_name.lower()
            if (table_hint_lower + 's' == table_name_lower or
                table_hint_lower == table_name_lower + 's' or
                table_hint_lower in table_name_lower or
                table_name_lower in table_hint_lower):
                return table_name
        
        return None
    
    def _get_table_schema(self, table_name: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get schema for a specific table"""
        return schema.get(table_name)
    
    def _resolve_column_name(self, column_hint: str, table_schema: Dict[str, Any]) -> Optional[str]:
        """Resolve column name from hint using table schema"""
        if not table_schema or 'columns' not in table_schema:
            return column_hint
        
        columns = table_schema['columns']
        column_hint_lower = column_hint.lower().strip()
        
        # Direct match
        for col in columns:
            if col['name'].lower() == column_hint_lower:
                return col['name']
        
        # Fuzzy match
        for col in columns:
            col_name_lower = col['name'].lower()
            if (column_hint_lower in col_name_lower or
                col_name_lower in column_hint_lower):
                return col['name']
        
        return column_hint
    
    def _find_numeric_column(self, table_schema: Dict[str, Any]) -> Optional[str]:
        """Find a numeric column in the table schema (GENERIC)"""
        if not table_schema or 'columns' not in table_schema:
            return None
        
        numeric_types = ['int', 'float', 'double', 'decimal', 'numeric', 'real', 'money']
        
        # Prefer columns with monetary/value names (GENERIC - works for any domain)
        monetary_names = ['total_value', 'total_amount', 'amount', 'value', 'price', 'total', 'cost', 'revenue', 'sales']
        
        # Priority 1: Exact match for monetary columns
        for pref in monetary_names:
            for col in table_schema['columns']:
                col_name = col.get('name', '').lower()
                col_type = col.get('type', '').lower()
                
                if col_name == pref and any(num_type in col_type for num_type in numeric_types):
                    logger.info(f"Found preferred numeric column (exact): {col['name']}")
                    return col['name']
        
        # Priority 2: Partial match for monetary columns
        for col in table_schema['columns']:
            col_type = col.get('type', '').lower()
            col_name = col.get('name', '').lower()
            
            if any(pref in col_name for pref in monetary_names):
                if any(num_type in col_type for num_type in numeric_types):
                    logger.info(f"Found preferred numeric column (partial): {col['name']}")
                    return col['name']
        
        # Priority 3: Any numeric column (excluding IDs)
        for col in table_schema['columns']:
            col_type = col.get('type', '').lower()
            col_name = col.get('name', '').lower()
            
            # Skip ID columns
            if 'id' in col_name and len(col_name) <= 10:
                continue
                
            if any(num_type in col_type for num_type in numeric_types):
                logger.info(f"Found fallback numeric column: {col['name']}")
                return col['name']
        
        logger.warning("No suitable numeric column found for aggregation")
        return None
    
    def _find_date_column(self, table_schema: Dict[str, Any]) -> Optional[str]:
        """Find a date/datetime column in the table schema"""
        if not table_schema or 'columns' not in table_schema:
            return None
        
        date_types = ['date', 'datetime', 'timestamp']
        
        for col in table_schema['columns']:
            col_type = col.get('type', '').lower()
            if any(date_type in col_type for date_type in date_types):
                return col['name']
        
        return None
    
    def _find_name_column(self, table_schema: Dict[str, Any]) -> Optional[str]:
        """
        Find a name column in the table - ZERO HARDCODED
        Looks for columns with 'name' or 'title' patterns
        """
        if not table_schema or 'columns' not in table_schema:
            return None
        
        # Priority 1: Exact matches for common name patterns
        name_patterns = ['name', 'title', 'label']
        for pattern in name_patterns:
            for col in table_schema['columns']:
                col_name_lower = col.get('name', '').lower()
                if col_name_lower == pattern:
                    return col['name']
        
        # Priority 2: Columns ending with _name or _title
        for col in table_schema['columns']:
            col_name_lower = col.get('name', '').lower()
            if col_name_lower.endswith('_name') or col_name_lower.endswith('_title'):
                return col['name']
        
        # Priority 3: Columns containing name/title
        for col in table_schema['columns']:
            col_name_lower = col.get('name', '').lower()
            if 'name' in col_name_lower or 'title' in col_name_lower:
                return col['name']
        
        return None
    
    def _find_location_column(self, table_schema: Dict[str, Any]) -> Optional[str]:
        """
        Find a location column in the table - ZERO HARDCODED
        Looks for columns with location-related patterns (city, state, country, address, region, etc.)
        """
        if not table_schema or 'columns' not in table_schema:
            return None
        
        # Priority 1: Exact matches for common location patterns
        location_patterns = [
            'city', 'state', 'country', 'address', 'location', 
            'region', 'province', 'territory', 'district', 'area',
            'place', 'locality', 'zone'
        ]
        
        for pattern in location_patterns:
            for col in table_schema['columns']:
                col_name_lower = col.get('name', '').lower()
                if col_name_lower == pattern:
                    logger.info(f"Found location column (exact match): {col['name']}")
                    return col['name']
        
        # Priority 2: Columns ending with location-related suffixes
        location_suffixes = [
            '_city', '_state', '_country', '_address', '_location',
            '_region', '_province', '_territory', '_area', '_place'
        ]
        
        for col in table_schema['columns']:
            col_name_lower = col.get('name', '').lower()
            for suffix in location_suffixes:
                if col_name_lower.endswith(suffix):
                    logger.info(f"Found location column (suffix match): {col['name']}")
                    return col['name']
        
        # Priority 3: Columns containing location-related keywords
        for col in table_schema['columns']:
            col_name_lower = col.get('name', '').lower()
            for pattern in location_patterns:
                if pattern in col_name_lower:
                    logger.info(f"Found location column (partial match): {col['name']}")
                    return col['name']
        
        logger.warning("No location column found in table schema")
        return None
    
    def _find_text_column(
        self,
        table_schema: Dict[str, Any],
        preferred_names: List[str]
    ) -> Optional[str]:
        """Find a text column, preferring certain names"""
        if not table_schema or 'columns' not in table_schema:
            return None
        
        # Check preferred names first
        for col in table_schema['columns']:
            col_name = col.get('name', '').lower()
            if any(pref in col_name for pref in preferred_names):
                return col['name']
        
        # Fallback: any varchar/text column
        text_types = ['varchar', 'char', 'text', 'string']
        for col in table_schema['columns']:
            col_type = col.get('type', '').lower()
            if any(text_type in col_type for text_type in text_types):
                return col['name']
        
        return None
    
    def _month_to_number(self, month_str: str) -> int:
        """Convert month name/abbreviation to number"""
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }
        
        month_lower = month_str.lower().strip()
        return month_map.get(month_lower, 1)


# Singleton instance
_builder_instance = None

def get_sql_builder() -> SQLBuilder:
    """Get singleton instance of SQLBuilder"""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = SQLBuilder()
    return _builder_instance

