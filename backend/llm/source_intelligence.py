"""
Source Intelligence Service
Intelligently determines the best source (database vs documents) for a query
GENERIC IMPLEMENTATION - Works with any database schema
"""
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SourceIntelligence:
    """Determines the best source for answering a query - GENERIC"""
    
    def __init__(self):
        """Initialize with generic detection patterns"""
        
        # GENERIC patterns that work for ANY database
        self.database_patterns = [
            # Data retrieval keywords (GENERIC)
            r'\b(show|list|get|find|fetch|retrieve|display|view)\s+(all|the|my)?\s*(data|records|rows|entries|items|results)',
            r'\bhow\s+many\b',
            r'\bcount\s+(of|the)?\b',
            r'\btotal\s+(of|for|in)?\b',
            r'\bsum\s+(of|for)?\b',
            r'\baverage\s+(of|for)?\b',
            r'\bmax(imum)?\s+(of|for)?\b',
            r'\bmin(imum)?\s+(of|for)?\b',
            
            # Data filtering keywords (GENERIC)
            r'\bwhere\b',
            r'\bfilter\s+by\b',
            r'\bbetween\s+\w+\s+and\s+\w+',
            r'\bfor\s+\w+',  # Generic "for X"
            r'\bin\s+\d{4}',  # Year mentions
            r'\blast\s+(month|year|week|quarter|day)',
            r'\bthis\s+(month|year|week|quarter|day)',
            
            # SQL-like terms (GENERIC)
            r'\bquery\b',
            r'\btable\b',
            r'\bcolumn\b',
            r'\bjoin\b',
            r'\bgroup\s+by\b',
            r'\border\s+by\b',
            r'\bselect\b',
            r'\blimit\b',
            
            # Generic data operations
            r'\b(report|dashboard|analytics|metrics|kpi|statistics)\b',
            
            # Date range patterns (GENERIC)
            r'\bfrom\s+\w+\s+to\s+\w+',
            r'\bjan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            
            # Comparison operators (GENERIC)
            r'\bgreater\s+than\b',
            r'\bless\s+than\b',
            r'\bequal\s+to\b',
            r'\b>\s*\d+',
            r'\b<\s*\d+',
            r'\b=\s*\d+',
        ]
        
        # GENERIC patterns for documentation queries
        self.documentation_patterns = [
            # Help/guidance keywords (GENERIC)
            r'\bhow\s+(do|can|to|should|does)\s+(i|we|you|it)\b',
            r'\bwhat\s+is\b',
            r'\bwhat\s+are\b',
            r'\bwhat\s+does\b',
            r'\bexplain\b',
            r'\bdescribe\b',
            r'\bdefine\b',
            r'\btell\s+me\s+about\b',
            r'\bhelp\s+me\s+(with|understand|to)\b',
            
            # Process/procedure keywords (GENERIC)
            r'\b(step|steps|process|procedure|workflow|guide|method)\b',
            r'\b(tutorial|documentation|docs|manual|instructions)\b',
            r'\bhow\s+does\s+\w+\s+work',
            r'\bcan\s+you\s+(explain|describe|tell|show)\b',
            
            # Feature/functionality keywords (GENERIC)
            r'\b(feature|functionality|capability|option|setting)\b',
            r'\b(setup|configure|configuration|settings|preferences)\b',
            r'\b(install|installation|deployment|integration)\b',
            r'\b(troubleshoot|debug|fix|solve|error|issue|problem)\b',
            
            # Question words indicating conceptual queries (GENERIC)
            r'\bwhy\s+(is|does|do|would|should|did|can)\b',
            r'\bwhen\s+(should|to|is|does|do|did)\b',
            r'\bwhich\s+(one|option|feature|way|method)\b',
            r'\bshould\s+i\b',
            r'\bcan\s+i\b',
        ]
        
        # Follow-up indicators (GENERIC)
        self.followup_patterns = [
            r'\b(this|that|these|those|same|previous|above|below)\b',
            r'\badd\s+(to|the|more|another)\b',
            r'\bmodify\b',
            r'\bchange\b',
            r'\bupdate\b',
            r'\bmore\s+(details|info|information|data)',
            r'\balso\s+(show|add|include)\b',
            r'\band\s+(also|what|include|add)\b',
            r'\binclude\s+\w+',
            r'\bwith\s+\w+\s+(column|field|data)',
        ]
        
        # Compile patterns for performance
        self.db_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.database_patterns]
        self.doc_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.documentation_patterns]
        self.followup_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.followup_patterns]
        
        # Dynamic patterns loaded from database schema (GENERIC)
        self.schema_keywords = {
            "tables": [],
            "columns": []
        }
    
    def load_schema_keywords(self, available_tables: Optional[List[str]] = None):
        """
        GENERIC: Dynamically load keywords from database schema
        This makes the system work with ANY database without hardcoding
        """
        if available_tables:
            self.schema_keywords["tables"] = [t.lower() for t in available_tables]
            logger.info(f"Loaded {len(available_tables)} table names for intelligent detection")
    
    def detect_source(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        available_tables: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        GENERIC: Detect the best source for a query
        Works with ANY database schema by dynamically loading table/column names
        
        Args:
            query: User's query
            conversation_history: Previous conversation
            available_tables: Available database tables (loaded dynamically)
        
        Returns:
            {
                "source": "database" | "documents" | "both",
                "confidence": 0.0-1.0,
                "reason": "explanation",
                "is_followup": bool
            }
        """
        query_lower = query.lower().strip()
        
        # Load schema keywords dynamically (GENERIC APPROACH)
        if available_tables:
            self.load_schema_keywords(available_tables)
        
        # Check if this is a follow-up question
        is_followup = self._is_followup(query_lower)
        
        # If it's a follow-up, use the same source as previous
        if is_followup and conversation_history and len(conversation_history) > 0:
            last_source = conversation_history[-1].get('module', '').lower()
            if last_source in ['database', 'documents']:
                logger.info(f"✅ Follow-up detected, using previous source: {last_source}")
                return {
                    "source": last_source,
                    "confidence": 0.95,
                    "reason": f"Follow-up to previous {last_source} query",
                    "is_followup": True
                }
        
        # Score both sources using GENERIC patterns
        db_score = self._score_patterns(query_lower, self.db_regex)
        doc_score = self._score_patterns(query_lower, self.doc_regex)
        
        # GENERIC: Check for table name mentions (works with ANY database)
        if self.schema_keywords["tables"]:
            for table in self.schema_keywords["tables"]:
                # Check both exact match and plural forms
                if table in query_lower or f"{table}s" in query_lower:
                    db_score += 3.0
                    logger.info(f"✅ Found table keyword '{table}' in query, boosting database score")
        
        # GENERIC: SQL keyword boosts (works for any database)
        sql_keywords = ['select', 'insert', 'update', 'delete', 'sql', 'query']
        if any(word in query_lower for word in sql_keywords):
            db_score += 3.0
            logger.info("✅ Found SQL keyword, boosting database score")
        
        # GENERIC: Documentation keyword boosts
        doc_keywords = ['documentation', 'docs', 'manual', 'guide', 'tutorial', 'help', 'explain']
        if any(word in query_lower for word in doc_keywords):
            doc_score += 3.0
            logger.info("✅ Found documentation keyword, boosting documentation score")
        
        # GENERIC: Make decision based on scores (works for any domain)
        total_score = db_score + doc_score
        
        logger.info(f"📊 Scoring: Database={db_score:.1f}, Documentation={doc_score:.1f}, Total={total_score:.1f}")
        
        if total_score == 0:
            # Ambiguous query, try both
            logger.info("⚠️ No clear indicators, will try multiple sources")
            return {
                "source": "both",
                "confidence": 0.5,
                "reason": "Query is ambiguous, will try multiple sources",
                "is_followup": False
            }
        
        db_confidence = db_score / total_score if total_score > 0 else 0
        doc_confidence = doc_score / total_score if total_score > 0 else 0
        
        # GENERIC: Threshold for clear decision (configurable)
        CONFIDENCE_THRESHOLD = 0.65  # Adjust this for your needs
        
        if db_confidence > CONFIDENCE_THRESHOLD:
            logger.info(f"✅ High database confidence: {db_confidence:.2f}")
            return {
                "source": "database",
                "confidence": db_confidence,
                "reason": f"Strong indicators of database query (DB: {db_score:.1f} vs Docs: {doc_score:.1f})",
                "is_followup": is_followup
            }
        elif doc_confidence > CONFIDENCE_THRESHOLD:
            logger.info(f"✅ High documentation confidence: {doc_confidence:.2f}")
            return {
                "source": "documents",
                "confidence": doc_confidence,
                "reason": f"Strong indicators of documentation query (Docs: {doc_score:.1f} vs DB: {db_score:.1f})",
                "is_followup": is_followup
            }
        else:
            # Close scores, try both
            logger.info(f"⚠️ Mixed confidence, will try both sources")
            return {
                "source": "both",
                "confidence": max(db_confidence, doc_confidence),
                "reason": f"Mixed indicators (DB: {db_score:.1f}, Docs: {doc_score:.1f})",
                "is_followup": is_followup
            }
    
    def _score_patterns(self, query: str, patterns: List) -> float:
        """Score how well query matches a list of patterns"""
        score = 0.0
        for pattern in patterns:
            matches = pattern.findall(query)
            if matches:
                score += len(matches)
        return score
    
    def _is_followup(self, query: str) -> bool:
        """Check if query is a follow-up to previous conversation"""
        for pattern in self.followup_regex:
            if pattern.search(query):
                return True
        return False


# Singleton instance
_source_intelligence_instance = None

def get_source_intelligence() -> SourceIntelligence:
    """Get singleton instance of SourceIntelligence"""
    global _source_intelligence_instance
    if _source_intelligence_instance is None:
        _source_intelligence_instance = SourceIntelligence()
    return _source_intelligence_instance



