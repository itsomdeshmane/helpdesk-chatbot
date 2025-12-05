"""
Query Rewriting/Expansion Module - Production Ready
Improves search quality by rewriting and expanding user queries
"""

from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from typing import List, Dict, Optional, Tuple
import re
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Query rewrite cache (in-memory, with TTL)
_rewrite_cache: Dict[str, Tuple[str, datetime]] = {}
_CACHE_TTL = timedelta(hours=1)


def _get_cache_key(query: str, context: str = "") -> str:
    """Generate cache key for query"""
    content = f"{query}:{context}"
    return hashlib.md5(content.encode()).hexdigest()


def _is_cache_valid(cache_time: datetime) -> bool:
    """Check if cache entry is still valid"""
    return datetime.now() - cache_time < _CACHE_TTL


def rewrite_query_for_search(
    query: str,
    conversation_history: List[Dict] = None,
    use_cache: bool = True
) -> str:
    """
    Rewrite a user query to be more specific and searchable.
    Uses conversation history to resolve pronouns and context.
    
    Args:
        query: Original user query
        conversation_history: List of previous messages [{query, response}, ...]
        use_cache: Whether to use cached rewrites
    
    Returns:
        Rewritten query optimized for search
    """
    # Check cache
    context_str = str(conversation_history[-1] if conversation_history else "")
    cache_key = _get_cache_key(query, context_str)
    
    if use_cache and cache_key in _rewrite_cache:
        cached_query, cache_time = _rewrite_cache[cache_key]
        if _is_cache_valid(cache_time):
            return cached_query
    
    # If query is already specific enough, return as-is
    if _is_query_specific(query):
        return query
    
    try:
        # Build context from conversation history
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            recent = conversation_history[-2:]  # Last 2 exchanges
            history_context = "\n".join([
                f"User: {h.get('query', '')}\nAssistant: {h.get('response', '')[:200]}..."
                for h in recent
            ])
        
        system_prompt = """You are a query rewriting assistant. Your job is to rewrite user queries to be more specific and searchable.

RULES:
1. Resolve pronouns (it, this, that, they) using conversation context
2. Expand abbreviations and acronyms
3. Add relevant keywords that might help find the answer
4. Keep the query concise (under 50 words)
5. Preserve the original intent
6. If the query is already clear and specific, return it unchanged
7. Output ONLY the rewritten query, nothing else

EXAMPLES:
- "how does it work" (context: inventory module) → "how does the inventory module work"
- "what are the steps" (context: creating PO) → "what are the steps to create a purchase order"
- "tell me more" (context: vendor management) → "explain vendor management features and capabilities"
- "fix the error" (context: login issues) → "how to fix login error in the system"
"""

        user_prompt = f"""Previous Conversation:
{history_context if history_context else "None"}

Current Query: {query}

Rewrite the query to be more specific and searchable. Output ONLY the rewritten query."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Faster/cheaper for query rewriting
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        rewritten = response.choices[0].message.content.strip()
        
        # Clean up the response
        rewritten = _clean_rewritten_query(rewritten, query)
        
        # Cache the result
        _rewrite_cache[cache_key] = (rewritten, datetime.now())
        
        return rewritten
        
    except Exception as e:
        print(f"⚠️ Query rewriting failed: {e}", flush=True)
        return query


def expand_query_with_synonyms(query: str) -> List[str]:
    """
    Expand query with synonyms and related terms for broader search coverage.
    
    Args:
        query: Original query
    
    Returns:
        List of expanded queries including original
    """
    # Generic synonym mappings
    synonym_map = {
        'user': ['user', 'account', 'profile'],
        'customer': ['customer', 'client'],
        'order': ['order', 'request'],
        'item': ['item', 'record', 'entry'],
        'document': ['document', 'file', 'record'],
        'create': ['create', 'add', 'new', 'make'],
        'delete': ['delete', 'remove', 'cancel'],
        'update': ['update', 'edit', 'modify', 'change'],
        'view': ['view', 'see', 'display', 'show', 'list'],
        'report': ['report', 'analytics', 'dashboard'],
        'error': ['error', 'issue', 'problem', 'bug', 'not working'],
        'configure': ['configure', 'setup', 'set up', 'settings'],
        'notification': ['notification', 'alert', 'message'],
    }
    
    expanded_queries = [query]
    query_lower = query.lower()
    
    for term, synonyms in synonym_map.items():
        if term in query_lower:
            for synonym in synonyms:
                if synonym != term:
                    expanded = query_lower.replace(term, synonym)
                    if expanded not in [q.lower() for q in expanded_queries]:
                        expanded_queries.append(expanded)
    
    return expanded_queries[:5]  # Limit to 5 variations


def generate_search_queries(
    query: str,
    conversation_history: List[Dict] = None,
    num_queries: int = 3
) -> List[str]:
    """
    Generate multiple search queries from a single user query.
    Useful for multi-query retrieval strategies.
    
    Args:
        query: Original user query
        conversation_history: Previous conversation for context
        num_queries: Number of alternative queries to generate
    
    Returns:
        List of search queries (including original)
    """
    queries = [query]
    
    try:
        # Build context
        context = ""
        if conversation_history and len(conversation_history) > 0:
            last = conversation_history[-1]
            context = f"Previous topic: {last.get('query', '')}"
        
        system_prompt = f"""Generate {num_queries} alternative search queries for finding relevant documentation.
Each query should approach the topic from a different angle while preserving the original intent.

Rules:
1. Each query should be distinct
2. Include different keywords and phrasings
3. Consider different aspects of the question
4. Output queries as a numbered list
5. Keep each query under 30 words"""

        user_prompt = f"""Context: {context if context else "None"}

Original Query: {query}

Generate {num_queries} alternative search queries:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        lines = content.split('\n')
        
        for line in lines:
            # Remove numbering and clean up
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', line.strip())
            cleaned = re.sub(r'^[-•*]\s*', '', cleaned)
            if cleaned and len(cleaned) > 10 and cleaned.lower() != query.lower():
                queries.append(cleaned)
        
        return queries[:num_queries + 1]  # Include original
        
    except Exception as e:
        print(f"⚠️ Multi-query generation failed: {e}", flush=True)
        return [query]


def extract_keywords(query: str) -> List[str]:
    """
    Extract important keywords from a query for keyword-based search boost.
    
    Args:
        query: User query
    
    Returns:
        List of important keywords
    """
    # Common stopwords to ignore
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'where', 'when',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'some', 'any', 'no', 'not', 'only', 'same', 'so', 'than', 'too',
        'very', 'just', 'also', 'tell', 'me', 'about', 'please', 'help',
        'want', 'know', 'like', 'get', 'give', 'show', 'find'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
    
    # Filter stopwords and short words
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    
    # Sort by length (longer = more specific = likely more important)
    keywords.sort(key=len, reverse=True)
    
    return keywords[:10]


def _is_query_specific(query: str) -> bool:
    """
    Check if a query is already specific enough and doesn't need rewriting.
    
    Args:
        query: User query
    
    Returns:
        True if query is specific enough
    """
    # Queries with specific entities are usually good
    specific_indicators = [
        'inventory', 'sales', 'purchase', 'vendor', 'customer', 'invoice',
        'order', 'report', 'module', 'configure', 'setup', 'create', 'delete',
        'update', 'workflow', 'manufacturing', 'warehouse', 'accounting'
    ]
    
    query_lower = query.lower()
    
    # Check if query contains specific terms
    has_specific_term = any(term in query_lower for term in specific_indicators)
    
    # Check query length (very short queries often need expansion)
    word_count = len(query.split())
    
    # Queries that are specific and have enough words are good
    return has_specific_term and word_count >= 4


def _clean_rewritten_query(rewritten: str, original: str) -> str:
    """
    Clean up the rewritten query.
    
    Args:
        rewritten: Rewritten query from LLM
        original: Original query
    
    Returns:
        Cleaned query
    """
    # Remove quotes if present
    rewritten = rewritten.strip('"\'')
    
    # Remove any prefixes like "Rewritten:" or "Query:"
    prefixes = ['rewritten:', 'query:', 'rewritten query:', 'output:']
    for prefix in prefixes:
        if rewritten.lower().startswith(prefix):
            rewritten = rewritten[len(prefix):].strip()
    
    # If rewritten is too long or seems wrong, use original
    if len(rewritten) > 200 or len(rewritten) < 3:
        return original
    
    return rewritten


def clear_rewrite_cache():
    """Clear the query rewrite cache"""
    global _rewrite_cache
    _rewrite_cache = {}
    print("🗑️ Query rewrite cache cleared", flush=True)

