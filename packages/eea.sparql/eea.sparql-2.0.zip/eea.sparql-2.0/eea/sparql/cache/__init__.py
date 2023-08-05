""" Caching module
"""
try:
    from eea.cache import cache as eeacache
    from lovely.memcached import event
    # pyflakes
    InvalidateCacheEvent = event.InvalidateCacheEvent
    ramcache = eeacache
except ImportError:
    # Fail quiet if required cache packages are not installed in order to use
    # this package without caching
    from eea.sparql.cache.nocache import ramcache
    from eea.sparql.cache.nocache import InvalidateCacheEvent

from eea.sparql.cache.cache import cacheSparqlKey

__all__ = [
    ramcache.__name__,
    InvalidateCacheEvent.__name__,
    cacheSparqlKey.__name__,
]
