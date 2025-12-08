"""
Generic Context Extractor - AI-Powered
Extracts topics, entities, and context from ANY conversation using GPT
Works dynamically for any domain without hardcoded patterns
"""
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
import json
from typing import Dict, List, Optional

client = OpenAI(api_key=OPENAI_API_KEY)


class ContextExtractor:
    """
    AI-powered context extractor
    Uses GPT to understand conversation context dynamically
    """
    
    def __init__(self):
        self.cache = {}  # In-memory cache for quick lookups
    
    def extract_context(self, query: str, response: str, module: str = None) -> Dict:
        """
        Extract context from a query-response pair using AI
        Works for ANY topic/domain
        
        Args:
            query: User's question
            response: Bot's answer
            module: Optional detected module
        
        Returns:
            {
                'main_topic': str,
                'entities': List[str],
                'keywords': List[str],
                'context_type': str,
                'confidence': float
            }
        """
        try:
            # Use GPT to extract context
            extraction_prompt = f"""Analyze this conversation and extract key context:

User Question: {query}
Assistant Response: {response[:300]}

Extract:
1. Main Topic: The primary subject being discussed (e.g., "Workflow Module", "Customer Creation", "Invoice Process")
2. Entities: Important nouns/entities mentioned (e.g., ["Workflow Module", "Design Jobs", "Router"])
3. Keywords: Key terms for search (e.g., ["workflow", "design", "job", "router"])
4. Context Type: Category (choose one: module, feature, process, entity, concept, general)

Return as JSON:
{{
    "main_topic": "...",
    "entities": [...],
    "keywords": [...],
    "context_type": "..."
}}"""

            response_gpt = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a context extraction expert. Extract structured information from conversations. Always return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                timeout=10
            )
            
            content = response_gpt.choices[0].message.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            extracted = json.loads(content)
            
            # Add confidence score (based on response quality)
            confidence = 0.9 if extracted.get('main_topic') and len(extracted.get('entities', [])) > 0 else 0.5
            extracted['confidence'] = confidence
            
            # Fallback to module if main_topic is empty
            if not extracted.get('main_topic') and module:
                extracted['main_topic'] = module
            
            return extracted
            
        except Exception as e:
            print(f"⚠️  Context extraction error: {e}")
            # Fallback: Simple extraction
            return self._simple_extraction(query, response, module)
    
    def _simple_extraction(self, query: str, response: str, module: str = None) -> Dict:
        """
        Fallback: Simple rule-based extraction
        Used when AI extraction fails
        """
        import re
        
        # Extract capitalized phrases (likely entities)
        entities = re.findall(r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)\b', query + " " + response[:200])
        entities = list(set(entities))[:5]  # Max 5 unique entities
        
        # Extract keywords (important words > 3 chars)
        stop_words = {'what', 'where', 'when', 'which', 'who', 'how', 'the', 'are', 'and', 'for'}
        words = re.findall(r'\b\w{4,}\b', query.lower())
        keywords = [w for w in set(words) if w not in stop_words][:5]
        
        # Main topic: Use module or first entity
        main_topic = module or (entities[0] if entities else "General Topic")
        
        return {
            'main_topic': main_topic,
            'entities': entities,
            'keywords': keywords,
            'context_type': 'general',
            'confidence': 0.5
        }
    
    def resolve_reference(self, current_query: str, conversation_history: List[Dict]) -> Optional[str]:
        """
        Resolve pronouns/references in current query using conversation history
        Uses AI to understand what "it", "this", "that" refers to
        Also handles very short queries that are likely follow-ups
        
        Args:
            current_query: Current user query (may contain pronouns)
            conversation_history: Previous messages
        
        Returns:
            Resolved entity/topic, or None if no reference found
        """
        if not conversation_history:
            return None
        
        # Check if query contains pronouns/references
        pronouns = ['it', 'this', 'that', 'these', 'those', 'the module', 'the feature', 
                   'the process', 'the system', 'the option', 'them', 'its']
        
        query_lower = current_query.lower()
        has_pronoun = any(pronoun in query_lower for pronoun in pronouns)
        
        # Also check if query is very short (1-2 words) - likely implicit reference
        query_words = current_query.strip().split()
        is_very_short = len(query_words) <= 2
        
        if not has_pronoun and not is_very_short:
            return None
        
        try:
            # Use AI to resolve reference
            history_text = "\n".join([
                f"User: {msg['query']}\nAssistant: {msg['response'][:150]}..."
                for msg in conversation_history[-2:]  # Last 2 messages
            ])
            
            resolution_prompt = f"""Previous conversation:
{history_text}

Current question: {current_query}

The user's current question is either:
1. A short query that continues the previous topic (e.g., "Lifecycle" after discussing "Job")
2. Contains a reference word (like "it", "this", "that")

What specific topic/entity from the previous conversation is the user asking about?
Combine the previous topic with the current query if needed.

Return ONLY the entity/topic name. Examples:
- If previous was about "Job" and current is "Lifecycle" → return "Job Lifecycle"
- If previous was about "Workflow Module" and current is "steps" → return "Workflow Module steps"
- If current is "How does it work?" → return the topic "it" refers to

If no clear connection to previous conversation, return "NONE".
"""

            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at resolving pronoun references in conversations. Return ONLY the entity name."},
                    {"role": "user", "content": resolution_prompt}
                ],
                temperature=0.2,
                max_tokens=50,
                timeout=10
            )
            
            resolved = response.choices[0].message.content.strip()
            
            if resolved and resolved != "NONE":
                print(f"   🔗 Resolved reference: '{current_query}' → refers to '{resolved}'")
                return resolved
            
            return None
            
        except Exception as e:
            print(f"⚠️  Reference resolution error: {e}")
            # Fallback: Use main topic from last message
            if conversation_history:
                last_msg = conversation_history[-1]
                return last_msg.get('main_topic')
            return None
    
    def build_context_enhanced_query(self, current_query: str, conversation_history: List[Dict]) -> str:
        """
        Build an enhanced search query with context
        Generic approach that works for any conversation
        
        Args:
            current_query: Current user query
            conversation_history: Previous messages
        
        Returns:
            Enhanced query for better search
        """
        if not conversation_history:
            return current_query
        
        # Resolve references
        resolved_entity = self.resolve_reference(current_query, conversation_history)
        
        if resolved_entity:
            # Add resolved entity to query
            return f"{resolved_entity} {current_query}"
        
        # No pronoun detected - check if query is very short
        # If short, add context from previous conversation
        if len(current_query.split()) <= 3:
            # Very short query - likely continuation of previous topic
            last_msg = conversation_history[-1]
            last_topic = last_msg.get('main_topic', '')
            
            if last_topic:
                return f"{last_topic} {current_query}"
        
        return current_query
    
    def save_context_to_db(self, db_manager, conversation_id: int, message_order: int, context: Dict):
        """
        Save extracted context to database
        
        Args:
            db_manager: Database manager instance
            conversation_id: Conversation ID
            message_order: Message order in conversation
            context: Extracted context dict
        """
        try:
            with db_manager.get_connection() as conn:
                conn.execute(
                    """INSERT INTO conversation_context
                       (conversation_id, message_order, main_topic, entities, keywords, 
                        context_type, confidence)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        conversation_id,
                        message_order,
                        context.get('main_topic'),
                        json.dumps(context.get('entities', [])),
                        json.dumps(context.get('keywords', [])),
                        context.get('context_type', 'general'),
                        context.get('confidence', 0.5)
                    )
                )
                conn.commit()
                print(f"   💾 Context saved: Topic='{context.get('main_topic')}'")
        except Exception as e:
            print(f"⚠️  Error saving context to DB: {e}")
    
    def get_conversation_context_from_db(self, db_manager, conversation_id: int, limit: int = 3) -> List[Dict]:
        """
        Load conversation context from database
        
        Args:
            db_manager: Database manager instance
            conversation_id: Conversation ID
            limit: Number of recent contexts to load
        
        Returns:
            List of context dicts
        """
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT main_topic, entities, keywords, context_type, confidence
                       FROM conversation_context
                       WHERE conversation_id = %s
                       ORDER BY message_order DESC
                       LIMIT %s""",
                    (conversation_id, limit)
                )
                results = cursor.fetchall()
                
                contexts = []
                for row in results:
                    contexts.append({
                        'main_topic': row['main_topic'],
                        'entities': json.loads(row['entities']) if row['entities'] else [],
                        'keywords': json.loads(row['keywords']) if row['keywords'] else [],
                        'context_type': row['context_type'],
                        'confidence': row['confidence']
                    })
                
                return contexts
        except Exception as e:
            print(f"⚠️  Error loading context from DB: {e}")
            return []


# Singleton instance
_context_extractor = None

def get_context_extractor() -> ContextExtractor:
    """Get or create context extractor instance"""
    global _context_extractor
    
    if _context_extractor is None:
        _context_extractor = ContextExtractor()
    
    return _context_extractor

