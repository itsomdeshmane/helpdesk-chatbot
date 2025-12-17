"""
Query Domain Models
Represents user queries and their context
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QueryContext:
    """
    Context information for a query
    Includes conversation history and user preferences
    """
    
    session_id: Optional[str] = None
    tenant_id: str = "default"
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_recent_history(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if self.conversation_history else []


@dataclass
class Query:
    """
    Represents a user query
    
    Following Domain-Driven Design (DDD):
    - Rich domain model with behavior
    - Encapsulates query-related logic
    """
    
    text: str
    source_preference: str = "auto"  # 'auto', 'documents', 'database'
    context: Optional[QueryContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize context if not provided"""
        if self.context is None:
            self.context = QueryContext()
    
    def is_empty(self) -> bool:
        """Check if query is empty"""
        return not self.text or not self.text.strip()
    
    def get_tenant_id(self) -> str:
        """Get tenant ID from context"""
        return self.context.tenant_id if self.context else "default"
    
    def get_session_id(self) -> Optional[str]:
        """Get session ID from context"""
        return self.context.session_id if self.context else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "source_preference": self.source_preference,
            "tenant_id": self.get_tenant_id(),
            "session_id": self.get_session_id(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

