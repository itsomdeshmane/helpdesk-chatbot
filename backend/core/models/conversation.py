"""
Conversation Domain Models
Represents conversations and messages
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    """Message role enumeration"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """
    Represents a single message in a conversation
    
    Following Domain-Driven Design (DDD):
    - Value object for messages
    - Immutable after creation
    """
    
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string role to MessageRole enum if needed"""
        if isinstance(self.role, str):
            self.role = MessageRole(self.role)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for LLM API"""
        return {
            "role": self.role.value,
            "content": self.content
        }
    
    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == MessageRole.USER
    
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == MessageRole.ASSISTANT


@dataclass
class Conversation:
    """
    Represents a conversation (session) between user and assistant
    
    Following Domain-Driven Design (DDD):
    - Aggregate root for messages
    - Enforces conversation rules
    """
    
    session_id: str
    tenant_id: str
    user_id: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to the conversation
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get messages from conversation
        
        Args:
            limit: Optional limit (most recent messages)
            
        Returns:
            List of messages
        """
        if limit is None:
            return self.messages
        return self.messages[-limit:] if len(self.messages) > limit else self.messages
    
    def get_messages_for_llm(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get messages in format suitable for LLM API
        
        Args:
            limit: Optional limit (most recent messages)
            
        Returns:
            List of message dictionaries
        """
        messages = self.get_messages(limit)
        return [msg.to_dict() for msg in messages]
    
    def get_last_user_message(self) -> Optional[Message]:
        """Get the last user message"""
        user_messages = [msg for msg in reversed(self.messages) if msg.is_user_message()]
        return user_messages[0] if user_messages else None
    
    def get_last_assistant_message(self) -> Optional[Message]:
        """Get the last assistant message"""
        assistant_messages = [msg for msg in reversed(self.messages) if msg.is_assistant_message()]
        return assistant_messages[0] if assistant_messages else None
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the conversation"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "message_count": len(self.messages),
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in self.messages
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }

