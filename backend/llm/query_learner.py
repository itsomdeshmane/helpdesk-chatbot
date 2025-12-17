"""
Query Learning System - Learn from successful NL→SQL conversions
Improves over time by learning from patterns
"""
import json
import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class QueryLearner:
    """
    Learn from successful NL → SQL query conversions
    Stores successful patterns and suggests similar queries
    
    Benefits:
    - Learn from user interactions
    - Avoid repeating mistakes
    - Suggest SQL from similar past queries
    - Build domain-specific query library
    """
    
    def __init__(self, storage_path: str = "data/query_history.jsonl", max_history: int = 10000):
        """
        Initialize query learner
        
        Args:
            storage_path: Path to store query history (JSONL format)
            max_history: Maximum number of queries to keep
        """
        self.storage_path = Path(storage_path)
        self.max_history = max_history
        self.history: List[Dict] = []
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Metrics
        self.total_recorded = 0
        self.successful_queries = 0
        self.failed_queries = 0
        
        # Create storage directory
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
        
        logger.info(f"✅ Query Learner initialized: {len(self.history)} queries loaded")
    
    def _load_history(self):
        """Load query history from storage"""
        if not self.storage_path.exists():
            logger.info("No existing query history found")
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self.history.append(entry)
                        
                        if entry.get('success', False):
                            self.successful_queries += 1
                        else:
                            self.failed_queries += 1
            
            # Keep only recent entries
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            self.total_recorded = len(self.history)
            
            logger.info(f"Loaded {len(self.history)} query history entries")
        except Exception as e:
            logger.error(f"Failed to load query history: {e}")
            self.history = []
    
    def _save_entry(self, entry: Dict):
        """Append entry to storage file"""
        try:
            with open(self.storage_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to save query entry: {e}")
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate text similarity between two queries
        Simple word-overlap based similarity
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            Similarity score (0-1)
        """
        # Tokenize
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def record_success(
        self,
        nl_query: str,
        sql_query: str,
        result_count: int,
        execution_time_ms: float,
        model_used: str,
        metadata: Optional[Dict] = None
    ):
        """
        Record a successful query conversion
        
        Args:
            nl_query: Natural language query
            sql_query: Generated SQL query
            result_count: Number of results returned
            execution_time_ms: Query execution time
            model_used: LLM model used
            metadata: Additional metadata
        """
        with self.lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'nl_query': nl_query,
                'sql_query': sql_query,
                'result_count': result_count,
                'execution_time_ms': execution_time_ms,
                'model_used': model_used,
                'success': True,
                'metadata': metadata or {}
            }
            
            self.history.append(entry)
            self.total_recorded += 1
            self.successful_queries += 1
            
            # Save to disk
            self._save_entry(entry)
            
            # Trim if too large
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            logger.debug(f"✅ Recorded successful query: '{nl_query[:50]}...'")
    
    def record_failure(
        self,
        nl_query: str,
        error_message: str,
        attempted_sql: Optional[str] = None,
        model_used: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Record a failed query conversion
        
        Args:
            nl_query: Natural language query
            error_message: Error that occurred
            attempted_sql: SQL that was attempted (if any)
            model_used: LLM model used
            metadata: Additional metadata
        """
        with self.lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'nl_query': nl_query,
                'attempted_sql': attempted_sql,
                'error_message': error_message,
                'model_used': model_used,
                'success': False,
                'metadata': metadata or {}
            }
            
            self.history.append(entry)
            self.total_recorded += 1
            self.failed_queries += 1
            
            # Save to disk
            self._save_entry(entry)
            
            # Trim if too large
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            logger.debug(f"❌ Recorded failed query: '{nl_query[:50]}...'")
    
    def find_similar_successful_query(
        self,
        nl_query: str,
        min_similarity: float = 0.85,
        max_results: int = 3
    ) -> List[Tuple[Dict, float]]:
        """
        Find similar successful queries from history
        
        Args:
            nl_query: Natural language query to match
            min_similarity: Minimum similarity threshold
            max_results: Maximum number of results
            
        Returns:
            List of (query_entry, similarity_score) tuples
        """
        with self.lock:
            # Filter successful queries
            successful = [q for q in self.history if q.get('success', False)]
            
            if not successful:
                return []
            
            # Calculate similarities
            scored = []
            for query_entry in successful:
                similarity = self._calculate_similarity(nl_query, query_entry['nl_query'])
                if similarity >= min_similarity:
                    scored.append((query_entry, similarity))
            
            # Sort by similarity (descending) and recency
            scored.sort(key=lambda x: (x[1], x[0]['timestamp']), reverse=True)
            
            results = scored[:max_results]
            
            if results:
                logger.info(f"🔍 Found {len(results)} similar queries (best: {results[0][1]:.2f})")
            
            return results
    
    def get_common_patterns(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most common query patterns
        
        Args:
            top_n: Number of top patterns to return
            
        Returns:
            List of (nl_query, count) tuples
        """
        with self.lock:
            # Count successful queries
            query_counts = {}
            for entry in self.history:
                if entry.get('success', False):
                    nl = entry['nl_query'].lower().strip()
                    query_counts[nl] = query_counts.get(nl, 0) + 1
            
            # Sort by count
            sorted_patterns = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_patterns[:top_n]
    
    def get_failure_patterns(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most common failure patterns
        Helps identify problematic query types
        
        Args:
            top_n: Number of top patterns to return
            
        Returns:
            List of (nl_query, count) tuples
        """
        with self.lock:
            # Count failed queries
            failure_counts = {}
            for entry in self.history:
                if not entry.get('success', False):
                    nl = entry['nl_query'].lower().strip()
                    failure_counts[nl] = failure_counts.get(nl, 0) + 1
            
            # Sort by count
            sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_failures[:top_n]
    
    def get_stats(self) -> Dict[str, any]:
        """Get learning statistics"""
        with self.lock:
            success_rate = (self.successful_queries / self.total_recorded * 100) if self.total_recorded > 0 else 0
            
            # Get average execution time for successful queries
            exec_times = [
                q['execution_time_ms']
                for q in self.history
                if q.get('success', False) and 'execution_time_ms' in q
            ]
            avg_exec_time = sum(exec_times) / len(exec_times) if exec_times else 0
            
            return {
                'total_queries': self.total_recorded,
                'successful_queries': self.successful_queries,
                'failed_queries': self.failed_queries,
                'success_rate': f"{success_rate:.1f}%",
                'history_size': len(self.history),
                'avg_execution_time_ms': f"{avg_exec_time:.1f}",
                'storage_path': str(self.storage_path)
            }


# Global singleton
_query_learner: Optional[QueryLearner] = None


def get_query_learner(storage_path: str = "data/query_history.jsonl", max_history: int = 10000) -> QueryLearner:
    """
    Get or create the global query learner instance
    
    Args:
        storage_path: Path to store query history
        max_history: Maximum history size
        
    Returns:
        QueryLearner instance
    """
    global _query_learner
    
    if _query_learner is None:
        _query_learner = QueryLearner(storage_path=storage_path, max_history=max_history)
    
    return _query_learner

