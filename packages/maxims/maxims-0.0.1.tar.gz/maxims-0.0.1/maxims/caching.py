"""
Tools for in-memory caching.
"""
import functools


def cached(attr):
    """
    In-memory caching for a nullary callable.
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated(self):
            try:
                return getattr(self, attr)
            except AttributeError:
                value = f(self)
                setattr(self, attr, value)
                return value

        return decorated
    return decorator
