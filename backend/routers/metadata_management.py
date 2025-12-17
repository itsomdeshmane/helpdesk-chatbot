"""
Metadata Management Router
API endpoints for managing database column/table metadata and learning suggestions
"""
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Optional, Dict, Any, List
import logging

from llm.column_metadata_service import get_column_metadata_service
from llm.metadata_learning_service import get_metadata_learning_service
from llm.schema_service import get_schema_service
from utils.auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Metadata Management"])


@router.post("/metadata/column/save", summary="Save column metadata")
async def save_column_metadata(
    tenant_id: str = Body(...),
    database_name: str = Body(...),
    table_name: str = Body(...),
    column_name: str = Body(...),
    description: str = Body(...),
    semantic_type: Optional[str] = Body(None),
    examples: Optional[List[str]] = Body(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Save or update column metadata
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        table_name: Table name
        column_name: Column name
        description: Column description
        semantic_type: Optional semantic type (e.g., 'location', 'financial')
        examples: Optional example values
        current_user: Current authenticated user
    
    Returns:
        Success status
    """
    try:
        metadata_service = get_column_metadata_service()
        user_id = current_user.get('username') if current_user else None
        
        success = metadata_service.save_column_metadata(
            tenant_id=tenant_id,
            database_name=database_name,
            table_name=table_name,
            column_name=column_name,
            description=description,
            semantic_type=semantic_type,
            examples=examples,
            user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Metadata saved for {table_name}.{column_name}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save metadata")
            
    except Exception as e:
        logger.error(f"Error saving column metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metadata/table/save", summary="Save table metadata")
async def save_table_metadata(
    tenant_id: str = Body(...),
    database_name: str = Body(...),
    table_name: str = Body(...),
    description: str = Body(...),
    business_purpose: Optional[str] = Body(None),
    primary_entity: Optional[str] = Body(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Save or update table metadata
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        table_name: Table name
        description: Table description
        business_purpose: Optional business purpose
        primary_entity: Optional primary entity type
        current_user: Current authenticated user
    
    Returns:
        Success status
    """
    try:
        metadata_service = get_column_metadata_service()
        user_id = current_user.get('username') if current_user else None
        
        success = metadata_service.save_table_metadata(
            tenant_id=tenant_id,
            database_name=database_name,
            table_name=table_name,
            description=description,
            business_purpose=business_purpose,
            primary_entity=primary_entity,
            user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Metadata saved for table {table_name}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save metadata")
            
    except Exception as e:
        logger.error(f"Error saving table metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metadata/auto-discover", summary="Auto-discover and save metadata")
async def auto_discover_metadata(
    tenant_id: str = Body(...),
    database_name: str = Body(...),
    connection_string: str = Body(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Auto-discover metadata for all tables and columns in a database
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        connection_string: Database connection string
        current_user: Current authenticated user
    
    Returns:
        Count of tables and columns processed
    """
    try:
        schema_service = get_schema_service()
        metadata_service = get_column_metadata_service()
        user_id = current_user.get('username') if current_user else None
        
        # Get database schema
        schema = await schema_service.get_database_schema(connection_string)
        
        # Auto-discover and save metadata
        result = metadata_service.auto_discover_and_save_metadata(
            tenant_id=tenant_id,
            database_name=database_name,
            schema=schema,
            user_id=user_id
        )
        
        return {
            "success": True,
            "message": f"Auto-discovered metadata for {result['tables']} tables and {result['columns']} columns",
            "tables_processed": result['tables'],
            "columns_processed": result['columns']
        }
        
    except Exception as e:
        logger.error(f"Error auto-discovering metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/suggestions", summary="Get metadata improvement suggestions")
async def get_suggestions(
    tenant_id: str,
    database_name: str,
    status: str = 'pending',
    min_confidence: float = 0.70,
    limit: int = 50,
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Get AI-generated metadata improvement suggestions
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        status: Status filter ('pending', 'approved', 'rejected', 'applied')
        min_confidence: Minimum confidence score (0.0-1.0)
        limit: Maximum number of suggestions
        current_user: Current authenticated user
    
    Returns:
        List of improvement suggestions
    """
    try:
        learning_service = get_metadata_learning_service()
        
        suggestions = learning_service.get_improvement_suggestions(
            tenant_id=tenant_id,
            database_name=database_name,
            status=status,
            min_confidence=min_confidence,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metadata/suggestions/approve", summary="Approve metadata suggestion")
async def approve_suggestion(
    suggestion_id: int = Body(...),
    apply_immediately: bool = Body(True),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Approve and optionally apply a metadata improvement suggestion
    
    Args:
        suggestion_id: Suggestion ID
        apply_immediately: Whether to apply the change immediately
        current_user: Current authenticated user
    
    Returns:
        Success status
    """
    try:
        learning_service = get_metadata_learning_service()
        user_id = current_user.get('username') if current_user else 'anonymous'
        
        success = learning_service.approve_suggestion(
            suggestion_id=suggestion_id,
            user_id=user_id,
            apply_immediately=apply_immediately
        )
        
        if success:
            return {
                "success": True,
                "message": f"Suggestion approved{'and applied' if apply_immediately else ''}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to approve suggestion")
            
    except Exception as e:
        logger.error(f"Error approving suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metadata/feedback", summary="Submit query feedback")
async def submit_feedback(
    query_id: int = Body(...),
    feedback: str = Body(...),
    rating: Optional[int] = Body(None),
    comment: Optional[str] = Body(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Submit user feedback for a query
    
    Args:
        query_id: Query ID from conversation history
        feedback: Feedback type ('positive', 'negative', 'neutral')
        rating: Optional rating (1-5)
        comment: Optional comment
        current_user: Current authenticated user
    
    Returns:
        Success status
    """
    try:
        learning_service = get_metadata_learning_service()
        
        if feedback not in ['positive', 'negative', 'neutral']:
            raise HTTPException(status_code=400, detail="Invalid feedback type")
        
        if rating and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        success = learning_service.record_user_feedback(
            query_id=query_id,
            feedback=feedback,
            rating=rating,
            comment=comment
        )
        
        if success:
            return {
                "success": True,
                "message": "Feedback recorded successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/quality-report", summary="Get quality report")
async def get_quality_report(
    tenant_id: str,
    database_name: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Get quality report for database metadata
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        current_user: Current authenticated user
    
    Returns:
        Quality report with statistics
    """
    try:
        learning_service = get_metadata_learning_service()
        
        report = learning_service.get_quality_report(
            tenant_id=tenant_id,
            database_name=database_name
        )
        
        return {
            "success": True,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/schema-enriched", summary="Get enriched schema with metadata")
async def get_enriched_schema(
    tenant_id: str,
    database_name: str,
    connection_string: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Get database schema enriched with metadata descriptions
    
    Args:
        tenant_id: Tenant ID
        database_name: Database name
        connection_string: Database connection string
        current_user: Current authenticated user
    
    Returns:
        Enriched schema
    """
    try:
        schema_service = get_schema_service()
        metadata_service = get_column_metadata_service()
        
        # Get base schema
        schema = await schema_service.get_database_schema(connection_string)
        
        # Enrich with metadata
        enriched_schema = metadata_service.enrich_schema(
            schema=schema,
            tenant_id=tenant_id,
            database_name=database_name
        )
        
        return {
            "success": True,
            "schema": enriched_schema
        }
        
    except Exception as e:
        logger.error(f"Error getting enriched schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

