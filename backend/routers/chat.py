from fastapi import APIRouter, Body, Depends
from typing import Optional
from llm.rag import search, generate_response_with_module_with_context
from utils.conversation_manager import get_conversation_manager
from utils.auth import get_current_user_optional
import asyncio
import time
import sys

router = APIRouter(tags=["Chat"])

@router.post("/query", summary="Send a chat query with conversation context")
async def chat(
    query: str = Body(...), 
    tenant_id: str = Body(...),
    session_id: str = Body(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Handle chat queries with conversation context support
    
    Args:
        query: User question
        tenant_id: Tenant identifier  
        session_id: Optional session ID for conversation continuity
                   If None, a new session is created
    
    Returns:
        {
            "response": str,
            "session_id": str,
            "has_context": bool
        }
    """
    start_time = time.time()
    print("\n" + "="*80, flush=True)
    print(f"🔵 NEW REQUEST RECEIVED", flush=True)
    print(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}", flush=True)
    print(f"   Tenant ID: {tenant_id}", flush=True)
    print(f"   Session ID: {session_id or 'NEW SESSION'}", flush=True)
    if current_user:
        print(f"   👤 User: {current_user['username']} (Role: {current_user['role']})", flush=True)
    else:
        print(f"   👤 User: Anonymous", flush=True)
    print(f"   Time: {time.strftime('%H:%M:%S')}", flush=True)
    print("="*80, flush=True)
    sys.stdout.flush()
    
    # Get conversation manager
    conv_manager = get_conversation_manager()
    
    try:
        # Step 0: Manage conversation session
        print("\n🔐 STEP 0: Managing conversation session...", flush=True)
        has_context = False
        conversation_history = []
        
        # Create or validate session
        if not session_id:
            print("   Creating new session...", flush=True)
            session_id = conv_manager.create_session(tenant_id)
            print(f"   ✅ New session created: {session_id}", flush=True)
        else:
            # Check if session is valid
            if conv_manager.check_session_valid(session_id):
                print(f"   ✅ Using existing session: {session_id}", flush=True)
                # Get conversation history
                conversation_history = conv_manager.get_conversation_history(session_id)
                has_context = len(conversation_history) > 0
                if has_context:
                    print(f"   📜 Found {len(conversation_history)} previous messages", flush=True)
                # Extend session
                conv_manager.extend_session(session_id)
            else:
                print("   ⚠️  Session expired, creating new one...", flush=True)
                session_id = conv_manager.create_session(tenant_id)
        
        sys.stdout.flush()
        
        # Step 1: Search for relevant documents
        print("\n📚 STEP 1: Searching for relevant documents...", flush=True)
        sys.stdout.flush()
        search_start = time.time()
        
        # Enhance query with conversation context if available
        search_query = query
        if has_context and conversation_history:
            # Try AI-powered context resolution first
            context_summary = conv_manager.get_context_summary(session_id, query)
            
            if context_summary:
                # For search: append context to help find relevant docs
                search_query = f"{context_summary} {query}"
                print(f"   🔗 Resolved context: '{context_summary}'", flush=True)
                print(f"   🔍 Enhanced search: '{query}' → '{search_query[:120]}...'", flush=True)
            else:
                # Fallback: Check if this is a follow-up question (short or contains pronouns)
                follow_up_indicators = ['it', 'this', 'that', 'these', 'those', 'explain', 'more', 'detail', 'step', 'how', 'why', 'what about']
                query_words = query.lower().split()
                is_follow_up = len(query_words) <= 5 or any(indicator in query.lower() for indicator in follow_up_indicators)
                
                if is_follow_up:
                    # Combine with previous query for better search
                    previous_query = conversation_history[-1].get('query', '')
                    if previous_query:
                        search_query = f"{previous_query} {query}"
                        print(f"   🔗 Follow-up detected, enhanced search: '{query}' → '{search_query[:120]}...'", flush=True)
                    else:
                        print(f"   ℹ️  No context resolution needed", flush=True)
                else:
                    print(f"   ℹ️  No context resolution needed", flush=True)
        
        docs_task = asyncio.create_task(asyncio.to_thread(search, search_query, tenant_id))
        
        # Get search results
        docs = await docs_task
        search_time = time.time() - search_start
        print(f"✅ Document search completed in {search_time:.2f}s", flush=True)
        print(f"   Found {len(docs)} document chunks", flush=True)
        for i, doc in enumerate(docs[:2], 1):
            preview = doc[:80].replace('\n', ' ')
            print(f"   Doc {i} preview: {preview}...", flush=True)
        sys.stdout.flush()
        
        doc_context = "\n".join(docs)
        
        # Step 2: Generate response with conversation context
        print("\n🤖 STEP 2: Generating AI response (with conversation context)...", flush=True)
        sys.stdout.flush()
        generation_start = time.time()
        
        result = await asyncio.to_thread(
            generate_response_with_module_with_context,
            query, 
            doc_context, 
            tenant_id,
            conversation_history
        )
        
        generation_time = time.time() - generation_start
        print(f"✅ Response generation completed in {generation_time:.2f}s", flush=True)
        print(f"   Response length: {len(result.get('response', ''))} characters", flush=True)
        sys.stdout.flush()
        
        # Step 3: Save to conversation history
        print("\n💾 STEP 3: Saving to conversation history...", flush=True)
        total_time = time.time() - start_time
        
        conv_manager.save_message(
            session_id=session_id,
            query=query,
            response=result.get('response', ''),
            module="General",
            response_time=total_time,
            context_used=conversation_history if has_context else None
        )
        print(f"   ✅ Message saved to session", flush=True)
        
        print("\n" + "="*80, flush=True)
        print(f"✅ REQUEST COMPLETED SUCCESSFULLY", flush=True)
        print(f"   Total time: {total_time:.2f}s", flush=True)
        print(f"   Breakdown: Search={search_time:.2f}s, Generation={generation_time:.2f}s", flush=True)
        print(f"   Conversation context: {'Yes' if has_context else 'No'}", flush=True)
        print("="*80 + "\n", flush=True)
        sys.stdout.flush()
        
        return {
            "response": result.get("response", ""),
            "session_id": session_id,
            "has_context": has_context
        }
    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "="*80, flush=True)
        print(f"❌ ERROR IN REQUEST (after {error_time:.2f}s)", flush=True)
        print(f"   Error: {str(e)}", flush=True)
        print("="*80 + "\n", flush=True)
        sys.stdout.flush()
        return {
            "response": "I apologize, but I encountered an error processing your request. Please make sure the backend services are properly configured.",
            "session_id": session_id if 'session_id' in locals() else None,
            "has_context": False
        }


@router.post("/end-session", summary="End a conversation session")
async def end_session(session_id: str = Body(...)):
    """
    End a conversation session (user closes chat)
    
    Args:
        session_id: Session identifier
    
    Returns:
        Success status
    """
    conv_manager = get_conversation_manager()
    success = conv_manager.end_session(session_id)
    
    return {
        "success": success,
        "message": "Session ended" if success else "Failed to end session"
    }


@router.get("/conversation-history/{session_id}", summary="Get conversation history")
async def get_history(session_id: str, limit: int = 10):
    """
    Get conversation history for a session
    
    Args:
        session_id: Session identifier
        limit: Maximum messages to return
    
    Returns:
        List of messages
    """
    conv_manager = get_conversation_manager()
    history = conv_manager.get_conversation_history(session_id, limit)
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": history
    }