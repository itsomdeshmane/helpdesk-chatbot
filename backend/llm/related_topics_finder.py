"""
Related Topics Finder
When direct answer isn't found, suggests related topics that ARE available in documentation
"""
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from typing import List, Dict, Optional

client = OpenAI(api_key=OPENAI_API_KEY)


def find_related_topics(query: str, tenant_id: str = "default") -> Optional[Dict]:
    """
    When answer isn't found, find related topics that ARE in documentation
    
    Args:
        query: User's question that couldn't be answered
        tenant_id: Tenant identifier
    
    Returns:
        Dict with related topics and suggestions, or None if nothing found
    """
    try:
        from llm.rag import search
        
        print(f"   🔍 Looking for related topics to: '{query}'", flush=True)
        
        # Extract key terms from query
        query_terms = extract_key_terms(query)
        print(f"   📝 Key terms: {query_terms}", flush=True)
        
        # Try alternative searches with broader terms
        related_docs = []
        for term in query_terms[:3]:  # Try top 3 terms
            try:
                docs = search(term, tenant_id)
                if docs and len(docs) > 0:
                    first_doc = docs[0].lower()
                    # Check if it's a real result
                    if not any(phrase in first_doc for phrase in [
                        'no documentation',
                        'no relevant',
                        'please upload'
                    ]):
                        related_docs.extend(docs[:2])  # Take top 2 from each term
            except Exception as e:
                print(f"   ⚠️  Search failed for term '{term}': {e}")
                continue
        
        if not related_docs:
            print(f"   ❌ No related topics found")
            return None
        
        # Remove duplicates
        unique_docs = list(set(related_docs))
        
        print(f"   ✅ Found {len(unique_docs)} related documents")
        
        # Use AI to extract topics from related docs
        topics = extract_topics_from_docs(query, unique_docs[:3])
        
        if not topics or len(topics) == 0:
            return None
        
        return {
            'found_topics': topics,
            'suggestion': generate_helpful_suggestion(query, topics)
        }
        
    except Exception as e:
        print(f"   ❌ Error finding related topics: {e}")
        return None


def extract_key_terms(query: str) -> List[str]:
    """
    Extract key terms from user query for alternative searches
    
    Args:
        query: User's question
    
    Returns:
        List of key terms
    """
    # Remove common question words
    stop_words = {
        'what', 'is', 'are', 'how', 'do', 'does', 'can', 'the', 'a', 'an',
        'to', 'in', 'on', 'for', 'with', 'about', 'tell', 'me', 'explain',
        'show', 'where', 'when', 'why', 'which', 'who', 'i', 'you', 'my'
    }
    
    words = query.lower().split()
    key_terms = [w.strip('?.,;:!()[]{}') for w in words if len(w) > 3 and w.lower() not in stop_words]
    
    # Also try the full query
    if query:
        key_terms.insert(0, query)
    
    return key_terms


def extract_topics_from_docs(query: str, docs: List[str]) -> List[str]:
    """
    Extract available topics from related documents
    
    Args:
        query: Original user query
        docs: Related documents found
    
    Returns:
        List of topic titles/descriptions
    """
    try:
        # Combine docs
        combined_docs = "\n\n".join(docs[:3])[:2000]  # Limit to 2000 chars
        
        prompt = f"""User asked: "{query}"

We don't have direct information about that, but here are some related topics from our documentation:

{combined_docs}

Extract 2-3 specific topics/features that are AVAILABLE in the documentation above that the user might find helpful.
Return ONLY a JSON array of topic names (short, 3-8 words each).

Example format: ["Job Management Workflow", "Customer Order Process", "Status Tracking"]

Return JSON array only:"""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You extract available topic names from documentation. Return only JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100,
            timeout=5
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        topics = json.loads(content)
        
        # Validate and clean
        validated = []
        for topic in topics[:3]:
            topic = topic.strip()
            if 5 <= len(topic) <= 100:
                validated.append(topic)
        
        return validated
        
    except Exception as e:
        print(f"   ⚠️  Could not extract topics: {e}")
        return []


def generate_helpful_suggestion(query: str, topics: List[str]) -> str:
    """
    Generate a helpful suggestion message with available topics
    
    Args:
        query: User's original query
        topics: Available topics found
    
    Returns:
        Formatted suggestion message
    """
    if not topics:
        return "Please try rephrasing your question or contact support."
    
    if len(topics) == 1:
        return f"However, I found information about **{topics[0]}** in our documentation. Would you like to know about that?"
    else:
        topics_list = "\n".join([f"• {topic}" for topic in topics])
        return f"However, I found related information about:\n\n{topics_list}\n\nWould you like to know about any of these?"


def generate_not_found_response_with_hints(query: str, tenant_id: str = "default") -> str:
    """
    Generate a helpful "not found" response with hints about related topics
    
    Args:
        query: User's question
        tenant_id: Tenant identifier
    
    Returns:
        Helpful response with related topics
    """
    # Find related topics
    related_info = find_related_topics(query, tenant_id)
    
    if related_info and related_info.get('found_topics'):
        topics = related_info['found_topics']
        suggestion = related_info['suggestion']
        
        response = f"""I don't have specific information about "{query}" in the loaded documentation.

{suggestion}"""
        
        return response
    else:
        # No related topics found - standard response
        return "I don't have information about this in the loaded documentation. Please check if the relevant document has been uploaded or contact support."


# Cache for related topics to avoid duplicate searches
_related_topics_cache = {}

def get_related_topics_cached(query: str, tenant_id: str = "default") -> Optional[Dict]:
    """
    Get related topics with caching
    
    Args:
        query: User's question
        tenant_id: Tenant identifier
    
    Returns:
        Related topics info or None
    """
    cache_key = f"{query[:100]}_{tenant_id}"
    
    if cache_key in _related_topics_cache:
        print(f"   💨 Using cached related topics")
        return _related_topics_cache[cache_key]
    
    related = find_related_topics(query, tenant_id)
    
    if related:
        _related_topics_cache[cache_key] = related
        # Limit cache size
        if len(_related_topics_cache) > 50:
            _related_topics_cache.pop(next(iter(_related_topics_cache)))
    
    return related

