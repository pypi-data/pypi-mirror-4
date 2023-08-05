from operator import __not__
from itertools import ifilter


__all__ = ['identity', 'constantly', 'caller',
           'partial', 'compose', 'complement',
           'juxt', 'ijuxt',
           'iffy']


def identity(x):
    return x

def constantly(x):
    return lambda *a, **kw: x

# an operator.methodcaller() brother
def caller(*a, **kw):
    return lambda f: f(*a, **kw)

# not using functools.partial to get real function
def partial(func, *args, **kwargs):
    return lambda *a, **kw: func(*(args + a), **dict(kwargs, **kw))

def compose(*fs):
    pair = lambda f, g: lambda *a, **kw: f(g(*a, **kw))
    return reduce(pair, fs, identity)

def complement(pred):
    return compose(__not__, pred)

def juxt(*fs):
    return lambda *a, **kw: [f(*a, **kw) for f in fs]

def ijuxt(*fs):
    return lambda *a, **kw: (f(*a, **kw) for f in fs)

def iffy(pred, action, default=identity):
    return lambda v: action(v) if pred(v) else default(v)
