"""
Global Analytics Router
Provides insights from ALL users' conversations to improve system quality
Helps admins understand usage patterns and improve documentation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from utils.auth import get_current_user_optional
from utils.conversation_manager import get_conversation_manager

router = APIRouter(tags=["Global Analytics"])


@router.get("/common-questions", summary="Get most common questions across all users")
async def get_common_questions(
    limit: int = 10,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get most frequently asked questions across ALL users (GLOBAL LEARNING)
    Helps identify knowledge gaps and popular topics
    
    Args:
        limit: Maximum questions to return (default: 10)
    
    Returns:
        List of common questions with frequency
    """
    # Admin only feature (optional - remove if you want public access)
    if not current_user or current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tenant_id = current_user.get('tenant_id', 'default')
    conv_manager = get_conversation_manager()
    
    questions = conv_manager.get_global_common_questions(tenant_id, limit)
    
    return {
        'tenant_id': tenant_id,
        'question_count': len(questions),
        'common_questions': questions,
        'note': 'This data aggregates questions from all users to improve system quality'
    }


@router.get("/query-patterns", summary="Analyze query patterns across all users")
async def get_query_patterns(
    days: int = 30,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze query patterns across ALL users (GLOBAL ANALYTICS)
    Provides insights into system usage and performance
    
    Args:
        days: Number of days to analyze (default: 30)
    
    Returns:
        Analytics data including query counts, topics, and performance metrics
    """
    # Admin only feature
    if not current_user or current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tenant_id = current_user.get('tenant_id', 'default')
    conv_manager = get_conversation_manager()
    
    patterns = conv_manager.get_global_query_patterns(tenant_id, days)
    
    return {
        'tenant_id': tenant_id,
        'analytics': patterns,
        'note': 'This data aggregates patterns from all users to improve system quality'
    }


@router.get("/feedback-insights", summary="Learn from user feedback across all users")
async def get_feedback_insights(
    min_samples: int = 5,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze user feedback across ALL users (GLOBAL LEARNING)
    Identifies which responses need improvement
    
    Args:
        min_samples: Minimum feedback samples required (default: 5)
    
    Returns:
        Insights and suggestions for improvement
    """
    # Admin only feature
    if not current_user or current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tenant_id = current_user.get('tenant_id', 'default')
    conv_manager = get_conversation_manager()
    
    insights = conv_manager.learn_from_feedback(tenant_id, min_samples)
    
    return {
        'tenant_id': tenant_id,
        'insights_count': len(insights),
        'insights': insights,
        'note': 'This data uses feedback from all users to identify areas for improvement'
    }


@router.get("/system-health", summary="Get overall system health metrics")
async def get_system_health(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get overall system health and performance metrics (GLOBAL)
    
    Returns:
        System-wide statistics
    """
    # Admin only feature
    if not current_user or current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tenant_id = current_user.get('tenant_id', 'default')
    conv_manager = get_conversation_manager()
    
    # Get 7-day and 30-day patterns
    patterns_7d = conv_manager.get_global_query_patterns(tenant_id, 7)
    patterns_30d = conv_manager.get_global_query_patterns(tenant_id, 30)
    
    return {
        'tenant_id': tenant_id,
        'last_7_days': patterns_7d,
        'last_30_days': patterns_30d,
        'status': 'healthy',
        'note': 'Aggregated metrics from all users to monitor system performance'
    }


@router.post("/cleanup-old-data", summary="Permanently delete conversations past retention period")
async def cleanup_old_data(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Permanently delete conversations past their retention period (ADMIN ONLY)
    This is for GDPR compliance and data hygiene
    
    Deletes conversations that:
    - Were soft-deleted by users
    - Have passed their permanent_delete_after date
    
    Returns:
        Number of conversations permanently deleted
    """
    # Admin only feature
    if not current_user or current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tenant_id = current_user.get('tenant_id', 'default')
    conv_manager = get_conversation_manager()
    
    deleted_count = conv_manager.permanently_delete_old_conversations(tenant_id)
    
    return {
        'success': True,
        'deleted_count': deleted_count,
        'message': f'Permanently deleted {deleted_count} conversations past retention period',
        'note': 'This action is irreversible and complies with GDPR data retention policies'
    }

