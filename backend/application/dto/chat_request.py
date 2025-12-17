"""
Chat Request DTOs
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request model for chat queries
    
    Validates and structures incoming API requests
    """
    
    query: str = Field(..., min_length=1, max_length=2000, description="User query text")
    source: str = Field(default="auto", description="Source preference: 'auto', 'documents', 'database'")
    tenant_id: str = Field(..., description="Tenant identifier")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    connection_string: Optional[str] = Field(default=None, description="Optional database connection string")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I create a work order?",
                "source": "auto",
                "tenant_id": "default",
                "session_id": None,
                "connection_string": None
            }
        }


class StreamingChatRequest(BaseModel):
    """
    Request model for streaming chat queries
    """
    
    query: str = Field(..., min_length=1, max_length=2000)
    source: str = Field(default="auto")
    tenant_id: str = Field(...)
    session_id: Optional[str] = Field(default=None)
    connection_string: Optional[str] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me all customers",
                "source": "auto",
                "tenant_id": "default"
            }
        }

