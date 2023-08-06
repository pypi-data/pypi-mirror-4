from datetime import datetime, timedelta
from functools import wraps
import inspect


__all__ = ['memoize', 'make_lookuper', 'cache']


class SkipMemoization(Exception):
    pass


def memoize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            try:
                cache[args] = func(*args)
            except SkipMemoization as e:
                return e.args[0] if e.args else None

        return cache[args]
    return wrapper
memoize.skip = SkipMemoization


def make_lookuper(func):
    spec = inspect.getargspec(func)
    assert not spec.keywords,  \
           'Lookup table building function should not have keyword arguments'

    if spec.args or spec.varargs:
        @memoize
        def wrapper(*args):
            return make_lookuper(lambda: func(*args))
    else:
        memory = {}

        @wraps(func)
        def wrapper(arg):
            if not memory:
                memory[object()] = None # prevent continuos memory refilling
                memory.update(func())
            return memory.get(arg)

    return wraps(func)(wrapper)


def cache(timeout):
    if isinstance(timeout, int):
        timeout = timedelta(seconds=timeout)

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args):
            if args in cache:
                result, timestamp = cache[args]
                if datetime.now() - timestamp < timeout:
                    return result
                else:
                    del cache[args]

            result = func(*args)
            cache[args] = result, datetime.now()
            return result

        def invalidate(*args):
            cache.pop(args)
        wrapper.invalidate = invalidate

        def invalidate_all():
            cache.clear()
        wrapper.invalidate_all = invalidate_all

        return wrapper
    return decorator

