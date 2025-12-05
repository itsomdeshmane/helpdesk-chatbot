"""
Suggestion Generator Module - Production Ready
Generates follow-up question suggestions and proactive recommendations
"""

from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from typing import List, Dict, Optional
import re
import hashlib
from datetime import datetime, timedelta


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Cache for suggestions
_suggestion_cache: Dict[str, tuple] = {}
_CACHE_TTL = timedelta(minutes=30)


def get_suggested_questions(
    current_topic: str,
    module: str = None,
    conversation_history: List[Dict] = None,
    num_suggestions: int = 3,
    use_cache: bool = True
) -> List[str]:
    """
    Generate follow-up question suggestions based on current topic.
    
    Args:
        current_topic: The current conversation topic/query
        module: ERP module being discussed
        conversation_history: Previous conversation messages
        num_suggestions: Number of suggestions to generate
        use_cache: Whether to use cached suggestions
    
    Returns:
        List of suggested follow-up questions
    """
    # Check cache
    cache_key = hashlib.md5(f"{current_topic}:{module}".encode()).hexdigest()
    
    if use_cache and cache_key in _suggestion_cache:
        suggestions, cache_time = _suggestion_cache[cache_key]
        if datetime.now() - cache_time < _CACHE_TTL:
            return suggestions[:num_suggestions]
    
    # Try AI-generated suggestions
    try:
        suggestions = _generate_ai_suggestions(
            current_topic, 
            module, 
            conversation_history,
            num_suggestions
        )
        
        if suggestions:
            _suggestion_cache[cache_key] = (suggestions, datetime.now())
            return suggestions
    except Exception as e:
        print(f"⚠️ AI suggestion generation failed: {e}", flush=True)
    
    # Fallback to rule-based suggestions
    return _generate_rule_based_suggestions(current_topic, module, num_suggestions)


def _generate_ai_suggestions(
    topic: str,
    module: str,
    history: List[Dict],
    num: int
) -> List[str]:
    """Generate suggestions using AI"""
    
    # Build context from history
    context = ""
    if history and len(history) > 0:
        recent = history[-2:]
        context = "\n".join([
            f"Q: {h.get('query', '')}\nA: {h.get('response', '')[:150]}..."
            for h in recent
        ])
    
    system_prompt = f"""You are a helpful assistant. Generate {num} relevant follow-up questions that a user might ask after discussing the current topic.

RULES:
1. Questions should be natural and helpful continuations of the conversation
2. Focus on related features, troubleshooting, or deeper explanations
3. Keep questions concise (under 15 words each)
4. Questions should be specific to the system being discussed
5. Output ONLY the questions, one per line, no numbering

GOOD EXAMPLES:
- "How do I create a new document?"
- "What reports are available?"
- "Can I set up automatic notifications?"

BAD EXAMPLES (too vague):
- "Tell me more"
- "What else can I do?"
- "How does that work?"
"""

    module_context = f"Module: {module}" if module else ""
    
    user_prompt = f"""Current Topic: {topic}
{module_context}

Recent Conversation:
{context if context else "Start of conversation"}

Generate {num} helpful follow-up questions:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Fast for suggestions
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,  # Some creativity for variety
        max_tokens=200
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse questions
    questions = []
    for line in content.split('\n'):
        line = line.strip()
        # Remove numbering and bullets
        line = re.sub(r'^[\d]+[\.\)]\s*', '', line)
        line = re.sub(r'^[-•*]\s*', '', line)
        line = line.strip('"\'')
        
        if line and len(line) > 10 and '?' in line:
            questions.append(line)
    
    return questions[:num]


def _generate_rule_based_suggestions(
    topic: str,
    module: str,
    num: int
) -> List[str]:
    """Generate rule-based suggestions when AI is unavailable"""
    
    topic_lower = topic.lower()
    suggestions = []
    
    # Module-specific suggestions
    module_suggestions = {
        'inventory': [
            "How do I check current stock levels?",
            "How can I set up automatic reorder points?",
            "What inventory reports are available?",
            "How do I perform a stock adjustment?",
            "How does inventory valuation work?"
        ],
        'purchasing': [
            "How do I create a purchase order?",
            "How can I track order status?",
            "How do I manage vendor relationships?",
            "What are the approval workflows for POs?",
            "How do I handle purchase returns?"
        ],
        'sales': [
            "How do I create a sales order?",
            "How can I apply discounts to orders?",
            "How do I track sales performance?",
            "How do I set up pricing rules?",
            "What sales reports are available?"
        ],
        'finance': [
            "How do I create an invoice?",
            "How do I reconcile accounts?",
            "What financial reports are available?",
            "How do I handle payments?",
            "How does the chart of accounts work?"
        ],
        'manufacturing': [
            "How do I create a work order?",
            "How does bill of materials work?",
            "How do I track production progress?",
            "How do I manage routing operations?",
            "What manufacturing reports are available?"
        ],
        'general': [
            "How do I configure system settings?",
            "How do I manage user permissions?",
            "How can I customize reports?",
            "How do I export data?",
            "What integrations are available?"
        ]
    }
    
    # Get module-specific suggestions
    module_key = module.lower() if module else 'general'
    if module_key in module_suggestions:
        suggestions.extend(module_suggestions[module_key])
    
    # Add topic-specific suggestions
    if 'create' in topic_lower or 'add' in topic_lower:
        suggestions.insert(0, "What fields are required?")
        suggestions.insert(1, "Are there any prerequisites?")
    elif 'error' in topic_lower or 'issue' in topic_lower:
        suggestions.insert(0, "What are common causes of this issue?")
        suggestions.insert(1, "How can I prevent this in the future?")
    elif 'report' in topic_lower:
        suggestions.insert(0, "Can I schedule this report?")
        suggestions.insert(1, "How do I export report data?")
    elif 'configure' in topic_lower or 'setup' in topic_lower:
        suggestions.insert(0, "What are the best practices for this setup?")
        suggestions.insert(1, "Can I test the configuration?")
    
    # Deduplicate and limit
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_suggestions.append(s)
    
    return unique_suggestions[:num]


def get_proactive_tips(
    query: str,
    response: str,
    module: str = None
) -> List[str]:
    """
    Generate proactive tips based on the query and response.
    These are helpful hints that weren't explicitly asked for.
    
    Args:
        query: User's question
        response: Generated answer
        module: ERP module
    
    Returns:
        List of proactive tips
    """
    tips = []
    query_lower = query.lower()
    response_lower = response.lower()
    
    # Tip rules based on query content
    if 'create' in query_lower or 'add' in query_lower:
        tips.append("💡 Tip: You can save frequently used entries as templates for faster data entry.")
    
    if 'report' in query_lower:
        tips.append("💡 Tip: Most reports can be scheduled to run automatically and sent via email.")
    
    if 'error' in query_lower or 'issue' in query_lower:
        tips.append("💡 Tip: Check the system logs for more detailed error information.")
    
    if 'import' in query_lower or 'upload' in query_lower:
        tips.append("💡 Tip: Always backup your data before performing bulk imports.")
    
    if 'delete' in query_lower or 'remove' in query_lower:
        tips.append("💡 Tip: Deleted records may be recoverable from the audit log within 30 days.")
    
    if 'permission' in query_lower or 'access' in query_lower:
        tips.append("💡 Tip: Use role-based access control for easier permission management.")
    
    # Module-specific tips
    if module:
        module_lower = module.lower()
        
        if 'inventory' in module_lower and 'stock' in query_lower:
            tips.append("💡 Tip: Enable stock alerts to get notified when items fall below minimum levels.")
        
        if 'purchasing' in module_lower:
            tips.append("💡 Tip: Set up approval workflows to automate purchase order approvals.")
        
        if 'sales' in module_lower:
            tips.append("💡 Tip: Use customer groups to apply bulk pricing rules efficiently.")
    
    return tips[:2]  # Limit to 2 tips


def get_related_topics(
    topic: str,
    module: str = None
) -> List[Dict[str, str]]:
    """
    Get related topics that might be helpful.
    
    Args:
        topic: Current topic
        module: ERP module
    
    Returns:
        List of related topics with descriptions
    """
    # Topic mapping
    topic_relations = {
        'purchase order': [
            {'title': 'Vendor Management', 'description': 'Managing supplier information'},
            {'title': 'Receiving', 'description': 'Processing received goods'},
            {'title': 'Purchase Returns', 'description': 'Handling returned items'}
        ],
        'sales order': [
            {'title': 'Customer Management', 'description': 'Managing customer profiles'},
            {'title': 'Shipping', 'description': 'Order fulfillment and shipping'},
            {'title': 'Sales Returns', 'description': 'Processing customer returns'}
        ],
        'inventory': [
            {'title': 'Warehouse Management', 'description': 'Managing storage locations'},
            {'title': 'Stock Transfers', 'description': 'Moving inventory between locations'},
            {'title': 'Cycle Counting', 'description': 'Inventory accuracy verification'}
        ],
        'invoice': [
            {'title': 'Payments', 'description': 'Processing and tracking payments'},
            {'title': 'Credit Memos', 'description': 'Issuing credits to customers'},
            {'title': 'Accounts Receivable', 'description': 'Managing outstanding invoices'}
        ],
        'report': [
            {'title': 'Dashboards', 'description': 'Visual analytics overview'},
            {'title': 'Custom Reports', 'description': 'Building custom report templates'},
            {'title': 'Data Export', 'description': 'Exporting data for analysis'}
        ]
    }
    
    topic_lower = topic.lower()
    
    for key, relations in topic_relations.items():
        if key in topic_lower:
            return relations
    
    # Default related topics
    return [
        {'title': 'Getting Started', 'description': 'Basic system navigation'},
        {'title': 'User Settings', 'description': 'Personalizing your experience'},
        {'title': 'Help Center', 'description': 'Additional documentation and guides'}
    ]


def clear_suggestion_cache():
    """Clear the suggestion cache"""
    global _suggestion_cache
    _suggestion_cache = {}
    print("🗑️ Suggestion cache cleared", flush=True)

