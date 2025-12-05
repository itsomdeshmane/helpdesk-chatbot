"""
Streaming Router - Production Ready
Provides Server-Sent Events (SSE) for real-time response streaming
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, AsyncGenerator
from utils.auth import get_current_user_optional
from utils.observability import get_logger
from utils.conversation_manager import get_conversation_manager
from llm.rag import search
from config import OPENAI_API_KEY, GPT_MODEL
from openai import OpenAI
import asyncio
import json
import time

router = APIRouter(tags=["Streaming"])
logger = get_logger()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


async def generate_streaming_response(
    query: str,
    tenant_id: str,
    session_id: str = None,
    conversation_history: list = None
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response using Server-Sent Events format.
    
    Args:
        query: User query
        tenant_id: Tenant identifier
        session_id: Session ID for context
        conversation_history: Previous conversation messages
    
    Yields:
        SSE formatted data chunks
    """
    start_time = time.time()
    
    try:
        # Send initial event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your question...'})}\n\n"
        
        # Step 1: Enhance search query with conversation context
        search_query = query
        conversation_context = ""
        previous_topic = ""
        
        if conversation_history and len(conversation_history) > 0:
            # Build conversation context for the prompt
            conversation_context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-3:]:
                conversation_context += f"User: {msg.get('query', '')}\n"
                conversation_context += f"Assistant: {msg.get('response', '')[:200]}...\n\n"
            
            # Get previous topic for search enhancement
            last_msg = conversation_history[-1]
            previous_topic = last_msg.get('query', '')
            
            # Check if current query is a follow-up (short or contains pronouns)
            follow_up_indicators = ['it', 'this', 'that', 'these', 'those', 'explain', 'more', 'detail', 'step', 'how', 'why', 'what about']
            query_words = query.lower().split()
            is_follow_up = len(query_words) <= 5 or any(indicator in query.lower() for indicator in follow_up_indicators)
            
            if is_follow_up and previous_topic:
                # Combine previous topic with current query for better search
                search_query = f"{previous_topic} {query}"
                print(f"   🔗 Enhanced search query: '{query}' → '{search_query}'", flush=True)
        
        # Step 2: Search for relevant documents using enhanced query
        yield f"data: {json.dumps({'type': 'status', 'message': 'Searching documentation...'})}\n\n"
        
        docs = await asyncio.to_thread(search, search_query, tenant_id)
        doc_count = len(docs) if docs else 0
        
        yield f"data: {json.dumps({'type': 'status', 'message': f'Found {doc_count} relevant documents'})}\n\n"
        
        # Prepare context
        context = "\n\n".join(docs) if docs else "No relevant documentation found."
        
        # Prepare prompts - STRICT: Only answer from document chunks
        system_prompt = """You are a helpdesk assistant that ONLY answers questions using the provided documentation.

🚨 ABSOLUTE RULES - MUST FOLLOW:
1. ONLY use information that is EXPLICITLY stated in the Documentation Context below
2. DO NOT use ANY external knowledge, training data, or general information
3. DO NOT make assumptions or infer information not directly written in the context
4. DO NOT provide generic answers that could apply to any system
5. If the documentation context does NOT contain the specific answer, you MUST respond with:
   "I don't have information about this in the loaded documentation. Please check if the relevant document has been uploaded or contact support."
6. Every fact in your answer MUST come directly from the provided context
7. Use clear formatting with bullet points where appropriate
8. Be comprehensive - include all relevant details from the documentation

⚠️ NEVER MAKE UP INFORMATION - ONLY USE WHAT IS IN THE CONTEXT ⚠️"""

        # Check if we have meaningful context
        if not docs or doc_count == 0 or context == "No relevant documentation found.":
            no_docs_message = "I do not have information about this in the loaded documentation. Please check if the relevant document has been uploaded or try rephrasing your question."
            yield f"data: {json.dumps({'type': 'content', 'content': no_docs_message})}\n\n"
            duration = int((time.time() - start_time) * 1000)
            yield f"data: {json.dumps({'type': 'complete', 'duration_ms': duration, 'doc_count': 0})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        user_prompt = f"""{conversation_context}Documentation Context (USE ONLY THIS INFORMATION):
{context[:4000]}

User Question: {query}

INSTRUCTIONS:
- Answer ONLY using information from the Documentation Context above
- If the answer is NOT in the context, say "I don't have information about this in the loaded documentation"
- DO NOT add any information from outside the provided context
- Be specific and quote relevant parts when possible"""

        # Step 2: Stream the response
        yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
        
        # Start streaming from OpenAI
        stream = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=500,
            stream=True
        )
        
        full_response = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                
                if content.strip():
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                    await asyncio.sleep(0)  # Allow other tasks to run
        
        # Calculate timing
        total_time = time.time() - start_time
        
        # Send completion event with metadata
        yield f"data: {json.dumps({'type': 'complete', 'duration_ms': int(total_time * 1000), 'doc_count': doc_count})}\n\n"
        
        # Send sources if available
        if docs:
            sources = []
            for i, doc in enumerate(docs[:3]):
                sources.append({
                    'index': i + 1,
                    'preview': doc[:100] + '...' if len(doc) > 100 else doc
                })
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        
        logger.info(
            "Streaming response completed",
            query_length=len(query),
            response_length=len(full_response),
            duration_ms=int(total_time * 1000)
        )
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    finally:
        yield f"data: {json.dumps({'type': 'done'})}\n\n"


@router.post("/query/stream", summary="Stream chat response with SSE")
async def chat_stream(
    query: str = Body(..., embed=True),
    tenant_id: str = Body("default", embed=True),
    session_id: str = Body(None, embed=True),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Stream a chat response using Server-Sent Events.
    
    Args:
        query: User question
        tenant_id: Tenant identifier
        session_id: Optional session ID for conversation continuity
    
    Returns:
        StreamingResponse with SSE data
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    logger.info(
        "Streaming request received",
        query_preview=query[:50],
        tenant_id=tenant_id,
        session_id=session_id or "new"
    )
    
    # Get conversation history if session exists
    conversation_history = []
    conv_manager = get_conversation_manager()
    
    if session_id:
        try:
            conversation_history = conv_manager.get_conversation_history(session_id)
        except Exception as e:
            logger.warning(f"Could not get conversation history: {e}")
    
    # Create and return streaming response
    return StreamingResponse(
        generate_streaming_response(
            query=query,
            tenant_id=tenant_id,
            session_id=session_id,
            conversation_history=conversation_history
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )


@router.get("/health", summary="Check streaming endpoint health")
async def streaming_health():
    """Health check for streaming endpoint"""
    return {
        "status": "healthy",
        "streaming_available": True,
        "model": GPT_MODEL
    }

