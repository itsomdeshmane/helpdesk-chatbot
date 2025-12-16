"""
Smart Chat Router - Multi-source intelligent chat with fallback
Equivalent to SmartChatController from .NET implementation

3-Layer Fallback Strategy:
1. RAG/Knowledge Base (Documents)
2. Database/SQL Analytics
3. Clarifying Questions
"""
from fastapi import APIRouter, Body, Depends, Response, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
import asyncio
import json
import logging
import time

from llm.rag import search, generate_response_with_module_with_context
from llm.database_query_service import get_database_query_service
from llm.schema_service import get_schema_service
from llm.clarifying_question_service import get_clarifying_question_service
from llm.source_intelligence import get_source_intelligence
from utils.conversation_manager import get_conversation_manager
from utils.auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Smart Chat"])


@router.post("/smart/query", summary="Smart multi-source chat query")
async def smart_query(
    query: str = Body(...),
    source: str = Body("auto", description="Source type: 'auto', 'documents', 'database'"),
    tenant_id: str = Body(...),
    session_id: str = Body(None),
    connection_string: str = Body(None, description="Optional database connection string (if None, uses user's saved connection)"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Smart chat with automatic source selection and fallback
    
    Sources:
    - auto: Try documents first, then database, then clarifying questions
    - documents: Only search documentation/knowledge base
    - database: Only query database
    
    Returns:
        {
            "success": bool,
            "message": str,
            "source": str,  # "documents", "database", "clarification"
            "requires_clarification": bool,
            "session_id": str,
            "data": optional data for database queries,
            "rows": optional rows for database queries,
            "columns": optional columns for database queries
        }
    """
    start_time = time.time()
    conv_manager = get_conversation_manager()
    source_intel = get_source_intelligence()
    
    logger.info(f"Smart query: {query} | Source: {source}")
    
    try:
        # Get user's database connection if not provided and user is authenticated
        if not connection_string and current_user and source in ["auto", "database"]:
            try:
                from database.db_manager import DatabaseManager
                from utils.encryption import decrypt_value
                
                db_manager = DatabaseManager()
                with db_manager.get_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT host, port, database_name, username, encrypted_password
                        FROM user_database_connections
                        WHERE user_id = %s AND tenant_id = %s
                        LIMIT 1
                        """,
                        (current_user['user_id'], current_user['tenant_id'])
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        password = decrypt_value(result['encrypted_password'])
                        connection_string = (
                            f"host={result['host']};"
                            f"port={result['port']};"
                            f"database={result['database_name']};"
                            f"user={result['username']};"
                            f"password={password}"
                        )
                        logger.info(f"✅ Using user's saved database connection: {result['host']}/{result['database_name']}")
                    else:
                        logger.warning("No saved database connection found for user, using default")
            except Exception as e:
                logger.warning(f"Could not load user's database connection: {e}")
        
        # Initialize session
        if not session_id:
            user_id = current_user.get('username') if current_user else None
            session_id = conv_manager.create_session(tenant_id, user_id=user_id)
        
        response = {
            "success": True,
            "session_id": session_id,
            "requires_clarification": False
        }
        
        # Intelligent source detection for 'auto' mode
        actual_source = source
        source_detection = None
        
        if source == "auto":
            # Get conversation history for context
            conversation_history = conv_manager.get_conversation_history(session_id, limit=5)
            
            # Get available tables for better detection
            available_tables = []
            try:
                schema_service = get_schema_service()
                tables = await schema_service.get_all_tables(connection_string)
                available_tables = [t['table_name'] for t in tables]
            except:
                pass
            
            # Detect best source
            source_detection = source_intel.detect_source(
                query,
                conversation_history=conversation_history,
                available_tables=available_tables
            )
            
            logger.info(f"Source detection: {source_detection}")
            
            # Use detected source, but "both" means try the fallback strategy
            if source_detection["source"] in ["database", "documents"]:
                actual_source = source_detection["source"]
            else:
                actual_source = "auto"  # Will try both in order
        
        # Strategy 1: Documents/RAG (if source is auto or documents)
        # Skip documents if intelligent source detection says "database"
        if actual_source in ["auto", "documents"]:
            logger.info("Step 1: Searching knowledge base/documents...")
            
            try:
                # Search documents
                docs = await asyncio.to_thread(search, query, tenant_id)
                
                if docs and len(docs) > 0:
                    doc_context = "\n".join(docs)
                    
                    # Get conversation history
                    conversation_history = conv_manager.get_conversation_history(session_id)
                    
                    # Generate response
                    result = await asyncio.to_thread(
                        generate_response_with_module_with_context,
                        query,
                        doc_context,
                        tenant_id,
                        conversation_history
                    )
                    
                    answer = result.get('response', '')
                    
                    # Check if answer is meaningful (not just "I don't know")
                    if answer and len(answer) > 50 and "don't have" not in answer.lower():
                        response["message"] = answer
                        response["source"] = "documents"
                        
                        # Save to conversation history
                        conv_manager.save_message(
                            session_id=session_id,
                            query=query,
                            response=answer,
                            module="Documents",
                            response_time=time.time() - start_time
                        )
                        
                        logger.info("Found answer in documents")
                        return response
            except Exception as e:
                logger.warning(f"Document search failed: {e}")
        
        # Strategy 2: Database/SQL Analytics (if source is auto or database)
        # Skip database if intelligent source detection says "documents"
        if actual_source in ["auto", "database"]:
            logger.info("Step 2: Trying database analytics...")
            
            try:
                db_service = get_database_query_service()
                schema_service = get_schema_service()
                
                # Get schema for context
                schema = await schema_service.get_database_schema(connection_string)
                schema_context = schema_service.get_schema_context(schema)
                schema_dict = schema_service.get_schema_dict(schema)
                
                # Get conversation history for context
                conversation_history = conv_manager.get_conversation_history(session_id, limit=5)
                
                logger.info(f"Converting query to SQL: {query}")
                logger.info(f"Using conversation history with {len(conversation_history)} messages")
                
                # Convert to SQL with conversation context (hybrid approach)
                sql_query = await db_service.convert_to_sql(
                    query, 
                    schema_context, 
                    conversation_history,
                    schema_dict=schema_dict,
                    available_tables=available_tables
                )
                
                logger.info(f"Generated SQL: {sql_query if sql_query else '(empty - could not generate)'}")
                
                if sql_query and sql_query != "SHOW TABLES" and len(sql_query) > 10:
                    # Execute SQL
                    logger.info(f"Executing SQL query...")
                    result = await db_service.execute_query(
                        sql_query,
                        connection_string,
                        query
                    )
                    
                    logger.info(f"Query execution result: success={result['success']}, rows={len(result.get('rows', []))}")
                    
                    # Return database results even if empty (let user know we tried)
                    if result["success"]:
                        # If we have rows, great!
                        if result.get("rows"):
                            response["message"] = result["message"]
                            response["source"] = "database"
                            response["data"] = result.get("rows", [])
                            response["rows"] = result.get("rows", [])
                            response["columns"] = result.get("columns", [])
                            response["response_format"] = result.get("response_format", "table")
                            response["sql_query"] = sql_query
                            
                            # Save to conversation history with SQL query for context
                            conv_manager.save_message(
                                session_id=session_id,
                                query=query,
                                response=result["message"],
                                module="Database",
                                response_time=time.time() - start_time,
                                context_used=[{"sql_query": sql_query, "row_count": len(result.get("rows", []))}]
                            )
                            
                            logger.info("Found answer in database")
                            return response
                        else:
                            # No rows but query was valid - inform user
                            logger.info("Query executed but returned no results")
                            response["message"] = "I executed the query but found no matching records in the database. Please try a different date range or check if the data exists."
                            response["source"] = "database"
                            response["rows"] = []
                            response["columns"] = []
                            response["sql_query"] = sql_query
                            
                            conv_manager.save_message(
                                session_id=session_id,
                                query=query,
                                response=response["message"],
                                module="Database",
                                response_time=time.time() - start_time,
                                context_used=[{"sql_query": sql_query, "row_count": 0}]
                            )
                            
                            return response
                    else:
                        logger.warning(f"Query execution failed: {result.get('message')}")
                else:
                    logger.warning(f"Could not generate valid SQL query for: {query}")
            except Exception as e:
                logger.error(f"Database query failed with exception: {e}", exc_info=True)
        
        # Strategy 3: Clarifying Question (fallback)
        logger.info("Step 3: Generating clarifying question...")
        
        clarifying_service = get_clarifying_question_service()
        schema_service = get_schema_service()
        
        # Get available resources
        available_tables = []
        try:
            tables = await schema_service.get_all_tables(connection_string)
            available_tables = [t['table_name'] for t in tables]
        except:
            pass
        
        # Get conversation history for context-aware clarification
        conversation_history = conv_manager.get_conversation_history(session_id, limit=5)
        
        # Generate clarifying question with conversation context
        clarifying_question = await clarifying_service.generate_clarifying_question(
            query,
            current_user.get('username') if current_user else 'anonymous',
            session_id,
            available_tables=available_tables,
            conversation_history=conversation_history
        )
        
        response["message"] = clarifying_question
        response["source"] = "clarification"
        response["requires_clarification"] = True
        
        # Include source detection info if available
        if source_detection:
            response["source_detection"] = source_detection
        
        # Save to conversation history
        conv_manager.save_message(
            session_id=session_id,
            query=query,
            response=clarifying_question,
            module="Clarification",
            response_time=time.time() - start_time
        )
        
        logger.info("Generated clarifying question")
        return response
        
    except Exception as e:
        logger.error(f"Error in smart query: {e}")
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "session_id": session_id,
            "source": "error",
            "requires_clarification": False
        }


@router.post("/smart/stream", summary="Smart chat with streaming response")
async def smart_stream(
    query: str = Body(...),
    source: str = Body("auto"),
    tenant_id: str = Body(...),
    session_id: str = Body(None),
    connection_string: str = Body(None, description="Optional database connection string (if None, uses user's saved connection)"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Smart chat with streaming response for better UX
    
    Returns Server-Sent Events (SSE) stream
    """
    async def generate_stream():
        """Generate SSE stream"""
        try:
            conv_manager = get_conversation_manager()
            source_intel = get_source_intelligence()
            
            # Get user's database connection if not provided and user is authenticated
            user_connection_string = connection_string
            if not user_connection_string and current_user and source in ["auto", "database"]:
                try:
                    from database.db_manager import DatabaseManager
                    from utils.encryption import decrypt_value
                    
                    db_manager = DatabaseManager()
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            """
                            SELECT host, port, database_name, username, encrypted_password
                            FROM user_database_connections
                            WHERE user_id = %s AND tenant_id = %s
                            LIMIT 1
                            """,
                            (current_user['user_id'], current_user['tenant_id'])
                        )
                        result = cursor.fetchone()
                        
                        if result:
                            password = decrypt_value(result['encrypted_password'])
                            user_connection_string = (
                                f"host={result['host']};"
                                f"port={result['port']};"
                                f"database={result['database_name']};"
                                f"user={result['username']};"
                                f"password={password}"
                            )
                            logger.info(f"✅ Using user's saved database connection: {result['host']}/{result['database_name']}")
                        else:
                            logger.warning("No saved database connection found for user")
                            yield f"data: {json.dumps({'type': 'error', 'content': 'Please configure your database connection in Settings first'})}\n\n"
                            return
                except Exception as e:
                    logger.warning(f"Could not load user's database connection: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Error loading database connection. Please check Settings.'})}\n\n"
                    return
            
            # Initialize session
            if not session_id:
                user_id = current_user.get('username') if current_user else None
                new_session_id = conv_manager.create_session(tenant_id, user_id=user_id)
            else:
                new_session_id = session_id
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'content': 'Processing your question...'})}\n\n"
            
            # Get available tables early for use throughout
            available_tables = []
            try:
                schema_service_init = get_schema_service()
                tables = await schema_service_init.get_all_tables(user_connection_string)
                available_tables = [t['table_name'] for t in tables]
            except Exception as e:
                logger.warning(f"Could not load available tables: {e}")
            
            # Intelligent source detection for 'auto' mode
            actual_source = source
            source_detection = None
            
            if source == "auto":
                # Get conversation history for context
                conversation_history = conv_manager.get_conversation_history(new_session_id, limit=5)
                
                # Detect best source
                source_detection = source_intel.detect_source(
                    query,
                    conversation_history=conversation_history,
                    available_tables=available_tables
                )
                
                logger.info(f"Source detection (stream): {source_detection}")
                
                # Use detected source
                if source_detection["source"] in ["database", "documents"]:
                    actual_source = source_detection["source"]
                    status_msg = f"🎯 {source_detection['reason']}"
                    yield f"data: {json.dumps({'type': 'status', 'content': status_msg})}\n\n"
                else:
                    actual_source = "auto"  # Will try both
            
            # Try documents first
            if actual_source in ["auto", "documents"]:
                yield f"data: {json.dumps({'type': 'status', 'content': 'Searching knowledge base...'})}\n\n"
                
                try:
                    docs = await asyncio.to_thread(search, query, tenant_id)
                    
                    if docs and len(docs) > 0:
                        doc_context = "\n".join(docs)
                        conversation_history = conv_manager.get_conversation_history(new_session_id)
                        
                        result = await asyncio.to_thread(
                            generate_response_with_module_with_context,
                            query,
                            doc_context,
                            tenant_id,
                            conversation_history
                        )
                        
                        answer = result.get('response', '')
                        
                        if answer and len(answer) > 50:
                            # Stream answer word by word
                            words = answer.split(' ')
                            for word in words:
                                yield f"data: {json.dumps({'type': 'text', 'content': word + ' '})}\n\n"
                                await asyncio.sleep(0.03)  # Small delay for streaming effect
                            
                            yield f"data: {json.dumps({'type': 'complete', 'content': answer, 'source': 'documents', 'session_id': new_session_id})}\n\n"
                            
                            # Save to history
                            conv_manager.save_message(new_session_id, query, answer, "Documents", 0)
                            return
                except Exception as e:
                    logger.warning(f"Document search failed: {e}")
            
            # Try database
            if actual_source in ["auto", "database"]:
                yield f"data: {json.dumps({'type': 'status', 'content': 'Analyzing database...'})}\n\n"
                
                try:
                    # Use the new layered pipeline for robust query processing
                    from llm.sql_query_pipeline import get_query_pipeline
                    
                    schema_service = get_schema_service()
                    
                    schema = await schema_service.get_database_schema(user_connection_string)
                    schema_context = schema_service.get_schema_context(schema)
                    schema_dict = schema_service.get_schema_dict(schema)
                    
                    # Get conversation history for context
                    conversation_history = conv_manager.get_conversation_history(new_session_id, limit=5)
                    
                    # Get pipeline and process query through all layers
                    pipeline = get_query_pipeline()
                    pipeline_result = await pipeline.process_query(
                        query,
                        schema_context,
                        schema_dict,
                        available_tables,
                        conversation_history
                    )
                    
                    if pipeline_result.success and pipeline_result.results is not None:
                        # Extract results from pipeline
                        result = {
                            "success": True,
                            "message": pipeline_result.natural_language_response,
                            "rows": pipeline_result.results,
                            "columns": list(pipeline_result.results[0].keys()) if pipeline_result.results else [],
                            "row_count": len(pipeline_result.results),
                            "sql_query": pipeline_result.sql_query
                        }
                        sql_query = pipeline_result.sql_query
                        
                        if result["success"] and result.get("rows") is not None:
                            message = result["message"]
                            
                            # Log pipeline metadata
                            logger.info(f"📊 Pipeline: Strategy={pipeline_result.strategy_used.value}, "
                                      f"Attempts={pipeline_result.attempts}, Confidence={pipeline_result.confidence:.2f}")
                            
                            # Stream message
                            words = message.split(' ')
                            for word in words:
                                yield f"data: {json.dumps({'type': 'text', 'content': word + ' '})}\n\n"
                                await asyncio.sleep(0.03)
                            
                            # Send data
                            yield f"data: {json.dumps({'type': 'data', 'rows': result['rows'], 'columns': result['columns']})}\n\n"
                            
                            # Send completion with confidence
                            completion_data = {
                                'type': 'complete',
                                'content': message,
                                'source': 'database',
                                'session_id': new_session_id,
                                'confidence': pipeline_result.confidence
                            }
                            yield f"data: {json.dumps(completion_data)}\n\n"
                            
                            # Save to history with SQL query and pipeline metadata
                            conv_manager.save_message(
                                new_session_id, 
                                query, 
                                message, 
                                "Database", 
                                len(result['rows']),
                                context_used={
                                    "sql_query": sql_query,
                                    "row_count": len(result['rows']),
                                    "confidence": pipeline_result.confidence,
                                    "strategy": pipeline_result.strategy_used.value
                                }
                            )
                            return
                except Exception as e:
                    logger.warning(f"Database query failed: {e}")
            
            # Fallback to clarifying question
            yield f"data: {json.dumps({'type': 'status', 'content': 'Generating clarifying question...'})}\n\n"
            
            clarifying_service = get_clarifying_question_service()
            schema_service = get_schema_service()
            
            available_tables_clarify = []
            try:
                tables = await schema_service.get_all_tables(user_connection_string)
                available_tables_clarify = [t['table_name'] for t in tables]
            except:
                pass
            
            # Get conversation history for context
            conversation_history = conv_manager.get_conversation_history(new_session_id, limit=5)
            
            clarifying_question = await clarifying_service.generate_clarifying_question(
                query,
                current_user.get('username') if current_user else 'anonymous',
                new_session_id,
                available_tables=available_tables_clarify,
                conversation_history=conversation_history
            )
            
            # Stream clarifying question
            words = clarifying_question.split(' ')
            for word in words:
                yield f"data: {json.dumps({'type': 'text', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.04)
            
            yield f"data: {json.dumps({'type': 'complete', 'content': clarifying_question, 'source': 'clarification', 'requires_clarification': True, 'session_id': new_session_id})}\n\n"
            
            # Save to history
            conv_manager.save_message(new_session_id, query, clarifying_question, "Clarification", 0)
            
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/schema", summary="Get database schema")
async def get_schema(
    connection_string: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get database schema information"""
    try:
        schema_service = get_schema_service()
        schema = await schema_service.get_database_schema(connection_string)
        return schema
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", summary="Get conversation history")
async def get_history(
    session_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get conversation history for a session"""
    try:
        conv_manager = get_conversation_manager()
        user_id = current_user.get('username') if current_user else None
        
        history = conv_manager.get_conversation_history(session_id, user_id=user_id)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

