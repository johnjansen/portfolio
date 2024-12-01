# src/catwalk/core/cache.py
from typing import Optional, Dict, Any, NamedTuple
from collections import OrderedDict
import time
import logging

logger = logging.getLogger(__name__)

class CacheEntry(NamedTuple):
    value: Any
    size_bytes: int
    last_accessed: float

class LRUCache:
    def __init__(self, max_size_bytes: int, soft_limit_bytes: Optional[int] = None):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size_bytes = max_size_bytes
        self._soft_limit_bytes = soft_limit_bytes or (max_size_bytes * 0.85)
        self._current_size_bytes = 0
        print(f"Cache initialized: max={max_size_bytes}, soft={self._soft_limit_bytes}")

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None

        # Move to end (most recently used)
        entry = self._cache.pop(key)
        self._cache[key] = CacheEntry(
            entry.value,
            entry.size_bytes,
            time.time()
        )
        return entry.value

    @property
    def available_space(self):
        return self._max_size_bytes - self._current_size_bytes

    def put(self, key: str, value: Any, size_bytes: int) -> None:
        print(f"\nPutting {key} (size={size_bytes})")
        print(f"Before put: current_size={self._current_size_bytes}, max={self._max_size_bytes}")

        if size_bytes > self._max_size_bytes:
            raise ValueError(f"Item size {size_bytes} exceeds cache maximum {self._max_size_bytes}")

        # If key exists, remove it first
        if key in self._cache:
            old_entry = self._cache.pop(key)
            self._current_size_bytes -= old_entry.size_bytes
            print(f"Removed existing entry for {key}, freed {old_entry.size_bytes}")

        # Calculate required space
        required_space = size_bytes

        # If we need more space, evict items
        if required_space > self.available_space:
            print(f"Need to free {required_space - self.available_space} bytes")
            self._make_space(required_space, key)

        # Add new entry
        self._cache[key] = CacheEntry(value, size_bytes, time.time())
        self._current_size_bytes += size_bytes

        print(f"After put: current_size={self._current_size_bytes}, max={self._max_size_bytes}")
        self._print_cache_state()

    def _make_space(self, needed_bytes: int, exclude_key: Optional[str] = None) -> None:
        """Make space for needed_bytes by evicting least recently used items first"""
        to_free = needed_bytes - self.available_space

        if to_free <= 0:
            return  # No need to free up space

        # Get items sorted by last access time (sorted() returns ascending order - oldest first)
        items = sorted(self._cache.items(), key=lambda x: x[1].last_accessed)

        # Track how much space we've freed
        freed_space = 0
        to_remove = []

        # Collect items to remove until we have enough space
        for key, entry in items:
            if key == exclude_key:
                continue
            to_remove.append(key)
            freed_space += entry.size_bytes
            if freed_space >= to_free:
                break

        # Remove the items
        for key in to_remove:
            entry = self._cache.pop(key)
            self._current_size_bytes -= entry.size_bytes
            print(f"Evicted {key}, freed {entry.size_bytes} bytes")

    def remove(self, key: str) -> None:
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_size_bytes -= entry.size_bytes

    def clear(self) -> None:
        self._cache.clear()
        self._current_size_bytes = 0

    def get_last_access_time(self, key: str) -> Optional[float]:
        if key in self._cache:
            return self._cache[key].last_accessed
        return None

    def stats(self) -> Dict[str, Any]:
        return {
            "item_count": len(self._cache),
            "current_size_bytes": self._current_size_bytes,
            "max_size_bytes": self._max_size_bytes,
            "utilization": self._current_size_bytes / self._max_size_bytes
        }

    @property
    def count(self) -> int:
        return len(self._cache)

    def _print_cache_state(self) -> None:
        print("\nCache state:")
        for key, entry in self._cache.items():
            print(f"  {key}: size={entry.size_bytes} => {entry}")
