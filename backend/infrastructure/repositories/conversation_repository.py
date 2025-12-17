"""
Conversation Repository
Handles persistence of conversations and messages
"""

import logging
import json
from typing import List, Optional
from datetime import datetime
from core.interfaces.repository import IRepository
from core.interfaces.database import IDatabaseConnection
from core.models.conversation import Conversation, Message, MessageRole

logger = logging.getLogger(__name__)


class ConversationRepository(IRepository[Conversation]):
    """
    Repository for conversation persistence
    
    Following Repository Pattern:
    - Abstracts data access for conversations
    - Maps between domain models and database
    
    Following SOLID:
    - SRP: Single responsibility - conversation data access
    - DIP: Depends on IDatabaseConnection interface
    """
    
    def __init__(self, db: IDatabaseConnection):
        """
        Initialize conversation repository
        
        Args:
            db: Database connection (system database)
        """
        self._db = db
        logger.info("Conversation Repository initialized")
    
    async def get_by_id(self, session_id: str) -> Optional[Conversation]:
        """
        Get conversation by session ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation if found, None otherwise
        """
        try:
            # Get conversation metadata
            query = """
                SELECT session_id, tenant_id, user_id, created_at, updated_at, is_active
                FROM conversations
                WHERE session_id = %s
            """
            results = await self._db.execute_query(query, (session_id,))
            
            if not results:
                return None
            
            conv_data = results[0]
            
            # Get messages
            messages_query = """
                SELECT role, content, created_at, metadata
                FROM conversation_messages
                WHERE session_id = %s
                ORDER BY created_at ASC
            """
            message_results = await self._db.execute_query(messages_query, (session_id,))
            
            # Build conversation
            messages = []
            for msg_data in message_results:
                messages.append(Message(
                    role=MessageRole(msg_data['role']),
                    content=msg_data['content'],
                    created_at=msg_data['created_at'],
                    metadata=json.loads(msg_data['metadata']) if msg_data.get('metadata') else {}
                ))
            
            conversation = Conversation(
                session_id=conv_data['session_id'],
                tenant_id=conv_data['tenant_id'],
                user_id=conv_data.get('user_id'),
                messages=messages,
                created_at=conv_data['created_at'],
                updated_at=conv_data['updated_at'],
                is_active=bool(conv_data['is_active'])
            )
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation {session_id}: {e}")
            return None
    
    async def get_all(
        self,
        filter: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get all conversations matching filter
        
        Args:
            filter: Optional filter (e.g., {"tenant_id": "x", "user_id": "y"})
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of conversations
        """
        try:
            query = "SELECT session_id FROM conversations WHERE 1=1"
            params = []
            
            if filter:
                if 'tenant_id' in filter:
                    query += " AND tenant_id = %s"
                    params.append(filter['tenant_id'])
                if 'user_id' in filter:
                    query += " AND user_id = %s"
                    params.append(filter['user_id'])
                if 'is_active' in filter:
                    query += " AND is_active = %s"
                    params.append(filter['is_active'])
            
            query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            results = await self._db.execute_query(query, tuple(params))
            
            # Get full conversation for each session_id
            conversations = []
            for row in results:
                conv = await self.get_by_id(row['session_id'])
                if conv:
                    conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    async def add(self, conversation: Conversation) -> Conversation:
        """
        Add new conversation
        
        Args:
            conversation: Conversation to add
            
        Returns:
            Added conversation
        """
        try:
            # Insert conversation metadata
            query = """
                INSERT INTO conversations
                (session_id, tenant_id, user_id, created_at, updated_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            await self._db.execute_non_query(
                query,
                (
                    conversation.session_id,
                    conversation.tenant_id,
                    conversation.user_id,
                    conversation.created_at,
                    conversation.updated_at,
                    conversation.is_active
                )
            )
            
            # Insert messages
            for message in conversation.messages:
                await self._add_message(conversation.session_id, message)
            
            logger.info(f"Added conversation {conversation.session_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error adding conversation: {e}")
            raise
    
    async def update(self, conversation: Conversation) -> bool:
        """
        Update existing conversation
        
        Args:
            conversation: Conversation to update
            
        Returns:
            True if successful
        """
        try:
            # Update conversation metadata
            query = """
                UPDATE conversations
                SET updated_at = %s, is_active = %s
                WHERE session_id = %s
            """
            await self._db.execute_non_query(
                query,
                (conversation.updated_at, conversation.is_active, conversation.session_id)
            )
            
            logger.info(f"Updated conversation {conversation.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            return False
    
    async def delete(self, session_id: str) -> bool:
        """
        Delete conversation
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            # Delete messages first
            await self._db.execute_non_query(
                "DELETE FROM conversation_messages WHERE session_id = %s",
                (session_id,)
            )
            
            # Delete conversation
            await self._db.execute_non_query(
                "DELETE FROM conversations WHERE session_id = %s",
                (session_id,)
            )
            
            logger.info(f"Deleted conversation {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    async def exists(self, session_id: str) -> bool:
        """
        Check if conversation exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if exists
        """
        try:
            query = "SELECT COUNT(*) as count FROM conversations WHERE session_id = %s"
            results = await self._db.execute_query(query, (session_id,))
            return results[0]['count'] > 0 if results else False
        except:
            return False
    
    async def add_message(self, session_id: str, message: Message) -> bool:
        """
        Add message to existing conversation
        
        Args:
            session_id: Session identifier
            message: Message to add
            
        Returns:
            True if successful
        """
        try:
            return await self._add_message(session_id, message)
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False
    
    async def _add_message(self, session_id: str, message: Message) -> bool:
        """Internal method to add message"""
        query = """
            INSERT INTO conversation_messages
            (session_id, role, content, created_at, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """
        await self._db.execute_non_query(
            query,
            (
                session_id,
                message.role.value,
                message.content,
                message.created_at,
                json.dumps(message.metadata) if message.metadata else '{}'
            )
        )
        return True
    
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Message]:
        """
        Get recent messages from conversation
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
            
        Returns:
            List of recent messages
        """
        try:
            query = """
                SELECT role, content, created_at, metadata
                FROM conversation_messages
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            results = await self._db.execute_query(query, (session_id, limit))
            
            messages = []
            for msg_data in reversed(results):  # Reverse to get chronological order
                messages.append(Message(
                    role=MessageRole(msg_data['role']),
                    content=msg_data['content'],
                    created_at=msg_data['created_at'],
                    metadata=json.loads(msg_data['metadata']) if msg_data.get('metadata') else {}
                ))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []

