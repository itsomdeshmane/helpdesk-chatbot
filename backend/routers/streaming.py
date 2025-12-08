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
        
        # Step 1: Enhance search query with conversation context (NEW FEATURE - with fallback)
        search_query = query
        conversation_context = ""
        has_context = conversation_history and len(conversation_history) > 0
        
        if has_context:
            # Build conversation context for the prompt
            conversation_context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-3:]:
                conversation_context += f"User: {msg.get('query', '')}\n"
                conversation_context += f"Assistant: {msg.get('response', '')[:200]}...\n\n"
            conversation_context += "Current question:\n"
            
            # Use AI-powered context resolution (NEW - optional enhancement)
            try:
                from utils.conversation_manager import get_conversation_manager
                conv_mgr = get_conversation_manager()
                context_summary = conv_mgr.get_context_summary(session_id, query)
                
                if context_summary:
                    # For search: append context to help find relevant docs
                    search_query = f"{context_summary} {query}"
                    print(f"   🔗 Resolved context: '{context_summary}'", flush=True)
                    print(f"   🔍 Enhanced search: '{query}' → '{search_query[:120]}...'", flush=True)
                else:
                    # Fallback: Check if this is a follow-up question
                    follow_up_indicators = ['it', 'this', 'that', 'these', 'those', 'explain', 'more', 'detail', 'step', 'how', 'why', 'what about']
                    query_words = query.lower().split()
                    is_follow_up = len(query_words) <= 5 or any(indicator in query.lower() for indicator in follow_up_indicators)
                    
                    if is_follow_up:
                        previous_query = conversation_history[-1].get('query', '')
                        if previous_query:
                            search_query = f"{previous_query} {query}"
                            print(f"   🔗 Follow-up detected, enhanced search: '{query}' → '{search_query[:120]}...'", flush=True)
            except Exception as e:
                # If context resolution fails, continue with original query (backward compatible)
                print(f"   ⚠️  Context resolution failed (using original query): {e}", flush=True)
                search_query = query
        
        # Step 2: Search for relevant documents using enhanced query
        yield f"data: {json.dumps({'type': 'status', 'message': 'Searching documentation...'})}\n\n"
        
        docs = await asyncio.to_thread(search, search_query, tenant_id)
        doc_count = len(docs) if docs else 0
        
        yield f"data: {json.dumps({'type': 'status', 'message': f'Found {doc_count} relevant documents'})}\n\n"
        
        # Prepare context
        context = "\n\n".join(docs) if docs else "No relevant documentation found."
        
        # Prepare prompts - STRICT: Only answer from document chunks
        system_prompt = """You are a helpdesk assistant that ONLY answers from the provided documentation.

CONTEXT RULES:
1. Pay attention to Previous Conversation to resolve pronouns ("this", "it", "that")
2. Stay on the SAME topic unless user explicitly changes it

🚨 ABSOLUTE RULES - YOU MUST FOLLOW:
1. ONLY use information EXPLICITLY written in the Documentation Context below
2. DO NOT use ANY external knowledge, training data, or general information
3. DO NOT make assumptions or infer anything not directly stated
4. DO NOT provide generic answers that could apply to any system
5. If the answer is NOT in the Documentation Context, respond EXACTLY with:
   "I don't have information about this in the loaded documentation. Please check if the relevant document has been uploaded or contact support."
6. Every single fact must come from the provided context
7. Use bullet points and clear formatting for lists
8. Be concise but complete

⚠️ NEVER MAKE UP OR GUESS INFORMATION - ONLY USE WHAT IS IN THE CONTEXT ⚠️"""

        # Check if we have meaningful context
        if not docs or doc_count == 0 or context == "No relevant documentation found.":
            # Try to find related topics and provide helpful hints (NEW FEATURE - optional)
            print(f"   ℹ️  No direct answer found, searching for related topics...", flush=True)
            try:
                from llm.related_topics_finder import generate_not_found_response_with_hints
                helpful_message = generate_not_found_response_with_hints(query, tenant_id)
            except Exception as e:
                print(f"   ⚠️  Could not find related topics: {e}", flush=True)
                helpful_message = "I do not have information about this in the loaded documentation. Please check if the relevant document has been uploaded or try rephrasing your question."
            
            # Stream the helpful message
            yield f"data: {json.dumps({'type': 'content', 'content': helpful_message})}\n\n"
            
            # Save to conversation history (without related question)
            if session_id:
                try:
                    from utils.conversation_manager import get_conversation_manager
                    conv_mgr = get_conversation_manager()
                    conv_mgr.save_message(
                        session_id=session_id,
                        query=query,
                        response=helpful_message,
                        module="General",
                        response_time=time.time() - start_time,
                        context_used=conversation_history if has_context else [],
                        main_topic=None  # No topic for "no answer"
                    )
                    print(f"   💾 No-answer message saved to session", flush=True)
                except Exception as e:
                    print(f"   ⚠️  Could not save message: {e}", flush=True)
            
            duration = int((time.time() - start_time) * 1000)
            yield f"data: {json.dumps({'type': 'complete', 'duration_ms': duration, 'doc_count': 0, 'has_related_question': False})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            # IMPORTANT: Return here - DO NOT generate related question
            return

        user_prompt = f"""{conversation_context}Documentation Context (USE ONLY THIS - DO NOT ADD EXTERNAL INFO):
{context[:8000]}

User Question: {query}

INSTRUCTIONS:
- Answer ONLY from the Documentation Context above
- If pronouns like "this", "it" are used, check Previous Conversation for context
- If the answer is NOT in the context, say "I don't have information about this in the loaded documentation"
- DO NOT add any external knowledge
- Format your response clearly with bullet points when listing steps or items"""

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
        
        # Extract main topic from query and response for context tracking (NEW FEATURE - optional)
        main_topic = None
        try:
            from utils.context_extractor import get_context_extractor
            extractor = get_context_extractor()
            context_data = extractor.extract_context(query, full_response)
            main_topic = context_data.get('main_topic', '') if context_data else None
            if main_topic:
                print(f"   🏷️  Extracted topic: '{main_topic}'", flush=True)
        except Exception as e:
            # Silently fail - context extraction is optional enhancement
            print(f"   ⚠️  Could not extract topic (continuing without it): {e}", flush=True)
            main_topic = None
        
        # Generate related question to guide conversation (NEW FEATURE - optional)
        # Do this BEFORE saving so we can include it in the saved response
        # ONLY if we have a real answer (not "no documentation" message)
        related_question = None
        
        # Skip related questions if this is a "no documentation" response
        is_no_doc_response = any(phrase in full_response.lower() for phrase in [
            "don't have information",
            "no information",
            "no documentation",
            "not found",
            "please check if the relevant document"
        ])
        
        if not is_no_doc_response:
            try:
                from llm.related_questions import get_related_question_cached
                # Pass tenant_id for answerability verification
                related_question = get_related_question_cached(
                    query, 
                    full_response, 
                    main_topic,
                    tenant_id=tenant_id,
                    verify_answerable=True  # Ensures question can be answered from docs
                )
                if related_question:
                    print(f"   💡 Generated related question: '{related_question}'", flush=True)
            except Exception as e:
                # Silently fail - this is optional enhancement
                print(f"   ⚠️  Could not generate related question (continuing without it): {e}", flush=True)
                related_question = None
        else:
            print(f"   ℹ️  Skipping related question generation (no documentation found)", flush=True)
        
        # Prepare full response with related question for saving
        response_to_save = full_response
        if related_question:
            separator = "\n\n---\n\n"
            question_text = f"💡 **You might also want to ask:** {related_question}"
            response_to_save = full_response + separator + question_text
        
        # Save message to conversation history (works with or without main_topic)
        if session_id:
            try:
                from utils.conversation_manager import get_conversation_manager
                conv_mgr = get_conversation_manager()
                context_to_save = conversation_history if has_context else []
                if main_topic:
                    print(f"   🏷️  Saving main topic for context: '{main_topic}'", flush=True)
                
                conv_mgr.save_message(
                    session_id=session_id,
                    query=query,
                    response=response_to_save,  # FIX: Save with related question included
                    module="General",
                    response_time=total_time,
                    context_used=context_to_save,
                    main_topic=main_topic  # Optional - will work even if None
                )
                print(f"   💾 Message saved to session", flush=True)
            except Exception as e:
                # Don't break the response if saving fails
                print(f"   ⚠️  Could not save message (non-critical): {e}", flush=True)
        
        # Stream the related question AFTER saving (NEW FEATURE - optional)
        if related_question:
            try:
                separator = "\n\n---\n\n"
                question_text = f"💡 **You might also want to ask:** {related_question}"
                
                # Stream separator
                yield f"data: {json.dumps({'type': 'content', 'content': separator})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for visual effect
                
                # Stream related question
                yield f"data: {json.dumps({'type': 'content', 'content': question_text})}\n\n"
                await asyncio.sleep(0)
            except Exception as e:
                print(f"   ⚠️  Could not stream related question: {e}", flush=True)
        
        # Send completion event with metadata
        yield f"data: {json.dumps({'type': 'complete', 'duration_ms': int(total_time * 1000), 'doc_count': doc_count, 'session_id': session_id, 'has_related_question': bool(related_question)})}\n\n"
        
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
            response_length=len(response_to_save),  # Include related question in length
            duration_ms=int(total_time * 1000),
            session_id=session_id,
            has_related_question=bool(related_question)
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
    
    # Get conversation manager
    conv_manager = get_conversation_manager()
    
    # Extract user_id and tenant_id from current_user if available (USER-SPECIFIC CONVERSATIONS)
    user_id = current_user.get('username') if current_user else None
    user_tenant_id = current_user.get('tenant_id', 'default') if current_user else 'default'
    
    # Override tenant_id if user is authenticated
    if current_user and user_tenant_id and user_tenant_id != 'default':
        tenant_id = user_tenant_id
        print(f"   🏢 Using user's tenant: {tenant_id}", flush=True)
    
    if user_id:
        print(f"   👤 User-specific conversation: {user_id} (Tenant: {tenant_id})", flush=True)
    
    # Create or validate session
    has_context = False
    conversation_history = []
    
    if not session_id:
        print("   Creating new session...", flush=True)
        session_id = conv_manager.create_session(tenant_id, user_id=user_id)
        print(f"   ✅ New session created: {session_id}", flush=True)
    else:
        # Check if session is valid
        if conv_manager.check_session_valid(session_id):
            print(f"   ✅ Using existing session: {session_id}", flush=True)
            # Get conversation history (user-specific with SECURITY CHECK)
            conversation_history = conv_manager.get_conversation_history(
                session_id,
                user_id=user_id  # Security: Validate session belongs to user
            )
            has_context = len(conversation_history) > 0
            if has_context:
                print(f"   📜 Found {len(conversation_history)} previous messages", flush=True)
            # Extend session
            conv_manager.extend_session(session_id)
        else:
            print("   ⚠️  Session expired, creating new one...", flush=True)
            session_id = conv_manager.create_session(tenant_id, user_id=user_id)
    
    logger.info(
        "Streaming request received",
        query_preview=query[:50],
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=user_id or "anonymous",  # FIX: Include user_id in log
        has_context=has_context
    )
    
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
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
            "X-Session-ID": session_id  # Send session ID to client
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

