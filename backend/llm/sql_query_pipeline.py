"""
SQL Query Pipeline - Layered NL to SQL conversion with verification & retry
Implements a robust, multi-layer approach:
1. Query Understanding Layer (NL → Intent)
2. SQL Generation Layer (Intent → SQL)
3. SQL Validation Layer (Verify SQL syntax & logic)
4. Execution Layer (Run SQL)
5. Response Generation Layer (Results → NL)
6. Retry Layer (Auto-fix & retry on failures)
"""
import logging
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QueryStrategy(Enum):
    """Strategy for SQL generation"""
    RULE_BASED = "rule_based"  # Fast, pattern-based
    LLM_SIMPLE = "llm_simple"   # GPT-3.5 for simple queries
    LLM_COMPLEX = "llm_complex" # GPT-4 for complex queries
    HYBRID = "hybrid"           # Combine rule-based + LLM


class ValidationResult(Enum):
    """SQL validation result"""
    VALID = "valid"
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    SECURITY_RISK = "security_risk"
    AMBIGUOUS = "ambiguous"


@dataclass
class QueryPipelineResult:
    """Result from the query pipeline"""
    success: bool
    sql_query: Optional[str]
    results: Optional[List[Dict]]
    natural_language_response: str
    confidence: float
    strategy_used: QueryStrategy
    attempts: int
    validation_issues: List[str]
    metadata: Dict[str, Any]


class SQLQueryPipeline:
    """
    Multi-layer pipeline for robust NL to SQL conversion
    Generic - works with ANY database schema
    """
    
    def __init__(
        self,
        query_classifier,
        sql_builder,
        database_service,
        max_retries: int = 3
    ):
        """
        Initialize the pipeline
        
        Args:
            query_classifier: QueryClassifier instance
            sql_builder: SQLBuilder instance
            database_service: DatabaseQueryService instance
            max_retries: Maximum retry attempts for failed queries
        """
        self.classifier = query_classifier
        self.sql_builder = sql_builder
        self.db_service = database_service
        self.max_retries = max_retries
    
    async def process_query(
        self,
        natural_language_query: str,
        schema: Dict[str, Any],
        schema_dict: Dict[str, Any],
        available_tables: List[str],
        conversation_history: Optional[List[Dict]] = None
    ) -> QueryPipelineResult:
        """
        Process natural language query through the full pipeline
        
        Args:
            natural_language_query: User's question
            schema: Database schema (string format for LLM)
            schema_dict: Structured schema dictionary
            available_tables: List of table names
            conversation_history: Previous conversation context
            
        Returns:
            QueryPipelineResult with SQL, results, and NL response
        """
        logger.info(f"🚀 Pipeline starting for query: {natural_language_query}")
        
        metadata = {
            "original_query": natural_language_query,
            "attempts": [],
            "validation_results": [],
            "strategy_selection": None
        }
        
        # LAYER 1: Query Understanding
        intent = await self._understand_query(
            natural_language_query,
            available_tables,
            conversation_history
        )
        
        # LAYER 2: Strategy Selection
        strategy = self._select_strategy(intent, schema_dict)
        metadata["strategy_selection"] = strategy.value
        
        # LAYER 3-6: Generate → Validate → Execute → Retry Loop
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"📊 Attempt {attempt}/{self.max_retries}")
            
            attempt_data = {
                "attempt_number": attempt,
                "strategy": strategy.value,
                "timestamp": None
            }
            
            # LAYER 3: SQL Generation
            sql_query = await self._generate_sql(
                natural_language_query,
                intent,
                schema,
                schema_dict,
                available_tables,
                strategy,
                attempt,
                metadata["attempts"]
            )
            
            if not sql_query:
                attempt_data["result"] = "no_sql_generated"
                metadata["attempts"].append(attempt_data)
                continue
            
            attempt_data["sql"] = sql_query
            
            # LAYER 4: SQL Validation
            validation = self._validate_sql(sql_query, schema_dict, intent)
            attempt_data["validation"] = validation.value
            metadata["validation_results"].append(validation.value)
            
            if validation != ValidationResult.VALID:
                logger.warning(f"⚠️ Validation failed: {validation.value}")
                attempt_data["result"] = f"validation_failed_{validation.value}"
                metadata["attempts"].append(attempt_data)
                
                # Try to fix and retry
                if attempt < self.max_retries:
                    strategy = self._adjust_strategy(strategy, validation)
                    continue
            
            # LAYER 5: Execution
            try:
                execution_result = await self.db_service.execute_query(
                    sql_query,
                    None,  # connection_string will be fetched from user settings
                    natural_language_query
                )
                
                attempt_data["execution"] = "success" if execution_result["success"] else "failed"
                
                if execution_result["success"]:
                    # LAYER 6: Natural Language Response Generation
                    nl_response = execution_result["message"]
                    results = execution_result.get("rows", [])
                    
                    attempt_data["result"] = "success"
                    attempt_data["row_count"] = len(results)
                    metadata["attempts"].append(attempt_data)
                    
                    # Calculate confidence score
                    confidence = self._calculate_confidence(
                        intent,
                        validation,
                        len(results),
                        strategy
                    )
                    
                    logger.info(f"✅ Pipeline success! Confidence: {confidence:.2f}")
                    
                    return QueryPipelineResult(
                        success=True,
                        sql_query=sql_query,
                        results=results,
                        natural_language_response=nl_response,
                        confidence=confidence,
                        strategy_used=strategy,
                        attempts=attempt,
                        validation_issues=[],
                        metadata=metadata
                    )
                else:
                    # Execution failed, analyze error
                    error_msg = execution_result.get("message", "")
                    attempt_data["error"] = error_msg
                    metadata["attempts"].append(attempt_data)
                    
                    logger.warning(f"❌ Execution failed: {error_msg}")
                    
                    # Try to fix based on error
                    if attempt < self.max_retries:
                        strategy = self._adjust_strategy_from_error(strategy, error_msg)
                        continue
            
            except Exception as e:
                logger.error(f"❌ Pipeline exception: {e}")
                attempt_data["exception"] = str(e)
                metadata["attempts"].append(attempt_data)
                
                if attempt < self.max_retries:
                    continue
        
        # All attempts failed
        logger.error(f"❌ Pipeline failed after {self.max_retries} attempts")
        
        return QueryPipelineResult(
            success=False,
            sql_query=None,
            results=None,
            natural_language_response="I couldn't generate a valid SQL query for your question. Please rephrase or ask differently.",
            confidence=0.0,
            strategy_used=strategy,
            attempts=self.max_retries,
            validation_issues=metadata["validation_results"],
            metadata=metadata
        )
    
    async def _understand_query(
        self,
        query: str,
        available_tables: List[str],
        conversation_history: Optional[List[Dict]]
    ) -> Any:
        """
        LAYER 1: Query Understanding
        Classify query intent using advanced algorithms with conversation context
        """
        logger.info("🔍 Layer 1: Understanding query intent...")
        
        # Log conversation history availability
        if conversation_history:
            logger.info(f"✅ Using conversation history ({len(conversation_history)} messages)")
        else:
            logger.warning("⚠️ No conversation history provided to pipeline")
        
        # Use query classifier with conversation history for context-aware classification
        intent = self.classifier.classify(query, available_tables, conversation_history)
        
        logger.info(f"Intent: {intent.intent_type}, Operation: {intent.operation}, Confidence: {intent.confidence}")
        logger.info(f"Entities: tables={intent.entities.get('tables')}, aggregate={intent.entities.get('aggregate')}")
        
        return intent
    
    def _select_strategy(
        self,
        intent: Any,
        schema_dict: Dict[str, Any]
    ) -> QueryStrategy:
        """
        LAYER 2: Strategy Selection
        Choose best approach based on query complexity
        """
        logger.info("🎯 Layer 2: Selecting generation strategy...")
        
        # Rule-based for simple, high-confidence patterns
        if intent.confidence >= 0.85 and intent.intent_type in ['list', 'count', 'filter']:
            logger.info("Selected: RULE_BASED (simple pattern)")
            return QueryStrategy.RULE_BASED
        
        # Hybrid for medium complexity
        if intent.confidence >= 0.7 and intent.intent_type in ['aggregate_group', 'aggregate']:
            logger.info("Selected: HYBRID (rule-based + LLM verification)")
            return QueryStrategy.HYBRID
        
        # LLM for complex queries
        if intent.intent_type in ['join', 'subquery', 'complex']:
            logger.info("Selected: LLM_COMPLEX (GPT-4)")
            return QueryStrategy.LLM_COMPLEX
        
        # Default to LLM simple
        logger.info("Selected: LLM_SIMPLE (GPT-3.5)")
        return QueryStrategy.LLM_SIMPLE
    
    async def _generate_sql(
        self,
        natural_language_query: str,
        intent: Any,
        schema: str,
        schema_dict: Dict[str, Any],
        available_tables: List[str],
        strategy: QueryStrategy,
        attempt: int,
        previous_attempts: List[Dict]
    ) -> Optional[str]:
        """
        LAYER 3: SQL Generation
        Generate SQL using selected strategy
        """
        logger.info(f"⚙️ Layer 3: Generating SQL (strategy={strategy.value}, attempt={attempt})...")
        
        # Add error feedback from previous attempts
        error_context = ""
        if attempt > 1 and previous_attempts:
            last_attempt = previous_attempts[-1]
            if "error" in last_attempt:
                error_context = f"\nPrevious attempt failed with: {last_attempt['error']}\nPlease fix this issue."
        
        if strategy == QueryStrategy.RULE_BASED:
            # Fast, pattern-based generation
            sql = self.sql_builder.build_query(intent, schema_dict, None)
            return sql if sql else None
        
        elif strategy == QueryStrategy.HYBRID:
            # Try rule-based first, fallback to LLM
            sql = self.sql_builder.build_query(intent, schema_dict, None)
            if sql and self._validate_sql(sql, schema_dict, intent) == ValidationResult.VALID:
                return sql
            # Fallback to LLM
            logger.info("Rule-based failed, falling back to LLM...")
            return await self.db_service.convert_to_sql(
                natural_language_query + error_context,
                schema,
                None,
                schema_dict,
                available_tables
            )
        
        else:
            # LLM-based generation (simple or complex)
            return await self.db_service.convert_to_sql(
                natural_language_query + error_context,
                schema,
                None,
                schema_dict,
                available_tables
            )
    
    def _validate_sql(
        self,
        sql_query: str,
        schema_dict: Dict[str, Any],
        intent: Any
    ) -> ValidationResult:
        """
        LAYER 4: SQL Validation
        Verify SQL is syntactically and logically correct
        """
        logger.info("✔️ Layer 4: Validating SQL...")
        
        if not sql_query or not sql_query.strip():
            return ValidationResult.SYNTAX_ERROR
        
        sql_upper = sql_query.upper().strip()
        
        # 1. Security checks (generic - no SQL injection)
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
        if any(keyword in sql_upper for keyword in dangerous_keywords):
            logger.warning("⚠️ Dangerous SQL keyword detected!")
            return ValidationResult.SECURITY_RISK
        
        # 2. Syntax checks (basic)
        if not sql_upper.startswith('SELECT'):
            return ValidationResult.SYNTAX_ERROR
        
        # Check for basic SQL structure
        if 'FROM' not in sql_upper:
            return ValidationResult.SYNTAX_ERROR
        
        # 3. Schema validation (table & column existence)
        # Extract table names from SQL
        from_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
        if from_match:
            table_name = from_match.group(1)
            if table_name not in schema_dict:
                logger.warning(f"⚠️ Table '{table_name}' not found in schema")
                return ValidationResult.LOGIC_ERROR
            
            # Validate columns (basic check)
            table_schema = schema_dict[table_name]
            column_names = [col['name'].lower() for col in table_schema.get('columns', [])]
            
            # Extract column names from SELECT clause
            select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql_query, re.IGNORECASE)
            if select_match and select_match.group(1) != '*':
                select_cols = select_match.group(1)
                # Simple column validation (not perfect, but helps)
                for word in select_cols.split(','):
                    col = word.strip().split()[0].lower()
                    if col not in ['count', 'sum', 'avg', 'max', 'min', 'distinct'] and col not in column_names:
                        # Check if it's an alias or function
                        if '(' not in col and ' as ' not in word.lower():
                            logger.warning(f"⚠️ Column '{col}' might not exist")
        
        # 4. Logical checks (based on intent)
        if intent.intent_type == 'aggregate_group':
            if 'GROUP BY' not in sql_upper:
                logger.warning("⚠️ Expected GROUP BY for aggregate_group intent")
                return ValidationResult.LOGIC_ERROR
        
        if intent.intent_type == 'count':
            if 'COUNT' not in sql_upper:
                logger.warning("⚠️ Expected COUNT for count intent")
                return ValidationResult.LOGIC_ERROR
        
        # 5. Result limit check (prevent huge result sets)
        if 'LIMIT' not in sql_upper and intent.intent_type == 'list':
            logger.warning("⚠️ No LIMIT clause for list query (could return many rows)")
            # This is a warning, not an error
        
        logger.info("✅ SQL validation passed")
        return ValidationResult.VALID
    
    def _adjust_strategy(
        self,
        current_strategy: QueryStrategy,
        validation_result: ValidationResult
    ) -> QueryStrategy:
        """Adjust strategy based on validation failure"""
        logger.info(f"🔄 Adjusting strategy from {current_strategy.value} due to {validation_result.value}")
        
        if current_strategy == QueryStrategy.RULE_BASED:
            return QueryStrategy.HYBRID
        elif current_strategy == QueryStrategy.HYBRID:
            return QueryStrategy.LLM_SIMPLE
        elif current_strategy == QueryStrategy.LLM_SIMPLE:
            return QueryStrategy.LLM_COMPLEX
        else:
            return QueryStrategy.LLM_COMPLEX
    
    def _adjust_strategy_from_error(
        self,
        current_strategy: QueryStrategy,
        error_message: str
    ) -> QueryStrategy:
        """Adjust strategy based on execution error"""
        logger.info(f"🔄 Adjusting strategy from {current_strategy.value} due to error: {error_message[:50]}...")
        
        # If syntax error, escalate to more sophisticated strategy
        if 'syntax' in error_message.lower():
            if current_strategy == QueryStrategy.RULE_BASED:
                return QueryStrategy.LLM_SIMPLE
            else:
                return QueryStrategy.LLM_COMPLEX
        
        # For other errors, try hybrid or complex
        if current_strategy == QueryStrategy.RULE_BASED:
            return QueryStrategy.HYBRID
        else:
            return QueryStrategy.LLM_COMPLEX
    
    def _calculate_confidence(
        self,
        intent: Any,
        validation: ValidationResult,
        result_count: int,
        strategy: QueryStrategy
    ) -> float:
        """Calculate confidence score for the result"""
        confidence = intent.confidence
        
        # Boost confidence if validation passed
        if validation == ValidationResult.VALID:
            confidence *= 1.1
        
        # Boost if we got results
        if result_count > 0:
            confidence *= 1.05
        
        # Penalize if using fallback strategies
        if strategy == QueryStrategy.LLM_COMPLEX:
            confidence *= 0.9
        
        # Cap at 1.0
        return min(confidence, 1.0)


# Factory function
_pipeline_instance = None

def get_query_pipeline(
    query_classifier=None,
    sql_builder=None,
    database_service=None,
    max_retries: int = 3
) -> SQLQueryPipeline:
    """
    Get or create singleton pipeline instance
    
    Args:
        query_classifier: QueryClassifier instance
        sql_builder: SQLBuilder instance  
        database_service: DatabaseQueryService instance
        max_retries: Maximum retry attempts
        
    Returns:
        SQLQueryPipeline instance
    """
    global _pipeline_instance
    
    if _pipeline_instance is None:
        if not all([query_classifier, sql_builder, database_service]):
            # Lazy import to avoid circular dependencies
            from llm.query_classifier import get_query_classifier
            from llm.sql_builder import get_sql_builder
            from llm.database_query_service import get_database_query_service
            
            query_classifier = query_classifier or get_query_classifier()
            sql_builder = sql_builder or get_sql_builder()
            database_service = database_service or get_database_query_service()
        
        _pipeline_instance = SQLQueryPipeline(
            query_classifier,
            sql_builder,
            database_service,
            max_retries
        )
    
    return _pipeline_instance
