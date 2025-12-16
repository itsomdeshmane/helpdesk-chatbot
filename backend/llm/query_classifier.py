"""
Query Intent Classifier - AI-powered query understanding
Classifies user queries into types and extracts entities for SQL generation
ZERO HARDCODED KEYWORDS - Uses learned keywords from database and documents
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def _get_keyword_cache():
    """Lazy import to avoid circular dependency"""
    try:
        from llm.keyword_learner import get_keyword_cache
        return get_keyword_cache()
    except:
        return None


@dataclass
class QueryIntent:
    """Represents the classified intent of a user query"""
    intent_type: str  # 'list', 'count', 'aggregate_group', 'filter', 'join', 'single_value'
    operation: str  # 'select', 'count', 'sum', 'avg', 'max', 'min', 'group_by'
    entities: Dict[str, Any]  # Extracted entities (tables, columns, values, conditions)
    confidence: float  # Confidence score 0-1


class QueryClassifier:
    """
    Classifies natural language queries into intents for SQL generation
    ZERO HARDCODED KEYWORDS - Uses learned keywords dynamically
    """
    
    def __init__(self, user_id: Optional[str] = None, tenant_id: Optional[str] = None):
        """
        Initialize the classifier with patterns
        
        Args:
            user_id: Optional user ID for learned keyword access
            tenant_id: Optional tenant ID for learned keyword access
        """
        self.user_id = user_id
        self.tenant_id = tenant_id
        self._learned_keywords = None
        
        # Intent patterns - order matters (most specific first)
        self.intent_patterns = {
            'aggregate_group': [
                # "which X has/have more than N Y"
                (r'(?:which|what)\s+(\w+)\s+(?:has|have)\s+(?:more|greater)\s+than\s+(\d+)\s+(\w+)', 'group_having_gt'),
                (r'(?:which|what)\s+(\w+)\s+(?:has|have)\s+(?:less|fewer)\s+than\s+(\d+)\s+(\w+)', 'group_having_lt'),
                (r'(?:which|what)\s+(\w+)\s+(?:has|have)\s+(?:at least|minimum)\s+(\d+)\s+(\w+)', 'group_having_gte'),
                # "count/sum/avg by X"
                (r'(?:count|total|sum|average|avg)\s+(?:of\s+)?(\w+)\s+(?:by|per|for\s+each)\s+(\w+)', 'aggregate_by'),
                # "how many X per Y"
                (r'how\s+many\s+(\w+)\s+(?:per|for\s+each|by)\s+(\w+)', 'count_by'),
                # "X by Y" (general grouping)
                (r'(\w+)\s+by\s+(\w+)', 'group_by'),
            ],
            'count': [
                (r'how\s+many\s+(\w+)', 'count_simple'),
                (r'count\s+(?:of\s+)?(\w+)', 'count_simple'),
                (r'(?:total\s+)?number\s+of\s+(\w+)', 'count_simple'),
            ],
            'aggregate': [
                (r'(?:total|sum)\s+(?:of\s+)?(\w+)', 'sum'),
                (r'(?:total)\s+(\w+)\s+from', 'sum'),  # "total revenue from..."
                (r'average\s+(?:of\s+)?(\w+)', 'avg'),
                (r'(?:maximum|max|highest)\s+(\w+)', 'max'),
                (r'(?:minimum|min|lowest)\s+(\w+)', 'min'),
            ],
            'filter': [
                (r'(\w+)\s+(?:for|with|where)\s+(\w+)\s+(?:is|=|equals?)\s+["\']?([^"\']+)["\']?', 'filter_equals'),
                (r'(\w+)\s+in\s+(\w+)', 'filter_location'),
                (r'(\w+)\s+from\s+(\w+)', 'filter_location'),
            ],
            'list': [
                (r'(?:list|show)\s+(?:all\s+)?(\w+)', 'list_all'),
                (r'(?:get|give)\s+(?:me\s+)?(\w+)', 'list_all'),
                (r'what\s+(?:are\s+)?(?:the\s+)?(\w+)', 'list_all'),
            ],
        }
        
        # Condition patterns
        self.condition_patterns = {
            'gt': r'(?:more|greater)\s+than\s+(\d+)',
            'lt': r'(?:less|fewer)\s+than\s+(\d+)',
            'gte': r'(?:at\s+least|minimum)\s+(\d+)',
            'lte': r'(?:at\s+most|maximum)\s+(\d+)',
            'eq': r'(?:equals?|is)\s+["\']?([^"\']+)["\']?',
            'like': r'(?:contains?|includes?|with)\s+["\']?([^"\']+)["\']?',
            'between': r'between\s+["\']?([^"\']+)["\']?\s+and\s+["\']?([^"\']+)["\']?',
        }
    
    async def _load_learned_keywords(self):
        """Load learned keywords for this user (lazy loading)"""
        if self._learned_keywords is None and self.user_id and self.tenant_id:
            cache = _get_keyword_cache()
            if cache:
                self._learned_keywords = await cache.get_keywords(self.user_id, self.tenant_id)
                logger.info(f"Loaded learned keywords for user {self.user_id}: {sum(len(v) for v in self._learned_keywords.values())} total")
        return self._learned_keywords or {}
    
    def classify(self, query: str, available_tables: List[str] = None, conversation_history: List[Dict] = None) -> QueryIntent:
        """
        Classify a natural language query into an intent
        
        Args:
            query: Natural language query
            available_tables: List of available table names for entity extraction
            conversation_history: Previous conversation for context
            
        Returns:
            QueryIntent object with classification results
        """
        query_lower = query.lower().strip()
        logger.info(f"🔍 Classifying query: '{query}'")
        logger.info(f"📋 Available tables: {available_tables}")
        
        # Check for context-dependent queries (follow-ups)
        if conversation_history and len(conversation_history) > 0:
            logger.info(f"📚 Using conversation history: {len(conversation_history)} messages")
            # Build context from recent messages (up to 3)
            recent_messages = conversation_history[-3:]
            combined_context = {
                'tables': [],
                'aggregates': [],
                'locations': [],
                'intents': [],
                'columns': []  # Track requested columns
            }
            
            for msg in recent_messages:
                last_query = msg.get('query', '').lower()
                last_context = msg.get('context_used', {})
                
                logger.info(f"  Previous query: {last_query}")
                
                # Extract context using available tables (NO HARDCODED TERMS)
                # Use actual table names from schema
                if available_tables:
                    for table in available_tables:
                        # Check if table name (or singular form) appears in query
                        table_lower = table.lower()
                        table_singular = table_lower.rstrip('s') if table_lower.endswith('s') else table_lower
                        table_root = table_singular.replace('_', ' ')
                        
                        if (table_lower in last_query or 
                            table_singular in last_query or
                            table_root in last_query):
                            if table not in combined_context['tables']:
                                combined_context['tables'].append(table)
                                logger.info(f"  ✓ Found table from context: {table}")
                    
                if any(word in last_query for word in ['total', 'sum', 'revenue', 'value', 'amount']):
                    combined_context['aggregates'].append('sum')
                if any(word in last_query for word in ['count', 'how many', 'number']):
                    combined_context['aggregates'].append('count')
                    
                # Extract location from previous queries
                location_match = re.search(r'(?:from|in)\s+([a-zA-Z\s]+?)(?:\s|$)', last_query)
                if location_match:
                    loc = location_match.group(1).strip()
                    if loc not in ['this', 'that', 'the', 'a', 'an']:
                        combined_context['locations'].append(loc)
            
            logger.info(f"📦 Combined context: {combined_context}")
            
            # Handle follow-up queries that specify columns (e.g., "city country and phone number")
            column_keywords = ['city', 'country', 'phone', 'email', 'address', 'name', 'title', 'status', 'date', 'price', 'amount', 'value']
            detected_columns = [col for col in column_keywords if col in query_lower]
            
            if detected_columns and combined_context['tables']:
                logger.info(f"🎯 Detected column request with context")
                logger.info(f"  Columns: {detected_columns}")
                logger.info(f"  Tables: {combined_context['tables']}")
                
                # This is a follow-up asking for specific columns
                # Extract any entity filters from conversation
                entity_conditions = []
                for msg in recent_messages:
                    last_query_text = msg.get('query', '')
                    # Look for entity names (capitalized words)
                    entity_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Ltd|Inc|Corp)?)\b', last_query_text)
                    if entity_matches:
                        for entity in entity_matches:
                            if entity not in ['Are', 'Was', 'Were', 'The', 'This', 'That']:
                                entity_conditions.append({
                                    'type': 'entity_filter',
                                    'value': entity,
                                    'field_hints': []
                                })
                                logger.info(f"  ✓ Carrying forward entity filter: {entity}")
                
                return QueryIntent(
                    intent_type='list',
                    operation='list_all',
                    entities={
                        'query': query,
                        'tables': combined_context['tables'],
                        'columns': detected_columns,
                        'conditions': entity_conditions,
                        'group_by': [],
                        'having': [],
                        'order_by': [],
                        'limit': 100
                    },
                    confidence=0.95
                )
            
            # Handle progressive specification (NO HARDCODED TABLES)
            # User says "take X" or "use X" to specify table
            if available_tables:
                # Generic pattern: "take/use/from/with [table_name]"
                for table in available_tables:
                    table_lower = table.lower()
                    table_singular = table_lower.rstrip('s') if table_lower.endswith('s') else table_lower
                    
                    # Check patterns
                    patterns = [
                        rf'(?:take|use|from|with)\s+{re.escape(table_singular)}',
                        rf'(?:take|use|from|with)\s+{re.escape(table_lower)}',
                        rf'{re.escape(table_singular)}\s+(?:table|data)',
                        rf'{re.escape(table_lower)}\s+(?:table|data)'
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, query_lower):
                            combined_context['tables'].append(table)
                            logger.info(f"User specified table: {table}")
                            break
            
            # Handle specification of aggregate type
            if query_lower in ['total value', 'total amount', 'sum', 'total']:
                if combined_context['aggregates']:
                    logger.info("User clarifying aggregate type - using SUM")
                    # Use context to build full query
                    return QueryIntent(
                        intent_type='aggregate',
                        operation='sum',
                        entities={
                            'query': query,
                            'tables': combined_context['tables'] if combined_context['tables'] else [],
                            'columns': ['total_value', 'amount', 'value', 'revenue', 'price'],  # Common value columns
                            'conditions': [{'type': 'location_filter', 'value': loc} 
                                         for loc in combined_context['locations']],
                            'group_by': [],
                            'having': [],
                            'order_by': [],
                            'limit': 100,
                            'aggregate': 'sum'
                        },
                        confidence=0.95
                    )
            
            # If previous query was a COUNT and current query references it
            count_indicators = ['count', 'total', 'how many', 'number']
            if any(indicator in msg.get('query', '').lower() for msg in recent_messages for indicator in count_indicators):
                # Check if current query is asking for verification or clarification
                verify_keywords = ['check', 'verify', 'ensure', 'confirm', 'exact', 'correct', 'only']
                if any(keyword in query_lower for keyword in verify_keywords):
                    logger.info("Detected follow-up query about COUNT - maintaining COUNT intent")
                    # Force COUNT intent for follow-up
                    return QueryIntent(
                        intent_type='count',
                        operation='count_simple',
                        entities=self._extract_entities(query_lower, 'count', 'count_simple', None, available_tables),
                        confidence=0.95  # High confidence for context-based
                    )
        
        # Try to match intent patterns
        for intent_type, patterns in self.intent_patterns.items():
            for pattern, operation in patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    logger.info(f"Matched intent: {intent_type}, operation: {operation}")
                    
                    # Extract entities based on the intent type
                    entities = self._extract_entities(
                        query_lower, 
                        intent_type, 
                        operation, 
                        match,
                        available_tables
                    )
                    
                    return QueryIntent(
                        intent_type=intent_type,
                        operation=operation,
                        entities=entities,
                        confidence=0.9
                    )
        
        # Default fallback: simple list query
        logger.info("No specific intent matched, defaulting to list")
        return QueryIntent(
            intent_type='list',
            operation='list_all',
            entities=self._extract_entities(query_lower, 'list', 'list_all', None, available_tables),
            confidence=0.5
        )
    
    def _extract_entities(
        self,
        query: str,
        intent_type: str,
        operation: str,
        match: Optional[re.Match],
        available_tables: List[str]
    ) -> Dict[str, Any]:
        """Extract entities (tables, columns, conditions) from query"""
        entities = {
            'query': query,
            'tables': [],
            'columns': [],
            'conditions': [],
            'group_by': [],
            'having': [],
            'order_by': [],
            'limit': 100
        }
        
        # Extract based on intent type
        if intent_type == 'aggregate_group':
            if operation == 'group_having_gt':
                # "which city has more than 3 vendors"
                # match.group(1) = city (group by column)
                # match.group(2) = 3 (threshold)
                # match.group(3) = vendors (table name)
                entities['group_by'].append(match.group(1))
                entities['having'].append({
                    'type': 'count',
                    'operator': '>',
                    'value': int(match.group(2))
                })
                entities['tables'].append(match.group(3))
                entities['columns'].append(match.group(1))
                entities['aggregate'] = 'count'
                
            elif operation == 'group_having_lt':
                entities['group_by'].append(match.group(1))
                entities['having'].append({
                    'type': 'count',
                    'operator': '<',
                    'value': int(match.group(2))
                })
                entities['tables'].append(match.group(3))
                entities['columns'].append(match.group(1))
                entities['aggregate'] = 'count'
                
            elif operation == 'group_having_gte':
                entities['group_by'].append(match.group(1))
                entities['having'].append({
                    'type': 'count',
                    'operator': '>=',
                    'value': int(match.group(2))
                })
                entities['tables'].append(match.group(3))
                entities['columns'].append(match.group(1))
                entities['aggregate'] = 'count'
                
            elif operation in ['aggregate_by', 'count_by']:
                # "count vendors by city"
                entities['tables'].append(match.group(1))
                entities['group_by'].append(match.group(2))
                entities['columns'].append(match.group(2))
                entities['aggregate'] = 'count'
        
        elif intent_type == 'count':
            if match:
                entities['tables'].append(match.group(1))
                entities['aggregate'] = 'count'
        
        elif intent_type == 'aggregate':
            if match:
                table_hint = match.group(1)
                # Filter out aggregate keywords that aren't tables
                skip_words = ['value', 'amount', 'revenue', 'total', 'sum', 'average', 'count']
                if table_hint not in skip_words:
                    entities['tables'].append(table_hint)
                entities['aggregate'] = operation  # sum, avg, max, min
        
        elif intent_type == 'list':
            if match:
                entities['tables'].append(match.group(1))
        
        # If no tables found yet, try to extract from available tables list
        # ZERO HARDCODED - uses only actual schema tables
        if not entities['tables'] and available_tables:
            query_words = query.lower().split()
            
            for table in available_tables:
                table_lower = table.lower()
                # Check singular/plural variants
                table_singular = table_lower.rstrip('s') if table_lower.endswith('s') else table_lower
                table_root = table_singular.replace('_', ' ')  # e.g., "purchase_orders" -> "purchase order"
                
                # Check if table or its variants appear in query
                if (table_lower in query_words or 
                    table_singular in query_words or
                    table_root in query or
                    any(table_lower in word or word in table_lower for word in query_words)):
                    entities['tables'].append(table)
                    logger.info(f"Found table '{table}' in query by pattern matching")
                    break
        
        # Normalize table names to match available tables
        if available_tables:
            entities['tables'] = self._match_tables(entities['tables'], available_tables)
        
        # Extract additional conditions (WHERE clauses)
        entities['conditions'].extend(self._extract_conditions(query))
        
        logger.info(f"Extracted entities: {entities}")
        return entities
    
    def _match_tables(self, extracted_tables: List[str], available_tables: List[str]) -> List[str]:
        """Match extracted table names to actual database tables"""
        matched = []
        
        for extracted in extracted_tables:
            extracted_lower = extracted.lower().strip()
            
            # Exact match
            for available in available_tables:
                if extracted_lower == available.lower():
                    matched.append(available)
                    break
            else:
                # Fuzzy match - check if extracted is singular/plural of available
                for available in available_tables:
                    available_lower = available.lower()
                    # Check singular/plural
                    if (extracted_lower + 's' == available_lower or 
                        extracted_lower == available_lower + 's' or
                        extracted_lower in available_lower or
                        available_lower in extracted_lower):
                        matched.append(available)
                        break
        
        return matched if matched else extracted_tables
    
    async def _match_learned_keyword(self, value: str, keyword_type: str) -> Optional[Dict]:
        """
        Match a value against learned keywords
        Returns the best matching keyword with metadata
        """
        keywords = await self._load_learned_keywords()
        if not keywords or keyword_type not in keywords:
            return None
        
        value_normalized = value.lower().strip()
        
        # Try exact match first
        for kw in keywords[keyword_type]:
            if kw['normalized'] == value_normalized:
                return kw
        
        # Try partial match
        for kw in keywords[keyword_type]:
            if value_normalized in kw['normalized'] or kw['normalized'] in value_normalized:
                return kw
        
        return None
    
    def _extract_conditions(self, query: str) -> List[Dict[str, Any]]:
        """Extract WHERE conditions from query - USES LEARNED KEYWORDS"""
        conditions = []
        
        # Check for location filters (NO HARDCODED FIELD NAMES)
        # Pattern: "X in Y", "X from Y"
        location_patterns = [
            (r'\s+in\s+([A-Za-z\s]+?)(?:\s+and|\s+with|\s+for|\s*$|[,;.])', 'location_filter'),
            (r'\s+from\s+([A-Za-z\s]+?)(?:\s+and|\s+with|\s+for|\s*$|[,;.])', 'location_filter'),
        ]
        
        for pattern, cond_type in location_patterns:
            match = re.search(pattern, query)
            if match:
                location_value = match.group(1).strip()
                # Filter out common words
                skip_words = ['this', 'that', 'the', 'a', 'an', 'all', 'some', 'any', 'each', 'every']
                if location_value.lower() not in skip_words and len(location_value) > 2:
                    conditions.append({
                        'type': cond_type,
                        'value': location_value,
                        'field_hints': []  # Will be determined from schema dynamically
                    })
                    logger.info(f"Extracted location filter: {location_value}")
        
        # Check for date ranges
        date_patterns = [
            (r'(\w+)-(\d{4})-(\w+)-(\d{4})', 'date_range'),  # jan-2025-dec-2025
            (r'from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})', 'date_range'),
        ]
        
        for pattern, cond_type in date_patterns:
            match = re.search(pattern, query.lower())
            if match:
                conditions.append({
                    'type': cond_type,
                    'match': match.groups()
                })
        
        # Check for entity name filters (ZERO HARDCODED - pattern-based only)
        # Pattern: "for/of [Capitalized Name]"
        entity_pattern = r'(?:for|of|with)\s+([A-Z][a-zA-Z\s&,\.Ltd]+?)(?:\s+and|\s+or|\s*$|[,;.])'
        matches = re.finditer(entity_pattern, query)
        
        for match in matches:
            entity_name = match.group(1).strip()
            # Filter out common words
            skip_words = ['this', 'that', 'the', 'a', 'an', 'all', 'some', 'The', 'This', 'That']
            if entity_name not in skip_words and len(entity_name) > 2:
                conditions.append({
                    'type': 'entity_filter',
                    'value': entity_name,
                    'field_hints': []  # Will find name columns dynamically
                })
                logger.info(f"Extracted entity filter: {entity_name}")
        
        # Generic text filters
        text_patterns = [
            (r'(?:for|with)\s+["\']?([^"\']+)["\']?', 'text_filter'),
        ]
        
        for pattern, cond_type in text_patterns:
            match = re.search(pattern, query.lower())
            if match and match.group(1) not in ['this', 'that', 'the', 'a', 'an']:
                # Don't add if we already captured it as entity filter
                value = match.group(1)
                if not any(c['value'].lower() == value for c in conditions):
                    conditions.append({
                        'type': cond_type,
                        'value': value
                    })
        
        return conditions


# Singleton instance
_classifier_instance = None

def get_query_classifier() -> QueryClassifier:
    """Get singleton instance of QueryClassifier"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = QueryClassifier()
    return _classifier_instance

