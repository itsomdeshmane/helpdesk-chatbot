"""
Response Formatter Service
Formats responses for API output
"""

import logging
from typing import Optional, List, Dict, Any
from core.models.response import ChatResponse, DataSourceResponse

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Formats responses for API output
    
    Following SOLID:
    - SRP: Single responsibility - response formatting
    - OCP: Can be extended with new formatting strategies
    """
    
    def __init__(self):
        """Initialize response formatter"""
        logger.info("Response Formatter initialized")
    
    def format_response(
        self,
        text: str,
        source: str,
        data_source_response: Optional[DataSourceResponse] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Format a successful response
        
        Args:
            text: Response text
            source: Data source type
            data_source_response: Optional DataSourceResponse
            session_id: Optional session ID
            **kwargs: Additional response fields
            
        Returns:
            Formatted ChatResponse
        """
        try:
            # Build base response
            response = ChatResponse(
                success=True,
                message=text,
                source=source,
                session_id=session_id,
                **kwargs
            )
            
            # Add data source metadata if available
            if data_source_response:
                response.metadata.update({
                    'execution_time_ms': data_source_response.execution_time_ms,
                    'source_metadata': data_source_response.metadata
                })
                
                # Add SQL query if database source
                if data_source_response.sql_query:
                    response.sql_query = data_source_response.sql_query
                
                # Add database results
                if source == "database" and data_source_response.data:
                    response.data = data_source_response.data
                    response.rows = data_source_response.data
                    response.columns = data_source_response.metadata.get('columns', [])
            
            return response
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return ChatResponse.error_response(
                message="Error formatting response",
                source=source
            )
    
    def format_error_response(
        self,
        error_message: str,
        source: str = "unknown",
        requires_clarification: bool = True,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Format an error response
        
        Args:
            error_message: Error message
            source: Data source type
            requires_clarification: Whether clarification is needed
            session_id: Optional session ID
            
        Returns:
            Error ChatResponse
        """
        return ChatResponse.error_response(
            message=error_message,
            source=source,
            requires_clarification=requires_clarification
        )
    
    def format_no_source_response(
        self,
        query_text: str,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Format response when no data source can handle the query
        
        Args:
            query_text: Original query text
            session_id: Optional session ID
            
        Returns:
            ChatResponse indicating no suitable source
        """
        return ChatResponse(
            success=False,
            message="I'm not sure how to help with that question. Could you rephrase it or provide more details?",
            source="none",
            requires_clarification=True,
            session_id=session_id,
            metadata={
                'reason': 'no_suitable_source',
                'original_query': query_text
            }
        )
    
    def format_database_response(
        self,
        generated_text: str,
        data_source_response: DataSourceResponse,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Format database query response
        
        Args:
            generated_text: LLM-generated explanation
            data_source_response: Database query results
            session_id: Optional session ID
            
        Returns:
            Formatted database ChatResponse
        """
        return self.format_response(
            text=generated_text,
            source="database",
            data_source_response=data_source_response,
            session_id=session_id
        )
    
    def format_document_response(
        self,
        generated_text: str,
        data_source_response: DataSourceResponse,
        session_id: Optional[str] = None,
        related_questions: Optional[List[str]] = None
    ) -> ChatResponse:
        """
        Format document search response
        
        Args:
            generated_text: LLM-generated answer
            data_source_response: Document search results
            session_id: Optional session ID
            related_questions: Optional related questions
            
        Returns:
            Formatted document ChatResponse
        """
        response = self.format_response(
            text=generated_text,
            source="documents",
            data_source_response=data_source_response,
            session_id=session_id
        )
        
        if related_questions:
            response.related_questions = related_questions
        
        return response

