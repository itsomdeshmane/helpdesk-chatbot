"""
Cache Manager - Production Ready
Provides caching for embeddings, queries, and search results
Supports both Redis (production) and in-memory (development) backends
"""

import hashlib
import json
import os
import pickle
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from functools import wraps
import time


class CacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    def clear(self, pattern: str = None) -> int:
        """Clear cache entries, optionally matching pattern"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        pass


class InMemoryCache(CacheBackend):
    """
    In-memory cache backend for development/testing.
    Thread-safe with LRU eviction.
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (1 hour)
        """
        self._cache: Dict[str, Tuple[Any, datetime, int]] = {}  # key -> (value, created_at, ttl)
        self._access_times: Dict[str, datetime] = {}  # For LRU tracking
        self._lock = threading.RLock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        
        print(f"✅ In-memory cache initialized (max_size={max_size}, default_ttl={default_ttl}s)", flush=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, created_at, ttl = self._cache[key]
            
            # Check TTL
            if ttl and datetime.now() - created_at > timedelta(seconds=ttl):
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                self._misses += 1
                return None
            
            # Update access time for LRU
            self._access_times[key] = datetime.now()
            self._hits += 1
            return value
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self._max_size:
                self._evict_lru()
            
            self._cache[key] = (value, datetime.now(), ttl or self._default_ttl)
            self._access_times[key] = datetime.now()
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            if key not in self._cache:
                return False
            
            value, created_at, ttl = self._cache[key]
            if ttl and datetime.now() - created_at > timedelta(seconds=ttl):
                del self._cache[key]
                return False
            
            return True
    
    def clear(self, pattern: str = None) -> int:
        """Clear cache entries"""
        with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                self._access_times.clear()
                return count
            
            # Clear matching pattern
            import fnmatch
            keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
            return len(keys_to_delete)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                'backend': 'in_memory',
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.2%}",
                'memory_usage_mb': self._estimate_memory_usage() / (1024 * 1024)
            }
    
    def _evict_lru(self):
        """Evict least recently used entries"""
        if not self._access_times:
            return
        
        # Find LRU key
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes"""
        try:
            return len(pickle.dumps(self._cache))
        except:
            return 0


class RedisCache(CacheBackend):
    """
    Redis cache backend for production.
    Requires redis-py package and running Redis server.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        default_ttl: int = 3600,
        prefix: str = "helpdesk:"
    ):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            default_ttl: Default TTL in seconds
            prefix: Key prefix for namespacing
        """
        self._default_ttl = default_ttl
        self._prefix = prefix
        self._hits = 0
        self._misses = 0
        
        try:
            import redis
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False  # Handle binary data
            )
            # Test connection
            self._client.ping()
            self._available = True
            print(f"✅ Redis cache connected ({host}:{port}, db={db})", flush=True)
        except Exception as e:
            print(f"⚠️ Redis not available, falling back to in-memory cache: {e}", flush=True)
            self._available = False
            self._fallback = InMemoryCache(default_ttl=default_ttl)
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self._prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._available:
            return self._fallback.get(key)
        
        try:
            data = self._client.get(self._make_key(key))
            if data is None:
                self._misses += 1
                return None
            
            self._hits += 1
            return pickle.loads(data)
        except Exception as e:
            print(f"⚠️ Redis get error: {e}", flush=True)
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self._available:
            return self._fallback.set(key, value, ttl)
        
        try:
            data = pickle.dumps(value)
            self._client.setex(
                self._make_key(key),
                ttl or self._default_ttl,
                data
            )
            return True
        except Exception as e:
            print(f"⚠️ Redis set error: {e}", flush=True)
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._available:
            return self._fallback.delete(key)
        
        try:
            return self._client.delete(self._make_key(key)) > 0
        except Exception as e:
            print(f"⚠️ Redis delete error: {e}", flush=True)
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._available:
            return self._fallback.exists(key)
        
        try:
            return self._client.exists(self._make_key(key)) > 0
        except:
            return False
    
    def clear(self, pattern: str = None) -> int:
        """Clear cache entries"""
        if not self._available:
            return self._fallback.clear(pattern)
        
        try:
            if pattern is None:
                pattern = "*"
            
            full_pattern = self._make_key(pattern)
            keys = self._client.keys(full_pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            print(f"⚠️ Redis clear error: {e}", flush=True)
            return 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self._available:
            stats = self._fallback.get_stats()
            stats['backend'] = 'in_memory_fallback'
            return stats
        
        try:
            info = self._client.info('stats')
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                'backend': 'redis',
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.2%}",
                'redis_hits': info.get('keyspace_hits', 0),
                'redis_misses': info.get('keyspace_misses', 0),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_mb': info.get('used_memory', 0) / (1024 * 1024)
            }
        except:
            return {'backend': 'redis', 'error': 'Could not fetch stats'}


class CacheManager:
    """
    High-level cache manager with specialized caching methods.
    Provides caching for embeddings, search results, and query responses.
    """
    
    def __init__(self, backend: CacheBackend = None):
        """
        Initialize cache manager.
        
        Args:
            backend: Cache backend to use (defaults to in-memory)
        """
        # Try Redis first, fall back to in-memory
        if backend:
            self._cache = backend
        else:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            # Try Redis, fallback to in-memory automatically
            self._cache = RedisCache(
                host=redis_host,
                port=redis_port,
                password=redis_password
            )
        
        # TTL configurations (in seconds)
        self.EMBEDDING_TTL = 86400  # 24 hours
        self.SEARCH_TTL = 3600       # 1 hour
        self.RESPONSE_TTL = 1800     # 30 minutes
        self.QUERY_REWRITE_TTL = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments"""
        content = ":".join(str(arg) for arg in args)
        hash_value = hashlib.md5(content.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    # ===== Embedding Caching =====
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        key = self._generate_key("emb", text)
        return self._cache.get(key)
    
    def set_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding for text"""
        key = self._generate_key("emb", text)
        return self._cache.set(key, embedding, self.EMBEDDING_TTL)
    
    def get_or_create_embedding(
        self,
        text: str,
        create_fn: callable
    ) -> List[float]:
        """
        Get embedding from cache or create it.
        
        Args:
            text: Text to embed
            create_fn: Function to create embedding if not cached
        
        Returns:
            Embedding vector
        """
        cached = self.get_embedding(text)
        if cached is not None:
            return cached
        
        embedding = create_fn(text)
        self.set_embedding(text, embedding)
        return embedding
    
    # ===== Search Results Caching =====
    
    def get_search_results(
        self,
        query: str,
        tenant_id: str
    ) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = self._generate_key("search", query, tenant_id)
        return self._cache.get(key)
    
    def set_search_results(
        self,
        query: str,
        tenant_id: str,
        results: List[Dict]
    ) -> bool:
        """Cache search results"""
        key = self._generate_key("search", query, tenant_id)
        return self._cache.set(key, results, self.SEARCH_TTL)
    
    # ===== Response Caching =====
    
    def get_response(
        self,
        query: str,
        context_hash: str
    ) -> Optional[Dict]:
        """Get cached response"""
        key = self._generate_key("resp", query, context_hash)
        return self._cache.get(key)
    
    def set_response(
        self,
        query: str,
        context_hash: str,
        response: Dict
    ) -> bool:
        """Cache response"""
        key = self._generate_key("resp", query, context_hash)
        return self._cache.set(key, response, self.RESPONSE_TTL)
    
    # ===== Query Rewrite Caching =====
    
    def get_rewritten_query(
        self,
        query: str,
        context: str = ""
    ) -> Optional[str]:
        """Get cached rewritten query"""
        key = self._generate_key("rewrite", query, context)
        return self._cache.get(key)
    
    def set_rewritten_query(
        self,
        query: str,
        context: str,
        rewritten: str
    ) -> bool:
        """Cache rewritten query"""
        key = self._generate_key("rewrite", query, context)
        return self._cache.set(key, rewritten, self.QUERY_REWRITE_TTL)
    
    # ===== Utility Methods =====
    
    def clear_all(self) -> int:
        """Clear all cache entries"""
        return self._cache.clear()
    
    def clear_embeddings(self) -> int:
        """Clear all cached embeddings"""
        return self._cache.clear("emb:*")
    
    def clear_search_results(self) -> int:
        """Clear all cached search results"""
        return self._cache.clear("search:*")
    
    def clear_responses(self) -> int:
        """Clear all cached responses"""
        return self._cache.clear("resp:*")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return self._cache.get_stats()


# Cache decorator for functions
def cached(
    cache_manager: CacheManager,
    prefix: str,
    ttl: int = None
):
    """
    Decorator for caching function results.
    
    Args:
        cache_manager: CacheManager instance
        prefix: Cache key prefix
        ttl: Time to live in seconds
    
    Usage:
        @cached(cache_manager, "my_func", ttl=3600)
        def my_expensive_function(arg1, arg2):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [prefix, func.__name__] + [str(a) for a in args]
            key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
            key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            full_key = f"{prefix}:{key}"
            
            # Try to get from cache
            cached_result = cache_manager._cache.get(full_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager._cache.set(full_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Singleton instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create the singleton CacheManager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

