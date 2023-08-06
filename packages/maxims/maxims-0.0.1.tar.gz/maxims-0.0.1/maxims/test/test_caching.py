"""
Tests for in-memory caching.
"""
from axiom import attributes, item
from maxims import caching
from twisted.trial import unittest


class CachingItem(item.Item):
    """
    An item that can do an expensive computation. It remembers how many times
    it has executed that computation, and caches its result.
    """
    calls = attributes.integer(default=0)
    _cachedValue = attributes.inmemory()

    @caching.cached("_cachedValue")
    def expensiveComputation(self):
        """
        A very expensive computation.
        """
        self.calls += 1
        return 1



class CacheTests(unittest.TestCase):
    """
    Tests for the in-memory nullary callable cache.
    """
    def setUp(self):
        self.item = CachingItem()


    def assertCallsEquals(self, n):
        """
        Asserts that the number of times the expensive computation function
        was called is equal to ``n``.
        """
        self.assertEquals(self.item.calls, n)


    def assertCacheCold(self):
        """
        Asserts that a value has not been cached.
        """
        self.assertRaises(AttributeError, getattr, self.item, "_cachedValue")


    def assertCacheWarm(self):
        """
        Asserts that a value has been cached.
        """
        self.assertNotIdentical(self.item._cachedValue, None)


    def test_cache(self):
        """
        Tests the cache.

        Checks starting conditions (zero calls, cold cache), then executes
        the computation and asserts that was a cache miss, then executes it
        again and asserts that was a cache hit.
        """
        self.assertCacheCold()
        self.assertCallsEquals(0)

        self.item.expensiveComputation()

        self.assertCacheWarm()
        self.assertCallsEquals(1)

        self.item.expensiveComputation()

        self.assertCacheWarm()
        self.assertCallsEquals(1)
