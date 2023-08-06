from decorator import decorator
import logging as log
from spockpy.utils.getcallargs import getcallargs

DEFAULT = 0
VERBOSE = 1

def _trace(f, out_level=DEFAULT, *args, **kwargs):
    callargs = getcallargs.getcallargs(f,*args,**kwargs)
    del callargs['self']
    if out_level == DEFAULT:
        log.info(
            '{0}({1})'.format(
                f.__name__,
                ', '.join(
                    map(lambda i: '{0[0]}={0[1]}'.format(i),callargs.items())
                )
            )
        )
    elif out_level == VERBOSE:
        log.info(
            '{0}\n({1})'.format(
                f.__name__,
                '\n'.join(
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

def trace2(f,out_level=VERBOSE):
    """
    Same as :function:`trace` but more verbose.
    :param f: the function
    :returns: the decorated function
    """
    return decorator(_trace, f)
