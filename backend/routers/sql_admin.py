"""
SQL Admin Router - Performance monitoring and cache management
Provides endpoints for viewing stats and managing caches
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from llm.database_query_service_enhanced import get_enhanced_database_query_service
from llm.sql_cache import get_sql_cache
from llm.schema_cache import get_schema_cache
from llm.result_cache import get_result_cache
from llm.query_learner import get_query_learner
from llm.sql_monitoring import get_sql_metrics
from llm.model_selector import get_model_selector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/sql-admin",
    tags=["SQL Admin"]
)


@router.get("/stats")
async def get_performance_stats():
    """
    Get comprehensive performance statistics
    
    Returns:
    - SQL cache stats (hit rate, size)
    - Schema cache stats
    - Result cache stats
    - Model selector stats (cost saved)
    - Query learner stats (success rate)
    - Metrics (latency, errors)
    """
    try:
        service = get_enhanced_database_query_service()
        stats = service.get_performance_stats()
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get high-level metrics summary"""
    try:
        metrics = get_sql_metrics()
        summary = metrics.get_summary()
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/recent-queries")
async def get_recent_queries(limit: int = 20):
    """Get recent queries with performance data"""
    try:
        metrics = get_sql_metrics()
        recent = metrics.get_recent_queries(limit=limit)
        
        return {
            "success": True,
            "count": len(recent),
            "queries": recent
        }
    except Exception as e:
        logger.error(f"Failed to get recent queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/slow-queries")
async def get_slow_queries(threshold_ms: float = 1000, limit: int = 10):
    """Get slowest queries above threshold"""
    try:
        metrics = get_sql_metrics()
        slow = metrics.get_slow_queries(threshold_ms=threshold_ms, limit=limit)
        
        return {
            "success": True,
            "threshold_ms": threshold_ms,
            "count": len(slow),
            "queries": slow
        }
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/error-patterns")
async def get_error_patterns():
    """Get queries grouped by error type"""
    try:
        metrics = get_sql_metrics()
        errors = metrics.get_error_patterns()
        
        return {
            "success": True,
            "error_types": len(errors),
            "patterns": errors
        }
    except Exception as e:
        logger.error(f"Failed to get error patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learner/common-patterns")
async def get_common_query_patterns(top_n: int = 10):
    """Get most common successful query patterns"""
    try:
        learner = get_query_learner()
        patterns = learner.get_common_patterns(top_n=top_n)
        
        return {
            "success": True,
            "count": len(patterns),
            "patterns": [
                {"query": query, "count": count}
                for query, count in patterns
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get common patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learner/failure-patterns")
async def get_failure_patterns(top_n: int = 10):
    """Get most common failure patterns"""
    try:
        learner = get_query_learner()
        failures = learner.get_failure_patterns(top_n=top_n)
        
        return {
            "success": True,
            "count": len(failures),
            "patterns": [
                {"query": query, "count": count}
                for query, count in failures
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get failure patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_all_caches():
    """Clear all caches (use with caution)"""
    try:
        sql_cache = get_sql_cache()
        schema_cache = get_schema_cache()
        result_cache = get_result_cache()
        
        sql_cache.invalidate()
        schema_cache.invalidate()
        result_cache.invalidate()
        
        logger.info("All caches cleared")
        
        return {
            "success": True,
            "message": "All caches cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear-sql")
async def clear_sql_cache():
    """Clear SQL query cache only"""
    try:
        sql_cache = get_sql_cache()
        sql_cache.invalidate()
        
        logger.info("SQL cache cleared")
        
        return {
            "success": True,
            "message": "SQL cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear SQL cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear-results")
async def clear_result_cache():
    """Clear query result cache only"""
    try:
        result_cache = get_result_cache()
        result_cache.invalidate()
        
        logger.info("Result cache cleared")
        
        return {
            "success": True,
            "message": "Result cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear result cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/cleanup")
async def cleanup_expired_caches():
    """Remove expired entries from all caches"""
    try:
        sql_cache = get_sql_cache()
        schema_cache = get_schema_cache()
        result_cache = get_result_cache()
        
        sql_cache.cleanup_expired()
        schema_cache.cleanup_expired()
        result_cache.cleanup_expired()
        
        logger.info("Expired cache entries cleaned up")
        
        return {
            "success": True,
            "message": "Expired cache entries cleaned up successfully"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup caches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-selector/stats")
async def get_model_selector_stats():
    """Get model selection statistics and cost savings"""
    try:
        selector = get_model_selector()
        stats = selector.get_stats()
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get model selector stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

