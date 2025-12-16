"""
Intelligent Entity Matcher - NLP-based column and value matching
Automatically detects entities in queries and matches them to database columns
Uses spaCy for entity recognition and RapidFuzz for fuzzy matching
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

# Try to import spaCy (optional dependency)
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
        nlp = None
except ImportError:
    logger.warning("spaCy not installed. Using fallback pattern matching. Install: pip install spacy")
    SPACY_AVAILABLE = False
    nlp = None


class IntelligentEntityMatcher:
    """
    Intelligent entity and keyword matcher for database queries
    Automatically detects ALL types of entities: locations, status, priority, categories, etc.
    """
    
    # Common entity patterns by semantic category
    ENTITY_PATTERNS = {
        'location': {
            'keywords': ['location', 'city', 'state', 'country', 'region', 'province', 
                        'territory', 'district', 'area', 'place', 'zone', 'address',
                        'locality', 'town', 'village', 'county', 'prefecture'],
            'patterns': [
                r'\s+(?:in|from|at|around|near)\s+([A-Z][a-zA-Z\s]+?)(?:\s+and|\s+with|\s*$|[,;.])',
                r'location\s*[:\-]?\s*([A-Z][a-zA-Z\s]+)',
            ]
        },
        'status': {
            'keywords': ['status', 'state', 'condition', 'stage', 'phase', 'situation'],
            'patterns': [
                r'(?:with|having|in)\s+status\s+["\']?([a-zA-Z\s]+)["\']?',
                r'(?:is|are)\s+([a-zA-Z]+)(?:\s+status)?',
                r'status\s*[:\-]?\s*([a-zA-Z\s]+)',
            ],
            'values': ['open', 'closed', 'pending', 'active', 'inactive', 'completed', 
                      'in progress', 'resolved', 'cancelled', 'approved', 'rejected',
                      'draft', 'published', 'archived', 'new', 'assigned']
        },
        'priority': {
            'keywords': ['priority', 'urgency', 'importance', 'severity', 'criticality'],
            'patterns': [
                r'(?:with|having)\s+(?:priority|urgency)\s+["\']?([a-zA-Z\s]+)["\']?',
                r'priority\s*[:\-]?\s*([a-zA-Z\s]+)',
            ],
            'values': ['high', 'medium', 'low', 'critical', 'urgent', 'normal', 
                      'minor', 'major', 'blocker', 'trivial']
        },
        'type': {
            'keywords': ['type', 'kind', 'category', 'class', 'classification', 
                        'genre', 'variant', 'style'],
            'patterns': [
                r'(?:of|with)\s+type\s+["\']?([a-zA-Z\s]+)["\']?',
                r'type\s*[:\-]?\s*([a-zA-Z\s]+)',
            ]
        },
        'category': {
            'keywords': ['category', 'group', 'section', 'division', 'department',
                        'team', 'unit', 'branch'],
            'patterns': [
                r'(?:in|from|of)\s+category\s+["\']?([a-zA-Z\s]+)["\']?',
                r'category\s*[:\-]?\s*([a-zA-Z\s]+)',
            ]
        },
        'date': {
            'keywords': ['date', 'time', 'datetime', 'timestamp', 'created', 'updated',
                        'modified', 'started', 'ended', 'completed', 'due'],
            'patterns': [
                r'(?:on|at|from|since|until|before|after)\s+(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ]
        },
        'name': {
            'keywords': ['name', 'title', 'label', 'identifier', 'tag', 'caption'],
            'patterns': [
                r'(?:named|called|titled)\s+["\']?([A-Za-z0-9\s]+)["\']?',
                r'name\s*[:\-]?\s*["\']?([A-Za-z0-9\s]+)["\']?',
            ]
        },
        'email': {
            'keywords': ['email', 'mail', 'contact'],
            'patterns': [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ]
        },
        'phone': {
            'keywords': ['phone', 'mobile', 'telephone', 'contact', 'number'],
            'patterns': [
                r'(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})',
            ]
        },
        'amount': {
            'keywords': ['amount', 'value', 'price', 'cost', 'total', 'sum',
                        'revenue', 'sales', 'profit', 'expense', 'fee'],
            'patterns': [
                r'(?:of|worth|total)\s+\$?(\d+(?:\.\d{2})?)',
            ]
        }
    }
    
    def __init__(self):
        """Initialize the intelligent entity matcher"""
        self.use_spacy = SPACY_AVAILABLE and nlp is not None
        if self.use_spacy:
            logger.info("✅ Intelligent Entity Matcher initialized with spaCy NLP")
        else:
            logger.info("⚠️ Intelligent Entity Matcher using pattern matching (spaCy unavailable)")
    
    def extract_entities(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract all entities from query using NLP and patterns
        
        Returns:
            Dict with entity types as keys and list of extracted entities
        """
        entities = {}
        
        # Use spaCy if available
        if self.use_spacy:
            entities.update(self._extract_with_spacy(query))
        
        # Always use pattern matching as well (complementary)
        entities.update(self._extract_with_patterns(query))
        
        logger.info(f"Extracted entities: {entities}")
        return entities
    
    def _extract_with_spacy(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities using spaCy NER"""
        entities = {}
        
        try:
            doc = nlp(query)
            
            # Extract named entities
            for ent in doc.ents:
                entity_type = ent.label_.lower()
                
                # Map spaCy entity types to our categories
                mapped_type = self._map_spacy_entity_type(entity_type)
                
                if mapped_type:
                    if mapped_type not in entities:
                        entities[mapped_type] = []
                    
                    entities[mapped_type].append({
                        'value': ent.text,
                        'confidence': 0.9,
                        'method': 'spacy_ner'
                    })
        except Exception as e:
            logger.warning(f"spaCy extraction failed: {e}")
        
        return entities
    
    def _map_spacy_entity_type(self, spacy_type: str) -> Optional[str]:
        """Map spaCy entity types to our semantic categories"""
        mapping = {
            'gpe': 'location',      # Geopolitical entity
            'loc': 'location',      # Location
            'fac': 'location',      # Facility
            'person': 'name',
            'org': 'name',
            'date': 'date',
            'time': 'date',
            'money': 'amount',
            'percent': 'amount',
            'quantity': 'amount',
            'cardinal': 'amount',
        }
        return mapping.get(spacy_type)
    
    def _extract_with_patterns(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities using regex patterns"""
        entities = {}
        
        for entity_type, config in self.ENTITY_PATTERNS.items():
            patterns = config.get('patterns', [])
            known_values = config.get('values', [])
            
            # Pattern-based extraction
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    
                    # Skip very short or generic values
                    if len(value) < 2 or value.lower() in ['the', 'a', 'an', 'this', 'that']:
                        continue
                    
                    if entity_type not in entities:
                        entities[entity_type] = []
                    
                    entities[entity_type].append({
                        'value': value,
                        'confidence': 0.8,
                        'method': 'pattern'
                    })
            
            # Check for known values
            if known_values:
                query_lower = query.lower()
                for known_value in known_values:
                    if known_value.lower() in query_lower:
                        if entity_type not in entities:
                            entities[entity_type] = []
                        
                        entities[entity_type].append({
                            'value': known_value,
                            'confidence': 0.85,
                            'method': 'known_value'
                        })
        
        return entities
    
    def find_matching_column(
        self,
        entity_type: str,
        table_schema: Dict[str, Any],
        threshold: float = 70.0
    ) -> Optional[str]:
        """
        Find the best matching column for an entity type using intelligent fuzzy matching
        
        Args:
            entity_type: Type of entity (location, status, priority, etc.)
            table_schema: Database table schema
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Best matching column name or None
        """
        if not table_schema or 'columns' not in table_schema:
            return None
        
        # Get keywords for this entity type
        keywords = self.ENTITY_PATTERNS.get(entity_type, {}).get('keywords', [entity_type])
        
        # Extract column names
        columns = [col['name'] for col in table_schema['columns']]
        column_names_lower = [col.lower() for col in columns]
        
        # Priority 1: Exact match
        for keyword in keywords:
            if keyword in column_names_lower:
                idx = column_names_lower.index(keyword)
                logger.info(f"✓ Found exact match for '{entity_type}': {columns[idx]}")
                return columns[idx]
        
        # Priority 2: Fuzzy match with each keyword
        best_match = None
        best_score = threshold
        
        for keyword in keywords:
            # Use RapidFuzz for intelligent fuzzy matching
            result = process.extractOne(
                keyword,
                columns,
                scorer=fuzz.WRatio,  # Weighted ratio for better matching
                score_cutoff=threshold
            )
            
            if result and result[1] > best_score:
                best_match = result[0]
                best_score = result[1]
        
        if best_match:
            logger.info(f"✓ Found fuzzy match for '{entity_type}': {best_match} (score: {best_score:.1f})")
            return best_match
        
        # Priority 3: Substring match
        for keyword in keywords:
            for i, col_name in enumerate(column_names_lower):
                if keyword in col_name or col_name in keyword:
                    logger.info(f"✓ Found substring match for '{entity_type}': {columns[i]}")
                    return columns[i]
        
        logger.warning(f"✗ No matching column found for entity type: {entity_type}")
        return None
    
    def create_filter_conditions(
        self,
        query: str,
        table_schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Automatically create filter conditions from query by detecting entities
        and matching them to appropriate columns
        
        Args:
            query: Natural language query
            table_schema: Database table schema
            
        Returns:
            List of filter conditions ready for SQL WHERE clause
        """
        conditions = []
        
        # Extract all entities from query
        entities = self.extract_entities(query)
        
        # For each detected entity, find matching column and create condition
        for entity_type, entity_list in entities.items():
            # Skip duplicates
            seen_values = set()
            
            for entity_info in entity_list:
                value = entity_info['value']
                
                if value in seen_values:
                    continue
                seen_values.add(value)
                
                # Find matching column
                column = self.find_matching_column(entity_type, table_schema)
                
                if column:
                    # Create appropriate condition based on entity type
                    condition = self._create_condition(
                        entity_type,
                        column,
                        value,
                        entity_info['confidence']
                    )
                    
                    if condition:
                        conditions.append(condition)
                        logger.info(f"✓ Created condition: {column} with value '{value}'")
        
        return conditions
    
    def _create_condition(
        self,
        entity_type: str,
        column: str,
        value: str,
        confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Create a filter condition based on entity type"""
        
        # For text-based entities (location, status, etc.)
        if entity_type in ['location', 'status', 'priority', 'type', 'category', 'name']:
            return {
                'type': 'text_filter',
                'column': column,
                'value': value,
                'operator': 'LIKE',  # Use LIKE for flexible matching
                'confidence': confidence
            }
        
        # For numeric entities
        elif entity_type in ['amount']:
            return {
                'type': 'numeric_filter',
                'column': column,
                'value': value,
                'operator': '=',
                'confidence': confidence
            }
        
        # For date entities
        elif entity_type in ['date']:
            return {
                'type': 'date_filter',
                'column': column,
                'value': value,
                'operator': '=',
                'confidence': confidence
            }
        
        # For contact entities (email, phone)
        elif entity_type in ['email', 'phone']:
            return {
                'type': 'text_filter',
                'column': column,
                'value': value,
                'operator': '=',
                'confidence': confidence
            }
        
        return None


# Singleton instance
_matcher_instance = None

def get_intelligent_matcher() -> IntelligentEntityMatcher:
    """Get singleton instance of IntelligentEntityMatcher"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = IntelligentEntityMatcher()
    return _matcher_instance

