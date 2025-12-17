"""
Database Schema Cache - Avoid repeated schema fetching
Reduces database load and improves response time
"""
import hashlib
import time
import logging
from typing import Optional, Dict, Tuple, Any
import threading

logger = logging.getLogger(__name__)


class SchemaCache:
    """
    Cache for database schema information
    Reduces repeated INFORMATION_SCHEMA queries
    """
    
    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize schema cache
        
        Args:
            ttl_minutes: Time-to-live for cached schemas in minutes
        """
        self.cache: Dict[str, Tuple[Any, Any, float]] = {}
        self.ttl = ttl_minutes * 60  # Convert to seconds
        self.lock = threading.Lock()
        
        # Metrics
        self.hits = 0
        self.misses = 0
        
        logger.info(f"✅ Schema Cache initialized: ttl={ttl_minutes} minutes")
    
    def _make_key(self, connection_string: str) -> str:
        """
        Generate cache key from connection string
        
        Args:
            connection_string: Database connection string
            
        Returns:
            Cache key (MD5 hash)
        """
        # Hash connection string for privacy & key generation
        return hashlib.md5(connection_string.encode()).hexdigest()
    
    def get(self, connection_string: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get cached schema
        
        Args:
            connection_string: Database connection string
            
        Returns:
            Tuple of (schema_string, schema_dict) or None if not found/expired
        """
        with self.lock:
            key = self._make_key(connection_string)
            
            if key in self.cache:
                schema_str, schema_dict, timestamp = self.cache[key]
                
                # Check if expired
                if time.time() - timestamp < self.ttl:
                    self.hits += 1
                    hit_rate = self.get_hit_rate()
                    
                    logger.info(f"✅ Schema cache HIT! (hit rate: {hit_rate:.1f}%)")
                    return (schema_str, schema_dict)
                else:
                    # Expired
                    del self.cache[key]
                    logger.debug("🕐 Schema cache entry expired")
            
            self.misses += 1
            logger.debug("❌ Schema cache MISS")
            return None
    
    def set(self, connection_string: str, schema_str: str, schema_dict: Dict[str, Any]):
        """
        Cache schema information
        
        Args:
            connection_string: Database connection string
            schema_str: Schema as formatted string (for LLM prompts)
            schema_dict: Schema as structured dictionary
        """
        with self.lock:
            key = self._make_key(connection_string)
            self.cache[key] = (schema_str, schema_dict, time.time())
            
            logger.info(f"💾 Cached schema: {len(schema_dict)} tables")
    
    def invalidate(self, connection_string: str = None):
        """
        Invalidate cached schema
        
        Args:
            connection_string: Specific connection to invalidate (None = all)
        """
        with self.lock:
            if connection_string:
                key = self._make_key(connection_string)
                if key in self.cache:
                    del self.cache[key]
                    logger.info("🗑️  Invalidated schema cache entry")
            else:
                old_size = len(self.cache)
                self.cache.clear()
                logger.info(f"🗑️  Schema cache cleared ({old_size} entries)")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, _, timestamp) in self.cache.items()
                if current_time - timestamp >= self.ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.info(f"🧹 Cleaned {len(expired_keys)} expired schema entries")
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_stats(self) -> Dict[str, any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{self.get_hit_rate():.1f}%",
                'ttl_minutes': self.ttl / 60
            }


# Global singleton
_schema_cache: Optional[SchemaCache] = None


def get_schema_cache(ttl_minutes: int = 60) -> SchemaCache:
    """
    Get or create the global schema cache instance
    
    Args:
        ttl_minutes: Time-to-live in minutes
        
    Returns:
        SchemaCache instance
    """
    global _schema_cache
    
    if _schema_cache is None:
        _schema_cache = SchemaCache(ttl_minutes=ttl_minutes)
    
    return _schema_cache

