"""
Cache Manager Module

This module provides caching functionality for SPARQL query results to improve
performance and reduce database load. Supports both in-memory and Redis caching.

Key Features:
- Automatic query result caching
- TTL (Time To Live) for cache entries
- Memory and Redis backend support
- Cache invalidation utilities
- Decorator for easy caching integration

Usage:
    from cache_manager import cache_query_result, CacheManager
    
    @cache_query_result(ttl=300)
    def expensive_query(param):
        # Execute SPARQL query
        return results
"""

import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional, Dict
import pickle

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager that provides a unified interface for caching with support
    for both in-memory and Redis backends.
    
    Attributes:
        backend: Cache backend ('memory' or 'redis')
        default_ttl: Default time-to-live for cache entries in seconds
        enabled: Whether caching is enabled
    """
    
    def __init__(self, backend: str = 'memory', default_ttl: int = 300, enabled: bool = True):
        """
        Initialize the cache manager.
        
        Args:
            backend: Cache backend type ('memory' or 'redis')
            default_ttl: Default TTL in seconds (default: 300 = 5 minutes)
            enabled: Whether caching is enabled (default: True)
        """
        self.backend = backend
        self.default_ttl = default_ttl
        self.enabled = enabled
        self._memory_cache: Dict[str, tuple] = {}  # key -> (value, expiry_timestamp)
        self._redis_client = None
        
        if backend == 'redis' and enabled:
            self._initialize_redis()
        
        logger.info(
            "Initialized CacheManager",
            extra={
                'backend': backend,
                'default_ttl': default_ttl,
                'enabled': enabled
            }
        )
    
    def _initialize_redis(self) -> None:
        """Initialize Redis client connection."""
        try:
            import redis
            from config import CACHE_REDIS_HOST, CACHE_REDIS_PORT, CACHE_REDIS_DB
            
            self._redis_client = redis.Redis(
                host=CACHE_REDIS_HOST,
                port=CACHE_REDIS_PORT,
                db=CACHE_REDIS_DB,
                decode_responses=False  # We'll handle encoding ourselves
            )
            # Test connection
            self._redis_client.ping()
            logger.info(
                "Redis cache backend initialized",
                extra={
                    'host': CACHE_REDIS_HOST,
                    'port': CACHE_REDIS_PORT,
                    'db': CACHE_REDIS_DB
                }
            )
        except ImportError:
            logger.warning("Redis library not installed. Falling back to memory cache.")
            self.backend = 'memory'
        except Exception as e:
            logger.error("Failed to connect to Redis: %s. Falling back to memory cache.", e)
            self.backend = 'memory'
            self._redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Args:
            prefix: Prefix for the cache key (usually function name)
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key as a string
        """
        # Create a deterministic string representation of the arguments
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items())  # Sort for consistency
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        # Hash the key to keep it a reasonable length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        return f"shacl_cache:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if not self.enabled:
            return None
        
        try:
            if self.backend == 'redis' and self._redis_client:
                value = self._redis_client.get(key)
                if value:
                    logger.debug("Cache hit (Redis): %s", key)
                    self._track_cache_metric('get', 'hit')
                    return pickle.loads(value)
                else:
                    self._track_cache_metric('get', 'miss')
            else:
                # Memory cache
                if key in self._memory_cache:
                    value, expiry = self._memory_cache[key]
                    import time
                    if expiry is None or time.time() < expiry:
                        logger.debug("Cache hit (memory): %s", key)
                        self._track_cache_metric('get', 'hit')
                        return value
                    else:
                        # Expired - remove it
                        del self._memory_cache[key]
                        logger.debug("Cache expired (memory): %s", key)
                        self._track_cache_metric('get', 'miss')
                else:
                    self._track_cache_metric('get', 'miss')
        except Exception as e:
            logger.error("Error retrieving from cache: %s", e)
            self._track_cache_metric('get', 'error')
        
        logger.debug("Cache miss: %s", key)
        return None
    
    def _track_cache_metric(self, operation: str, result: str):
        """Track cache operation metrics."""
        try:
            from metrics import get_metrics_manager
            metrics = get_metrics_manager()
            metrics.track_cache_operation(operation, result)
        except Exception:
            pass  # Silently ignore metrics errors
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (None = use default)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        ttl = ttl or self.default_ttl
        
        try:
            if self.backend == 'redis' and self._redis_client:
                serialized = pickle.dumps(value)
                self._redis_client.setex(key, ttl, serialized)
                logger.debug("Cached in Redis: %s (TTL: %ds)", key, ttl)
                self._track_cache_metric('set', 'success')
                return True
            else:
                # Memory cache
                import time
                expiry = time.time() + ttl if ttl else None
                self._memory_cache[key] = (value, expiry)
                logger.debug("Cached in memory: %s (TTL: %ds)", key, ttl)
                self._track_cache_metric('set', 'success')
                return True
        except Exception as e:
            logger.error("Error storing in cache: %s", e)
            self._track_cache_metric('set', 'error')
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.backend == 'redis' and self._redis_client:
                self._redis_client.delete(key)
                logger.debug("Deleted from Redis cache: %s", key)
                self._track_cache_metric('delete', 'success')
                return True
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    logger.debug("Deleted from memory cache: %s", key)
                self._track_cache_metric('delete', 'success')
                return True
        except Exception as e:
            logger.error("Error deleting from cache: %s", e)
            self._track_cache_metric('delete', 'error')
            return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match keys (Redis only, e.g., 'shacl_cache:*')
                    If None, clears all entries
            
        Returns:
            Number of entries cleared
        """
        count = 0
        try:
            if self.backend == 'redis' and self._redis_client:
                if pattern:
                    keys = self._redis_client.keys(pattern)
                    if keys:
                        count = self._redis_client.delete(*keys)
                else:
                    self._redis_client.flushdb()
                    count = -1  # Unknown count
                logger.info("Cleared Redis cache (pattern: %s, count: %d)", pattern, count)
            else:
                if pattern:
                    # Simple pattern matching for memory cache
                    keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                    for key in keys_to_delete:
                        del self._memory_cache[key]
                    count = len(keys_to_delete)
                else:
                    count = len(self._memory_cache)
                    self._memory_cache.clear()
                logger.info("Cleared memory cache (pattern: %s, count: %d)", pattern, count)
        except Exception as e:
            logger.error("Error clearing cache: %s", e)
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'backend': self.backend,
            'enabled': self.enabled,
            'default_ttl': self.default_ttl
        }
        
        if self.backend == 'memory':
            stats['entries'] = len(self._memory_cache)
        elif self.backend == 'redis' and self._redis_client:
            try:
                info = self._redis_client.info('stats')
                stats['redis_connected'] = True
                stats['total_connections_received'] = info.get('total_connections_received', 0)
                stats['keyspace_hits'] = info.get('keyspace_hits', 0)
                stats['keyspace_misses'] = info.get('keyspace_misses', 0)
            except Exception as e:
                stats['redis_connected'] = False
                stats['error'] = str(e)
        
        return stats


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        The global CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        from config import (
            CACHE_ENABLED, CACHE_BACKEND, CACHE_DEFAULT_TTL
        )
        _cache_manager = CacheManager(
            backend=CACHE_BACKEND,
            default_ttl=CACHE_DEFAULT_TTL,
            enabled=CACHE_ENABLED
        )
    return _cache_manager


def cache_query_result(ttl: Optional[int] = None, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds (None = use default)
        key_prefix: Optional prefix for cache key (default: function name)
        
    Usage:
        @cache_query_result(ttl=300)
        def get_shapes(graph_uri):
            return execute_query(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            cache.set(cache_key, result, ttl)
            logger.debug(
                "Cached result for %s (execution: %.3fs)",
                func.__name__,
                execution_time
            )
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str = 'shacl_cache:*') -> int:
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys
        
    Returns:
        Number of entries invalidated
    """
    cache = get_cache_manager()
    return cache.clear(pattern)
