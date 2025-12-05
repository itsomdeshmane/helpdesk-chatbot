"""
Enhanced RAG Module - Production Ready
Integrates all advanced features: hybrid search, caching, quality scoring, etc.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, GPT_MODEL
from typing import List, Dict, Optional, Tuple
import time
import hashlib

# Import new modules
from llm.hybrid_search import get_hybrid_search_engine, SearchResult
from llm.query_rewriter import rewrite_query_for_search, extract_keywords, generate_search_queries
from llm.cache_manager import get_cache_manager
from llm.answer_quality import score_answer_quality, detect_hallucination, generate_escalation_message
from llm.source_attribution import format_response_with_sources, get_source_attributor
from llm.suggestion_generator import get_suggested_questions, get_proactive_tips
from utils.observability import get_logger, log_operation, timed_operation

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0, max_retries=2)
logger = get_logger()
cache_manager = get_cache_manager()

# Pinecone initialization
pinecone_available = False
pinecone_index = None

if PINECONE_API_KEY:
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_available = True
        if PINECONE_INDEX_NAME:
            try:
                pinecone_index = pc.Index(PINECONE_INDEX_NAME)
                logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
            except Exception as e:
                logger.warning(f"Could not connect to Pinecone index: {e}")
    except Exception as e:
        logger.warning(f"Could not initialize Pinecone: {e}")


@log_operation("enhanced_search")
def enhanced_search(
    query: str,
    tenant_id: str,
    conversation_history: List[Dict] = None,
    use_hybrid: bool = True,
    use_query_rewrite: bool = True,
    use_cache: bool = True
) -> Tuple[List[Dict], Dict]:
    """
    Enhanced search with hybrid retrieval, query rewriting, and caching.
    
    Args:
        query: User query
        tenant_id: Tenant identifier
        conversation_history: Previous conversation for context
        use_hybrid: Whether to use hybrid (BM25 + vector) search
        use_query_rewrite: Whether to rewrite/expand the query
        use_cache: Whether to use cached results
    
    Returns:
        Tuple of (search results, metadata)
    """
    search_metadata = {
        'original_query': query,
        'rewritten_query': None,
        'cache_hit': False,
        'search_type': 'vector',
        'result_count': 0,
        'search_time_ms': 0
    }
    
    start_time = time.time()
    
    # Step 1: Check cache
    if use_cache:
        cached_results = cache_manager.get_search_results(query, tenant_id)
        if cached_results:
            search_metadata['cache_hit'] = True
            search_metadata['result_count'] = len(cached_results)
            search_metadata['search_time_ms'] = (time.time() - start_time) * 1000
            logger.info("Search cache hit", query_preview=query[:50])
            return cached_results, search_metadata
    
    # Step 2: Query rewriting (if enabled)
    search_query = query
    if use_query_rewrite and conversation_history:
        rewritten = rewrite_query_for_search(query, conversation_history)
        if rewritten != query:
            search_query = rewritten
            search_metadata['rewritten_query'] = rewritten
            logger.debug(f"Query rewritten: '{query[:50]}' -> '{rewritten[:50]}'")
    
    # Step 3: Vector search
    vector_results = _vector_search(search_query, tenant_id)
    
    # Step 4: Hybrid search (if enabled and we have results)
    if use_hybrid and vector_results:
        search_metadata['search_type'] = 'hybrid'
        hybrid_engine = get_hybrid_search_engine()
        
        # Convert vector results to proper format
        vector_dicts = [
            {
                'text': r.get('text', ''),
                'score': r.get('score', 0.0),
                'source': r.get('filename', 'unknown'),
                'section': r.get('module', ''),
                'chunk_id': r.get('chunk_id'),
                'metadata': r
            }
            for r in vector_results
        ]
        
        # Perform hybrid search
        hybrid_results = hybrid_engine.hybrid_search(
            query=search_query,
            vector_results=vector_dicts,
            tenant_id=tenant_id,
            top_k=5,
            alpha=0.6  # 60% vector, 40% BM25
        )
        
        # Convert back to list of dicts
        results = [
            {
                'text': r.text,
                'score': r.score,
                'source': r.source,
                'section': r.section,
                'chunk_id': r.chunk_id,
                'search_type': r.search_type,
                'module': r.metadata.get('module', '') if r.metadata else ''
            }
            for r in hybrid_results
        ]
    else:
        results = vector_results
    
    # Step 5: Cache results
    if use_cache and results:
        cache_manager.set_search_results(query, tenant_id, results)
    
    search_metadata['result_count'] = len(results)
    search_metadata['search_time_ms'] = (time.time() - start_time) * 1000
    
    logger.info(
        "Search completed",
        result_count=len(results),
        search_type=search_metadata['search_type'],
        cache_hit=search_metadata['cache_hit'],
        duration_ms=search_metadata['search_time_ms']
    )
    
    return results, search_metadata


def _vector_search(query: str, tenant_id: str, top_k: int = 5) -> List[Dict]:
    """Perform vector search using Pinecone or fallback"""
    
    if pinecone_available and pinecone_index:
        try:
            # Get embedding (with caching)
            embedding = cache_manager.get_or_create_embedding(
                query,
                lambda q: _create_embedding(q)
            )
            
            # Search Pinecone
            results = pinecone_index.query(
                vector=embedding,
                filter={"tenant_id": tenant_id},
                top_k=top_k,
                include_metadata=True
            )
            
            matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
            
            return [
                {
                    'text': m.metadata.get('text', '') if hasattr(m, 'metadata') else m.get('metadata', {}).get('text', ''),
                    'score': m.score if hasattr(m, 'score') else m.get('score', 0),
                    'filename': m.metadata.get('filename', 'unknown') if hasattr(m, 'metadata') else m.get('metadata', {}).get('filename', 'unknown'),
                    'module': m.metadata.get('module', '') if hasattr(m, 'metadata') else m.get('metadata', {}).get('module', ''),
                    'chunk_id': m.metadata.get('chunk_id') if hasattr(m, 'metadata') else m.get('metadata', {}).get('chunk_id')
                }
                for m in matches if m
            ]
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
    
    # Fallback to in-memory search
    return _in_memory_search(query, tenant_id, top_k)


def _create_embedding(text: str) -> List[float]:
    """Create embedding using OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-3-small",  # Upgraded model
        input=text
    )
    return response.data[0].embedding


def _in_memory_search(query: str, tenant_id: str, top_k: int = 5) -> List[Dict]:
    """Fallback in-memory keyword search"""
    from llm.rag import in_memory_docs
    
    if not in_memory_docs:
        return []
    
    query_keywords = extract_keywords(query)
    query_set = set(query_keywords)
    
    scored_docs = []
    for doc in in_memory_docs:
        if doc.get('tenant_id') != tenant_id:
            continue
        
        text_keywords = set(extract_keywords(doc.get('text', '')))
        overlap = len(query_set & text_keywords)
        
        if overlap > 0:
            score = overlap / max(len(query_set), 1)
            scored_docs.append({
                'text': doc.get('text', ''),
                'score': score,
                'filename': doc.get('filename', 'unknown'),
                'module': doc.get('module', ''),
                'chunk_id': doc.get('chunk_id')
            })
    
    scored_docs.sort(key=lambda x: x['score'], reverse=True)
    return scored_docs[:top_k]


@log_operation("enhanced_generate_response")
def enhanced_generate_response(
    query: str,
    search_results: List[Dict],
    tenant_id: str = "default",
    conversation_history: List[Dict] = None,
    include_sources: bool = True,
    include_suggestions: bool = True,
    score_quality: bool = True
) -> Dict:
    """
    Generate an enhanced response with quality scoring and source attribution.
    
    Args:
        query: User query
        search_results: Results from enhanced_search
        tenant_id: Tenant identifier
        conversation_history: Previous conversation
        include_sources: Whether to include source citations
        include_suggestions: Whether to include follow-up suggestions
        score_quality: Whether to score response quality
    
    Returns:
        Dictionary with response, module, sources, suggestions, quality score
    """
    start_time = time.time()
    
    # Build context from search results
    context_parts = [r.get('text', '') for r in search_results if r.get('text')]
    context = "\n\n".join(context_parts)
    
    if not context:
        context = "No relevant documentation found."
    
    # Build conversation context
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-3:]:
            conversation_context += f"User: {msg.get('query', '')}\n"
            conversation_context += f"Assistant: {msg.get('response', '')[:200]}...\n\n"
    
    # Prepare prompts
    system_prompt = _get_system_prompt()
    user_prompt = f"""{conversation_context}Documentation Context:
{context[:5000]}

User Question: {query}

INSTRUCTIONS:
- Answer STRICTLY using ONLY the information from the Documentation Context
- DO NOT use any external knowledge
- If the answer is not in the context, say: "I don't have this information in the current documentation."
- Use clear formatting with bullet points where appropriate"""

    # Generate response
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=500,
            timeout=30
        )
        
        content = response.choices[0].message.content
        answer = content.strip()
        
        generation_time = time.time() - start_time
        
        # Build result
        result = {
            'response': answer,
            'module': module,
            'generation_time_ms': generation_time * 1000
        }
        
        # Add source attribution
        if include_sources and search_results:
            source_data = format_response_with_sources(
                answer, search_results, query, include_citations=True
            )
            result['sources'] = source_data.get('sources', [])
            result['citation_text'] = source_data.get('citation_text', '')
            result['response'] = answer + source_data.get('citation_text', '')
        
        # Add suggested follow-up questions
        if include_suggestions:
            suggestions = get_suggested_questions(
                query, module, conversation_history, num_suggestions=3
            )
            result['suggested_questions'] = suggestions
            
            # Add proactive tips
            tips = get_proactive_tips(query, answer, module)
            result['tips'] = tips
        
        # Score response quality
        if score_quality:
            quality = score_answer_quality(query, context, answer, use_ai=False)
            result['quality_score'] = quality.to_dict()
            
            # Add escalation message if needed
            if quality.needs_escalation:
                escalation_msg = generate_escalation_message(query, quality)
                if escalation_msg:
                    result['escalation_message'] = escalation_msg
                    result['needs_escalation'] = True
        
        logger.info(
            "Response generated",
            query_length=len(query),
            response_length=len(answer),
            module=module,
            duration_ms=generation_time * 1000
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return {
            'response': f"I apologize, but I encountered an error processing your request. Please try again.",
            'module': 'General',
            'error': str(e)
        }


def _get_system_prompt() -> str:
    """Get the system prompt for response generation"""
    return """You are a helpful AI assistant for the helpdesk system.

CRITICAL RULES - MUST FOLLOW:
1. ONLY use information from the provided Documentation Context
2. DO NOT use your general knowledge or external training data
3. DO NOT make assumptions or infer information not explicitly stated
4. If the context doesn't contain the answer, respond with: "I don't have this information in the current documentation."
5. Extract ALL relevant details from the context
6. For lists, include EVERYTHING mentioned - don't skip items
7. Use clear, simple language
8. Use bullet points and formatting for clarity

⚠️ NEVER HALLUCINATE OR MAKE UP INFORMATION ⚠️"""


def full_rag_pipeline(
    query: str,
    tenant_id: str = "default",
    session_id: str = None,
    conversation_history: List[Dict] = None,
    config: Dict = None
) -> Dict:
    """
    Complete RAG pipeline with all enhancements.
    
    Args:
        query: User query
        tenant_id: Tenant identifier
        session_id: Session ID for tracking
        conversation_history: Previous messages
        config: Optional configuration overrides
    
    Returns:
        Complete response dictionary
    """
    config = config or {}
    
    with logger.context(
        tenant_id=tenant_id,
        session_id=session_id,
        operation="full_rag_pipeline"
    ):
        logger.info("Starting RAG pipeline", query_preview=query[:50])
        
        pipeline_start = time.time()
        
        # Step 1: Enhanced search
        search_results, search_metadata = enhanced_search(
            query=query,
            tenant_id=tenant_id,
            conversation_history=conversation_history,
            use_hybrid=config.get('use_hybrid', True),
            use_query_rewrite=config.get('use_query_rewrite', True),
            use_cache=config.get('use_cache', True)
        )
        
        # Step 2: Generate response
        response = enhanced_generate_response(
            query=query,
            search_results=search_results,
            tenant_id=tenant_id,
            conversation_history=conversation_history,
            include_sources=config.get('include_sources', True),
            include_suggestions=config.get('include_suggestions', True),
            score_quality=config.get('score_quality', True)
        )
        
        # Add search metadata
        response['search_metadata'] = search_metadata
        response['total_time_ms'] = (time.time() - pipeline_start) * 1000
        
        logger.info(
            "RAG pipeline completed",
            total_time_ms=response['total_time_ms'],
            result_count=search_metadata['result_count']
        )
        
        return response

