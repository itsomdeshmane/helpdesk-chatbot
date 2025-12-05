"""
Feedback Router - Production Ready
Handles user feedback collection and analytics
"""

from fastapi import APIRouter, Body, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from utils.auth import get_current_user_optional
from utils.observability import get_logger

router = APIRouter(tags=["Feedback"])
logger = get_logger()


class FeedbackSubmission(BaseModel):
    """Feedback submission model"""
    message_id: str
    session_id: str
    helpful: bool
    rating: Optional[int] = None  # 1-5 star rating
    feedback_text: Optional[str] = None
    feedback_type: Optional[str] = "general"  # general, incorrect, incomplete, unclear
    query: Optional[str] = None
    response: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response model"""
    success: bool
    message: str
    feedback_id: Optional[str] = None


# In-memory feedback storage (in production, use database)
_feedback_store: List[dict] = []


@router.post("/submit", response_model=FeedbackResponse, summary="Submit user feedback")
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Submit feedback for a chatbot response.
    
    Args:
        feedback: Feedback submission data
        current_user: Optional authenticated user
    
    Returns:
        FeedbackResponse with success status
    """
    try:
        logger.info(
            "Feedback received",
            message_id=feedback.message_id,
            helpful=feedback.helpful,
            rating=feedback.rating
        )
        
        # Create feedback record
        feedback_record = {
            'id': f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(_feedback_store)}",
            'message_id': feedback.message_id,
            'session_id': feedback.session_id,
            'helpful': feedback.helpful,
            'rating': feedback.rating,
            'feedback_text': feedback.feedback_text,
            'feedback_type': feedback.feedback_type,
            'query': feedback.query,
            'response': feedback.response[:500] if feedback.response else None,
            'user_id': current_user.get('user_id') if current_user else None,
            'created_at': datetime.now().isoformat()
        }
        
        # Store feedback (in production, save to database)
        _feedback_store.append(feedback_record)
        
        # Also save to database if available
        try:
            from database.db_manager import db_manager
            _save_feedback_to_db(db_manager, feedback_record)
        except Exception as db_error:
            logger.warning(f"Could not save feedback to database: {db_error}")
        
        # Trigger analysis for negative feedback
        if not feedback.helpful or (feedback.rating and feedback.rating <= 2):
            await _analyze_negative_feedback(feedback_record)
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback!",
            feedback_id=feedback_record['id']
        )
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Get feedback statistics")
async def get_feedback_stats(
    tenant_id: str = "default",
    days: int = 30
):
    """
    Get aggregated feedback statistics.
    
    Args:
        tenant_id: Tenant identifier
        days: Number of days to analyze
    
    Returns:
        Feedback statistics
    """
    try:
        total = len(_feedback_store)
        if total == 0:
            return {
                'total_feedback': 0,
                'helpful_rate': 0.0,
                'average_rating': 0.0,
                'feedback_types': {},
                'recent_issues': []
            }
        
        helpful_count = sum(1 for f in _feedback_store if f.get('helpful'))
        ratings = [f.get('rating') for f in _feedback_store if f.get('rating')]
        
        # Count feedback types
        type_counts = {}
        for f in _feedback_store:
            ft = f.get('feedback_type', 'general')
            type_counts[ft] = type_counts.get(ft, 0) + 1
        
        # Get recent negative feedback
        negative_feedback = [
            f for f in _feedback_store 
            if not f.get('helpful') or (f.get('rating') and f.get('rating') <= 2)
        ][-10:]  # Last 10
        
        return {
            'total_feedback': total,
            'helpful_rate': helpful_count / total if total > 0 else 0.0,
            'average_rating': sum(ratings) / len(ratings) if ratings else 0.0,
            'feedback_types': type_counts,
            'recent_issues': [
                {
                    'query': f.get('query', '')[:100],
                    'feedback_text': f.get('feedback_text', ''),
                    'feedback_type': f.get('feedback_type'),
                    'created_at': f.get('created_at')
                }
                for f in negative_feedback
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export", summary="Export feedback data")
async def export_feedback(
    format: str = "json",
    limit: int = 1000
):
    """
    Export feedback data for analysis.
    
    Args:
        format: Export format (json or csv)
        limit: Maximum records to export
    
    Returns:
        Feedback data
    """
    try:
        data = _feedback_store[-limit:]
        
        if format == "csv":
            # Convert to CSV string
            if not data:
                return {"csv": "No data available"}
            
            headers = list(data[0].keys())
            rows = [",".join(headers)]
            
            for record in data:
                row = [str(record.get(h, '')).replace(',', ';') for h in headers]
                rows.append(",".join(row))
            
            return {"csv": "\n".join(rows)}
        else:
            return {"data": data, "count": len(data)}
            
    except Exception as e:
        logger.error(f"Failed to export feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _analyze_negative_feedback(feedback: dict):
    """
    Analyze negative feedback for improvement opportunities.
    
    Args:
        feedback: Feedback record
    """
    logger.info(
        "Analyzing negative feedback",
        message_id=feedback.get('message_id'),
        feedback_type=feedback.get('feedback_type')
    )
    
    # In production, this could:
    # 1. Send alerts to support team
    # 2. Trigger re-training or prompt adjustment
    # 3. Add to a review queue
    # 4. Update quality metrics
    
    # For now, just log it
    if feedback.get('feedback_text'):
        logger.warning(
            f"Negative feedback received: {feedback.get('feedback_text')[:200]}",
            query=feedback.get('query', '')[:100]
        )


def _save_feedback_to_db(db_manager, feedback: dict):
    """
    Save feedback to database.
    
    Args:
        db_manager: Database manager instance
        feedback: Feedback record
    """
    try:
        with db_manager.get_connection() as conn:
            conn.execute(
                """INSERT INTO feedback 
                   (message_id, session_id, helpful, rating, feedback_text, 
                    feedback_type, query_text, response_text, user_id, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    feedback.get('message_id'),
                    feedback.get('session_id'),
                    1 if feedback.get('helpful') else 0,
                    feedback.get('rating'),
                    feedback.get('feedback_text'),
                    feedback.get('feedback_type'),
                    feedback.get('query'),
                    feedback.get('response'),
                    feedback.get('user_id'),
                    datetime.now()
                )
            )
            conn.commit()
    except Exception as e:
        logger.warning(f"Database feedback save failed: {e}")

