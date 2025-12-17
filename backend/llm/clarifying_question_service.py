"""
Clarifying Question Service
Generates helpful clarifying questions when the system can't answer
"""
import os
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class ClarifyingQuestionService:
    """Service for generating clarifying questions"""
    
    def __init__(self):
        """Initialize with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    async def generate_clarifying_question(
        self,
        query: str,
        user_id: str,
        session_id: str,
        available_tables: Optional[List[str]] = None,
        available_topics: Optional[List[str]] = None,
        conversation_history: Optional[List] = None
    ) -> str:
        """
        Generate a helpful clarifying question
        
        Args:
            query: User's original query
            user_id: User identifier
            session_id: Session identifier
            available_tables: List of available database tables
            available_topics: List of available documentation topics
            conversation_history: Previous conversation for context
        
        Returns:
            Clarifying question string
        """
        logger.info(f"Generating clarifying question for: {query}")
        
        if not self.client:
            return self._fallback_clarifying_question(query, available_tables, available_topics)
        
        try:
            # Build context (WITHOUT exposing database table names)
            context_parts = []
            
            # Add conversation history if available
            if conversation_history and len(conversation_history) > 0:
                context_parts.append("Previous conversation:")
                for msg in conversation_history[-3:]:  # Last 3 messages
                    context_parts.append(f"User: {msg.get('query', '')}")
                    context_parts.append(f"Assistant: {msg.get('response', '')[:100]}...")
            
            # Map tables to user-friendly terms (GENERIC approach)
            if available_tables:
                friendly_resources = []
                table_map = {
                    'purchase_orders': 'purchase orders',
                    'sales_orders': 'sales orders',
                    'vendors': 'vendor information',
                    'customers': 'customer information',
                    'products': 'product catalog',
                    'orders': 'orders',
                    'invoices': 'invoices',
                    'payments': 'payments'
                }
                
                for table in available_tables[:10]:
                    friendly_name = table_map.get(table, table.replace('_', ' '))
                    friendly_resources.append(friendly_name)
                
                if friendly_resources:
                    context_parts.append(f"Available data: {', '.join(friendly_resources)}")
            
            if available_topics:
                topics_str = ", ".join(available_topics[:10])
                context_parts.append(f"Available documentation: {topics_str}")
            
            context = "\n".join(context_parts) if context_parts else "No specific context available."
            
            # Generate clarifying question
            system_prompt = """You are a helpful assistant. When a user's question is unclear or cannot be answered directly, 
generate a helpful clarifying question that will help them get the information they need. 

IMPORTANT RULES:
1. NEVER mention database tables, SQL, schemas, or technical database terms
2. Use business-friendly language (e.g., "sales orders" not "sales_orders table")
3. Focus on WHAT the user wants to know, not HOW the data is stored
4. Be specific and helpful, not technical

Be specific and suggest concrete alternatives based on available resources."""

            user_prompt = f"""The user asked: "{query}"

We couldn't find a direct answer. 

{context}

Generate a helpful clarifying question that:
1. Uses BUSINESS-FRIENDLY language (never mention "database", "table", "schema")
2. Asks about WHAT they want (e.g., "Are you looking for order details, totals, or customer information?")
3. Suggests specific alternatives based on their question
4. Acknowledges previous conversation context if available
5. Is friendly and encouraging

Keep it concise (1-2 sentences).

WRONG: "Which database table contains the information?"
RIGHT: "Are you looking for order details, customer information, or something else?"

WRONG: "Do you want to query the sales_orders table?"
RIGHT: "Would you like to see sales order details or summary totals?"
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            clarifying_question = response.choices[0].message.content.strip()
            logger.info(f"Generated clarifying question: {clarifying_question}")
            
            return clarifying_question
            
        except Exception as e:
            logger.error(f"Error generating clarifying question: {e}")
            return self._fallback_clarifying_question(query, available_tables, available_topics)
    
    def _fallback_clarifying_question(
        self,
        query: str,
        available_tables: Optional[List[str]] = None,
        available_topics: Optional[List[str]] = None
    ) -> str:
        """
        Generate a basic clarifying question without AI (GENERIC - no table exposure)
        
        Args:
            query: Original query
            available_tables: Available database tables (converted to friendly terms)
            available_topics: Available documentation topics
        
        Returns:
            Basic clarifying question with business-friendly language
        """
        base_message = "I'm not sure I understood that. "
        
        suggestions = []
        
        # Convert tables to user-friendly terms (GENERIC)
        if available_tables:
            table_map = {
                'purchase_orders': 'purchase orders',
                'sales_orders': 'sales orders',
                'vendors': 'vendors',
                'customers': 'customers',
                'products': 'products',
                'orders': 'orders',
                'invoices': 'invoices',
                'payments': 'payments'
            }
            
            friendly_resources = []
            for table in available_tables[:5]:
                friendly_name = table_map.get(table, table.replace('_', ' '))
                friendly_resources.append(friendly_name)
            
            if friendly_resources:
                suggestions.append(f"I can help you with: {', '.join(friendly_resources)}")
        
        if available_topics:
            suggestions.append(f"I have documentation about: {', '.join(available_topics[:5])}")
        
        if not suggestions:
            # Generic helpful message
            return "Could you please provide more details? For example, are you looking for counts, totals, lists, or specific details?"
        
        return base_message + " ".join(suggestions) + ". Could you rephrase your question?"


# Singleton instance
_clarifying_service_instance = None

def get_clarifying_question_service() -> ClarifyingQuestionService:
    """Get singleton instance of ClarifyingQuestionService"""
    global _clarifying_service_instance
    if _clarifying_service_instance is None:
        _clarifying_service_instance = ClarifyingQuestionService()
    return _clarifying_service_instance



