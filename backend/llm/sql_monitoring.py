"""
SQL Performance Monitoring - Track metrics and performance
Provides insights for optimization and debugging
"""
import logging
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class SQLMetrics:
    """
    Performance monitoring and metrics collection for SQL operations
    
    Tracks:
    - Query success/failure rates
    - Execution times
    - Cache hit rates
    - Model usage
    - Cost estimates
    - Error patterns
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics collector
        
        Args:
            window_size: Number of recent queries to keep for metrics
        """
        self.window_size = window_size
        
        # Sliding window of recent queries
        self.recent_queries = deque(maxlen=window_size)
        
        # Aggregated metrics
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        
        # Timing metrics
        self.total_nl_to_sql_time = 0.0
        self.total_db_execution_time = 0.0
        self.total_end_to_end_time = 0.0
        
        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Model usage
        self.model_usage = defaultdict(int)
        
        # Cost tracking (estimated)
        self.estimated_total_cost = 0.0
        
        # Error tracking
        self.errors_by_type = defaultdict(int)
        
        # Performance buckets (ms)
        self.latency_buckets = {
            '<100ms': 0,
            '100-500ms': 0,
            '500ms-1s': 0,
            '1-3s': 0,
            '>3s': 0
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Start time for uptime
        self.start_time = datetime.now()
        
        logger.info(f"✅ SQL Metrics initialized (window: {window_size})")
    
    def track_query(
        self,
        nl_query: str,
        sql_query: Optional[str],
        success: bool,
        nl_to_sql_time_ms: float,
        db_execution_time_ms: float,
        model_used: Optional[str] = None,
        cache_hit: bool = False,
        error_type: Optional[str] = None,
        result_count: int = 0,
        estimated_cost: float = 0.0
    ):
        """
        Track a query execution
        
        Args:
            nl_query: Natural language query
            sql_query: Generated SQL (or None if failed)
            success: Whether query succeeded
            nl_to_sql_time_ms: Time to convert NL to SQL
            db_execution_time_ms: Time to execute DB query
            model_used: LLM model used
            cache_hit: Whether result came from cache
            error_type: Error type if failed
            result_count: Number of results returned
            estimated_cost: Estimated API cost
        """
        with self.lock:
            # Total time
            total_time = nl_to_sql_time_ms + db_execution_time_ms
            
            # Create query record
            record = {
                'timestamp': datetime.now().isoformat(),
                'nl_query': nl_query[:100],  # Truncate for storage
                'sql_query': sql_query[:200] if sql_query else None,
                'success': success,
                'nl_to_sql_time_ms': nl_to_sql_time_ms,
                'db_execution_time_ms': db_execution_time_ms,
                'total_time_ms': total_time,
                'model_used': model_used,
                'cache_hit': cache_hit,
                'error_type': error_type,
                'result_count': result_count,
                'estimated_cost': estimated_cost
            }
            
            # Add to recent queries
            self.recent_queries.append(record)
            
            # Update aggregates
            self.total_queries += 1
            
            if success:
                self.successful_queries += 1
            else:
                self.failed_queries += 1
                if error_type:
                    self.errors_by_type[error_type] += 1
            
            # Update timing
            self.total_nl_to_sql_time += nl_to_sql_time_ms
            self.total_db_execution_time += db_execution_time_ms
            self.total_end_to_end_time += total_time
            
            # Update cache metrics
            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            
            # Update model usage
            if model_used:
                self.model_usage[model_used] += 1
            
            # Update cost
            self.estimated_total_cost += estimated_cost
            
            # Update latency buckets
            if total_time < 100:
                self.latency_buckets['<100ms'] += 1
            elif total_time < 500:
                self.latency_buckets['100-500ms'] += 1
            elif total_time < 1000:
                self.latency_buckets['500ms-1s'] += 1
            elif total_time < 3000:
                self.latency_buckets['1-3s'] += 1
            else:
                self.latency_buckets['>3s'] += 1
            
            # Log summary
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(
                f"{status} | Query: '{nl_query[:40]}...' | "
                f"Time: {total_time:.0f}ms | Model: {model_used} | "
                f"Cache: {'HIT' if cache_hit else 'MISS'}"
            )
    
    def get_summary(self) -> Dict[str, any]:
        """Get comprehensive metrics summary"""
        with self.lock:
            # Calculate rates
            success_rate = (self.successful_queries / self.total_queries * 100) if self.total_queries > 0 else 0
            cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
            
            # Calculate averages
            avg_nl_to_sql = self.total_nl_to_sql_time / self.total_queries if self.total_queries > 0 else 0
            avg_db_exec = self.total_db_execution_time / self.total_queries if self.total_queries > 0 else 0
            avg_total = self.total_end_to_end_time / self.total_queries if self.total_queries > 0 else 0
            
            # Uptime
            uptime = datetime.now() - self.start_time
            
            return {
                'overview': {
                    'total_queries': self.total_queries,
                    'successful_queries': self.successful_queries,
                    'failed_queries': self.failed_queries,
                    'success_rate': f"{success_rate:.1f}%",
                    'uptime': str(uptime).split('.')[0]  # Remove microseconds
                },
                'performance': {
                    'avg_nl_to_sql_ms': f"{avg_nl_to_sql:.1f}",
                    'avg_db_execution_ms': f"{avg_db_exec:.1f}",
                    'avg_total_ms': f"{avg_total:.1f}",
                    'latency_distribution': self.latency_buckets
                },
                'caching': {
                    'cache_hits': self.cache_hits,
                    'cache_misses': self.cache_misses,
                    'hit_rate': f"{cache_hit_rate:.1f}%"
                },
                'models': {
                    'usage': dict(self.model_usage),
                    'total_queries': sum(self.model_usage.values())
                },
                'costs': {
                    'total_estimated': f"${self.estimated_total_cost:.4f}",
                    'avg_per_query': f"${(self.estimated_total_cost / self.total_queries):.6f}" if self.total_queries > 0 else "$0.000000"
                },
                'errors': {
                    'by_type': dict(self.errors_by_type),
                    'total_errors': self.failed_queries
                }
            }
    
    def get_recent_queries(self, limit: int = 20) -> List[Dict]:
        """Get recent query records"""
        with self.lock:
            return list(self.recent_queries)[-limit:]
    
    def get_slow_queries(self, threshold_ms: float = 1000, limit: int = 10) -> List[Dict]:
        """Get slowest queries above threshold"""
        with self.lock:
            slow_queries = [
                q for q in self.recent_queries
                if q['total_time_ms'] >= threshold_ms
            ]
            
            # Sort by time (descending)
            slow_queries.sort(key=lambda x: x['total_time_ms'], reverse=True)
            
            return slow_queries[:limit]
    
    def get_error_patterns(self) -> Dict[str, List[Dict]]:
        """Get queries grouped by error type"""
        with self.lock:
            error_patterns = defaultdict(list)
            
            for query in self.recent_queries:
                if not query['success'] and query['error_type']:
                    error_patterns[query['error_type']].append(query)
            
            return dict(error_patterns)
    
    def reset_metrics(self):
        """Reset all metrics (use with caution)"""
        with self.lock:
            self.recent_queries.clear()
            self.total_queries = 0
            self.successful_queries = 0
            self.failed_queries = 0
            self.total_nl_to_sql_time = 0.0
            self.total_db_execution_time = 0.0
            self.total_end_to_end_time = 0.0
            self.cache_hits = 0
            self.cache_misses = 0
            self.model_usage.clear()
            self.estimated_total_cost = 0.0
            self.errors_by_type.clear()
            self.latency_buckets = {k: 0 for k in self.latency_buckets.keys()}
            self.start_time = datetime.now()
            
            logger.info("🔄 Metrics reset")


# Global singleton
_sql_metrics: Optional[SQLMetrics] = None


def get_sql_metrics(window_size: int = 1000) -> SQLMetrics:
    """
    Get or create the global SQL metrics instance
    
    Args:
        window_size: Recent queries window size
        
    Returns:
        SQLMetrics instance
    """
    global _sql_metrics
    
    if _sql_metrics is None:
        _sql_metrics = SQLMetrics(window_size=window_size)
    
    return _sql_metrics

