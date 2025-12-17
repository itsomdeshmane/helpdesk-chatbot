"""
Metadata Repository
Handles persistence of metadata (keywords, FAQs, entities, etc.)
"""

import logging
from typing import List, Optional, Dict, Any
from core.interfaces.repository import IRepository
from core.interfaces.database import IDatabaseConnection

logger = logging.getLogger(__name__)


class MetadataRepository(IRepository[Dict[str, Any]]):
    """
    Repository for metadata persistence
    
    Handles:
    - Keywords
    - FAQs
    - Entities
    - Column metadata
    - Query patterns
    
    Following SOLID:
    - SRP: Single responsibility - metadata data access
    - DIP: Depends on IDatabaseConnection interface
    """
    
    def __init__(self, db: IDatabaseConnection):
        """
        Initialize metadata repository
        
        Args:
            db: Database connection (system database)
        """
        self._db = db
        logger.info("Metadata Repository initialized")
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata by ID
        
        Args:
            id: Metadata identifier
            
        Returns:
            Metadata if found
        """
        # Generic implementation - override for specific metadata types
        return None
    
    async def get_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all metadata matching filter"""
        return []
    
    async def add(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Add new metadata"""
        return entity
    
    async def update(self, entity: Dict[str, Any]) -> bool:
        """Update existing metadata"""
        return False
    
    async def delete(self, id: str) -> bool:
        """Delete metadata"""
        return False
    
    async def exists(self, id: str) -> bool:
        """Check if metadata exists"""
        return False
    
    # Specific methods for different metadata types
    
    async def get_keywords(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get learned keywords"""
        try:
            query = """
                SELECT keyword, category, confidence, usage_count
                FROM learned_keywords
                WHERE tenant_id = %s
                ORDER BY usage_count DESC, confidence DESC
                LIMIT %s
            """
            return await self._db.execute_query(query, (tenant_id, limit))
        except Exception as e:
            logger.error(f"Error getting keywords: {e}")
            return []
    
    async def add_keyword(self, keyword_data: Dict[str, Any]) -> bool:
        """Add learned keyword"""
        try:
            query = """
                INSERT INTO learned_keywords
                (tenant_id, keyword, category, confidence, usage_count)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                usage_count = usage_count + 1,
                confidence = %s
            """
            await self._db.execute_non_query(
                query,
                (
                    keyword_data['tenant_id'],
                    keyword_data['keyword'],
                    keyword_data.get('category'),
                    keyword_data.get('confidence', 1.0),
                    keyword_data.get('usage_count', 1),
                    keyword_data.get('confidence', 1.0)
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error adding keyword: {e}")
            return False
    
    async def get_faqs(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get FAQs"""
        try:
            query = """
                SELECT question, answer, category, popularity
                FROM faq_questions
                WHERE tenant_id = %s OR tenant_id = 'global'
                ORDER BY popularity DESC
                LIMIT %s
            """
            return await self._db.execute_query(query, (tenant_id, limit))
        except Exception as e:
            logger.error(f"Error getting FAQs: {e}")
            return []
    
    async def add_faq(self, faq_data: Dict[str, Any]) -> bool:
        """Add FAQ"""
        try:
            query = """
                INSERT INTO faq_questions
                (tenant_id, question, answer, category, popularity)
                VALUES (%s, %s, %s, %s, %s)
            """
            await self._db.execute_non_query(
                query,
                (
                    faq_data['tenant_id'],
                    faq_data['question'],
                    faq_data['answer'],
                    faq_data.get('category'),
                    faq_data.get('popularity', 0)
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error adding FAQ: {e}")
            return False
    
    async def get_entities(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get system entities"""
        try:
            query = """
                SELECT entity_key, entity_name, entity_type, description
                FROM system_entities
                WHERE is_active = TRUE
                ORDER BY priority DESC
            """
            return await self._db.execute_query(query, ())
        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []
    
    async def get_column_metadata(
        self,
        tenant_id: str,
        database_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get column metadata (descriptions, synonyms)"""
        try:
            query = """
                SELECT table_name, column_name, description, synonyms
                FROM column_metadata
                WHERE tenant_id = %s
            """
            params = [tenant_id]
            
            if database_name:
                query += " AND database_name = %s"
                params.append(database_name)
            
            return await self._db.execute_query(query, tuple(params))
        except Exception as e:
            logger.error(f"Error getting column metadata: {e}")
            return []
    
    async def save_column_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save column metadata"""
        try:
            query = """
                INSERT INTO column_metadata
                (tenant_id, database_name, table_name, column_name, description, synonyms)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                description = %s,
                synonyms = %s
            """
            await self._db.execute_non_query(
                query,
                (
                    metadata['tenant_id'],
                    metadata.get('database_name'),
                    metadata['table_name'],
                    metadata['column_name'],
                    metadata.get('description'),
                    metadata.get('synonyms'),
                    metadata.get('description'),
                    metadata.get('synonyms')
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error saving column metadata: {e}")
            return False

