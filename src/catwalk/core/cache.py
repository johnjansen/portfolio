# src/core/cache.py
from typing import Generic, TypeVar, Dict, Optional
from collections import OrderedDict
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """Represents a single cache entry with metadata"""
    value: T
    size_bytes: int
    last_accessed: float
    access_count: int

class LRUCache(Generic[T]):
    """
    Memory-aware LRU cache implementation for model management.

    Features:
    - Tracks memory usage of cached items
    - Maintains access patterns and timestamps
    - Supports soft and hard memory limits
    - Provides eviction strategies based on memory pressure
    """

    def __init__(
        self,
        max_size_bytes: int,
        soft_limit_bytes: Optional[int] = None
    ):
        """
        Initialize the LRU cache.

        Args:
            max_size_bytes: Hard limit for cache size in bytes
            soft_limit_bytes: Optional soft limit triggering background cleanup
        """
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._max_size_bytes = max_size_bytes
        self._soft_limit_bytes = soft_limit_bytes or (max_size_bytes * 0.85)
        self._current_size_bytes = 0

        logger.info(
            f"Initialized LRU Cache with max size: {max_size_bytes:,} bytes "
            f"(soft limit: {self._soft_limit_bytes:,} bytes)"
        )

    def get(self, key: str) -> Optional[T]:
        """
        Retrieve an item from the cache, updating its access patterns.

        Args:
            key: Cache key to lookup

        Returns:
            The cached value if found, None otherwise
        """
        if key not in self._cache:
            return None

        # Update access patterns
        entry = self._cache.pop(key)
        entry.last_accessed = time.time()
        entry.access_count += 1
        self._cache[key] = entry

        logger.debug(f"Cache hit for key: {key}")
        return entry.value

    def put(self, key: str, value: T, size_bytes: int) -> None:
        """
        Add or update an item in the cache.

        Args:
            key: Cache key
            value: Value to cache
            size_bytes: Memory size of the value in bytes
        """
        if key in self._cache:
            self._current_size_bytes -= self._cache[key].size_bytes

        # Check if we need to evict items
        while (self._current_size_bytes + size_bytes) > self._max_size_bytes:
            if not self._evict_lru():
                raise ValueError("Cannot add item: cache full and nothing to evict")

        entry = CacheEntry(
            value=value,
            size_bytes=size_bytes,
            last_accessed=time.time(),
            access_count=1
        )

        self._cache[key] = entry
        self._current_size_bytes += size_bytes

        logger.info(
            f"Added key {key} to cache "
            f"(size: {size_bytes:,} bytes, "
            f"total: {self._current_size_bytes:,} bytes)"
        )

    def _evict_lru(self) -> bool:
        """
        Evict the least recently used item from the cache.

        Returns:
            True if an item was evicted, False if cache is empty
        """
        if not self._cache:
            return False

        # Get the least recently used item
        key, entry = next(iter(self._cache.items()))
        self._cache.pop(key)
        self._current_size_bytes -= entry.size_bytes

        logger.info(
            f"Evicted key {key} from cache "
            f"(freed: {entry.size_bytes:,} bytes)"
        )
        return True

    def clear(self) -> None:
        """Clear all items from the cache"""
        self._cache.clear()
        self._current_size_bytes = 0
        logger.info("Cache cleared")

    @property
    def size_bytes(self) -> int:
        """Current size of cached items in bytes"""
        return self._current_size_bytes

    @property
    def count(self) -> int:
        """Number of items in cache"""
        return len(self._cache)

    def stats(self) -> Dict[str, any]:
        """
        Get current cache statistics

        Returns:
            Dictionary of cache metrics
        """
        return {
            "item_count": len(self._cache),
            "current_size_bytes": self._current_size_bytes,
            "max_size_bytes": self._max_size_bytes,
            "utilization": self._current_size_bytes / self._max_size_bytes,
        }
