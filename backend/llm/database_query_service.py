"""
Database Query Service - SQL generation and execution
Equivalent to LlmService + SqlExecutionService + NaturalLanguageGenerator from .NET implementation

Uses hybrid approach:
1. Rule-based classification and SQL building (fast, accurate for common patterns)
2. LLM fallback for complex queries
"""
import os
import json
import logging
import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI
import pymysql
from pymysql.cursors import DictCursor
from llm.query_classifier import get_query_classifier
from llm.sql_builder import get_sql_builder

logger = logging.getLogger(__name__)


class DatabaseQueryService:
    """Service for converting natural language to SQL and executing queries"""
    
    def __init__(self):
        """Initialize the service with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
    def get_db_connection(self, connection_string: Optional[str] = None):
        """
        Create MySQL database connection
        
        Args:
            connection_string: Optional connection string, otherwise uses environment
        
        Returns:
            MySQL connection object
        """
        if connection_string:
            # Parse connection string (format: host=x;database=y;user=z;password=w;port=p)
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
    
    async def convert_to_sql(
        self, 
        natural_language_query: str,
        schema_context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        schema_dict: Optional[Dict[str, Any]] = None,
        available_tables: Optional[List[str]] = None
    ) -> str:
        """
        Convert natural language to SQL using hybrid approach:
        1. Try rule-based classification and SQL building (fast, reliable)
        2. Fallback to LLM for complex queries
        
        Args:
            natural_language_query: User's question in natural language
            schema_context: Optional database schema information (string format)
            conversation_history: Optional previous conversation for context
            schema_dict: Optional structured schema dictionary
            available_tables: Optional list of available table names
        
        Returns:
            Generated SQL query string
        """
        logger.info(f"Converting query to SQL: {natural_language_query}")
        
        # STEP 1: Try rule-based approach first
        try:
            logger.info("Attempting rule-based SQL generation...")
            classifier = get_query_classifier()
            sql_builder = get_sql_builder()
            
            # Classify the query
            intent = classifier.classify(natural_language_query, available_tables)
            
            logger.info(f"Classified intent: type={intent.intent_type}, operation={intent.operation}, confidence={intent.confidence}")
            
            # If confidence is high enough, try to build SQL
            if intent.confidence >= 0.7 and schema_dict:
                sql_query = sql_builder.build_query(intent, schema_dict, conversation_history)
                
                if sql_query and self._is_valid_sql(sql_query):
                    logger.info(f"✅ Rule-based SQL generation successful: {sql_query}")
                    return sql_query
                else:
                    logger.info("Rule-based SQL generation produced invalid query, falling back to LLM")
            else:
                logger.info(f"Confidence too low ({intent.confidence}) or no schema dict, falling back to LLM")
        
        except Exception as e:
            logger.warning(f"Rule-based SQL generation failed: {e}, falling back to LLM")
        
        # STEP 2: Fallback to LLM
        logger.info("Using LLM for SQL generation...")
        
        if not self.client:
            logger.warning("OpenAI client not initialized, using fallback")
            return self._fallback_simple_mode(natural_language_query)
        
        try:
            # GENERIC system prompt - works with ANY database
            system_prompt = """You are a SQL expert assistant. Convert natural language queries to MySQL SQL queries.

CRITICAL: You MUST return ONLY a valid SQL query. NO explanations, NO comments, NO questions.
If you cannot understand the query, return: SELECT 'query_unclear' as message

GENERIC Rules (work with ANY database):
1. Return ONLY the SQL query - absolutely NO explanations or text
2. Use proper MySQL syntax
3. Use appropriate WHERE clauses for filters
4. Use JOINs when querying multiple tables
5. Use LIMIT 100 for result sets (unless specified otherwise)
6. Handle date ranges properly (use BETWEEN or >= AND <=)
7. For names/text fields, use LIKE with wildcards for partial matching
8. Convert date ranges like "jan-2025-dec-2025" to proper SQL DATE format
9. Use GROUP BY and HAVING for aggregation questions
10. Use COUNT(*), SUM(), AVG(), MAX(), MIN() for statistics

GENERIC Patterns (adapt to actual table/column names from schema):
- "show X" = SELECT * FROM {{table_about_X}}
- "count X" = SELECT COUNT(*) as total FROM {{table_about_X}}
- "total/sum" = SELECT SUM({{amount_column}}) as total FROM {{table}}
- "X for Y" = WHERE {{y_field}} LIKE '%Y%'
- "X in Y" = WHERE country = 'Y' OR city = 'Y' (check country first, then city)
- "X from Y" = WHERE country = 'Y' OR city = 'Y'
- "X belongs to Y" = WHERE {{location_field}} = 'Y' OR {{country_field}} = 'Y'
- "jan-2025-dec-2025" = WHERE {{date_field}} BETWEEN '2025-01-01' AND '2025-12-31'

AGGREGATION Patterns (VERY IMPORTANT):
- "which X has/have more than N Y" = SELECT {{x_column}}, COUNT(*) as count FROM {{table}} GROUP BY {{x_column}} HAVING COUNT(*) > N
- "which X has/have less than N Y" = SELECT {{x_column}}, COUNT(*) as count FROM {{table}} GROUP BY {{x_column}} HAVING COUNT(*) < N
- "which X has the most Y" = SELECT {{x_column}}, COUNT(*) as count FROM {{table}} GROUP BY {{x_column}} ORDER BY count DESC LIMIT 1
- "count by X" = SELECT {{x_column}}, COUNT(*) as count FROM {{table}} GROUP BY {{x_column}}
- "sum by X" = SELECT {{x_column}}, SUM({{amount_column}}) as total FROM {{table}} GROUP BY {{x_column}}

Remember: Use the actual table and column names from the provided schema. ONLY return SQL code."""

            # Build conversation context if available
            context_str = ""
            last_sql_query = None
            
            if conversation_history and len(conversation_history) > 0:
                logger.info(f"Building context from {len(conversation_history)} previous messages")
                context_str = "\n\nPrevious Conversation:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    context_str += f"User: {msg.get('query', '')}\n"
                    # If there was a SQL query in the response, include it
                    if msg.get('module') == 'Database':
                        context_str += f"Response: {msg.get('response', '')}\n"
                        # Track the last SQL query
                        if msg.get('sql_query'):
                            last_sql_query = msg.get('sql_query')
                            context_str += f"SQL Used: {last_sql_query}\n"
                            logger.info(f"Found previous SQL: {last_sql_query}")
                
                if last_sql_query:
                    logger.info(f"Adding follow-up instructions with previous SQL: {last_sql_query}")
                    context_str += f"\nImportant: The user's new question might reference 'this data', 'these results', 'same query', etc.\n"
                    context_str += f"Previous SQL query was: {last_sql_query}\n"
                    context_str += "If the new question asks to add/modify columns or filters, modify this previous query.\n"
                    context_str += "Example: 'add city' means add city column to SELECT clause of previous query.\n"
                    context_str += f"Example: 'give me this data with city' means: {last_sql_query} but add 'city' to SELECT\n"
            else:
                logger.warning("No conversation history available for context")
            
            # GENERIC user prompt - adapts to ANY schema
            user_prompt = f"""Convert to SQL (ONLY SQL code, NO text):
{context_str}
Current Question: {natural_language_query}

{f"Available Database Schema (USE THESE EXACT table/column names):\n{schema_context}\n" if schema_context else ""}

GENERIC Instructions (work for ANY database):
1. Use EXACT table and column names from the schema above
2. For text searches: Use LIKE '%search_term%' in WHERE clause
3. For date ranges: Convert to BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD' format
4. For location filters (VERY IMPORTANT): 
   - "vendors in India" = WHERE country = 'India' (check country column first)
   - "customers from USA" = WHERE country = 'USA'
   - "orders in New York" = WHERE city = 'New York' (if no country match, use city)
   - ALWAYS check country column first for location names
5. For "belongs to X": WHERE city='X' OR country='X' OR location LIKE '%X%'
6. Add LIMIT 100 to prevent huge result sets
7. Follow-up queries: Modify previous SQL (e.g., "add city" = add city to SELECT)
8. For aggregations: Use COUNT(), SUM(), AVG(), MAX(), MIN() as appropriate
9. For "which/what X has/have more than N Y": Use GROUP BY {{x_column}} HAVING COUNT(*) > N
10. For "which/what X has/have less than N Y": Use GROUP BY {{x_column}} HAVING COUNT(*) < N
11. For "how many Y per X": Use GROUP BY {{x_column}} with COUNT(*)
12. ALWAYS return valid SQL - don't ask clarifying questions!

EXAMPLES (adapt to actual schema):
- "which city has more than 3 vendors" → SELECT city, COUNT(*) as vendor_count FROM vendors GROUP BY city HAVING COUNT(*) > 3
- "vendors in India" → SELECT * FROM vendors WHERE country = 'India' LIMIT 100
- "customers from USA" → SELECT * FROM customers WHERE country = 'USA' LIMIT 100
- "orders in New York" → SELECT * FROM orders WHERE city = 'New York' LIMIT 100
- "which customer has the most orders" → SELECT customer_name, COUNT(*) as order_count FROM orders GROUP BY customer_name ORDER BY order_count DESC LIMIT 1
- "count vendors by city" → SELECT city, COUNT(*) as vendor_count FROM vendors GROUP BY city

OUTPUT FORMAT: Just the SQL query, nothing else.
Example: SELECT column1, column2 FROM table_name WHERE condition LIMIT 100
Example: SELECT group_col, COUNT(*) as count FROM table GROUP BY group_col HAVING COUNT(*) > 5"""

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            logger.info(f"OpenAI raw response: {sql_query[:200]}")
            
            # Extract SQL from response
            sql_query = self._extract_sql_query(sql_query)
            
            # Validate that we got actual SQL, not an explanation
            if not sql_query or not self._is_valid_sql(sql_query):
                logger.warning(f"OpenAI returned invalid SQL or explanation: {sql_query}")
                return ""  # Return empty to trigger fallback or clarification
            
            logger.info(f"✅ Generated valid SQL: {sql_query}")
            return sql_query
            
        except KeyError as e:
            logger.error(f"KeyError in SQL generation - missing variable: {e}")
            logger.error(f"This usually means an unescaped template variable in prompt")
            return self._fallback_simple_mode(natural_language_query)
        except NameError as e:
            logger.error(f"NameError in SQL generation - undefined variable: {e}")
            logger.error(f"Check for unescaped {{variable}} in f-strings")
            return self._fallback_simple_mode(natural_language_query)
        except Exception as e:
            logger.error(f"Unexpected error in SQL generation: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._fallback_simple_mode(natural_language_query)
    
    def _extract_sql_query(self, response: str) -> str:
        """
        Extract SQL query from OpenAI response
        
        Args:
            response: Raw response from OpenAI
        
        Returns:
            Cleaned SQL query
        """
        if not response:
            return ""
        
        # Remove markdown code blocks
        cleaned = response.strip()
        
        if cleaned.startswith("```sql"):
            cleaned = cleaned[6:].strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:].strip()
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        
        # Check for special "query unclear" indicator
        if "query_unclear" in cleaned.lower():
            logger.warning("OpenAI indicated query is unclear")
            return ""
        
        # Check if response is an explanation, not SQL
        explanation_phrases = [
            "not specific",
            "please provide",
            "could you clarify",
            "need more information",
            "cannot determine",
            "unclear",
            "I need",
            "can you specify",
            "sorry",
            "I cannot",
            "I'm unable"
        ]
        
        cleaned_lower = cleaned.lower()
        if any(phrase in cleaned_lower for phrase in explanation_phrases):
            logger.warning(f"OpenAI returned explanation instead of SQL: {cleaned[:100]}")
            return ""
        
        # Remove trailing semicolon
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()
        
        return cleaned
    
    def _is_valid_sql(self, sql: str) -> bool:
        """
        Validate that the string is likely a SQL query
        
        Args:
            sql: String to validate
        
        Returns:
            True if looks like SQL, False otherwise
        """
        if not sql:
            return False
        
        # Must start with a SQL keyword
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN']
        sql_upper = sql.upper().strip()
        
        if not any(sql_upper.startswith(keyword) for keyword in sql_keywords):
            return False
        
        # Should not contain typical explanation phrases
        if any(phrase in sql.lower() for phrase in ['please', 'could you', 'i need', 'not sure', 'unclear']):
            return False
        
        # Should contain FROM for SELECT queries (most common)
        if sql_upper.startswith('SELECT') and 'FROM' not in sql_upper:
            # Allow COUNT(*) without FROM in some cases
            if 'COUNT' not in sql_upper and '*' not in sql:
                return False
        
        return True
    
    def _fallback_simple_mode(self, query: str) -> str:
        """
        Generate simple SQL without AI (fallback mode)
        
        Args:
            query: Natural language query
        
        Returns:
            Basic SQL query
        """
        query_lower = query.lower()
        
        # Detect table from common keywords
        table_keywords = {
            'vendors': ['vendor', 'supplier'],
            'customers': ['customer', 'client', 'buyer'],
            'products': ['product', 'item', 'good'],
            'orders': ['order', 'purchase'],
            'employees': ['employee', 'staff', 'worker'],
            'users': ['user', 'account'],
            'sales': ['sale', 'revenue'],
            'inventory': ['inventory', 'stock']
        }
        
        detected_table = None
        for table, keywords in table_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected_table = table
                break
        
        # Generate query based on intent
        if 'count' in query_lower or 'how many' in query_lower:
            if detected_table:
                return f"SELECT COUNT(*) as total FROM {detected_table}"
            else:
                return "SHOW TABLES"
        
        elif 'total' in query_lower or 'sum' in query_lower:
            if detected_table:
                return f"SELECT SUM(amount) as total FROM {detected_table}"
            else:
                return "SHOW TABLES"
        
        elif detected_table:
            return f"SELECT * FROM {detected_table} LIMIT 10"
        
        else:
            return "SHOW TABLES"
    
    async def execute_query(
        self,
        sql_query: str,
        connection_string: Optional[str] = None,
        original_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query and return results with natural language summary
        
        Args:
            sql_query: SQL query to execute
            connection_string: Optional database connection string
            original_query: Original natural language query for context
        
        Returns:
            Dictionary with success status, data, columns, and message
        """
        try:
            # Connect to database
            connection = self.get_db_connection(connection_string)
            
            with connection.cursor() as cursor:
                # Execute query
                cursor.execute(sql_query)
                
                # Fetch results
                if cursor.description:  # SELECT query
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Convert rows to JSON-serializable format
                    serializable_rows = self._serialize_rows(rows)
                    
                    # Generate natural language summary
                    message = await self._generate_summary(
                        original_query or "Query",
                        serializable_rows,
                        columns
                    )
                    
                    return {
                        "success": True,
                        "message": message,
                        "rows": serializable_rows,
                        "columns": columns,
                        "row_count": len(rows),
                        "response_format": "table",
                        "sql_query": sql_query
                    }
                else:  # INSERT/UPDATE/DELETE
                    connection.commit()
                    affected_rows = cursor.rowcount
                    
                    return {
                        "success": True,
                        "message": f"Query executed successfully. {affected_rows} row(s) affected.",
                        "rows": [],
                        "columns": [],
                        "row_count": affected_rows,
                        "response_format": "text",
                        "sql_query": sql_query
                    }
            
        except pymysql.MySQLError as e:
            # Specific MySQL errors (similar to .NET MySqlException handling)
            error_code = e.args[0] if e.args else 0
            error_msg = e.args[1] if len(e.args) > 1 else str(e)
            logger.error(f"MySQL Error [{error_code}]: {error_msg}")
            logger.error(f"Failed SQL: {sql_query}")
            
            # Provide user-friendly error messages
            if error_code == 1146:  # Table doesn't exist
                friendly_msg = f"Table not found. {error_msg}"
            elif error_code == 1054:  # Unknown column
                friendly_msg = f"Column not found. {error_msg}"
            elif error_code == 1064:  # SQL syntax error
                friendly_msg = f"SQL syntax error. {error_msg}"
            else:
                friendly_msg = f"Database error: {error_msg}"
            
            return {
                "success": False,
                "message": friendly_msg,
                "rows": [],
                "columns": [],
                "row_count": 0,
                "error_code": error_code,
                "sql_query": sql_query
            }
        except Exception as e:
            # General exceptions (similar to .NET general Exception handling)
            logger.error(f"Unexpected error executing query: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"Failed SQL: {sql_query}")
            return {
                "success": False,
                "message": f"Error executing query: {str(e)}",
                "rows": [],
                "columns": [],
                "row_count": 0,
                "response_format": "error",
                "sql_query": sql_query
            }
        finally:
            if 'connection' in locals():
                connection.close()
    
    def _serialize_rows(self, rows: List[Dict]) -> List[Dict]:
        """
        Convert database rows to JSON-serializable format
        Handles datetime, date, Decimal, and other special types
        
        Args:
            rows: List of row dictionaries from database
            
        Returns:
            List of JSON-serializable dictionaries
        """
        serializable_rows = []
        
        for row in rows:
            serializable_row = {}
            for key, value in row.items():
                # Handle datetime and date objects
                if isinstance(value, (datetime, date)):
                    serializable_row[key] = value.isoformat()
                # Handle Decimal objects
                elif isinstance(value, Decimal):
                    serializable_row[key] = float(value)
                # Handle bytes (binary data)
                elif isinstance(value, bytes):
                    try:
                        serializable_row[key] = value.decode('utf-8')
                    except:
                        serializable_row[key] = str(value)
                # Handle None and other types
                else:
                    serializable_row[key] = value
            
            serializable_rows.append(serializable_row)
        
        return serializable_rows
    
    async def _generate_summary(
        self,
        question: str,
        rows: List[Dict],
        columns: List[str]
    ) -> str:
        """
        Generate natural language summary of query results (matches .NET implementation)
        
        Args:
            question: Original question
            rows: Query result rows
            columns: Column names
        
        Returns:
            Natural language summary
        """
        if not rows:
            return "I couldn't find any results matching your query. Please try rephrasing your question or check if the data exists."
        
        query = question.lower().strip()
        row_count = len(rows)
        
        # Check query type and generate appropriate response
        if self._is_count_query(query):
            return self._generate_count_response(query, rows, columns)
        
        if self._is_sum_or_total_query(query):
            return self._generate_sum_response(query, rows, columns)
        
        if self._is_average_query(query):
            return self._generate_average_response(query, rows, columns)
        
        if self._is_max_min_query(query):
            return self._generate_max_min_response(query, rows, columns)
        
        if self._is_list_query(query):
            return self._generate_list_response(query, rows, columns)
        
        # Single value query or single value result
        if self._is_single_value_query(query) or (row_count == 1 and len(columns) == 1):
            return self._generate_single_value_response(query, rows, columns)
        
        if row_count == 1:
            return self._generate_single_record_response(query, rows, columns)
        
        # Default: Multi-record response
        return self._generate_multi_record_response(query, rows, columns)
    
    def _is_count_query(self, query: str) -> bool:
        """Check if query is asking for count"""
        return any(word in query for word in ['how many', 'count', 'number of', 'total number'])
    
    def _is_sum_or_total_query(self, query: str) -> bool:
        """Check if query is asking for sum/total"""
        return any(word in query for word in ['total', 'sum of', 'combined'])
    
    def _is_average_query(self, query: str) -> bool:
        """Check if query is asking for average"""
        return any(word in query for word in ['average', 'avg', 'mean'])
    
    def _is_max_min_query(self, query: str) -> bool:
        """Check if query is asking for max/min"""
        return any(word in query for word in ['maximum', 'max', 'highest', 'minimum', 'min', 'lowest'])
    
    def _is_list_query(self, query: str) -> bool:
        """Check if query is asking for a list"""
        return any(word in query for word in ['list', 'show me', 'what are', 'which', 'what'])
    
    def _is_single_value_query(self, query: str) -> bool:
        """Check if query is asking for single value"""
        return any(word in query for word in ['what is', "what's", 'when is', 'where is', 'who is'])
    
    def _extract_subject(self, query: str) -> str:
        """Extract the subject from the query"""
        # Remove location phrases first
        working_query = re.sub(r'\s+(in|from|at|for|with|by)\s+[a-z\s]+$', '', query, flags=re.IGNORECASE)
        
        # Remove common question words
        clean_query = working_query
        for phrase in ['how many', 'how much', 'what is', "what's", 'what are', 'show me', 
                      'give me', 'get me', 'list all', 'list of', 'list', 'total', 'count of',
                      'count', 'number of', 'average of', 'average', 'sum of', 'sum', 
                      'available', 'the', 'all', 'of', 'are', 'is']:
            clean_query = clean_query.replace(phrase, '')
        
        clean_query = clean_query.strip()
        clean_query = re.sub(r'\s+', ' ', clean_query)
        
        # Take first meaningful words (up to 3)
        words = [w for w in clean_query.split() if len(w) > 1][:3]
        
        if words:
            return ' '.join(words)
        
        return 'results'
    
    def _extract_location(self, query: str) -> str:
        """Extract location from the query"""
        location_patterns = [
            r'\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)',
            r'\s+from\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)',
            r'\s+at\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)',
            r'\savailable\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)',
            r'\slocated\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Capitalize each word
                return ' '.join(word.capitalize() for word in location.split())
        
        return ''
    
    def _format_number(self, value: any) -> str:
        """Format number with thousands separator"""
        if value is None:
            return '0'
        
        try:
            num = float(value)
            if num == int(num):
                return f"{int(num):,}"
            else:
                return f"{num:,.2f}"
        except:
            return str(value)
    
    def _generate_count_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for count queries"""
        if len(rows) == 1 and columns:
            value = rows[0][columns[0]]
            subject = self._extract_subject(query)
            location = self._extract_location(query)
            
            response = f"Total available {subject}"
            if location:
                response += f" in {location}"
            
            if value is None:
                response += " is: No data available"
            else:
                try:
                    num_value = int(value)
                    verb = "is" if num_value == 1 else "are"
                    response += f" {verb} {num_value}."
                except:
                    response += f" is: {value}"
            
            return response
        
        return f"I found {len(rows)} records that match your query."
    
    def _generate_sum_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for sum/total queries"""
        if len(rows) == 1 and columns:
            value = rows[0][columns[0]]
            subject = self._extract_subject(query)
            location = self._extract_location(query)
            
            response = f"The total {subject}"
            if location:
                response += f" in {location}"
            
            if value is None:
                response += " is: No data available"
            else:
                response += f" is {self._format_number(value)}."
            
            return response
        
        return f"Based on your query, I found {len(rows)} records."
    
    def _generate_average_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for average queries"""
        if len(rows) == 1 and columns:
            value = rows[0][columns[0]]
            subject = self._extract_subject(query)
            location = self._extract_location(query)
            
            response = f"The average {subject}"
            if location:
                response += f" in {location}"
            
            if value is None:
                response += " is: No data available"
            else:
                response += f" is {self._format_number(value)}."
            
            return response
        
        return f"I calculated the average from {len(rows)} records."
    
    def _generate_max_min_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for max/min queries"""
        if not rows or not columns:
            return "I couldn't determine the value from the results."
        
        is_max = 'max' in query or 'highest' in query
        is_min = 'min' in query or 'lowest' in query
        
        if len(rows) == 1:
            subject = self._extract_subject(query)
            value = rows[0][columns[0]]
            
            if is_max:
                response = f"The highest {subject} is {value}"
            elif is_min:
                response = f"The lowest {subject} is {value}"
            else:
                response = f"The {subject} is {value}"
            
            # Add additional details if available
            if len(columns) > 1:
                details = []
                for i in range(1, min(len(columns), 3)):
                    details.append(f"{columns[i]}: {rows[0][columns[i]]}")
                if details:
                    response += f" ({', '.join(details)})"
            
            response += "."
            return response
        
        return f"I found {len(rows)} records that match your criteria."
    
    def _generate_list_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for list queries (NOT count queries)"""
        if not columns:
            return "I couldn't generate a list from the results."
        
        # Special handling: If it's actually a COUNT query result (single row with count/total), format as count
        if len(rows) == 1 and len(columns) == 1:
            col_name = columns[0].lower()
            if col_name in ['total', 'count', 'result']:
                count_value = list(rows[0].values())[0]
                subject = self._extract_subject(query)
                location = self._extract_location(query)
                
                response = f"Total available {subject}"
                if location:
                    response += f" in {location}"
                response += f" {'is' if not subject.endswith('s') else 'are'} {self._format_number(count_value)}."
                return response
        
        # Check if this is a grouped/aggregated result (has count/sum/total columns)
        has_aggregation = any(col.lower() in ['count', 'total', 'sum', 'avg', 'average', 'vendor_count', 'order_count', 'customer_count'] 
                             for col in columns)
        
        # Check if query has filtering criteria like "more than", "less than", "greater than"
        has_filter_criteria = any(phrase in query.lower() for phrase in ['more than', 'less than', 'greater than', 'at least', 'minimum'])
        
        subject = self._extract_subject(query)
        location = self._extract_location(query)
        
        if not subject or subject == 'results':
            # Try to infer from columns
            if columns:
                subject = columns[0].replace('_', ' ')
            else:
                subject = 'items'
        
        if not rows:
            response = f"I couldn't find any {subject}"
            if location:
                response += f" in {location}"
            if has_filter_criteria:
                response += " matching your criteria"
            response += "."
            return response
        
        # Generate appropriate response based on query type
        if has_aggregation and has_filter_criteria:
            # e.g., "which city has more than 3 vendors?"
            if len(rows) == 0:
                return f"No {subject} match your criteria."
            else:
                plural_subject = subject if subject.endswith('s') or subject in ['data', 'information'] else subject + 's'
                response = f"I found {len(rows)} {plural_subject} matching your criteria:"
        elif has_aggregation:
            # e.g., "count vendors by city"
            if len(rows) == 1:
                singular_subject = subject.rstrip('s')
                response = f"Here's the {singular_subject} breakdown:"
            else:
                plural_subject = subject if subject.endswith('s') or subject in ['data', 'information'] else subject + 's'
                response = f"Here's the breakdown for {len(rows)} {plural_subject}:"
        else:
            # Regular list query
            if len(rows) == 1:
                singular_subject = subject.rstrip('s')
                response = f"I found 1 {singular_subject}"
            else:
                plural_subject = subject if subject.endswith('s') or subject in ['data', 'information'] else subject + 's'
                response = f"I found {len(rows)} {plural_subject}"
            
            if location:
                response += f" in {location}"
            response += ":"
        
        return response
    
    def _generate_single_value_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for single value queries"""
        if not columns:
            return "I couldn't extract the value from the results."
        
        value = rows[0][columns[0]]
        subject = self._extract_subject(query)
        
        if 'what is' in query or "what's" in query:
            return f"The {subject} is {value}."
        elif 'when' in query:
            return f"It was {value}."
        elif 'where' in query:
            return f"It is located at {value}."
        elif 'who' in query:
            return f"It is {value}."
        
        return f"{columns[0]}: {value}"
    
    def _generate_single_record_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for single record queries"""
        if not columns:
            return "I found one record but couldn't extract the details."
        
        response = "Here's what I found:\n\n"
        for column in columns:
            value = rows[0].get(column)
            if value is not None and str(value).strip():
                response += f"• {column}: {value}\n"
        
        return response.rstrip()
    
    def _generate_multi_record_response(self, query: str, rows: List[Dict], columns: List[str]) -> str:
        """Generate response for multiple record queries"""
        if not columns:
            return f"I found {len(rows)} records that match your query."
        
        subject = self._extract_subject(query)
        location = self._extract_location(query)
        
        if not subject or subject == 'results':
            subject = 'records'
        
        if not rows:
            response = f"I couldn't find any {subject}"
            if location:
                response += f" in {location}"
            response += "."
            return response
        
        if len(rows) == 1:
            singular_subject = subject.rstrip('s')
            response = f"I found 1 {singular_subject}"
        else:
            # Handle plural
            plural_subject = subject if subject.endswith('s') or subject in ['data', 'information'] else subject + 's'
            response = f"I found {len(rows)} {plural_subject}"
        
        if location:
            response += f" in {location}"
        
        response += ":"
        return response


# Singleton instance
_service_instance = None

def get_database_query_service() -> DatabaseQueryService:
    """Get singleton instance of DatabaseQueryService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DatabaseQueryService()
    return _service_instance

