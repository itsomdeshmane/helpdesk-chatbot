"""
Chat Response DTOs
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from core.models.response import ChatResponse


class ChatResponseDTO(BaseModel):
    """
    Response model for chat queries
    
    Serializes ChatResponse for API output
    """
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    source: str = Field(..., description="Data source used ('documents', 'database', etc.)")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    requires_clarification: bool = Field(default=False, description="Whether user clarification is needed")
    
    # Optional database fields
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Database query results")
    rows: Optional[List[Dict[str, Any]]] = Field(default=None, description="Database rows")
    columns: Optional[List[str]] = Field(default=None, description="Database column names")
    sql_query: Optional[str] = Field(default=None, description="Generated SQL query")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    confidence_score: float = Field(default=0.0, description="Confidence score (0-1)")
    response_time_ms: float = Field(default=0.0, description="Response time in milliseconds")
    
    # Related questions
    related_questions: List[str] = Field(default_factory=list, description="Related questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Here's how to create a work order...",
                "source": "documents",
                "session_id": "abc123",
                "requires_clarification": False,
                "response_time_ms": 1234.5
            }
        }
    
    @classmethod
    def from_domain(cls, chat_response: ChatResponse) -> "ChatResponseDTO":
        """
        Convert domain ChatResponse to DTO
        
        Args:
            chat_response: Domain ChatResponse object
            
        Returns:
            ChatResponseDTO
        """
        return cls(
            success=chat_response.success,
            message=chat_response.message,
            source=chat_response.source,
            session_id=chat_response.session_id,
            requires_clarification=chat_response.requires_clarification,
            data=chat_response.data,
            rows=chat_response.rows,
            columns=chat_response.columns,
            sql_query=chat_response.sql_query,
            metadata=chat_response.metadata,
            confidence_score=chat_response.confidence_score,
            response_time_ms=chat_response.response_time_ms,
            related_questions=chat_response.related_questions
        )

