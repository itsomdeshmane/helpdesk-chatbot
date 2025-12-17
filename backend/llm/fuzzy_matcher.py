"""
Fuzzy Column/Table Matching - Handle typos and variations
Improves user experience by handling misspellings
"""
import logging
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher, get_close_matches

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Fuzzy matching for database schema elements (tables, columns)
    Handles typos, abbreviations, and variations
    
    Examples:
        "vedor_name" → "vendor_name"
        "cust_nm" → "customer_name"
        "phn" → "phone"
    """
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize fuzzy matcher
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider a match
        """
        self.threshold = similarity_threshold
        
        # Common abbreviations mapping
        self.abbreviations = {
            'nm': 'name',
            'nbr': 'number',
            'num': 'number',
            'phn': 'phone',
            'ph': 'phone',
            'addr': 'address',
            'ct': 'count',
            'cnt': 'count',
            'amt': 'amount',
            'qty': 'quantity',
            'desc': 'description',
            'dt': 'date',
            'ts': 'timestamp',
            'id': 'id',
            'pk': 'id',
            'fk': 'id',
            'usr': 'user',
            'cust': 'customer',
            'prod': 'product',
            'ord': 'order',
            'vend': 'vendor',
            'dept': 'department',
            'mgr': 'manager',
            'emp': 'employee',
            'loc': 'location',
            'ctry': 'country',
            'st': 'state',
            'zip': 'zipcode',
            'msg': 'message',
            'stat': 'status',
            'cat': 'category',
            'img': 'image',
            'doc': 'document',
            'ref': 'reference',
            'temp': 'temporary',
            'perm': 'permanent',
            'req': 'required'
        }
        
        logger.info(f"✅ Fuzzy Matcher initialized (threshold: {similarity_threshold})")
    
    def _expand_abbreviations(self, text: str) -> str:
        """
        Expand common abbreviations
        
        Args:
            text: Text with potential abbreviations
            
        Returns:
            Expanded text
        """
        words = text.lower().replace('_', ' ').split()
        expanded = []
        
        for word in words:
            if word in self.abbreviations:
                expanded.append(self.abbreviations[word])
            else:
                expanded.append(word)
        
        return '_'.join(expanded)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        # Expand abbreviations first
        expanded1 = self._expand_abbreviations(str1)
        expanded2 = self._expand_abbreviations(str2)
        
        # Calculate base similarity
        similarity = SequenceMatcher(None, expanded1.lower(), expanded2.lower()).ratio()
        
        # Bonus for exact match after expansion
        if expanded1.lower() == expanded2.lower():
            similarity = 1.0
        
        # Bonus for substring match
        elif expanded1.lower() in expanded2.lower() or expanded2.lower() in expanded1.lower():
            similarity = max(similarity, 0.85)
        
        return similarity
    
    def match_column(
        self,
        column_hint: str,
        available_columns: List[str],
        min_similarity: Optional[float] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Find best matching column name
        
        Args:
            column_hint: User's column reference (might be misspelled)
            available_columns: List of actual column names
            min_similarity: Minimum similarity threshold (uses default if None)
            
        Returns:
            Tuple of (matched_column, similarity_score) or None
        """
        if not column_hint or not available_columns:
            return None
        
        threshold = min_similarity if min_similarity is not None else self.threshold
        
        best_match = None
        best_score = 0.0
        
        for column in available_columns:
            score = self._calculate_similarity(column_hint, column)
            
            if score > best_score:
                best_score = score
                best_match = column
        
        if best_score >= threshold:
            if best_score < 1.0:
                logger.info(f"✨ Fuzzy matched column: '{column_hint}' → '{best_match}' (score: {best_score:.2f})")
            return (best_match, best_score)
        
        logger.debug(f"❌ No fuzzy match for column: '{column_hint}' (best score: {best_score:.2f})")
        return None
    
    def match_table(
        self,
        table_hint: str,
        available_tables: List[str],
        min_similarity: Optional[float] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Find best matching table name
        
        Args:
            table_hint: User's table reference (might be misspelled)
            available_tables: List of actual table names
            min_similarity: Minimum similarity threshold (uses default if None)
            
        Returns:
            Tuple of (matched_table, similarity_score) or None
        """
        if not table_hint or not available_tables:
            return None
        
        threshold = min_similarity if min_similarity is not None else self.threshold
        
        best_match = None
        best_score = 0.0
        
        for table in available_tables:
            score = self._calculate_similarity(table_hint, table)
            
            if score > best_score:
                best_score = score
                best_match = table
        
        if best_score >= threshold:
            if best_score < 1.0:
                logger.info(f"✨ Fuzzy matched table: '{table_hint}' → '{best_match}' (score: {best_score:.2f})")
            return (best_match, best_score)
        
        logger.debug(f"❌ No fuzzy match for table: '{table_hint}' (best score: {best_score:.2f})")
        return None
    
    def suggest_corrections(
        self,
        user_input: str,
        valid_options: List[str],
        max_suggestions: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get suggestions for correcting user input
        
        Args:
            user_input: User's input (potentially incorrect)
            valid_options: List of valid options
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of (suggestion, similarity_score) tuples, sorted by score
        """
        if not user_input or not valid_options:
            return []
        
        # Calculate similarity for all options
        scored_options = [
            (option, self._calculate_similarity(user_input, option))
            for option in valid_options
        ]
        
        # Sort by score (descending)
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold and limit
        suggestions = [
            (option, score)
            for option, score in scored_options[:max_suggestions]
            if score >= self.threshold * 0.8  # Slightly lower threshold for suggestions
        ]
        
        return suggestions
    
    def find_column_by_type(
        self,
        column_type: str,
        table_schema: Dict,
        prefer_name_like: Optional[str] = None
    ) -> Optional[str]:
        """
        Find a column by its type and optional name preference
        
        Args:
            column_type: Column type to search for (e.g., 'varchar', 'int', 'date')
            table_schema: Table schema dictionary with columns
            prefer_name_like: Preferred column name pattern (fuzzy matched)
            
        Returns:
            Column name or None
        """
        if not table_schema or 'columns' not in table_schema:
            return None
        
        columns = table_schema['columns']
        matching_columns = []
        
        # Find columns matching the type
        for col in columns:
            col_type = col.get('type', '').lower()
            if column_type.lower() in col_type:
                matching_columns.append(col['name'])
        
        if not matching_columns:
            return None
        
        # If name preference provided, find best match
        if prefer_name_like:
            result = self.match_column(prefer_name_like, matching_columns)
            if result:
                return result[0]
        
        # Otherwise return first match
        return matching_columns[0]


# Global singleton
_fuzzy_matcher: Optional[FuzzyMatcher] = None


def get_fuzzy_matcher(similarity_threshold: float = 0.75) -> FuzzyMatcher:
    """
    Get or create the global fuzzy matcher instance
    
    Args:
        similarity_threshold: Minimum similarity score for matches
        
    Returns:
        FuzzyMatcher instance
    """
    global _fuzzy_matcher
    
    if _fuzzy_matcher is None:
        _fuzzy_matcher = FuzzyMatcher(similarity_threshold=similarity_threshold)
    
    return _fuzzy_matcher

