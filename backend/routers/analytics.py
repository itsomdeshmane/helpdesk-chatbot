"""
Analytics endpoints
"""
from fastapi import APIRouter, Query
from database.db_manager import db_manager

router = APIRouter(tags=["Analytics"])

@router.get("/chat-history", summary="Get chat history")
def get_chat_history(
    tenant_id: str = Query("default", description="Tenant ID"),
    limit: int = Query(50, description="Number of messages to return")
):
    """Get recent chat history for a tenant"""
    try:
        interactions = db_manager.get_recent_interactions(tenant_id, limit)
        return {
            "status": "success",
            "count": len(interactions),
            "interactions": interactions
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "interactions": []
        }


@router.get("/stats", summary="Get system statistics")
def get_stats():
    """Get overall system statistics"""
    try:
        with db_manager.get_connection() as conn:
            # Total interactions
            cursor = conn.execute("SELECT COUNT(*) as count FROM chat_interactions")
            total_interactions = cursor.fetchone()['count']
            
            # Most popular modules
            cursor = conn.execute("""
                SELECT module, COUNT(*) as count 
                FROM chat_interactions 
                WHERE module IS NOT NULL
                GROUP BY module 
                ORDER BY count DESC 
                LIMIT 5
            """)
            popular_modules = [dict(row) for row in cursor.fetchall()]
            
            # Average response time
            cursor = conn.execute("""
                SELECT AVG(response_time) as avg_time 
                FROM chat_interactions 
                WHERE response_time IS NOT NULL
            """)
            avg_time = cursor.fetchone()['avg_time']
            
            return {
                "status": "success",
                "stats": {
                    "total_interactions": total_interactions,
                    "popular_modules": popular_modules,
                    "average_response_time": round(avg_time, 2) if avg_time else 0
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/faq", summary="Get frequently asked questions")
def get_frequently_asked_questions(
    limit: int = Query(10, description="Number of FAQs to return", ge=1, le=50),
    module: str = Query(None, description="Filter by module"),
    tenant_id: str = Query("default", description="Tenant ID")
):
    """
    Analyze chat history and return the most frequently asked questions.
    Groups similar questions together and returns top N by frequency.
    """
    try:
        with db_manager.get_connection() as conn:
            # Build query based on filters
            query = """
                SELECT 
                    LOWER(TRIM(query)) as normalized_query,
                    query as original_query,
                    module,
                    COUNT(*) as frequency,
                    MAX(created_at) as last_asked
                FROM chat_interactions
                WHERE tenant_id = ?
                    AND LENGTH(query) > 10
            """
            params = [tenant_id]
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            query += """
                GROUP BY normalized_query
                ORDER BY frequency DESC, last_asked DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor = conn.execute(query, params)
            results = cursor.fetchall()
            
            # Format FAQs
            faqs = []
            for row in results:
                faqs.append({
                    "question": row['original_query'],
                    "frequency": row['frequency'],
                    "module": row['module'],
                    "last_asked": row['last_asked']
                })
            
            return {
                "status": "success",
                "count": len(faqs),
                "faqs": faqs
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "faqs": []
        }


