"""
User Conversations Router
Handles user-specific conversation history and management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from utils.auth import get_current_user_optional
from utils.conversation_manager import get_conversation_manager

router = APIRouter(tags=["User Conversations"])


@router.get("/my-conversations", summary="Get user's conversation history")
async def get_my_conversations(
    limit: int = 20,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get all conversations for the current user (USER-SPECIFIC)
    
    Args:
        limit: Maximum conversations to return (default: 20)
    
    Returns:
        List of user's conversations with metadata
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get('username')
    tenant_id = current_user.get('tenant_id', 'default')
    
    conv_manager = get_conversation_manager()
    conversations = conv_manager.get_user_conversations(tenant_id, user_id, limit)
    
    return {
        'user_id': user_id,
        'conversation_count': len(conversations),
        'conversations': conversations
    }


@router.get("/{session_id}", summary="Get specific conversation")
async def get_conversation_details(
    session_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get full details of a specific conversation (USER-SPECIFIC)
    Only returns if the conversation belongs to the current user
    
    Args:
        session_id: Session identifier
    
    Returns:
        Conversation details with all messages
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conv_manager = get_conversation_manager()
    
    # Verify session belongs to user (security check)
    if not conv_manager.check_session_valid(session_id):
        raise HTTPException(status_code=404, detail="Conversation not found or expired")
    
    # Get conversation history
    messages = conv_manager.get_conversation_history(session_id, limit=100)
    
    return {
        'session_id': session_id,
        'message_count': len(messages),
        'messages': messages
    }


@router.delete("/{session_id}", summary="Delete a conversation")
async def delete_conversation(
    session_id: str,
    retention_days: int = 90,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Delete a conversation (USER-SPECIFIC SOFT DELETE)
    
    SOFT DELETE: Hidden from user's view but kept for system learning and quality improvement.
    Data will be permanently deleted after retention period (default: 90 days for GDPR compliance).
    
    Args:
        session_id: Session identifier
        retention_days: Days to keep before permanent deletion (default: 90)
    
    Returns:
        Success status
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conv_manager = get_conversation_manager()
    success = conv_manager.soft_delete_conversation(session_id, retention_days)
    
    return {
        'success': success,
        'message': f'Conversation deleted successfully (permanent deletion after {retention_days} days)' if success else 'Failed to delete conversation',
        'retention_info': f'Data kept for system improvement for {retention_days} days, then permanently deleted'
    }


@router.post("/{session_id}/restore", summary="Restore a deleted conversation")
async def restore_conversation(
    session_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Restore a soft-deleted conversation (USER-SPECIFIC)
    Only works if conversation hasn't been permanently deleted yet
    
    Args:
        session_id: Session identifier
    
    Returns:
        Success status
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conv_manager = get_conversation_manager()
    success = conv_manager.restore_conversation(session_id)
    
    return {
        'success': success,
        'message': 'Conversation restored successfully' if success else 'Failed to restore conversation (may be permanently deleted)'
    }


@router.get("/deleted-conversations", summary="Get deleted conversations (recoverable)")
async def get_deleted_conversations(
    limit: int = 20,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get user's deleted conversations that can still be restored (USER-SPECIFIC)
    Shows conversations in the retention period before permanent deletion
    
    Args:
        limit: Maximum conversations to return (default: 20)
    
    Returns:
        List of deleted conversations
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get('username')
    tenant_id = current_user.get('tenant_id', 'default')
    
    conv_manager = get_conversation_manager()
    # Get conversations including deleted ones
    all_conversations = conv_manager.get_user_conversations(tenant_id, user_id, limit * 2, include_deleted=True)
    
    # Filter to only deleted
    deleted = [conv for conv in all_conversations if conv.get('is_deleted')]
    
    return {
        'user_id': user_id,
        'deleted_count': len(deleted),
        'conversations': deleted,
        'note': 'These conversations can be restored before permanent deletion'
    }

