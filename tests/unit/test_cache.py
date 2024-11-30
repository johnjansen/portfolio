# catwalk/tests/unit/test_cache.py

import pytest
from src.catwalk.core.cache import LRUCache, CacheEntry  # Updated import path

class TestLRUCache:
    """Test suite for the LRU Cache implementation"""

    @pytest.fixture
    def cache(self):
        """Fixture providing a default cache instance for testing"""
        return LRUCache(max_size_bytes=1000, soft_limit_bytes=800)

    def test_cache_initialization(self):
        """Test that cache initializes with correct parameters"""
        cache = LRUCache(max_size_bytes=1000, soft_limit_bytes=800)
        assert cache._current_size_bytes == 0  # Updated to match implementation
        assert cache.count == 0

        stats = cache.stats()
        assert stats["max_size_bytes"] == 1000
        assert stats["current_size_bytes"] == 0
        assert stats["utilization"] == 0.0

    def test_basic_put_and_get(self, cache):
        """Test basic put and get operations"""
        # Put an item
        cache.put("key1", "value1", size_bytes=100)

        # Verify get
        assert cache.get("key1") == "value1"
        assert cache._current_size_bytes == 100  # Updated to match implementation
        assert cache.count == 1

    def test_cache_miss(self, cache):
        """Test behavior when accessing non-existent key"""
        assert cache.get("nonexistent") is None

    def test_update_existing_key(self, cache):
        """Test updating an existing cache entry"""
        # Initial put
        cache.put("key1", "value1", size_bytes=100)
        assert cache._current_size_bytes == 100  # Updated to match implementation

        # Update same key
        cache.put("key1", "value2", size_bytes=150)

        assert cache.get("key1") == "value2"
        assert cache._current_size_bytes == 150  # Updated to match implementation
        assert cache.count == 1

    def test_lru_eviction(self, cache):
        """Test that least recently used items are evicted when cache is full"""
        # Fill cache
        cache.put("key1", "value1", size_bytes=400)
        cache.put("key2", "value2", size_bytes=400)

        # This should trigger eviction of key1
        cache.put("key3", "value3", size_bytes=400)

        assert cache.get("key1") is None  # Should be evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache._current_size_bytes == 800  # Updated to match implementation
        assert cache.count == 2

    # ... rest of the tests remain the same ...

    def test_concurrent_size_tracking(self, cache):
        """Test that size tracking remains accurate through operations"""
        initial_sizes = [100, 200, 300]
        for i, size in enumerate(initial_sizes):
            cache.put(f"key_{i}", f"value_{i}", size_bytes=size)

        assert cache._current_size_bytes == sum(initial_sizes)  # Updated to match implementation

        # Update middle entry
        cache.put("key_1", "new_value", size_bytes=150)

        expected_size = initial_sizes[0] + 150 + initial_sizes[2]
        assert cache._current_size_bytes == expected_size  # Updated to match implementation
