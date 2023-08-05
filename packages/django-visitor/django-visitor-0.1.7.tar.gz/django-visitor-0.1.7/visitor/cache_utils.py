from django.core.cache import cache

CACHE_TIMEOUT = 60 * 60 * 1 # one hour

def make_cache_key(visitor_key):
    """ make the cache key for visitor """
    return 'visitor_%s' % (visitor_key)

def check_cache(visitor_key):
    """ check the cache for this visitor """
    cached = cache.get(make_cache_key(visitor_key))
    if cached:
       return cached
       
    return None

def set_cache(visitor):
    """ set the visitor object in the cache """
    if visitor.visitor_key:
        cache_key = make_cache_key(visitor.visitor_key) 
        cache.set(cache_key, visitor, CACHE_TIMEOUT)
