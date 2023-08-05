from __future__ import division
from collections import namedtuple
from functools import partial
from math import log, exp

# A collection of common bijections. Bijections can be composed by addition: (f
# + g)(x) = (g.f)(x) or something like that. I can't remember. It seemed good
# way at the time!

_Bijection = namedtuple('Bijection', ('a', 'b', 'ab', 'ba'))


class Bijection(_Bijection):
    @property
    def inverse(self):
        return Bijection(a=self.b, b=self.a,
                         ab=self.ba, ba=self.ab)

    def __add__(a, b):
        return compose(a, b)

    def __call__(self, x):
        return self.ab(x)


def _composed_f(f, g, x):
    return g(f(x))


def f_compose(f, g):
    return partial(_composed_f, f, g)


def compose(f, g):
    if f.b != g.a:
        raise RuntimeError('Codomain of f must be the domain of g')

    return Bijection(a=f.a,
                     b=g.b,
                     ab=f_compose(f.ab, g.ab),
                     ba=f_compose(g.ba, f.ba))


# Linear spaces
def linspace_ab(a, m, x):
    return a + m * x


def linspace_ba(a, r, x):
    return r * (x - a)


def linspace(u, v, a='', b=''):
    m = v - u

    ab = partial(linspace_ab, u, m)
    ba = partial(linspace_ba, u, 1.0 / m)

    return Bijection(a=a, b=b, ab=ab, ba=ba)


# Logarithmic spaces
def logspace_ab(y0, b, x):
    return y0 * exp(b * x)


def logspace_ba(iy0, ib, x):
    return ib * log(iy0 * x)


def logspace(u, v, a='', b=''):
    nb = log(v / u)
    ib = 1.0 / nb
    y0 = u
    iy0 = 1.0 / y0

    ab = partial(logspace_ab, y0, nb)
    ba = partial(logspace_ba, iy0, ib)

    return Bijection(a=a, b=b, ab=ab, ba=ba)


# Combinations
def separable_ab(fx, fy, (x, y)):
    return fx(x), fy(y)


def separable(x, y, a=None, b=None):
    ab = partial(separable_ab, x.ab, y.ab)
    ba = partial(separable_ab, x.ba, y.ba)
    a = a or (x.a, y.a)
    b = b or (x.b, y.b)
    return Bijection(ab=ab, ba=ba, a=a, b=b)


# Convenience constructors
def bilin((ux, uy), (vx, vy), a=None, b=None):
    return separable(linspace(ux, vx),
                     linspace(uy, vy),
                     a=a, b=b)


def bilog((ux, uy), (vx, vy), a=None, b=None):
    return separable(logspace(ux, vx),
                     logspace(uy, vy),
                     a=a, b=b)

# TODO: optimisations, if they're necessary. This is one of the possible
# bottlenecks, but it may turn out not to be; especially if full-stack
# transformations are relatively rare in plotting. There are a few nice
# things we can do, like combine runs of log and linear transformations
# (bunching), but whether they'll actually beat just writing an optional
# swapout module in Cython is dubious at best. I'll be placing bets on
# Cython. :)

#a = bilin((0, 0), (100, 100))
#b = bilog((10, 10), (1000, 1000))
#c = bilin((0, 1), (50, 51))
#
#d = a.inverse + b.inverse + c
#
#from random import random
#
#for i in xrange(10000):
#    x = random()
#    y = random()
#    d((x, y))
