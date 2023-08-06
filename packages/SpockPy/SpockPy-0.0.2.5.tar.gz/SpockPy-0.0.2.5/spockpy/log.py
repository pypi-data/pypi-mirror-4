from decorator import decorator
import logging as log
from spockpy.utils import getcallargs

DEFAULT = 0
VERBOSE = 1

def _trace(f, *args, **kwargs):
    callargs = getcallargs(f,*args,**kwargs)
    if 'self' in callargs: del callargs['self']
    log.info(
        '{0}({1})'.format(
            f.__name__,
            ', '.join(
                map(lambda i: '{0[0]}={0[1]}'.format(i),callargs.items())
            )
        )
    )
    return f(*args, **kwargs)

def trace(f):
    """
    Automatically logs the decorated method and its parameters each time it is called.
    :param f: the method
    """
    return decorator(_trace, f)

def _trace2(f, *args, **kwargs):
    callargs = getcallargs.getcallargs(f,*args,**kwargs)
    if 'self' in callargs: del callargs['self']
    if 'kwargs' in callargs and len(callargs['kwargs']) == 0: del callargs['kwargs']
    if 'args' in callargs and len(callargs['wargs']) == 0: del callargs['args']
    log.info(
        '{0}(\n    {1}\n)'.format(
            f.__name__,
            '\n    '.join(
                map(lambda i: '{0[0]}={0[1]}'.format(i),callargs.items())
            )
        )
    )
    return f(*args, **kwargs)
def trace2(f):
    """
    Same as :function:`trace` but more verbose.
    :param f: the function
    :returns: the decorated function
    """
    return decorator(_trace2, f)
