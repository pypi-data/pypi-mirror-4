from threading import Thread
from functools import wraps
import time


def retry(tries, exceptions=None, delay=0):
    """
    Decorator for retrying a function if exception occurs

    tries -- num tries
    exceptions -- exceptions to catch
    delay -- wait between retries
    """
    exceptions_ = exceptions or (Exception, )

    def _retry(func):
        @wraps(func)
        def __retry(*args, **kwargs):
            for _ in xrange(tries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions_:
                    time.sleep(delay)
            #if no success after tries raise last exception
            raise
        return __retry
    return _retry


def run_async(func):
    """
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object

            E.g.:
            @run_async
            def task1():
                do_something

            @run_async
            def task2():
                do_something_too

            t1 = task1()
            t2 = task2()
            ...
            t1.join()
            t2.join()
    """
    @wraps(func)
    def async_func(*args, **kwargs):
        tfunc = Thread(target=func, args=args, kwargs=kwargs)
        tfunc.start()
        return tfunc

    return async_func


def memoize(func):
    cache = {}

    @wraps(func)
    def _memoize(*args, **kwargs):
        key = (args, sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return _memoize
