"""
Related Questions Generator
Generates contextually relevant follow-up questions to guide conversation flow
Questions are DOCUMENTATION-SPECIFIC and ANSWERABLE
"""
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from typing import Optional

client = OpenAI(api_key=OPENAI_API_KEY)


def verify_question_is_answerable(question: str, tenant_id: str = "default") -> bool:
    """
    Verify that a question can be answered from available documentation (OPTIONAL CHECK)
    
    Args:
        question: The generated question
        tenant_id: Tenant identifier
    
    Returns:
        True if question is likely answerable, False otherwise
    """
    try:
        # Quick search to see if we have relevant content
        from llm.rag import search
        
        docs = search(question, tenant_id)
        
        # Check if we got meaningful results
        if not docs or len(docs) == 0:
            return False
        
        # Check if results contain relevant content (not just "No documentation found")
        first_doc = docs[0].lower()
        if any(phrase in first_doc for phrase in [
            'no documentation',
            'no relevant documents',
            'no matching',
            'please upload'
        ]):
            return False
        
        # Check if results have substantial content
        total_length = sum(len(doc) for doc in docs)
        if total_length < 100:  # Too short to be meaningful
            return False
        
        return True
        
    except Exception as e:
        # If verification fails, assume it's answerable (don't block question)
        print(f"   ⚠️  Could not verify question answerability: {e}")
        return True  # Default to True to avoid blocking


def generate_related_question(query: str, response: str, main_topic: str = None, context_preview: str = None) -> Optional[str]:
    """
    Generate a single related question to guide the conversation (NEW FEATURE - optional)
    Question MUST be answerable from the documentation
    
    Args:
        query: User's original question
        response: Bot's answer (from documentation)
        main_topic: Main topic from context extraction
        context_preview: Preview of available documentation topics
    
    Returns:
        A single related question, or None if generation fails
    """
    try:
        # Build context-aware prompt
        topic_context = f"\nMain Topic: {main_topic}" if main_topic else ""
        
        # Extract key concepts from the response to ensure question is documentation-based
        key_concepts = []
        lines = response[:500].split('\n')
        for line in lines:
            # Look for bullet points, numbered items, or definitions
            if any(indicator in line for indicator in ['•', '-', '1.', '2.', ':', 'includes', 'contains', 'such as']):
                key_concepts.append(line.strip())
        
        concepts_text = "\n".join(key_concepts[:5]) if key_concepts else ""
        
        prompt = f"""Based on this conversation from a documentation system, suggest ONE natural follow-up question.

User Question: {query}
Assistant Answer (FROM DOCUMENTATION): {response[:400]}...{topic_context}

Key concepts mentioned in the answer:
{concepts_text}

🚨 CRITICAL RULES:
1. Question MUST be about concepts/features MENTIONED in the assistant's answer above
2. Question MUST be answerable from the same documentation source
3. DO NOT ask general questions unrelated to the documentation
4. DO NOT ask about things not mentioned in the answer
5. Build on what was just explained

Good examples (based on answer content):
- If answer mentions "Job lifecycle" → "What are the stages in Job lifecycle?"
- If answer mentions "required fields" → "What are the required fields?"
- If answer mentions "workflow steps" → "How do I configure workflow steps?"
- If answer mentions "validation" → "What validation rules are applied?"

Bad examples (avoid these):
- "What is the weather?" (not in documentation)
- "How do I login?" (if login wasn't mentioned)
- "Tell me more?" (too vague)
- "What else?" (too general)

Return ONLY ONE specific question (max 10 words) about topics in the answer."""

        response_gpt = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at guiding conversations. Generate ONE natural, specific follow-up question."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Higher for creativity
            max_tokens=30,    # Short question
            timeout=5         # Fast timeout - this is optional enhancement
        )
        
        related_question = response_gpt.choices[0].message.content.strip()
        
        # Clean up the question
        related_question = related_question.strip('"').strip("'").strip()
        
        # Validate it's a reasonable question
        if len(related_question) > 100 or len(related_question) < 5:
            return None
        
        # Ensure it ends with a question mark
        if not related_question.endswith('?'):
            related_question += '?'
        
        # Validate question is documentation-specific (not generic)
        generic_indicators = [
            'tell me more',
            'what else',
            'anything else',
            'more information',
            'more details',
            'explain more',
            'weather',
            'news',
            'date',
            'time',
            'how are you',
            'who are you'
        ]
        
        question_lower = related_question.lower()
        if any(indicator in question_lower for indicator in generic_indicators):
            print(f"   ⚠️  Rejected generic question: '{related_question}'")
            return None
        
        # Ensure question relates to concepts in the original response
        # Extract key terms from response
        response_terms = set()
        for word in response[:500].lower().split():
            if len(word) > 4:  # Meaningful words
                response_terms.add(word.strip('.,;:!?()[]{}'))
        
        # Check if question contains at least one term from response
        question_terms = set(related_question.lower().split())
        has_overlap = bool(response_terms.intersection(question_terms))
        
        if not has_overlap:
            print(f"   ⚠️  Question not related to answer content: '{related_question}'")
            return None
        
        return related_question
        
    except Exception as e:
        # Silently fail - this is an optional enhancement
        print(f"   ⚠️  Could not generate related question: {e}")
        return None


def generate_related_questions_batch(queries: list, responses: list, limit: int = 3) -> list:
    """
    Generate multiple related questions from conversation history (OPTIONAL)
    Used for creating suggested questions panel
    
    Args:
        queries: List of recent user queries
        responses: List of recent bot responses
        limit: Maximum questions to generate
    
    Returns:
        List of related questions
    """
    try:
        # Build conversation context
        conversation = ""
        for q, r in zip(queries[-3:], responses[-3:]):
            conversation += f"User: {q}\nAssistant: {r[:200]}...\n\n"
        
        prompt = f"""Based on this conversation history, suggest {limit} natural follow-up questions.

Conversation:
{conversation}

Generate {limit} questions that:
1. Build on what was discussed
2. Are specific and actionable
3. Help user explore related features
4. Are short (max 10 words each)

Return as JSON array: ["question1?", "question2?", "question3?"]"""

        response_gpt = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at guiding conversations. Generate specific follow-up questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
            timeout=5
        )
        
        content = response_gpt.choices[0].message.content.strip()
        
        # Parse JSON
        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        questions = json.loads(content)
        
        # Validate and clean
        validated = []
        for q in questions[:limit]:
            q = q.strip().strip('"').strip("'")
            if 5 <= len(q) <= 100:
                if not q.endswith('?'):
                    q += '?'
                validated.append(q)
        
        return validated
        
    except Exception as e:
        print(f"   ⚠️  Could not generate related questions batch: {e}")
        return []


# Singleton cache to avoid regenerating same questions
_question_cache = {}

def get_related_question_cached(query: str, response: str, main_topic: str = None, 
                                tenant_id: str = "default", verify_answerable: bool = True) -> Optional[str]:
    """
    Get related question with caching and answerability verification
    
    Args:
        query: User's question
        response: Bot's answer
        main_topic: Main topic
        tenant_id: Tenant identifier (for verification)
        verify_answerable: If True, verifies question can be answered (default: True)
    
    Returns:
        Related question or None
    """
    # Create cache key from query + main topic
    cache_key = f"{query[:50]}_{main_topic or ''}"
    
    if cache_key in _question_cache:
        cached_q = _question_cache[cache_key]
        print(f"   💨 Using cached related question: '{cached_q}'")
        return cached_q
    
    related_q = generate_related_question(query, response, main_topic)
    
    if related_q:
        # Verify question is answerable from documentation (OPTIONAL - can be disabled)
        if verify_answerable:
            print(f"   🔍 Verifying if question is answerable: '{related_q}'")
            is_answerable = verify_question_is_answerable(related_q, tenant_id)
            
            if not is_answerable:
                print(f"   ❌ Question not answerable from documentation: '{related_q}'")
                return None
            else:
                print(f"   ✅ Question verified as answerable: '{related_q}'")
        
        # Cache the verified question
        _question_cache[cache_key] = related_q
        # Limit cache size
        if len(_question_cache) > 100:
            # Remove oldest entry
            _question_cache.pop(next(iter(_question_cache)))
    
    return related_q

