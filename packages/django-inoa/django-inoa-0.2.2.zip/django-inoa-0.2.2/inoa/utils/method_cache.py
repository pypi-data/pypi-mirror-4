# -*- coding: utf-8 -*-

def method_cache(seconds=0):
    """
    A `seconds` value of `0` means that we will not memcache it.
    
    If a result is cached on instance, return that first.  If that fails, check 
    memcached. If all else fails, hit the db and cache on instance and in memcache.
    
    If `True` is passed to a `skip_method_cache` argument when calling the method, the cache is skipped.
    
    ** NOTE: Methods that return None are always "recached".
    
    Expanded from http://djangosnippets.org/snippets/2477/ on 2012-11-01
    
    
    -----
    Usage
    ------
    A very simple decorator that caches both on-class and in memcached:
    
    @method_cache(3600)
    def some_intensive_method(self):
        return # do intensive stuff`
    Alternatively, if you just want to keep it per request and forgo memcaching, just do:
    
    @method_cache()
    def some_intensive_method(self):
        return # do intensive stuff`
    """
    
    from hashlib import sha224
    from django.core.cache import cache
    
    def inner_cache(method):
        
        def x(instance, *args, **kwargs):
            key = sha224(str(method.__module__) + str(method.__name__) + \
                str(getattr(instance, 'id', 0)) + str(args) + str(kwargs)).hexdigest()
            
            skip_method_cache = kwargs.pop('skip_method_cache', False)
            if not skip_method_cache and hasattr(instance, key):
                # has on instance cache, return that
                result = getattr(instance, key)
            else:
                result = cache.get(key)
                
                if skip_method_cache or result is None:
                    # all caches failed, call the actual method
                    result = method(instance, *args, **kwargs)
                    
                    # save to memcache and class attr
                    if seconds and isinstance(seconds, int):
                        cache.set(key, result, seconds)
                    setattr(instance, key, result)
            
            return result
        
        return x
    
    return inner_cache
