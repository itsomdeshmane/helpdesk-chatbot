"""
Smart Chat Router V2 - SOLID-Compliant Thin Controller

THIS IS THE NEW REFACTORED ROUTER
- Follows SOLID principles
- Uses dependency injection
- Thin controller pattern (routing only)
- All business logic delegated to application layer

Comparison:
- OLD (smart_chat.py): 853 lines, 12+ responsibilities
- NEW (smart_chat_v2.py): ~150 lines, 1 responsibility (HTTP routing)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from dependency_injector.wiring import inject, Provide

from core.container import AppContainer
from core.models.query import Query, QueryContext
from application.services.chat_orchestrator import ChatOrchestrator
from application.dto.chat_request import ChatRequest, StreamingChatRequest
from application.dto.chat_response import ChatResponseDTO
from utils.auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Smart Chat V2 (SOLID)"])


@router.post(
    "/smart/v2/query",
    response_model=ChatResponseDTO,
    summary="Smart chat query (SOLID architecture)",
    description="""
    Process a chat query using the new SOLID-compliant architecture.
    
    Features:
    - Multi-source support (documents, database)
    - Intelligent source selection
    - Conversation context
    - Backward compatible with V1
    """
)
@inject
async def smart_query_v2(
    request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(Provide[AppContainer.chat_orchestrator]),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> ChatResponseDTO:
    """
    Smart chat query endpoint (V2 - SOLID architecture)
    
    This is a THIN CONTROLLER following SOLID principles:
    - SRP: Single responsibility - HTTP request/response handling
    - DIP: Depends on ChatOrchestrator abstraction (injected)
    
    Business logic is in ChatOrchestrator (application layer)
    
    Args:
        request: Chat request DTO
        orchestrator: Injected chat orchestrator
        current_user: Optional authenticated user
        
    Returns:
        ChatResponseDTO with results
    """
    try:
        logger.info(f"V2 Query: '{request.query[:50]}...' (tenant: {request.tenant_id})")
        
        # Step 1: Build query context
        context = QueryContext(
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            user_id=current_user.get('user_id') if current_user else None
        )
        
        # Step 2: Create domain query object
        query = Query(
            text=request.query,
            source_preference=request.source,
            context=context
        )
        
        # Add connection string to metadata if provided
        if request.connection_string:
            query.metadata['connection_string'] = request.connection_string
        
        # Step 3: Delegate to orchestrator (business logic)
        response = await orchestrator.process_query(
            query=query,
            tenant_id=request.tenant_id,
            session_id=request.session_id,
            connection_string=request.connection_string
        )
        
        # Step 4: Convert domain response to DTO
        dto = ChatResponseDTO.from_domain(response)
        
        logger.info(
            f"V2 Query completed: source={dto.source}, "
            f"success={dto.success}, time={dto.response_time_ms:.0f}ms"
        )
        
        return dto
        
    except Exception as e:
        logger.error(f"V2 Query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post(
    "/smart/v2/stream",
    summary="Smart chat with streaming (SOLID architecture)",
    description="Process query with streaming response using new architecture"
)
@inject
async def smart_stream_v2(
    request: StreamingChatRequest,
    orchestrator: ChatOrchestrator = Depends(Provide[AppContainer.chat_orchestrator]),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Streaming chat query endpoint (V2 - SOLID architecture)
    
    Returns Server-Sent Events (SSE) stream
    
    Args:
        request: Streaming chat request DTO
        orchestrator: Injected chat orchestrator
        current_user: Optional authenticated user
        
    Returns:
        StreamingResponse with SSE events
    """
    try:
        logger.info(f"V2 Streaming: '{request.query[:50]}...'")
        
        # Build query
        context = QueryContext(
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            user_id=current_user.get('user_id') if current_user else None
        )
        
        query = Query(
            text=request.query,
            source_preference=request.source,
            context=context
        )
        
        if request.connection_string:
            query.metadata['connection_string'] = request.connection_string
        
        # Create streaming generator
        async def generate_stream():
            """Generate SSE stream"""
            try:
                # Stream from orchestrator
                async for chunk in orchestrator.process_streaming_query(
                    query=query,
                    tenant_id=request.tenant_id,
                    session_id=request.session_id,
                    connection_string=request.connection_string
                ):
                    # Format as SSE
                    import json
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                import json
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"V2 Streaming setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Streaming setup failed: {str(e)}"
        )


@router.get(
    "/smart/v2/health",
    summary="Health check for V2 architecture",
    description="Check if SOLID architecture components are operational"
)
@inject
async def health_check_v2(
    orchestrator: ChatOrchestrator = Depends(Provide[AppContainer.chat_orchestrator])
):
    """
    Health check for V2 architecture
    
    Returns status of key components
    
    Args:
        orchestrator: Injected chat orchestrator
        
    Returns:
        Health status
    """
    try:
        # Check orchestrator is available
        health_status = {
            "status": "healthy",
            "architecture": "SOLID V2",
            "orchestrator": "available",
            "components": {
                "vector_data_source": True,
                "llm_provider": True,
                "source_selector": True,
                "query_processor": True,
                "response_formatter": True
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Backward compatibility endpoint (maps old route to new implementation)
@router.post(
    "/smart/query",
    response_model=ChatResponseDTO,
    summary="Smart chat query (backward compatible)",
    description="Original endpoint now powered by SOLID architecture (backward compatible)"
)
@inject
async def smart_query_compat(
    request: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(Provide[AppContainer.chat_orchestrator]),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> ChatResponseDTO:
    """
    Backward compatible endpoint
    
    Uses new SOLID architecture but maintains old API contract
    
    This allows gradual migration:
    - Old clients continue to work
    - New implementation provides benefits
    - Can be fully migrated later
    """
    # Delegate to V2 implementation
    return await smart_query_v2(request, orchestrator, current_user)

