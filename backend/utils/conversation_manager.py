"""
Conversation Manager - Handles multi-turn conversations with context
Maintains session state and conversation history
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ConversationManager:
    """
    Manages conversation sessions and context
    Provides context-aware responses by remembering previous messages
    """
    
    def __init__(self, db_manager=None):
        """Initialize conversation manager"""
        self.db_manager = db_manager
        self.default_session_duration = timedelta(hours=2)  # 2 hour sessions
        self.max_context_messages = 5  # Remember last 5 messages
    
    def create_session(self, tenant_id: str, user_id: str = None) -> str:
        """
        Create a new conversation session
        
        Args:
            tenant_id: Tenant identifier
            user_id: Optional user identifier
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + self.default_session_duration
        
        if self.db_manager:
            try:
                with self.db_manager.get_connection() as conn:
                    conn.execute(
                        """INSERT INTO conversations 
                           (session_id, tenant_id, user_id, status, expires_at)
                           VALUES (%s, %s, %s, 'active', %s)""",
                        (session_id, tenant_id, user_id, expires_at)
                    )
                    conn.commit()
                print(f"✅ Created session: {session_id}")
            except Exception as e:
                print(f"❌ Error creating session: {e}")
                return None
        
        return session_id
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve (default: max_context_messages)
        
        Returns:
            List of messages in chronological order
        """
        if limit is None:
            limit = self.max_context_messages
        
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Get conversation_id from session_id
                cursor = conn.execute(
                    "SELECT id FROM conversations WHERE session_id = %s AND status = 'active'",
                    (session_id,)
                )
                conversation = cursor.fetchone()
                
                if not conversation:
                    print(f"⚠️  Session not found: {session_id}")
                    return []
                
                conversation_id = conversation['id']
                
                # Get recent messages
                cursor = conn.execute(
                    """SELECT query, response, created_at, message_order
                       FROM chat_interactions
                       WHERE conversation_id = %s
                       ORDER BY message_order DESC
                       LIMIT %s""",
                    (conversation_id, limit)
                )
                messages = cursor.fetchall()
                
                # Reverse to get chronological order
                messages.reverse()
                
                # Parse and include extracted context if available
                result = []
                for msg in messages:
                    msg_data = {
                        'query': msg['query'],
                        'response': msg['response'],
                        'timestamp': str(msg['created_at'])
                    }
                    
                    # Try to extract main_topic from context_used JSON
                    if msg.get('context_used'):
                        try:
                            import json
                            context_data = json.loads(msg['context_used']) if isinstance(msg['context_used'], str) else msg['context_used']
                            if isinstance(context_data, list) and len(context_data) > 0:
                                # Last item might have main_topic
                                last_context = context_data[-1]
                                if isinstance(last_context, dict) and 'main_topic' in last_context:
                                    msg_data['main_topic'] = last_context['main_topic']
                        except:
                            pass
                    
                    result.append(msg_data)
                
                return result
        
        except Exception as e:
            print(f"❌ Error getting conversation history: {e}")
            return []
    
    def save_message(self, session_id: str, query: str, response: str, 
                    module: str = None, response_time: float = None,
                    context_used: List[Dict] = None) -> bool:
        """
        Save a message to conversation history
        
        Args:
            session_id: Session identifier
            query: User query
            response: Bot response
            module: Deprecated - kept for compatibility
            response_time: Response generation time
            context_used: Previous messages used as context
        
        Returns:
            Success status
        """
        if not self.db_manager:
            return False
        
        try:
            with self.db_manager.get_connection() as conn:
                # Get conversation_id and tenant_id
                cursor = conn.execute(
                    """SELECT id, tenant_id FROM conversations 
                       WHERE session_id = %s AND status = 'active'""",
                    (session_id,)
                )
                conversation = cursor.fetchone()
                
                if not conversation:
                    print(f"⚠️  Session not found or expired: {session_id}")
                    return False
                
                conversation_id = conversation['id']
                tenant_id = conversation['tenant_id']
                
                # Get next message order
                cursor = conn.execute(
                    """SELECT COALESCE(MAX(message_order), -1) + 1 as next_order
                       FROM chat_interactions
                       WHERE conversation_id = %s""",
                    (conversation_id,)
                )
                result = cursor.fetchone()
                message_order = result['next_order']
                
                # Convert context to JSON string
                import json
                context_json = json.dumps(context_used) if context_used else None
                
                # Save message (module field kept for DB compatibility but always null)
                conn.execute(
                    """INSERT INTO chat_interactions
                       (conversation_id, tenant_id, query, response, 
                        response_time, message_order, context_used)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (conversation_id, tenant_id, query, response, 
                     response_time, message_order, context_json)
                )
                
                # Update conversation timestamp and title (first message)
                if message_order == 0:
                    # Use first query as title (truncated)
                    title = query[:100] if len(query) <= 100 else query[:97] + "..."
                    conn.execute(
                        """UPDATE conversations 
                           SET title = %s, updated_at = NOW()
                           WHERE id = %s""",
                        (title, conversation_id)
                    )
                else:
                    # Just update timestamp
                    conn.execute(
                        """UPDATE conversations 
                           SET updated_at = NOW()
                           WHERE id = %s""",
                        (conversation_id,)
                    )
                
                conn.commit()
                return True
        
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return False
    
    def build_context_prompt(self, session_id: str, current_query: str) -> str:
        """
        Build context-aware prompt including conversation history
        
        Args:
            session_id: Session identifier
            current_query: Current user query
        
        Returns:
            Enhanced query with conversation context
        """
        history = self.get_conversation_history(session_id)
        
        if not history:
            return current_query
        
        # Build context string
        context_parts = ["Previous conversation:"]
        
        for i, msg in enumerate(history, 1):
            context_parts.append(f"\nUser: {msg['query']}")
            context_parts.append(f"Assistant: {msg['response'][:200]}...")  # Truncate responses
        
        context_parts.append(f"\n\nCurrent question: {current_query}")
        
        return "\n".join(context_parts)
    
    def get_context_summary(self, session_id: str, current_query: str = "") -> str:
        """
        Get a concise summary of conversation context (AI-POWERED, GENERIC)
        Works for ANY conversation topic using AI to understand context
        
        Args:
            session_id: Session identifier
            current_query: Current user query (to resolve references)
        
        Returns:
            Context summary string with key topics/entities
        """
        history = self.get_conversation_history(session_id, limit=2)  # Last 2 messages
        
        if not history:
            return ""
        
        try:
            # Use AI-powered context extractor (generic, works for any topic)
            from utils.context_extractor import get_context_extractor
            
            extractor = get_context_extractor()
            
            # If current query has pronouns, resolve them
            resolved_entity = extractor.resolve_reference(current_query, history)
            
            if resolved_entity:
                # We know exactly what the user is referring to
                return resolved_entity
            
            # No pronoun - check if query is very short (likely continuation)
            if current_query and len(current_query.split()) <= 3:
                # Short query - add context from previous conversation
                last_msg = history[-1]
                
                # Try to get main_topic from last message metadata
                if 'main_topic' in last_msg and last_msg['main_topic']:
                    return last_msg['main_topic']
                
                # Fallback: Extract from last response
                last_query = last_msg['query']
                last_response = last_msg['response']
                
                # Use simple extraction
                context = extractor._simple_extraction(last_query, last_response, last_msg.get('module'))
                return context.get('main_topic', '')
            
            # Query is long enough - likely doesn't need context
            return ""
            
        except Exception as e:
            print(f"⚠️  Error getting context summary: {e}")
            return ""
    
    def check_session_valid(self, session_id: str) -> bool:
        """
        Check if session is still valid
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if valid, False otherwise
        """
        if not self.db_manager:
            return True  # Assume valid if no DB
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT status, expires_at FROM conversations
                       WHERE session_id = %s""",
                    (session_id,)
                )
                conversation = cursor.fetchone()
                
                if not conversation:
                    return False
                
                # Check status
                if conversation['status'] != 'active':
                    return False
                
                # Check expiry
                if conversation['expires_at']:
                    if datetime.now() > conversation['expires_at']:
                        # Mark as expired
                        conn.execute(
                            "UPDATE conversations SET status = 'expired' WHERE session_id = %s",
                            (session_id,)
                        )
                        conn.commit()
                        return False
                
                return True
        
        except Exception as e:
            print(f"❌ Error checking session: {e}")
            return False
    
    def extend_session(self, session_id: str, hours: int = 2) -> bool:
        """
        Extend session expiry time
        
        Args:
            session_id: Session identifier
            hours: Hours to extend
        
        Returns:
            Success status
        """
        if not self.db_manager:
            return True
        
        try:
            with self.db_manager.get_connection() as conn:
                new_expiry = datetime.now() + timedelta(hours=hours)
                conn.execute(
                    """UPDATE conversations 
                       SET expires_at = %s, updated_at = NOW()
                       WHERE session_id = %s AND status = 'active'""",
                    (new_expiry, session_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error extending session: {e}")
            return False
    
    def end_session(self, session_id: str) -> bool:
        """
        End a conversation session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Success status
        """
        if not self.db_manager:
            return True
        
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(
                    """UPDATE conversations 
                       SET status = 'archived', updated_at = NOW()
                       WHERE session_id = %s""",
                    (session_id,)
                )
                conn.commit()
                print(f"✅ Session ended: {session_id}")
                return True
        except Exception as e:
            print(f"❌ Error ending session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (background task)
        
        Returns:
            Number of sessions cleaned up
        """
        if not self.db_manager:
            return 0
        
        try:
            with self.db_manager.get_connection() as conn:
                # Mark expired sessions
                conn.execute(
                    """UPDATE conversations 
                       SET status = 'expired'
                       WHERE status = 'active' 
                       AND expires_at < NOW()"""
                )
                conn.commit()
                
                # Could also delete very old sessions here if needed
                # For now, just mark as expired
                
                return 0
        except Exception as e:
            print(f"❌ Error cleaning up sessions: {e}")
            return 0


# Singleton instance
conversation_manager = None

def get_conversation_manager():
    """Get or create conversation manager instance"""
    global conversation_manager
    
    if conversation_manager is None:
        try:
            from database.db_manager import db_manager
            conversation_manager = ConversationManager(db_manager)
        except ImportError:
            print("⚠️  Database not available, conversation manager disabled")
            conversation_manager = ConversationManager(None)
    
    return conversation_manager

