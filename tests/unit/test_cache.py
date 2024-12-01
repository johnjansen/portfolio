# portfolio/tests/unit/test_cache.py
import time
import pytest
from src.portfolio.core.cache import LRUCache, CacheEntry  # Updated import path

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

    def test_basic_eviction(self, cache):
        """Test that adding items beyond capacity triggers eviction"""
        # Fill cache to capacity
        cache.put("model1", "value1", size_bytes=400)
        cache.put("model2", "value2", size_bytes=400)

        # Verify initial state
        assert cache.get("model1") == "value1"
        assert cache.get("model2") == "value2"
        assert cache._current_size_bytes == 800

        # Add new model that pushes us over capacity
        cache.put("model3", "value3", size_bytes=400)

        # Verify least recently used (model1) was evicted
        assert cache.get("model1") is None
        assert cache.get("model2") == "value2"
        assert cache.get("model3") == "value3"
        assert cache._current_size_bytes == 800

    def test_access_pattern_affects_eviction(self, cache):
        """Test that accessing items affects eviction order"""
        # Add initial items
        cache.put("model1", "value1", size_bytes=300)
        cache.put("model2", "value2", size_bytes=300)
        cache.put("model3", "value3", size_bytes=300)

        # Access model1 to make it most recently used
        cache.get("model1")

        # Add new item that requires eviction
        cache.put("model4", "value4", size_bytes=300)

        # model2 should be evicted as it's least recently used
        assert cache.get("model1") == "value1"  # Should still be present
        assert cache.get("model2") is None      # Should be evicted
        assert cache.get("model3") == "value3"  # Should still be present
        assert cache.get("model4") == "value4"  # Should be present

    def test_large_item_eviction(self, cache):
        """Test handling of items larger than soft limit"""
        # Fill cache with small items
        cache.put("small1", "value1", size_bytes=200)
        cache.put("small2", "value2", size_bytes=200)
        cache.put("small3", "value3", size_bytes=200)

        # Add item larger than soft limit but within max size
        cache.put("large", "large_value", size_bytes=900)

        # Verify all small items were evicted
        assert cache.get("small1") is None
        assert cache.get("small2") is None
        assert cache.get("small3") is None
        assert cache.get("large") == "large_value"
        assert cache._current_size_bytes == 900

    def test_multiple_evictions(self, cache):
        """Test multiple items are evicted if needed"""
        # Add multiple small items
        for i in range(5):
            cache.put(f"model{i}", f"value{i}", size_bytes=200)
            time.sleep(0.001)  # Ensure distinct access times

        print("A")
        cache._print_cache_state()
        print("B")

        # Add large item requiring multiple evictions
        cache.put("large", "large_value", size_bytes=700)
        print("C")

        cache._print_cache_state()
        print("D")

        # Verify oldest items were evicted and newest remain
        assert cache.get("model0") is None
        assert cache.get("model1") is None
        assert cache.get("model2") is None
        assert cache.get("model3") is None
        assert cache.get("model4") == "value4"
        assert cache.get("large") == "large_value"
        assert cache._current_size_bytes <= 1000

    def test_eviction_with_updates(self, cache):
        """Test eviction behavior when updating existing items"""
        # Fill cache
        cache.put("model1", "value1", size_bytes=400)
        cache.put("model2", "value2", size_bytes=400)

        # Update existing item with larger size
        cache.put("model1", "new_value", size_bytes=800)

        # Verify model2 was evicted to make space
        assert cache.get("model1") == "new_value"
        assert cache.get("model2") is None
        assert cache._current_size_bytes == 800

    def test_soft_limit_behavior(self, cache):
        """Test behavior around soft limit threshold"""
        # Fill to just below soft limit
        cache.put("model1", "value1", size_bytes=700)  # Below 800 soft limit

        # Add small item that pushes us over soft limit but under max
        cache.put("model2", "value2", size_bytes=200)  # Total: 900

        # Verify both items remain since we're under max size
        assert cache.get("model1") == "value1"
        assert cache.get("model2") == "value2"
        assert cache._current_size_bytes == 900

        # Add another item that would push us over max
        cache.put("model3", "value3", size_bytes=200)

        # Verify oldest item was evicted
        assert cache.get("model1") is None
        assert cache.get("model2") == "value2"
        assert cache.get("model3") == "value3"
        assert cache._current_size_bytes <= 1000

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
