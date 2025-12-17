"""
Query Processor Service
Processes queries using LLM and generates responses
"""

import logging
from typing import List, Dict, Any, Optional
from core.interfaces.llm_provider import ILLMProvider
from core.models.query import Query

logger = logging.getLogger(__name__)


class QueryProcessor:
    """
    Processes queries and generates LLM responses
    
    Following SOLID:
    - SRP: Single responsibility - query processing with LLM
    - DIP: Depends on ILLMProvider interface
    """
    
    def __init__(self, llm_provider: ILLMProvider):
        """
        Initialize query processor
        
        Args:
            llm_provider: LLM provider for text generation
        """
        self._llm = llm_provider
        logger.info(f"Query Processor initialized with {llm_provider.get_provider_name()}")
    
    async def generate_response(
        self,
        query: Query,
        context: Any,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response using LLM with context
        
        Args:
            query: User query
            context: Context (documents, data, etc.)
            system_prompt: Optional custom system prompt
            
        Returns:
            Generated response text
        """
        try:
            # Build messages for LLM
            messages = self._build_messages(query, context, system_prompt)
            
            # Generate response
            response = await self._llm.generate_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            logger.info(f"Generated response: {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    def _build_messages(
        self,
        query: Query,
        context: Any,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages for LLM
        
        Args:
            query: User query
            context: Context data
            system_prompt: Optional system prompt
            
        Returns:
            List of messages
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful assistant. Answer questions based on the provided context."
            })
        
        # Add conversation history if available
        if query.context:
            history = query.context.get_recent_history(limit=5)
            for msg in history:
                messages.append(msg)
        
        # Add current query with context
        user_message = self._format_user_message(query, context)
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _format_user_message(self, query: Query, context: Any) -> str:
        """
        Format user message with context
        
        Args:
            query: User query
            context: Context data
            
        Returns:
            Formatted message
        """
        if isinstance(context, list):
            # Document context
            context_text = "\n\n".join([
                doc.get('text', str(doc)) if isinstance(doc, dict) else str(doc)
                for doc in context[:3]  # Limit to top 3 documents
            ])
            return f"Context:\n{context_text}\n\nQuestion: {query.text}"
        
        elif isinstance(context, dict):
            # Database result context
            if 'data' in context:
                return f"Data:\n{context['data']}\n\nQuestion: {query.text}"
            return f"Context: {context}\n\nQuestion: {query.text}"
        
        else:
            # Direct context
            return f"Context: {context}\n\nQuestion: {query.text}"
    
    async def generate_streaming(
        self,
        query: Query,
        context: Any,
        system_prompt: Optional[str] = None
    ):
        """
        Generate streaming response
        
        Args:
            query: User query
            context: Context data
            system_prompt: Optional system prompt
            
        Yields:
            Text chunks as they are generated
        """
        try:
            # Build messages
            messages = self._build_messages(query, context, system_prompt)
            
            # Generate streaming response
            async for chunk in self._llm.generate_streaming(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield "Error generating response."

