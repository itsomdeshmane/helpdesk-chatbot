"""
Response Domain Models
Represents responses from data sources and the chatbot
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataSourceResponse:
    """
    Response from a data source (documents, database, etc.)
    
    Following SOLID:
    - SRP: Single responsibility - represent data source results
    - OCP: Can be extended with new fields without modification
    """
    
    success: bool
    source_type: str  # 'documents', 'database', 'api', etc.
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sql_query: Optional[str] = None  # For database sources
    execution_time_ms: float = 0.0
    
    def is_successful(self) -> bool:
        """Check if response is successful"""
        return self.success and self.data is not None
    
    def has_data(self) -> bool:
        """Check if response has data"""
        if not self.data:
            return False
        if isinstance(self.data, list):
            return len(self.data) > 0
        return True
    
    def get_row_count(self) -> int:
        """Get number of rows in response"""
        if isinstance(self.data, list):
            return len(self.data)
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "source_type": self.source_type,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "sql_query": self.sql_query,
            "execution_time_ms": self.execution_time_ms
        }


@dataclass
class ChatResponse:
    """
    Final response to user from chatbot
    
    Aggregates data from multiple sources and LLM generation
    """
    
    success: bool
    message: str
    source: str = "unknown"
    requires_clarification: bool = False
    session_id: Optional[str] = None
    
    # Optional data for database queries
    data: Optional[Any] = None
    rows: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    sql_query: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    response_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Related questions (for UI)
    related_questions: List[str] = field(default_factory=list)
    
    def is_database_response(self) -> bool:
        """Check if this is a database query response"""
        return self.source in ['database', 'database_exact_match'] and self.data is not None
    
    def is_document_response(self) -> bool:
        """Check if this is a document search response"""
        return self.source == 'documents'
    
    def needs_user_action(self) -> bool:
        """Check if user action is required"""
        return self.requires_clarification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        result = {
            "success": self.success,
            "message": self.message,
            "source": self.source,
            "requires_clarification": self.requires_clarification,
            "session_id": self.session_id,
            "confidence_score": self.confidence_score,
            "response_time_ms": self.response_time_ms,
            "metadata": self.metadata
        }
        
        # Add optional fields if present
        if self.data is not None:
            result["data"] = self.data
        if self.rows is not None:
            result["rows"] = self.rows
        if self.columns is not None:
            result["columns"] = self.columns
        if self.sql_query is not None:
            result["sql_query"] = self.sql_query
        if self.related_questions:
            result["related_questions"] = self.related_questions
        
        return result
    
    @classmethod
    def error_response(
        cls,
        message: str,
        source: str = "unknown",
        requires_clarification: bool = True
    ) -> "ChatResponse":
        """Factory method for error responses"""
        return cls(
            success=False,
            message=message,
            source=source,
            requires_clarification=requires_clarification
        )
    
    @classmethod
    def success_response(
        cls,
        message: str,
        source: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> "ChatResponse":
        """Factory method for success responses"""
        return cls(
            success=True,
            message=message,
            source=source,
            session_id=session_id,
            **kwargs
        )

