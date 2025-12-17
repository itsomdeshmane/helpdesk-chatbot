"""
User-Friendly Error Handler - Convert technical errors to plain English
Improves user experience with helpful error messages
"""
import re
import logging
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)


class SQLErrorHandler:
    """
    Convert technical SQL errors into user-friendly messages
    Provides helpful suggestions for resolution
    
    Examples:
        "Table 'db.vendr' doesn't exist" 
        → "I couldn't find a table called 'vendr'. Did you mean 'vendor'?"
        
        "Unknown column 'nam' in 'field list'" 
        → "The column 'nam' doesn't exist. Available columns: name, id, email"
    """
    
    def __init__(self):
        """Initialize error handler"""
        # MySQL error code mapping
        self.error_codes = {
            1064: 'syntax_error',
            1146: 'table_not_found',
            1054: 'column_not_found',
            1045: 'access_denied',
            1049: 'database_not_found',
            1062: 'duplicate_entry',
            1366: 'invalid_value',
            1364: 'missing_required_field',
            1452: 'foreign_key_constraint',
            2002: 'connection_failed',
            2003: 'cannot_connect',
            2006: 'connection_lost',
            2013: 'connection_timeout'
        }
        
        logger.info("✅ SQL Error Handler initialized")
    
    def make_friendly(
        self,
        error_code: Optional[int],
        error_message: str,
        nl_query: str,
        available_tables: Optional[List[str]] = None,
        available_columns: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, any]:
        """
        Convert technical error to user-friendly message
        
        Args:
            error_code: MySQL error code (if available)
            error_message: Technical error message
            nl_query: User's natural language query
            available_tables: List of available table names
            available_columns: Dict of table -> column names
            
        Returns:
            Dictionary with friendly message and suggestions
        """
        error_type = self.error_codes.get(error_code, 'unknown_error')
        
        # Route to specific handler
        if error_type == 'table_not_found':
            return self._handle_table_not_found(error_message, nl_query, available_tables)
        
        elif error_type == 'column_not_found':
            return self._handle_column_not_found(error_message, nl_query, available_columns)
        
        elif error_type == 'syntax_error':
            return self._handle_syntax_error(error_message, nl_query)
        
        elif error_type == 'access_denied':
            return self._handle_access_denied(error_message)
        
        elif error_type in ['connection_failed', 'cannot_connect', 'connection_lost', 'connection_timeout']:
            return self._handle_connection_error(error_message, error_type)
        
        else:
            return self._handle_generic_error(error_message, nl_query)
    
    def _handle_table_not_found(
        self,
        error_message: str,
        nl_query: str,
        available_tables: Optional[List[str]]
    ) -> Dict[str, any]:
        """Handle table not found error"""
        # Extract table name from error
        match = re.search(r"Table '.*?\.(\w+)'", error_message)
        table_name = match.group(1) if match else "unknown"
        
        message = f"I couldn't find a table called '{table_name}' in the database."
        suggestions = []
        
        # Suggest similar tables
        if available_tables:
            similar = self._find_similar(table_name, available_tables)
            if similar:
                suggestions = [f"Did you mean '{t}'?" for t in similar[:3]]
                message += f" Did you mean: {', '.join(similar[:3])}?"
            else:
                suggestions = [f"Available tables: {', '.join(available_tables[:5])}"]
                message += f"\n\nAvailable tables: {', '.join(available_tables[:5])}"
        
        return {
            'error_type': 'table_not_found',
            'message': message,
            'suggestions': suggestions,
            'original_error': error_message,
            'help': "Try rephrasing your question or ask 'What tables are available?'"
        }
    
    def _handle_column_not_found(
        self,
        error_message: str,
        nl_query: str,
        available_columns: Optional[Dict[str, List[str]]]
    ) -> Dict[str, any]:
        """Handle column not found error"""
        # Extract column name from error
        match = re.search(r"Unknown column '(\w+)'", error_message)
        column_name = match.group(1) if match else "unknown"
        
        message = f"The column '{column_name}' doesn't exist in the table."
        suggestions = []
        
        # Suggest similar columns from all tables
        if available_columns:
            all_columns = []
            for table, columns in available_columns.items():
                all_columns.extend(columns)
            
            similar = self._find_similar(column_name, all_columns)
            if similar:
                suggestions = [f"Did you mean '{c}'?" for c in similar[:3]]
                message += f" Did you mean: {', '.join(similar[:3])}?"
            else:
                # Show columns from first table
                first_table = next(iter(available_columns.keys()))
                cols = available_columns[first_table][:5]
                suggestions = [f"Available columns in {first_table}: {', '.join(cols)}"]
                message += f"\n\nAvailable columns: {', '.join(cols)}"
        
        return {
            'error_type': 'column_not_found',
            'message': message,
            'suggestions': suggestions,
            'original_error': error_message,
            'help': "Try using different column names or ask 'What columns are in the table?'"
        }
    
    def _handle_syntax_error(self, error_message: str, nl_query: str) -> Dict[str, any]:
        """Handle SQL syntax error"""
        message = "I had trouble converting your question to a database query."
        
        suggestions = [
            "Try rephrasing your question more simply",
            "Break complex questions into smaller parts",
            "Use simpler language (e.g., 'Show vendors' instead of 'Display vendor information')"
        ]
        
        # Specific guidance based on query
        if "join" in nl_query.lower():
            suggestions.insert(0, "For queries involving multiple tables, try asking about one table at a time")
        
        elif any(word in nl_query.lower() for word in ["average", "total", "sum", "count"]):
            suggestions.insert(0, "For calculations, try: 'Count all vendors' or 'Show total sales'")
        
        return {
            'error_type': 'syntax_error',
            'message': message,
            'suggestions': suggestions,
            'original_error': error_message,
            'help': "Examples: 'Show all vendors', 'Count customers in India', 'List products'"
        }
    
    def _handle_access_denied(self, error_message: str) -> Dict[str, any]:
        """Handle access denied error"""
        return {
            'error_type': 'access_denied',
            'message': "I don't have permission to access this database.",
            'suggestions': [
                "Contact your database administrator",
                "Check if your database credentials are correct"
            ],
            'original_error': error_message,
            'help': "This is a permissions issue that needs to be resolved by an administrator."
        }
    
    def _handle_connection_error(self, error_message: str, error_type: str) -> Dict[str, any]:
        """Handle database connection errors"""
        messages = {
            'connection_failed': "I couldn't connect to the database.",
            'cannot_connect': "I cannot reach the database server.",
            'connection_lost': "The connection to the database was lost.",
            'connection_timeout': "The database took too long to respond."
        }
        
        return {
            'error_type': error_type,
            'message': messages.get(error_type, "There's a problem connecting to the database."),
            'suggestions': [
                "Check if the database server is running",
                "Verify your network connection",
                "Try again in a moment"
            ],
            'original_error': error_message,
            'help': "This is likely a temporary issue. If it persists, contact support."
        }
    
    def _handle_generic_error(self, error_message: str, nl_query: str) -> Dict[str, any]:
        """Handle generic/unknown errors"""
        # Try to extract meaningful info
        simplified = error_message
        if len(error_message) > 200:
            simplified = error_message[:200] + "..."
        
        return {
            'error_type': 'unknown_error',
            'message': "I encountered an unexpected problem while processing your query.",
            'suggestions': [
                "Try rephrasing your question",
                "Make your question simpler",
                "Try asking about one thing at a time"
            ],
            'original_error': simplified,
            'help': "If this problem continues, please contact support with your query."
        }
    
    def _find_similar(self, target: str, options: List[str], max_results: int = 3) -> List[str]:
        """
        Find similar strings using fuzzy matching
        
        Args:
            target: String to match
            options: List of possible matches
            max_results: Maximum number of results
            
        Returns:
            List of similar strings
        """
        from difflib import get_close_matches
        
        try:
            matches = get_close_matches(target.lower(), [opt.lower() for opt in options], n=max_results, cutoff=0.6)
            
            # Return original casing
            return [opt for opt in options if opt.lower() in matches]
        except:
            return []
    
    def format_for_user(self, error_dict: Dict[str, any], include_original: bool = False) -> str:
        """
        Format error dictionary into a user-friendly string
        
        Args:
            error_dict: Error dictionary from make_friendly()
            include_original: Whether to include original technical error
            
        Returns:
            Formatted error message
        """
        parts = [error_dict['message']]
        
        if error_dict.get('suggestions'):
            parts.append("\n\nSuggestions:")
            for suggestion in error_dict['suggestions']:
                parts.append(f"  • {suggestion}")
        
        if error_dict.get('help'):
            parts.append(f"\n\n💡 {error_dict['help']}")
        
        if include_original and error_dict.get('original_error'):
            parts.append(f"\n\nTechnical details: {error_dict['original_error']}")
        
        return '\n'.join(parts)


# Global singleton
_error_handler: Optional[SQLErrorHandler] = None


def get_error_handler() -> SQLErrorHandler:
    """
    Get or create the global error handler instance
    
    Returns:
        SQLErrorHandler instance
    """
    global _error_handler
    
    if _error_handler is None:
        _error_handler = SQLErrorHandler()
    
    return _error_handler

