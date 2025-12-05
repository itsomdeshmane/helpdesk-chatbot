"""
Query Clarity Detection Module
Analyzes user queries to determine if they are clear enough to answer
or if clarifying questions are needed.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from datetime import datetime, timedelta
import re

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Cache for system entities (refreshes every 10 minutes)
_entity_cache = None
_entity_cache_timestamp = None
ENTITY_CACHE_DURATION = timedelta(minutes=10)


def load_system_entities():
    """
    Load system entities from database with caching
    Returns dict mapping entity_key to entity_name
    """
    global _entity_cache, _entity_cache_timestamp
    
    # Check if cache is valid
    if _entity_cache and _entity_cache_timestamp:
        if datetime.now() - _entity_cache_timestamp < ENTITY_CACHE_DURATION:
            return _entity_cache
    
    # Try to load from database
    try:
        from database.db_manager import db_manager
        entities_dict = db_manager.get_system_entities(active_only=True)
        
        if entities_dict:
            _entity_cache = entities_dict
            _entity_cache_timestamp = datetime.now()
            return entities_dict
    except Exception as e:
        print(f"Warning: Could not load entities from database: {e}", flush=True)
    
    # Fallback to default entities if database unavailable
    return get_default_entities()


def get_default_entities():
    """Fallback default entities if database is unavailable"""
    return {
        'user': 'User',
        'customer': 'Customer',
        'order': 'Order',
        'item': 'Item',
        'document': 'Document',
        'report': 'Report',
        'setting': 'Setting',
        'notification': 'Notification',
    }


def refresh_entity_cache():
    """Force refresh the entity cache"""
    global _entity_cache, _entity_cache_timestamp
    _entity_cache = None
    _entity_cache_timestamp = None
    return load_system_entities()


def analyze_query_clarity(query: str) -> dict:
    """
    Analyze if a user's query is clear enough to answer.
    
    Returns:
        dict: {
            'is_clear': bool,
            'clarity_score': float (0.0 to 1.0),
            'issues': list of str,
            'suggestions': list of str (clarifying questions),
            'query_type': str
        }
    """
    if not query or len(query.strip()) < 2:
        return {
            'is_clear': False,
            'clarity_score': 0.0,
            'issues': ['Query is too short or empty'],
            'suggestions': ['Could you please provide more details about what you need help with?'],
            'query_type': 'empty'
        }
    
    query_lower = query.strip().lower()
    issues = []
    clarity_score = 1.0
    
    # Check 1: Very vague/single word queries
    vague_queries = ['help', 'hi', 'hello', 'please help', 'need help', 'support']
    if query_lower in vague_queries or len(query.split()) <= 2 and any(v in query_lower for v in vague_queries):
        issues.append('Query is too vague')
        clarity_score -= 0.5
    
    # Check 2: Incomplete questions
    incomplete_patterns = [
        r'^how to\?*$',
        r'^what about\?*$',
        r'^why\?*$',
        r'^when\?*$',
        r'^where\?*$',
    ]
    if any(re.match(pattern, query_lower) for pattern in incomplete_patterns):
        issues.append('Question is incomplete')
        clarity_score -= 0.4
    
    # Check 3: Missing context (e.g., "it not working")
    missing_context_patterns = [
        r'\bit\b.*not working',
        r'not working',
        r'broken',
        r'error',
        r'issue',
        r'problem'
    ]
    if any(re.search(pattern, query_lower) for pattern in missing_context_patterns):
        if not any(module in query_lower for module in ['inventory', 'sales', 'purchasing', 'finance', 'hr', 'crm', 'manufacturing']):
            issues.append('Missing specific context (what is not working?)')
            clarity_score -= 0.3
    
    # Check 4: Too many questions at once
    question_markers = [' and ', ' or ', ' also ', ' plus ']
    question_count = sum(1 for marker in question_markers if marker in query_lower)
    if question_count >= 2 or query.count('?') > 2:
        issues.append('Multiple questions in one query')
        clarity_score -= 0.3
    
    # Check 5: Very short queries that need more context
    words = query.split()
    if len(words) <= 3 and not any(q in query_lower for q in ['what is', 'how to', 'where is']):
        issues.append('Query needs more context')
        clarity_score -= 0.2
    
    # Ensure score is between 0 and 1
    clarity_score = max(0.0, min(1.0, clarity_score))
    
    # Determine if query is clear
    is_clear = clarity_score >= 0.6 and len(issues) == 0
    
    # Detect query type
    query_type = _detect_query_type(query)
    
    # Generate clarifying questions if needed
    suggestions = []
    if not is_clear:
        suggestions = _generate_clarifying_questions(query, query_type, issues)
    
    return {
        'is_clear': is_clear,
        'clarity_score': clarity_score,
        'issues': issues,
        'suggestions': suggestions,
        'query_type': query_type
    }


def _detect_query_type(query: str) -> str:
    """Detect the type of query"""
    query_lower = query.lower()
    
    # Load entities from database (with caching)
    entities = load_system_entities()
    
    # Extract entity mentions (user, customer, order, etc.)
    mentioned_entity = None
    for entity_key in entities.keys():
        if entity_key in query_lower:
            mentioned_entity = entity_key
            break
    
    # Detect action
    if 'create' in query_lower or 'add' in query_lower:
        return 'create'
    elif 'update' in query_lower or 'edit' in query_lower or 'modify' in query_lower:
        return 'update'
    elif 'delete' in query_lower or 'remove' in query_lower:
        return 'delete'
    elif 'view' in query_lower or 'see' in query_lower or 'find' in query_lower:
        return 'view'
    elif 'setup' in query_lower or 'configure' in query_lower or 'install' in query_lower:
        return 'setup'
    elif 'not working' in query_lower or 'error' in query_lower or 'issue' in query_lower:
        return 'troubleshooting'
    elif 'how to' in query_lower or 'how do' in query_lower:
        return 'how-to'
    elif 'what is' in query_lower or 'what are' in query_lower:
        return 'definition'
    elif 'list' in query_lower or 'show all' in query_lower:
        return 'list'
    else:
        return 'general'


def _generate_clarifying_questions(query: str, query_type: str, issues: list) -> list:
    """
    Generate contextual clarifying questions using AI
    Maintains specific context from the user's query
    """
    try:
        # Load entities from database (with caching)
        entities = load_system_entities()
        
        # Extract key entities from the query
        query_lower = query.lower()
        
        detected_entity = None
        for key, value in entities.items():
            if key in query_lower:
                detected_entity = value
                break
        
        # Build context-aware prompt
        issues_text = ', '.join(issues) if issues else 'needs clarification'
        
        system_prompt = f"""You are a helpful assistant. A user asked a question but it {issues_text}.

Generate 2-3 SHORT clarifying questions to understand what they need.

CRITICAL RULES:
1. If the user mentioned a specific entity (like "item", "customer", "vendor"), USE THAT EXACT ENTITY in your questions
2. NEVER use generic phrases like "this topic" or "this area"
3. Keep questions SHORT and SIMPLE (one line each)
4. Make questions SPECIFIC and ACTIONABLE
5. Focus on what's missing from their query

Examples:

Bad: "What specific task do you want to perform in this topic?"
Good: "Which module do you want to create Item in? (e.g., Inventory, Purchasing)"

Bad: "Are you asking about creating something in this area?"
Good: "Do you need help with the steps to create a new Customer?"

Bad: "Could you clarify what you need in this module?"
Good: "Are you looking for Purchase Order reports or Vendor performance reports?"
"""

        entity_context = f"\nThe user mentioned: {detected_entity}" if detected_entity else ""
        
        user_prompt = f"""User Query: "{query}"
Query Type: {query_type}
Issues: {issues_text}{entity_context}

Generate 2-3 clarifying questions that are specific and maintain the context of what the user asked about."""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        # Parse questions from response
        questions_text = response.choices[0].message.content.strip()
        
        # Extract questions (numbered or bulleted)
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            # Remove numbering/bullets
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^[-•*]\s*', '', line)
            if line and len(line) > 10:  # Meaningful question
                questions.append(line)
        
        # Limit to 3 questions
        questions = questions[:3]
        
        # Fallback if AI didn't generate good questions
        if len(questions) == 0:
            questions = _generate_fallback_questions(query, query_type, detected_entity, issues)
        
        return questions
        
    except Exception as e:
        print(f"Error generating clarifying questions: {e}")
        # Fallback to rule-based questions
        return _generate_fallback_questions(query, query_type, detected_entity, issues)


def _generate_fallback_questions(query: str, query_type: str, entity: str = None, issues: list = None) -> list:
    """Generate fallback clarifying questions when AI is unavailable"""
    questions = []
    
    entity_name = entity if entity else "this"
    
    if 'too vague' in str(issues).lower() or 'too short' in str(issues).lower():
        questions.append(f"What would you like to know about the system?")
        questions.append(f"Which feature or area are you asking about?")
    
    if 'incomplete' in str(issues).lower():
        if query_type == 'how-to':
            questions.append(f"What specific task do you want to accomplish?")
        else:
            questions.append(f"Could you complete your question with more details?")
    
    if 'missing context' in str(issues).lower() or 'not working' in query.lower():
        questions.append(f"Which feature or module is having issues?")
        questions.append(f"What error message or problem are you seeing?")
    
    if 'multiple questions' in str(issues).lower():
        questions.append(f"Let's focus on one topic. Which question would you like answered first?")
    
    if query_type == 'create' and entity:
        questions.append(f"In which module do you want to create {entity}?")
        questions.append(f"Do you need help with the steps to create a new {entity}?")
    
    if not questions:
        questions.append(f"Could you provide more details about what you need help with?")
        questions.append(f"Which feature or area is your question related to?")
    
    return questions[:3]


def format_clarification_response(query: str, questions: list) -> str:
    """
    Format a friendly clarification response
    
    Args:
        query: The original user query
        questions: List of clarifying questions
    
    Returns:
        str: Formatted response string
    """
    if not questions:
        return "I'd like to help you better. Could you provide more details about your question?"
    
    response = "I'd like to help you better. Could you clarify:\n\n"
    
    for i, question in enumerate(questions, 1):
        response += f"{i}. {question}\n"
    
    return response.strip()


def generate_clarifying_questions(query: str, num_questions: int = 3) -> list:
    """
    Alternative interface for generating clarifying questions
    (for backward compatibility with some imports)
    """
    analysis = analyze_query_clarity(query)
    return analysis.get('suggestions', [])[:num_questions]
