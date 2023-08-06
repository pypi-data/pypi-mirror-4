from functools import wraps


def _get_memoized_value(func, args, kwargs):
    """Used internally by memoize decorator to get/store function results"""
    key = (repr(args), repr(kwargs))

    if not key in func._cache_dict:
        ret = func(*args, **kwargs)
        func._cache_dict[key] = ret

    return func._cache_dict[key]


# def memoize(func):
#     """Decorator that stores function results in a dictionary to be used on the
#     next time that the same arguments were informed."""
#
#     func._cache_dict = {}
#
#     @wraps(func)
#     def _inner(*args, **kwargs):
#         return _get_memoized_value(func, args, kwargs)
#
#     return _inner

_cache_unique = {}


def unique(func, num_args=0):
    """
    wraps a function so that produce unique results

    :param func:
    :param num_args:
    :return:

    >>> import random
    >>> choices = [1,2]
    >>> a = unique(random.choice, 1)
    >>> a,b = a(choices), a(choices)
    >>> a == b
    False
    """

    @wraps(func)
    def wrapper(*args):
        key = "%s_%s" % (str(func.__name__), str(args[:num_args]))
        attempt = 0
        while attempt < 100:
            drawn = _cache_unique.get(key, [])
            result = func(*args)
            if result not in drawn:
                drawn.append(result)
                _cache_unique[key] = drawn
                return result
        raise StopIteration
    return wrapper


