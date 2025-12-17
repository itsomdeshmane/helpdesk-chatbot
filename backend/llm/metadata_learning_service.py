"""
Metadata Learning Service
Learns from query execution data to continuously improve column descriptions
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def get_db_manager():
    """Import DB manager (lazy import to avoid circular dependencies)"""
    from database.db_manager import DatabaseManager
    return DatabaseManager()


def get_column_metadata_service():
    """Import metadata service (lazy import)"""
    from llm.column_metadata_service import get_column_metadata_service as get_meta_svc
    return get_meta_svc()


class MetadataLearningService:
    """
    Service for learning from query execution and improving metadata
    """
    
    def __init__(self):
        """Initialize learning service"""
        self.auto_improve_threshold = 0.80  # 80% confidence to auto-apply
        self.min_queries_for_suggestion = 3  # Minimum queries to suggest improvement
    
    def record_query_execution(
        self,
        tenant_id: str,
        session_id: str,
        user_id: Optional[str],
        natural_query: str,
        sql_query: Optional[str],
        tables_used: Optional[List[str]],
        columns_used: Optional[List[str]],
        success: bool,
        execution_time_ms: Optional[int] = None,
        rows_returned: Optional[int] = None,
        error_message: Optional[str] = None,
        source_type: Optional[str] = None,
        confidence_score: Optional[float] = None,
        database_name: Optional[str] = None
    ) -> int:
        """
        Record query execution data for learning
        
        Args:
            tenant_id: Tenant ID
            session_id: Session ID
            user_id: User ID
            natural_query: Natural language query
            sql_query: Generated SQL query
            tables_used: List of tables used
            columns_used: List of columns used
            success: Whether execution was successful
            execution_time_ms: Execution time in milliseconds
            rows_returned: Number of rows returned
            error_message: Error message if failed
            source_type: Source type (database, documents, etc.)
            confidence_score: Confidence score of the query
            database_name: Database name
        
        Returns:
            ID of the recorded query
        """
        try:
            db_manager = get_db_manager()
            
            tables_json = json.dumps(tables_used) if tables_used else None
            columns_json = json.dumps(columns_used) if columns_used else None
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO query_learning_data
                    (tenant_id, session_id, user_id, natural_language_query, generated_sql,
                     tables_used, columns_used, execution_success, execution_time_ms,
                     rows_returned, error_message, source_type, confidence_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (tenant_id, session_id, user_id, natural_query, sql_query,
                      tables_json, columns_json, success, execution_time_ms,
                      rows_returned, error_message, source_type, confidence_score))
                
                query_id = cursor.lastrowid
                conn.commit()
                
                # Update usage metrics
                if success and tables_used and database_name:
                    self._update_usage_metrics(
                        tenant_id, database_name, tables_used, columns_used, success
                    )
                
                # Analyze for potential improvements
                if success and sql_query and database_name:
                    self._analyze_for_improvements(
                        tenant_id, database_name, natural_query, sql_query,
                        tables_used, columns_used, query_id
                    )
                
                logger.info(f"✅ Recorded query execution (ID: {query_id}, Success: {success})")
                return query_id
                
        except Exception as e:
            logger.error(f"Failed to record query execution: {e}")
            return -1
    
    def record_user_feedback(
        self,
        query_id: int,
        feedback: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Record user feedback for a query
        
        Args:
            query_id: Query ID from query_learning_data
            feedback: Feedback type ('positive', 'negative', 'neutral')
            rating: Rating 1-5
            comment: User comment
        
        Returns:
            True if successful
        """
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE query_learning_data
                    SET user_feedback = %s, user_rating = %s, user_comment = %s
                    WHERE id = %s
                """, (feedback, rating, comment, query_id))
                
                conn.commit()
                
                # Update quality metrics based on feedback
                cursor.execute("""
                    SELECT tenant_id, tables_used, columns_used
                    FROM query_learning_data
                    WHERE id = %s
                """, (query_id,))
                
                result = cursor.fetchone()
                if result:
                    # This will trigger re-analysis for improvements
                    logger.info(f"✅ Recorded user feedback for query {query_id}: {feedback}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to record user feedback: {e}")
            return False
    
    def _update_usage_metrics(
        self,
        tenant_id: str,
        database_name: str,
        tables_used: List[str],
        columns_used: Optional[List[str]],
        success: bool
    ):
        """
        Update usage and quality metrics for tables/columns
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            tables_used: List of tables used
            columns_used: List of columns used
            success: Whether query was successful
        """
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Update table-level metrics
                for table in tables_used:
                    cursor.execute("""
                        INSERT INTO metadata_quality_metrics
                        (tenant_id, database_name, table_name, query_success_count, query_failure_count, times_used, last_used_at)
                        VALUES (%s, %s, %s, %s, %s, 1, NOW())
                        ON DUPLICATE KEY UPDATE
                            query_success_count = query_success_count + %s,
                            query_failure_count = query_failure_count + %s,
                            times_used = times_used + 1,
                            last_used_at = NOW()
                    """, (tenant_id, database_name, table, 
                          1 if success else 0, 0 if success else 1,
                          1 if success else 0, 0 if success else 1))
                
                # Update column-level metrics
                if columns_used:
                    for col_info in columns_used:
                        # col_info format: "table.column" or just "column"
                        if '.' in col_info:
                            table, column = col_info.split('.', 1)
                        else:
                            # Try to match with tables_used
                            table = tables_used[0] if tables_used else None
                            column = col_info
                        
                        if table:
                            cursor.execute("""
                                INSERT INTO metadata_quality_metrics
                                (tenant_id, database_name, table_name, column_name, query_success_count, query_failure_count, times_used, last_used_at)
                                VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())
                                ON DUPLICATE KEY UPDATE
                                    query_success_count = query_success_count + %s,
                                    query_failure_count = query_failure_count + %s,
                                    times_used = times_used + 1,
                                    last_used_at = NOW()
                            """, (tenant_id, database_name, table, column,
                                  1 if success else 0, 0 if success else 1,
                                  1 if success else 0, 0 if success else 1))
                
                # Recalculate quality scores
                cursor.execute("""
                    UPDATE metadata_quality_metrics
                    SET quality_score = (
                        (query_success_count + positive_feedback_count) / 
                        GREATEST(query_success_count + query_failure_count + positive_feedback_count + negative_feedback_count, 1)
                    ) * 100
                    WHERE tenant_id = %s AND database_name = %s
                """, (tenant_id, database_name))
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to update usage metrics: {e}")
    
    def _analyze_for_improvements(
        self,
        tenant_id: str,
        database_name: str,
        natural_query: str,
        sql_query: str,
        tables_used: Optional[List[str]],
        columns_used: Optional[List[str]],
        query_id: int
    ):
        """
        Analyze query for potential metadata improvements
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            natural_query: Natural language query
            sql_query: Generated SQL
            tables_used: Tables used in query
            columns_used: Columns used in query
            query_id: Query ID
        """
        try:
            # Extract insights from natural language query
            insights = self._extract_query_insights(natural_query, sql_query)
            
            if not insights:
                return
            
            db_manager = get_db_manager()
            metadata_service = get_column_metadata_service()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check for column description improvements
                for table, column, suggested_desc, confidence in insights:
                    # Get current description
                    cursor.execute("""
                        SELECT description FROM column_metadata
                        WHERE tenant_id = %s AND database_name = %s 
                        AND table_name = %s AND column_name = %s
                    """, (tenant_id, database_name, table, column))
                    
                    result = cursor.fetchone()
                    current_desc = result['description'] if result else None
                    
                    # Check if suggestion is different and better
                    if current_desc != suggested_desc:
                        # Save suggestion
                        cursor.execute("""
                            INSERT INTO metadata_improvement_suggestions
                            (tenant_id, database_name, table_name, column_name,
                             current_description, suggested_description, suggestion_reason,
                             confidence_score, source_query_id, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                based_on_queries_count = based_on_queries_count + 1,
                                confidence_score = GREATEST(confidence_score, %s)
                        """, (tenant_id, database_name, table, column,
                              current_desc, suggested_desc,
                              f"Learned from query: {natural_query[:100]}",
                              confidence, query_id,
                              'approved' if confidence >= self.auto_improve_threshold else 'pending',
                              confidence))
                        
                        # Auto-apply if confidence is high enough
                        if confidence >= self.auto_improve_threshold:
                            metadata_service.save_column_metadata(
                                tenant_id, database_name, table, column,
                                suggested_desc, user_id='auto_learning'
                            )
                            logger.info(f"🤖 Auto-applied metadata improvement: {table}.{column}")
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to analyze for improvements: {e}")
    
    def _extract_query_insights(
        self,
        natural_query: str,
        sql_query: str
    ) -> List[tuple]:
        """
        Extract insights about column usage from natural and SQL queries
        
        Args:
            natural_query: Natural language query
            sql_query: Generated SQL query
        
        Returns:
            List of (table, column, suggested_description, confidence) tuples
        """
        insights = []
        
        try:
            import re
            
            # Extract meaningful phrases from natural query
            natural_lower = natural_query.lower()
            sql_lower = sql_query.lower()
            
            # Pattern: "vendors in India" suggests country column represents location
            if 'in' in natural_lower:
                match = re.search(r'(\w+)\s+in\s+([A-Z][a-z]+)', natural_query)
                if match and 'country' in sql_lower:
                    entity = match.group(1)
                    location = match.group(2)
                    insights.append((
                        entity, 'country',
                        f"Country where {entity} are located",
                        0.85
                    ))
            
            # Pattern: "vendors from USA" - similar to above
            if 'from' in natural_lower:
                match = re.search(r'(\w+)\s+from\s+([A-Z][a-z]+)', natural_query)
                if match and ('country' in sql_lower or 'location' in sql_lower):
                    entity = match.group(1)
                    location = match.group(2)
                    insights.append((
                        entity, 'country',
                        f"Country of origin for {entity}",
                        0.85
                    ))
            
            # Pattern: "total amount" suggests amount is a financial field
            if 'total' in natural_lower and 'amount' in natural_lower:
                if 'amount' in sql_lower:
                    # Try to find table name
                    table_match = re.search(r'from\s+(\w+)', sql_lower)
                    if table_match:
                        table = table_match.group(1)
                        insights.append((
                            table, 'amount',
                            "Total monetary amount",
                            0.80
                        ))
            
            # Pattern: "count by city" suggests city is a grouping/category field
            if 'by city' in natural_lower or 'by country' in natural_lower:
                grouping = 'city' if 'by city' in natural_lower else 'country'
                if f'group by {grouping}' in sql_lower:
                    table_match = re.search(r'from\s+(\w+)', sql_lower)
                    if table_match:
                        table = table_match.group(1)
                        insights.append((
                            table, grouping,
                            f"{grouping.title()} for geographic grouping and analysis",
                            0.82
                        ))
            
            logger.debug(f"Extracted {len(insights)} insights from query")
            
        except Exception as e:
            logger.warning(f"Failed to extract query insights: {e}")
        
        return insights
    
    def get_improvement_suggestions(
        self,
        tenant_id: str,
        database_name: str,
        status: str = 'pending',
        min_confidence: float = 0.70,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get metadata improvement suggestions
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
            status: Status filter ('pending', 'approved', 'rejected', 'applied')
            min_confidence: Minimum confidence score
            limit: Maximum number of suggestions
        
        Returns:
            List of suggestion dictionaries
        """
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, table_name, column_name, current_description,
                        suggested_description, suggestion_reason, confidence_score,
                        based_on_queries_count, status, created_at
                    FROM metadata_improvement_suggestions
                    WHERE tenant_id = %s AND database_name = %s
                    AND status = %s AND confidence_score >= %s
                    ORDER BY confidence_score DESC, based_on_queries_count DESC
                    LIMIT %s
                """, (tenant_id, database_name, status, min_confidence, limit))
                
                suggestions = cursor.fetchall()
                
                return [dict(row) for row in suggestions]
                
        except Exception as e:
            logger.error(f"Failed to get improvement suggestions: {e}")
            return []
    
    def approve_suggestion(
        self,
        suggestion_id: int,
        user_id: str,
        apply_immediately: bool = True
    ) -> bool:
        """
        Approve and optionally apply a metadata improvement suggestion
        
        Args:
            suggestion_id: Suggestion ID
            user_id: User who approved
            apply_immediately: Whether to apply the change immediately
        
        Returns:
            True if successful
        """
        try:
            db_manager = get_db_manager()
            metadata_service = get_column_metadata_service()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get suggestion details
                cursor.execute("""
                    SELECT tenant_id, database_name, table_name, column_name,
                           suggested_description
                    FROM metadata_improvement_suggestions
                    WHERE id = %s
                """, (suggestion_id,))
                
                suggestion = cursor.fetchone()
                
                if not suggestion:
                    return False
                
                # Update suggestion status
                cursor.execute("""
                    UPDATE metadata_improvement_suggestions
                    SET status = %s, reviewed_by = %s, reviewed_at = NOW()
                    WHERE id = %s
                """, ('applied' if apply_immediately else 'approved', user_id, suggestion_id))
                
                conn.commit()
                
                # Apply if requested
                if apply_immediately:
                    success = metadata_service.save_column_metadata(
                        suggestion['tenant_id'],
                        suggestion['database_name'],
                        suggestion['table_name'],
                        suggestion['column_name'],
                        suggestion['suggested_description'],
                        user_id=user_id
                    )
                    
                    if success:
                        logger.info(f"✅ Applied metadata improvement (ID: {suggestion_id})")
                    
                    return success
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to approve suggestion: {e}")
            return False
    
    def get_quality_report(
        self,
        tenant_id: str,
        database_name: str
    ) -> Dict[str, Any]:
        """
        Get quality report for database metadata
        
        Args:
            tenant_id: Tenant ID
            database_name: Database name
        
        Returns:
            Quality report dictionary
        """
        try:
            db_manager = get_db_manager()
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_queries,
                        SUM(CASE WHEN execution_success = 1 THEN 1 ELSE 0 END) as successful_queries,
                        SUM(CASE WHEN user_feedback = 'positive' THEN 1 ELSE 0 END) as positive_feedback,
                        SUM(CASE WHEN user_feedback = 'negative' THEN 1 ELSE 0 END) as negative_feedback,
                        AVG(CASE WHEN user_rating IS NOT NULL THEN user_rating ELSE NULL END) as avg_rating
                    FROM query_learning_data
                    WHERE tenant_id = %s
                    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """, (tenant_id,))
                
                stats = cursor.fetchone()
                
                # Top performing tables
                cursor.execute("""
                    SELECT table_name, quality_score, times_used,
                           query_success_count, query_failure_count
                    FROM metadata_quality_metrics
                    WHERE tenant_id = %s AND database_name = %s
                    AND column_name IS NULL
                    ORDER BY quality_score DESC, times_used DESC
                    LIMIT 10
                """, (tenant_id, database_name))
                
                top_tables = cursor.fetchall()
                
                # Pending improvements
                cursor.execute("""
                    SELECT COUNT(*) as pending_count,
                           AVG(confidence_score) as avg_confidence
                    FROM metadata_improvement_suggestions
                    WHERE tenant_id = %s AND database_name = %s
                    AND status = 'pending'
                """, (tenant_id, database_name))
                
                improvements = cursor.fetchone()
                
                return {
                    'overall': dict(stats) if stats else {},
                    'top_tables': [dict(row) for row in top_tables],
                    'improvements': dict(improvements) if improvements else {}
                }
                
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            return {}


# Singleton instance
_learning_service_instance = None

def get_metadata_learning_service() -> MetadataLearningService:
    """Get singleton instance of MetadataLearningService"""
    global _learning_service_instance
    if _learning_service_instance is None:
        _learning_service_instance = MetadataLearningService()
    return _learning_service_instance

