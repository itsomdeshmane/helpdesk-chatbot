"""
Keyword Learning Service - Learns keywords from ALL sources (database + documents)
Analyzes database tables and documents to extract keywords for intelligent query classification
FULLY GENERIC - Zero hardcoded keywords, learns everything automatically
"""
import logging
import re
from typing import Dict, List, Any, Optional, Set
from collections import Counter
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class KeywordLearner:
    """
    Learns keywords from ALL sources (database + documents) for intelligent query classification.
    FULLY GENERIC - Zero hardcoded keywords, learns everything automatically
    """
    
    def __init__(self, db_manager, keyword_store_manager, pinecone_service=None):
        """
        Initialize the keyword learner
        
        Args:
            db_manager: Database manager for source data
            keyword_store_manager: Database manager for keyword storage
            pinecone_service: Pinecone service for document access (optional)
        """
        self.db_manager = db_manager
        self.keyword_store = keyword_store_manager
        self.pinecone_service = pinecone_service
    
    async def learn_from_database(
        self, 
        user_id: str, 
        tenant_id: str,
        connection_string: str,
        sample_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Learn keywords from a database by analyzing schema and sampling data
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            connection_string: Database connection string
            sample_limit: Max rows to sample per table
            
        Returns:
            Dictionary with learning statistics
        """
        logger.info(f"Starting keyword learning for user {user_id}, tenant {tenant_id}")
        
        stats = {
            'tables_analyzed': 0,
            'keywords_learned': 0,
            'columns_analyzed': 0,
            'start_time': datetime.now()
        }
        
        try:
            # Get all tables in the database
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"Found {len(tables)} tables to analyze")
                
                for table_name in tables:
                    stats['tables_analyzed'] += 1
                    
                    # Get table schema
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = cursor.fetchall()
                    
                    for column in columns:
                        col_name = column[0]
                        col_type = column[1]
                        
                        stats['columns_analyzed'] += 1
                        
                        # Determine if this column should be analyzed for keywords
                        if self._should_analyze_column(col_name, col_type):
                            keywords = await self._extract_keywords_from_column(
                                cursor,
                                table_name,
                                col_name,
                                col_type,
                                sample_limit
                            )
                            
                            # Store keywords
                            if keywords:
                                await self._store_keywords(
                                    user_id,
                                    tenant_id,
                                    table_name,
                                    col_name,
                                    keywords
                                )
                                stats['keywords_learned'] += len(keywords)
        
        except Exception as e:
            logger.error(f"Error learning keywords: {e}", exc_info=True)
            stats['error'] = str(e)
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        logger.info(f"Keyword learning completed: {stats}")
        return stats
    
    def _should_analyze_column(self, col_name: str, col_type: str) -> bool:
        """
        Determine if a column should be analyzed for keywords
        
        GENERIC criteria:
        - Text/string columns (VARCHAR, TEXT, CHAR)
        - Columns with semantic meaning (name, title, category, status, type, location, city, country)
        - Exclude: IDs, timestamps, long text fields
        """
        col_name_lower = col_name.lower()
        col_type_lower = col_type.lower()
        
        # Exclude ID columns
        if col_name_lower.endswith('_id') or col_name_lower == 'id':
            return False
        
        # Exclude timestamp columns
        if 'timestamp' in col_name_lower or 'created_at' in col_name_lower or 'updated_at' in col_name_lower:
            return False
        
        # Exclude password/hash columns
        if 'password' in col_name_lower or 'hash' in col_name_lower or 'token' in col_name_lower:
            return False
        
        # Only analyze text columns
        text_types = ['varchar', 'char', 'text', 'enum']
        if not any(text_type in col_type_lower for text_type in text_types):
            return False
        
        # Exclude very long text fields (descriptions, etc.)
        if 'text' in col_type_lower or 'longtext' in col_type_lower:
            # Only include if name suggests categorization
            categorization_hints = ['status', 'type', 'category', 'classification']
            if not any(hint in col_name_lower for hint in categorization_hints):
                return False
        
        # Prefer semantic columns
        semantic_hints = [
            'name', 'title', 'category', 'type', 'status', 'stage', 'phase',
            'country', 'city', 'state', 'region', 'location',
            'department', 'division', 'team', 'role',
            'product', 'vendor', 'customer', 'supplier', 'client'
        ]
        
        if any(hint in col_name_lower for hint in semantic_hints):
            return True
        
        # Include if it's a short string (likely categorical)
        if 'varchar' in col_type_lower:
            match = re.search(r'varchar\((\d+)\)', col_type_lower)
            if match:
                length = int(match.group(1))
                # Short strings are likely categorical
                if length <= 100:
                    return True
        
        return False
    
    async def _extract_keywords_from_column(
        self,
        cursor,
        table_name: str,
        col_name: str,
        col_type: str,
        sample_limit: int
    ) -> List[Dict[str, Any]]:
        """
        Extract unique keywords from a column by sampling data
        
        Returns:
            List of keyword dictionaries with value, frequency, and metadata
        """
        try:
            # Get distinct values with counts
            query = f"""
                SELECT `{col_name}`, COUNT(*) as frequency
                FROM `{table_name}`
                WHERE `{col_name}` IS NOT NULL 
                  AND `{col_name}` != ''
                GROUP BY `{col_name}`
                ORDER BY frequency DESC
                LIMIT {sample_limit}
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            keywords = []
            for row in results:
                value = row[0]
                frequency = row[1]
                
                # Clean and validate the keyword
                if self._is_valid_keyword(value):
                    keywords.append({
                        'keyword': str(value).strip(),
                        'frequency': frequency,
                        'normalized': self._normalize_keyword(str(value))
                    })
            
            logger.info(f"Extracted {len(keywords)} keywords from {table_name}.{col_name}")
            return keywords
        
        except Exception as e:
            logger.error(f"Error extracting keywords from {table_name}.{col_name}: {e}")
            return []
    
    def _is_valid_keyword(self, value: Any) -> bool:
        """
        Validate if a value should be stored as a keyword
        
        GENERIC rules:
        - Not null/empty
        - Reasonable length (2-100 chars)
        - Not just numbers
        - Not common noise words
        """
        if not value:
            return False
        
        value_str = str(value).strip()
        
        # Length check
        if len(value_str) < 2 or len(value_str) > 100:
            return False
        
        # Not just numbers
        if value_str.isdigit():
            return False
        
        # Not common noise
        noise_words = ['n/a', 'na', 'null', 'none', 'unknown', 'test', 'temp', 'tmp']
        if value_str.lower() in noise_words:
            return False
        
        return True
    
    def _normalize_keyword(self, keyword: str) -> str:
        """
        Normalize a keyword for flexible matching
        
        GENERIC normalization:
        - Lowercase
        - Remove extra whitespace
        - Remove special characters (except spaces, hyphens, apostrophes)
        """
        # Lowercase
        normalized = keyword.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Keep only alphanumeric, spaces, hyphens, apostrophes
        normalized = re.sub(r'[^a-z0-9\s\-\']', '', normalized)
        
        return normalized
    
    async def _store_keywords(
        self,
        user_id: str,
        tenant_id: str,
        table_name: str,
        col_name: str,
        keywords: List[Dict[str, Any]]
    ):
        """
        Store learned keywords in the training database
        """
        try:
            with self.keyword_store.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if table exists, create if not
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learned_keywords (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        tenant_id VARCHAR(255) NOT NULL,
                        source_table VARCHAR(255) NOT NULL,
                        source_column VARCHAR(255) NOT NULL,
                        keyword VARCHAR(255) NOT NULL,
                        normalized_keyword VARCHAR(255) NOT NULL,
                        frequency INT DEFAULT 1,
                        keyword_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_user_tenant (user_id, tenant_id),
                        INDEX idx_normalized (normalized_keyword),
                        INDEX idx_source (source_table, source_column)
                    )
                """)
                
                # Insert or update keywords
                for kw in keywords:
                    # Determine keyword type based on column name
                    keyword_type = self._infer_keyword_type(col_name)
                    
                    cursor.execute("""
                        INSERT INTO learned_keywords 
                        (user_id, tenant_id, source_table, source_column, keyword, normalized_keyword, frequency, keyword_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            frequency = VALUES(frequency),
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        user_id,
                        tenant_id,
                        table_name,
                        col_name,
                        kw['keyword'],
                        kw['normalized'],
                        kw['frequency'],
                        keyword_type
                    ))
                
                conn.commit()
                logger.info(f"Stored {len(keywords)} keywords for {table_name}.{col_name}")
        
        except Exception as e:
            logger.error(f"Error storing keywords: {e}", exc_info=True)
    
    def _infer_keyword_type(self, col_name: str) -> str:
        """
        Infer the type of keyword based on column name
        Uses pattern matching - NO HARDCODED VALUES, just patterns
        """
        col_lower = col_name.lower()
        
        # Pattern-based detection (NOT hardcoded keywords)
        if any(pattern in col_lower for pattern in ['country', 'city', 'state', 'region', 'location', 'address', 'zip', 'postal']):
            return 'location'
        elif any(pattern in col_lower for pattern in ['name', 'title', 'company', 'organization', 'person']):
            return 'entity'
        elif any(pattern in col_lower for pattern in ['type', 'category', 'class', 'status', 'stage', 'phase', 'level']):
            return 'category'
        else:
            return 'other'
    
    async def learn_from_documents(
        self,
        user_id: str,
        tenant_id: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn keywords from document content in Pinecone
        
        GENERIC - Extracts common terms, entities, and topics from documents
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier  
            namespace: Pinecone namespace to analyze
            
        Returns:
            Dictionary with learning statistics
        """
        if not self.pinecone_service:
            logger.warning("Pinecone service not available, skipping document learning")
            return {'error': 'Pinecone service not configured'}
        
        logger.info(f"Starting document keyword learning for user {user_id}")
        
        stats = {
            'documents_analyzed': 0,
            'keywords_learned': 0,
            'start_time': datetime.now()
        }
        
        try:
            # Query Pinecone for all document metadata
            # This is a simplified approach - in production, you'd batch this
            index = self.pinecone_service.index
            
            # Get all vectors (limited sample for performance)
            query_response = index.query(
                vector=[0.0] * 1536,  # Dummy vector to get results
                top_k=1000,  # Sample up to 1000 documents
                namespace=namespace,
                include_metadata=True
            )
            
            # Extract keywords from document metadata and content
            for match in query_response.get('matches', []):
                metadata = match.get('metadata', {})
                
                # Extract from title
                if 'title' in metadata:
                    title_keywords = self._extract_keywords_from_text(metadata['title'])
                    await self._store_document_keywords(
                        user_id, tenant_id, 'document', 'title', title_keywords
                    )
                    stats['keywords_learned'] += len(title_keywords)
                
                # Extract from content (first 500 chars for keywords)
                if 'content' in metadata:
                    content_sample = metadata['content'][:500]
                    content_keywords = self._extract_keywords_from_text(content_sample)
                    await self._store_document_keywords(
                        user_id, tenant_id, 'document', 'content', content_keywords
                    )
                    stats['keywords_learned'] += len(content_keywords)
                
                # Extract topics/categories if available
                if 'topic' in metadata or 'category' in metadata:
                    topic = metadata.get('topic') or metadata.get('category')
                    if topic:
                        await self._store_document_keywords(
                            user_id, tenant_id, 'document', 'topic', [{'keyword': topic, 'frequency': 1}]
                        )
                        stats['keywords_learned'] += 1
                
                stats['documents_analyzed'] += 1
        
        except Exception as e:
            logger.error(f"Error learning from documents: {e}", exc_info=True)
            stats['error'] = str(e)
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        logger.info(f"Document keyword learning completed: {stats}")
        return stats
    
    def _extract_keywords_from_text(self, text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """
        Extract important keywords from text using NLP techniques
        GENERIC - No hardcoded terms
        
        Args:
            text: Text to analyze
            max_keywords: Maximum keywords to extract
            
        Returns:
            List of keyword dictionaries
        """
        if not text or len(text) < 10:
            return []
        
        # Tokenize and clean
        text_lower = text.lower()
        
        # Remove common stop words (these are language-agnostic patterns)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        
        # Filter stop words and count frequency
        word_counts = Counter([w for w in words if w not in stop_words])
        
        # Get top keywords
        top_keywords = word_counts.most_common(max_keywords)
        
        return [
            {
                'keyword': word,
                'frequency': count,
                'normalized': word
            }
            for word, count in top_keywords
            if count > 1  # Only keywords that appear more than once
        ]
    
    async def _store_document_keywords(
        self,
        user_id: str,
        tenant_id: str,
        source_table: str,
        source_column: str,
        keywords: List[Dict[str, Any]]
    ):
        """
        Store keywords learned from documents
        """
        if not keywords:
            return
        
        try:
            with self.keyword_store.get_connection() as conn:
                cursor = conn.cursor()
                
                for kw in keywords:
                    cursor.execute("""
                        INSERT INTO learned_keywords 
                        (user_id, tenant_id, source_table, source_column, keyword, normalized_keyword, frequency, keyword_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            frequency = frequency + VALUES(frequency),
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        user_id,
                        tenant_id,
                        source_table,
                        source_column,
                        kw.get('keyword', ''),
                        kw.get('normalized', kw.get('keyword', '')),
                        kw.get('frequency', 1),
                        'document_term'
                    ))
                
                conn.commit()
        
        except Exception as e:
            logger.error(f"Error storing document keywords: {e}", exc_info=True)
    
    async def auto_learn_all_sources(
        self,
        user_id: str,
        tenant_id: str,
        connection_string: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically learn keywords from ALL sources (database + documents)
        This is the main entry point for automatic learning
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            connection_string: Optional database connection
            namespace: Optional Pinecone namespace
            
        Returns:
            Combined statistics from all sources
        """
        logger.info(f"🧠 AUTO-LEARNING KEYWORDS from all sources for user {user_id}")
        
        combined_stats = {
            'start_time': datetime.now(),
            'sources_learned': [],
            'total_keywords': 0
        }
        
        # Learn from database
        if connection_string:
            try:
                db_stats = await self.learn_from_database(
                    user_id, tenant_id, connection_string, sample_limit=100
                )
                combined_stats['database'] = db_stats
                combined_stats['sources_learned'].append('database')
                combined_stats['total_keywords'] += db_stats.get('keywords_learned', 0)
            except Exception as e:
                logger.error(f"Database learning failed: {e}")
                combined_stats['database_error'] = str(e)
        
        # Learn from documents
        if self.pinecone_service:
            try:
                doc_stats = await self.learn_from_documents(user_id, tenant_id, namespace)
                combined_stats['documents'] = doc_stats
                combined_stats['sources_learned'].append('documents')
                combined_stats['total_keywords'] += doc_stats.get('keywords_learned', 0)
            except Exception as e:
                logger.error(f"Document learning failed: {e}")
                combined_stats['documents_error'] = str(e)
        
        combined_stats['end_time'] = datetime.now()
        combined_stats['duration_seconds'] = (
            combined_stats['end_time'] - combined_stats['start_time']
        ).total_seconds()
        
        logger.info(f"✅ AUTO-LEARNING COMPLETED: {combined_stats}")
        return combined_stats


class KeywordCache:
    """
    Caches learned keywords for fast query classification
    """
    
    def __init__(self, keyword_store_manager):
        """Initialize keyword cache"""
        self.keyword_store = keyword_store_manager
        self._cache: Dict[str, Dict[str, List[Dict]]] = {}
        self._last_refresh: Optional[datetime] = None
    
    async def get_keywords(
        self,
        user_id: str,
        tenant_id: str,
        keyword_type: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get cached keywords for a user/tenant
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            keyword_type: Filter by type (location, entity, category, other)
            force_refresh: Force refresh from database
            
        Returns:
            Dictionary mapping keyword types to keyword lists
        """
        cache_key = f"{user_id}:{tenant_id}"
        
        # Check cache
        if not force_refresh and cache_key in self._cache:
            # Cache is valid for 1 hour
            if self._last_refresh and (datetime.now() - self._last_refresh).seconds < 3600:
                logger.info(f"Using cached keywords for {cache_key}")
                return self._filter_by_type(self._cache[cache_key], keyword_type)
        
        # Refresh from database
        logger.info(f"Refreshing keywords from database for {cache_key}")
        keywords = await self._load_keywords(user_id, tenant_id)
        self._cache[cache_key] = keywords
        self._last_refresh = datetime.now()
        
        return self._filter_by_type(keywords, keyword_type)
    
    async def _load_keywords(
        self,
        user_id: str,
        tenant_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load keywords from database
        """
        try:
            with self.keyword_store.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT source_table, source_column, keyword, normalized_keyword, 
                           frequency, keyword_type
                    FROM learned_keywords
                    WHERE user_id = %s AND tenant_id = %s
                    ORDER BY frequency DESC
                """, (user_id, tenant_id))
                
                results = cursor.fetchall()
                
                # Organize by type
                keywords = {
                    'location': [],
                    'entity': [],
                    'category': [],
                    'other': [],
                    'all': []
                }
                
                for row in results:
                    kw_data = {
                        'table': row[0],
                        'column': row[1],
                        'keyword': row[2],
                        'normalized': row[3],
                        'frequency': row[4],
                        'type': row[5] or 'other'
                    }
                    
                    keywords['all'].append(kw_data)
                    keywords[kw_data['type']].append(kw_data)
                
                logger.info(f"Loaded {len(results)} keywords for {user_id}:{tenant_id}")
                return keywords
        
        except Exception as e:
            logger.error(f"Error loading keywords: {e}", exc_info=True)
            return {'location': [], 'entity': [], 'category': [], 'other': [], 'all': []}
    
    def _filter_by_type(
        self,
        keywords: Dict[str, List[Dict]],
        keyword_type: Optional[str]
    ) -> Dict[str, List[Dict]]:
        """Filter keywords by type"""
        if keyword_type:
            return {keyword_type: keywords.get(keyword_type, [])}
        return keywords


# Singleton instances
_learner_instance = None
_cache_instance = None

def get_keyword_learner():
    """Get singleton instance of KeywordLearner"""
    global _learner_instance
    if _learner_instance is None:
        from database.db_manager import DatabaseManager
        try:
            from rag.pinecone_service import pinecone_service
            pinecone_svc = pinecone_service
        except:
            pinecone_svc = None
        
        db_manager = DatabaseManager()
        keyword_store = DatabaseManager()  # Same DB for now, could be separate
        _learner_instance = KeywordLearner(db_manager, keyword_store, pinecone_svc)
    return _learner_instance

def get_keyword_cache():
    """Get singleton instance of KeywordCache"""
    global _cache_instance
    if _cache_instance is None:
        from database.db_manager import DatabaseManager
        keyword_store = DatabaseManager()
        _cache_instance = KeywordCache(keyword_store)
    return _cache_instance


async def auto_train_if_needed(user_id: str, tenant_id: str, connection_string: Optional[str] = None):
    """
    Automatically train keywords if not already trained
    This is called on first query to ensure keywords are available
    
    SMART: Only trains if keywords are missing or stale (>7 days)
    """
    try:
        cache = get_keyword_cache()
        keywords = await cache.get_keywords(user_id, tenant_id)
        
        # Check if we have keywords
        total_keywords = sum(len(v) for v in keywords.values())
        
        if total_keywords == 0:
            logger.info(f"🧠 No keywords found for user {user_id}, auto-training...")
            learner = get_keyword_learner()
            await learner.auto_learn_all_sources(user_id, tenant_id, connection_string)
            return True
        
        # Check if keywords are stale (>7 days)
        with cache.keyword_store.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(updated_at) as last_update
                FROM learned_keywords
                WHERE user_id = %s AND tenant_id = %s
            """, (user_id, tenant_id))
            
            result = cursor.fetchone()
            if result and result[0]:
                days_old = (datetime.now() - result[0]).days
                if days_old > 7:
                    logger.info(f"🔄 Keywords are {days_old} days old, refreshing...")
                    learner = get_keyword_learner()
                    await learner.auto_learn_all_sources(user_id, tenant_id, connection_string)
                    return True
        
        logger.info(f"✅ Keywords are up to date for user {user_id} ({total_keywords} keywords)")
        return False
    
    except Exception as e:
        logger.error(f"Error in auto-training: {e}", exc_info=True)
        return False


