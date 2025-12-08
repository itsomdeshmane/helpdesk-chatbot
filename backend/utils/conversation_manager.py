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
    
    def get_conversation_history(self, session_id: str, limit: int = None, user_id: str = None) -> List[Dict]:
        """
        Get conversation history for a session (USER-SPECIFIC - SECURITY CHECK)
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve (default: max_context_messages)
            user_id: Optional user_id for security validation
        
        Returns:
            List of messages in chronological order
        """
        if limit is None:
            limit = self.max_context_messages
        
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Get conversation_id from session_id with SECURITY CHECK
                # If user_id provided, ensure session belongs to that user
                if user_id:
                    cursor = conn.execute(
                        """SELECT id, user_id FROM conversations 
                           WHERE session_id = %s AND status = 'active'""",
                        (session_id,)
                    )
                    conversation = cursor.fetchone()
                    
                    if not conversation:
                        print(f"⚠️  Session not found: {session_id}")
                        return []
                    
                    # SECURITY CHECK: Verify session belongs to user
                    if conversation['user_id'] != user_id:
                        print(f"🚨 SECURITY: User {user_id} tried to access session belonging to {conversation['user_id']}")
                        return []  # Deny access to other user's session
                    
                    conversation_id = conversation['id']
                else:
                    # No user_id provided (backward compatibility)
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
                        'query': msg.get('query', ''),
                        'response': msg.get('response', ''),
                        'timestamp': str(msg.get('created_at', ''))
                    }
                    
                    # Try to extract main_topic from context_used JSON (NEW FEATURE - optional)
                    if msg.get('context_used'):
                        try:
                            import json
                            context_data = json.loads(msg['context_used']) if isinstance(msg['context_used'], str) else msg['context_used']
                            if isinstance(context_data, list) and len(context_data) > 0:
                                # Last item might have main_topic
                                last_context = context_data[-1]
                                if isinstance(last_context, dict) and 'main_topic' in last_context:
                                    msg_data['main_topic'] = last_context['main_topic']
                        except Exception as e:
                            # Silently fail - this is optional context enhancement
                            pass
                    
                    result.append(msg_data)
                
                return result
        
        except Exception as e:
            print(f"❌ Error getting conversation history: {e}")
            return []
    
    def save_message(self, session_id: str, query: str, response: str, 
                    module: str = None, response_time: float = None,
                    context_used: List[Dict] = None, main_topic: str = None) -> bool:
        """
        Save a message to conversation history
        
        Args:
            session_id: Session identifier
            query: User query
            response: Bot response
            module: Deprecated - kept for compatibility
            response_time: Response generation time
            context_used: Previous messages used as context
            main_topic: Main topic extracted from the conversation
        
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
                
                # Convert context to JSON string and add main_topic for next turn (NEW FEATURE - optional)
                import json
                context_json = None
                try:
                    if context_used is not None:
                        # Add main_topic to the context for the next message to use
                        context_with_topic = context_used.copy() if isinstance(context_used, list) else []
                        if main_topic:
                            context_with_topic.append({'main_topic': main_topic})
                        context_json = json.dumps(context_with_topic)
                    elif main_topic:
                        # First message in conversation - save just the topic
                        context_json = json.dumps([{'main_topic': main_topic}])
                    else:
                        # Fallback: Save original context_used as-is (backward compatible)
                        context_json = json.dumps(context_used) if context_used else None
                except Exception as e:
                    # If anything fails, fall back to saving original context (backward compatible)
                    print(f"   ⚠️  Context serialization error (using fallback): {e}", flush=True)
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
        history = self.get_conversation_history(session_id, limit=3)  # Last 3 messages
        
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
                print(f"   🔗 Resolved pronoun reference: '{resolved_entity}'", flush=True)
                return resolved_entity
            
            # No pronoun - check if query is very short (likely continuation)
            if current_query and len(current_query.split()) <= 3:
                # Short query - likely a follow-up about the same topic
                print(f"   🔍 Short query detected, looking for context...", flush=True)
                
                # Try to get main_topic from recent messages (newest first)
                for msg in reversed(history):
                    if 'main_topic' in msg and msg['main_topic']:
                        print(f"   ✅ Found context topic: '{msg['main_topic']}'", flush=True)
                        return msg['main_topic']
                
                # Fallback: Extract from last response using AI
                print(f"   🤖 Extracting context from last message...", flush=True)
                last_msg = history[-1]
                last_query = last_msg['query']
                last_response = last_msg['response']
                
                # Use AI extraction
                context = extractor.extract_context(last_query, last_response)
                topic = context.get('main_topic', '')
                if topic:
                    print(f"   ✅ Extracted context: '{topic}'", flush=True)
                    return topic
            
            # Check for follow-up indicators even in longer queries
            follow_up_words = ['explain', 'more', 'detail', 'how', 'why', 'when', 'where']
            query_lower = current_query.lower()
            if any(word in query_lower for word in follow_up_words) and len(current_query.split()) <= 5:
                # Looks like a follow-up question
                for msg in reversed(history):
                    if 'main_topic' in msg and msg['main_topic']:
                        print(f"   🔗 Follow-up detected, using context: '{msg['main_topic']}'", flush=True)
                        return msg['main_topic']
            
            # Query is long enough or doesn't need context
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
        End a conversation session (archive it)
        
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
    
    def soft_delete_conversation(self, session_id: str, retention_days: int = 90) -> bool:
        """
        Soft delete a conversation (SOFT DELETE - keeps data for learning)
        Hidden from user's view but kept for analytics and system improvement
        
        Args:
            session_id: Session identifier
            retention_days: Days to keep before permanent deletion (default: 90 for GDPR compliance)
        
        Returns:
            Success status
        """
        if not self.db_manager:
            return True
        
        try:
            with self.db_manager.get_connection() as conn:
                from datetime import datetime, timedelta
                permanent_delete_date = datetime.now() + timedelta(days=retention_days)
                
                conn.execute(
                    """UPDATE conversations 
                       SET deleted_by_user = TRUE,
                           deleted_at = NOW(),
                           permanent_delete_after = %s,
                           updated_at = NOW()
                       WHERE session_id = %s""",
                    (permanent_delete_date, session_id)
                )
                conn.commit()
                print(f"✅ Conversation soft-deleted: {session_id} (permanent delete after {retention_days} days)")
                return True
        except Exception as e:
            print(f"❌ Error soft-deleting conversation: {e}")
            return False
    
    def restore_conversation(self, session_id: str) -> bool:
        """
        Restore a soft-deleted conversation
        
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
                       SET deleted_by_user = FALSE,
                           deleted_at = NULL,
                           permanent_delete_after = NULL,
                           updated_at = NOW()
                       WHERE session_id = %s""",
                    (session_id,)
                )
                conn.commit()
                print(f"✅ Conversation restored: {session_id}")
                return True
        except Exception as e:
            print(f"❌ Error restoring conversation: {e}")
            return False
    
    def permanently_delete_old_conversations(self, tenant_id: str = None) -> int:
        """
        Permanently delete conversations past their retention period (HARD DELETE)
        Run this as a background job for GDPR compliance
        
        Args:
            tenant_id: Optional tenant identifier to limit deletion
        
        Returns:
            Number of conversations permanently deleted
        """
        if not self.db_manager:
            return 0
        
        try:
            with self.db_manager.get_connection() as conn:
                if tenant_id:
                    cursor = conn.execute(
                        """DELETE FROM conversations
                           WHERE deleted_by_user = TRUE
                           AND permanent_delete_after IS NOT NULL
                           AND permanent_delete_after < NOW()
                           AND tenant_id = %s""",
                        (tenant_id,)
                    )
                else:
                    cursor = conn.execute(
                        """DELETE FROM conversations
                           WHERE deleted_by_user = TRUE
                           AND permanent_delete_after IS NOT NULL
                           AND permanent_delete_after < NOW()"""
                    )
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    print(f"🗑️  Permanently deleted {deleted_count} conversations past retention period")
                
                return deleted_count
        except Exception as e:
            print(f"❌ Error permanently deleting conversations: {e}")
            return 0
    
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
    
    # ========== USER-SPECIFIC CONVERSATION METHODS ==========
    
    def get_user_conversations(self, tenant_id: str, user_id: str, limit: int = 20, include_deleted: bool = False) -> List[Dict]:
        """
        Get all conversations for a specific user (USER-SPECIFIC)
        By default, EXCLUDES soft-deleted conversations (clean user view)
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            limit: Maximum conversations to return
            include_deleted: If True, includes soft-deleted conversations (default: False)
        
        Returns:
            List of conversations with metadata
        """
        if not self.db_manager or not user_id:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Filter out soft-deleted conversations unless explicitly requested
                deleted_filter = "" if include_deleted else "AND (deleted_by_user IS NULL OR deleted_by_user = FALSE)"
                
                query = f"""SELECT session_id, title, status, created_at, updated_at,
                              deleted_by_user, deleted_at,
                              (SELECT COUNT(*) FROM chat_interactions 
                               WHERE conversation_id = conversations.id) as message_count
                       FROM conversations
                       WHERE tenant_id = %s AND user_id = %s
                       {deleted_filter}
                       ORDER BY updated_at DESC
                       LIMIT %s"""
                
                cursor = conn.execute(query, (tenant_id, user_id, limit))
                conversations = cursor.fetchall()
                
                result = []
                for conv in conversations:
                    result.append({
                        'session_id': conv['session_id'],
                        'title': conv['title'] or 'Untitled Conversation',
                        'status': conv['status'],
                        'created_at': str(conv['created_at']),
                        'updated_at': str(conv['updated_at']),
                        'message_count': conv['message_count'],
                        'is_deleted': bool(conv.get('deleted_by_user', False)) if include_deleted else False
                    })
                
                return result
        
        except Exception as e:
            print(f"❌ Error getting user conversations: {e}")
            return []
    
    # ========== GLOBAL LEARNING & ANALYTICS METHODS ==========
    
    def get_global_common_questions(self, tenant_id: str, limit: int = 10) -> List[Dict]:
        """
        Get most common questions across ALL users (GLOBAL LEARNING)
        Used to improve response quality and create FAQs
        
        ⚠️ INCLUDES SOFT-DELETED CONVERSATIONS for learning (privacy-friendly aggregation)
        
        Args:
            tenant_id: Tenant identifier
            limit: Maximum questions to return
        
        Returns:
            List of common questions with frequency
        """
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Includes ALL interactions, even from soft-deleted conversations
                # This helps improve system quality without exposing individual user data
                cursor = conn.execute(
                    """SELECT query, COUNT(*) as frequency,
                              AVG(response_time) as avg_response_time
                       FROM chat_interactions
                       WHERE tenant_id = %s
                       GROUP BY query
                       ORDER BY frequency DESC
                       LIMIT %s""",
                    (tenant_id, limit)
                )
                questions = cursor.fetchall()
                
                result = []
                for q in questions:
                    result.append({
                        'question': q['query'],
                        'frequency': q['frequency'],
                        'avg_response_time': float(q['avg_response_time']) if q['avg_response_time'] else 0
                    })
                
                return result
        
        except Exception as e:
            print(f"❌ Error getting common questions: {e}")
            return []
    
    def get_global_query_patterns(self, tenant_id: str, days: int = 30) -> Dict:
        """
        Analyze query patterns across ALL users (GLOBAL ANALYTICS)
        Helps improve search and response generation
        
        ⚠️ INCLUDES SOFT-DELETED CONVERSATIONS for learning (privacy-friendly aggregation)
        
        Args:
            tenant_id: Tenant identifier
            days: Number of days to analyze
        
        Returns:
            Dict with pattern statistics
        """
        if not self.db_manager:
            return {}
        
        try:
            with self.db_manager.get_connection() as conn:
                # Get query statistics
                cursor = conn.execute(
                    """SELECT 
                           COUNT(*) as total_queries,
                           COUNT(DISTINCT conversation_id) as unique_conversations,
                           AVG(response_time) as avg_response_time,
                           AVG(helpful) as avg_helpfulness
                       FROM chat_interactions
                       WHERE tenant_id = %s 
                       AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)""",
                    (tenant_id, days)
                )
                stats = cursor.fetchone()
                
                # Get topic distribution (if available)
                cursor = conn.execute(
                    """SELECT module, COUNT(*) as count
                       FROM chat_interactions
                       WHERE tenant_id = %s 
                       AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                       AND module IS NOT NULL
                       GROUP BY module
                       ORDER BY count DESC
                       LIMIT 10""",
                    (tenant_id, days)
                )
                topics = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'total_queries': stats['total_queries'],
                    'unique_conversations': stats['unique_conversations'],
                    'avg_response_time': float(stats['avg_response_time']) if stats['avg_response_time'] else 0,
                    'avg_helpfulness': float(stats['avg_helpfulness']) if stats['avg_helpfulness'] else 0,
                    'top_topics': [{'topic': t['module'], 'count': t['count']} for t in topics]
                }
        
        except Exception as e:
            print(f"❌ Error analyzing query patterns: {e}")
            return {}
    
    def learn_from_feedback(self, tenant_id: str, min_samples: int = 5) -> List[Dict]:
        """
        Learn from user feedback across ALL users (GLOBAL LEARNING)
        Identifies which responses work well and which need improvement
        
        Args:
            tenant_id: Tenant identifier
            min_samples: Minimum feedback samples required
        
        Returns:
            List of insights with suggestions
        """
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                # Find queries with negative feedback
                cursor = conn.execute(
                    """SELECT query, 
                              COUNT(*) as times_asked,
                              AVG(helpful) as avg_rating,
                              GROUP_CONCAT(DISTINCT response SEPARATOR ' | ') as sample_responses
                       FROM chat_interactions
                       WHERE tenant_id = %s 
                       AND helpful IS NOT NULL
                       GROUP BY query
                       HAVING times_asked >= %s AND avg_rating < 0.5
                       ORDER BY times_asked DESC
                       LIMIT 20""",
                    (tenant_id, min_samples)
                )
                problem_queries = cursor.fetchall()
                
                insights = []
                for pq in problem_queries:
                    insights.append({
                        'query': pq['query'],
                        'times_asked': pq['times_asked'],
                        'avg_rating': float(pq['avg_rating']),
                        'status': 'needs_improvement',
                        'suggestion': 'This question frequently receives negative feedback. Consider updating documentation or improving response.'
                    })
                
                return insights
        
        except Exception as e:
            print(f"❌ Error learning from feedback: {e}")
            return []


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

