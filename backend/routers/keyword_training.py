"""
Keyword Training Router - Endpoints for learning and managing keywords
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Dict, Any
from utils.auth import get_current_user
from llm.keyword_learner import get_keyword_learner, get_keyword_cache
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/keywords", tags=["keywords"])

db_manager = DatabaseManager()


@router.post("/train")
async def train_keywords(
    sample_limit: int = Body(100, description="Max rows to sample per table"),
    connection_string: Optional[str] = Body(None, description="Optional connection string"),
    current_user: dict = Depends(get_current_user)
):
    """
    Train/learn keywords from the database
    
    This endpoint analyzes the database schema and data to extract keywords
    for intelligent query classification.
    
    GENERIC - Works with any database schema
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id", "default")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Starting keyword training for user {user_id}")
        
        # Get user's connection string if not provided
        if not connection_string:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT host, port, database_name, username, encrypted_password
                    FROM user_database_connections
                    WHERE user_id = %s AND tenant_id = %s
                    LIMIT 1
                """, (user_id, tenant_id))
                
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail="No database connection found. Please configure your database connection in Settings first."
                    )
                
                # Decrypt password
                from utils.encryption import decrypt_value
                host, port, db_name, username, encrypted_pwd = result
                password = decrypt_value(encrypted_pwd)
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
        
        # Run keyword learning
        learner = get_keyword_learner()
        stats = await learner.learn_from_database(
            user_id=user_id,
            tenant_id=tenant_id,
            connection_string=connection_string,
            sample_limit=sample_limit
        )
        
        # Force cache refresh
        cache = get_keyword_cache()
        await cache.get_keywords(user_id, tenant_id, force_refresh=True)
        
        return {
            "success": True,
            "message": "Keyword training completed successfully",
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"Error training keywords: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Keyword training failed: {str(e)}")


@router.get("/list")
async def list_keywords(
    keyword_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List learned keywords for the current user
    
    Args:
        keyword_type: Filter by type (location, entity, category, other)
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id", "default")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        cache = get_keyword_cache()
        keywords = await cache.get_keywords(user_id, tenant_id, keyword_type)
        
        # Count by type
        counts = {k: len(v) for k, v in keywords.items()}
        
        return {
            "success": True,
            "keywords": keywords,
            "counts": counts
        }
    
    except Exception as e:
        logger.error(f"Error listing keywords: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list keywords: {str(e)}")


@router.get("/stats")
async def get_keyword_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get keyword statistics for the current user
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id", "default")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT source_table) as tables,
                       COUNT(DISTINCT source_column) as columns,
                       MAX(updated_at) as last_updated
                FROM learned_keywords
                WHERE user_id = %s AND tenant_id = %s
            """, (user_id, tenant_id))
            
            result = cursor.fetchone()
            
            # Get counts by type
            cursor.execute("""
                SELECT keyword_type, COUNT(*) as count
                FROM learned_keywords
                WHERE user_id = %s AND tenant_id = %s
                GROUP BY keyword_type
            """, (user_id, tenant_id))
            
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "success": True,
                "stats": {
                    "total_keywords": result[0] if result else 0,
                    "tables_analyzed": result[1] if result else 0,
                    "columns_analyzed": result[2] if result else 0,
                    "last_updated": result[3].isoformat() if result and result[3] else None,
                    "by_type": type_counts
                }
            }
    
    except Exception as e:
        logger.error(f"Error getting keyword stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/reset")
async def reset_keywords(
    current_user: dict = Depends(get_current_user)
):
    """
    Reset/delete all learned keywords for the current user
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id", "default")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM learned_keywords
                WHERE user_id = %s AND tenant_id = %s
            """, (user_id, tenant_id))
            
            deleted_count = cursor.rowcount
            conn.commit()
        
        # Clear cache
        cache = get_keyword_cache()
        await cache.get_keywords(user_id, tenant_id, force_refresh=True)
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} keywords",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        logger.error(f"Error resetting keywords: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset keywords: {str(e)}")
