"""
Chat Orchestrator
Main business logic for processing chat queries
Coordinates data sources, LLM, and response formatting
"""

import logging
import time
from typing import Optional, List
from core.interfaces.data_source import IDataSource
from core.interfaces.llm_provider import ILLMProvider
from core.models.query import Query
from core.models.response import ChatResponse, DataSourceResponse
from application.services.source_selector import SourceSelector
from application.services.query_processor import QueryProcessor
from application.services.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Main chat orchestration service
    
    Coordinates:
    - Data source selection
    - Data retrieval
    - LLM response generation
    - Response formatting
    
    Following SOLID:
    - SRP: Single responsibility - orchestrate chat flow
    - OCP: Works with any IDataSource and ILLMProvider
    - DIP: Depends on abstractions, not concrete classes
    
    This is the heart of the SOLID-compliant architecture.
    All business logic flows through this orchestrator.
    """
    
    def __init__(
        self,
        vector_data_source: IDataSource,
        sql_data_source_factory,
        llm_provider: ILLMProvider,
        source_selector: SourceSelector,
        response_formatter: ResponseFormatter,
        query_processor: QueryProcessor,
        conversation_repo
    ):
        """
        Initialize chat orchestrator
        
        Args:
            vector_data_source: Document/RAG data source
            sql_data_source_factory: Factory for SQL data sources
            llm_provider: LLM provider
            source_selector: Source selection service
            response_formatter: Response formatting service
            query_processor: Query processing service
            conversation_repo: Conversation repository
        """
        self._vector_data_source = vector_data_source
        self._sql_data_source_factory = sql_data_source_factory
        self._llm = llm_provider
        self._source_selector = source_selector
        self._response_formatter = response_formatter
        self._query_processor = query_processor
        self._conversation_repo = conversation_repo
        
        logger.info("Chat Orchestrator initialized")
    
    async def process_query(
        self,
        query: Query,
        tenant_id: str,
        session_id: Optional[str] = None,
        connection_string: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a chat query through the complete flow
        
        Args:
            query: User query
            tenant_id: Tenant identifier
            session_id: Optional session ID
            connection_string: Optional database connection string
            
        Returns:
            ChatResponse with results
            
        Flow:
            1. Select appropriate data source
            2. Search data source
            3. Generate LLM response with context
            4. Format response
            5. Save to conversation history
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: '{query.text[:50]}...' (tenant: {tenant_id})")
            
            # Step 1: Get available data sources
            available_sources = await self._get_available_sources(connection_string)
            
            if not available_sources:
                return self._response_formatter.format_error_response(
                    error_message="No data sources available",
                    source="none",
                    session_id=session_id
                )
            
            # Step 2: Select best data source
            selected_source = await self._source_selector.select_source(
                query=query,
                available_sources=available_sources
            )
            
            if not selected_source:
                return self._response_formatter.format_no_source_response(
                    query_text=query.text,
                    session_id=session_id
                )
            
            source_type = selected_source.get_source_type()
            logger.info(f"Using data source: {source_type}")
            
            # Step 3: Search data source
            search_result = await selected_source.search(
                query=query,
                tenant_id=tenant_id,
                limit=5
            )
            
            if not search_result.success:
                # Try fallback sources
                search_result = await self._try_fallback_sources(
                    query=query,
                    tenant_id=tenant_id,
                    exclude=selected_source,
                    available_sources=available_sources
                )
                
                if not search_result or not search_result.success:
                    return self._response_formatter.format_error_response(
                        error_message="Could not find relevant information",
                        source=source_type,
                        session_id=session_id
                    )
                
                source_type = search_result.source_type
            
            # Step 4: Generate response using LLM
            response_text = await self._query_processor.generate_response(
                query=query,
                context=search_result.data
            )
            
            # Step 5: Format response
            if source_type == "database":
                response = self._response_formatter.format_database_response(
                    generated_text=response_text,
                    data_source_response=search_result,
                    session_id=session_id
                )
            else:
                response = self._response_formatter.format_document_response(
                    generated_text=response_text,
                    data_source_response=search_result,
                    session_id=session_id
                )
            
            # Add total response time
            response.response_time_ms = (time.time() - start_time) * 1000
            
            # Step 6: Save to conversation history
            if session_id and self._conversation_repo:
                try:
                    # Implementation would save conversation
                    pass
                except Exception as e:
                    logger.warning(f"Failed to save conversation: {e}")
            
            logger.info(f"Query processed successfully in {response.response_time_ms:.0f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return ChatResponse(
                success=False,
                message=f"I encountered an error while processing your request: {str(e)}",
                source="error",
                requires_clarification=True,
                session_id=session_id,
                response_time_ms=execution_time
            )
    
    async def _get_available_sources(
        self,
        connection_string: Optional[str]
    ) -> List[IDataSource]:
        """
        Get list of available data sources
        
        Args:
            connection_string: Optional database connection
            
        Returns:
            List of available data sources
        """
        sources = []
        
        # Always add vector data source (documents)
        try:
            if await self._vector_data_source.health_check():
                sources.append(self._vector_data_source)
        except Exception as e:
            logger.warning(f"Vector data source not available: {e}")
        
        # Add SQL data source if connection available
        if connection_string:
            try:
                sql_source = self._sql_data_source_factory(connection_string=connection_string)
                if await sql_source.health_check():
                    sources.append(sql_source)
            except Exception as e:
                logger.warning(f"SQL data source not available: {e}")
        
        return sources
    
    async def _try_fallback_sources(
        self,
        query: Query,
        tenant_id: str,
        exclude: IDataSource,
        available_sources: List[IDataSource]
    ) -> Optional[DataSourceResponse]:
        """
        Try remaining sources as fallback
        
        Args:
            query: User query
            tenant_id: Tenant ID
            exclude: Source to exclude (already tried)
            available_sources: All available sources
            
        Returns:
            DataSourceResponse if any fallback succeeds, None otherwise
        """
        for source in available_sources:
            if source == exclude:
                continue
            
            try:
                logger.info(f"Trying fallback source: {source.get_source_type()}")
                result = await source.search(query, tenant_id)
                
                if result.success:
                    logger.info(f"Fallback successful with {source.get_source_type()}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Fallback source {source.get_source_type()} failed: {e}")
                continue
        
        logger.warning("All fallback sources failed")
        return None
    
    async def process_streaming_query(
        self,
        query: Query,
        tenant_id: str,
        session_id: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Process query with streaming response
        
        Args:
            query: User query
            tenant_id: Tenant ID
            session_id: Optional session ID
            connection_string: Optional database connection
            
        Yields:
            Response chunks as they are generated
        """
        try:
            logger.info(f"Processing streaming query: '{query.text[:50]}...'")
            
            # Get available sources
            available_sources = await self._get_available_sources(connection_string)
            
            if not available_sources:
                yield {"type": "error", "content": "No data sources available"}
                return
            
            # Select data source
            selected_source = await self._source_selector.select_source(
                query=query,
                available_sources=available_sources
            )
            
            if not selected_source:
                yield {"type": "error", "content": "No suitable data source found"}
                return
            
            yield {"type": "status", "content": f"Searching {selected_source.get_source_type()}..."}
            
            # Search data source
            search_result = await selected_source.search(query, tenant_id)
            
            if not search_result.success:
                yield {"type": "error", "content": "Search failed"}
                return
            
            yield {"type": "status", "content": "Generating response..."}
            
            # Stream LLM response
            async for chunk in self._query_processor.generate_streaming(
                query=query,
                context=search_result.data
            ):
                yield {"type": "text", "content": chunk}
            
            # Send completion
            yield {"type": "done", "source": selected_source.get_source_type()}
            
        except Exception as e:
            logger.error(f"Streaming query failed: {e}")
            yield {"type": "error", "content": str(e)}

