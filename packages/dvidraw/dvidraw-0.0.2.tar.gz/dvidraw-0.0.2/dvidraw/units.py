from collections import namedtuple
from functools import partial
from operator import mul

# Units are distinct from spaces, but nonetheless important.

# Define our namedtuples, many of which will be bases
Unit = namedtuple('Unit', ('name', 'to_pt', 'from_pt'))
_Coord = namedtuple('Coord', ('point', 'units', 'unit'))
_Point = namedtuple('Point', ('x', 'y'))


def unit(pts, name=''):
    return Unit(to_pt=partial(mul, pts),
                from_pt=partial(mul, 1.0 / pts),
                name=name)


DEFAULT_UNITS = dict(
    mm=unit(72.0 / 25.4, 'mm'),
    cm=unit(72.0 / 2.54, 'cm'),
    inch=unit(72.0, 'inch'),
    pt=unit(1.0, 'pt')
)
DEFAULT_UNIT = DEFAULT_UNITS['pt']


class Point(_Point):
    def __call__(self, x, y):
        return self._replace(x=x, y=y)

    @property
    def point(self):
        return self

    def __sub__(a, b):
        return Point(a.x - b.x, a.y - b.y)


class UnitChanger(object):
    """Change space"""
    __slots__ = 'unit', '__doc__'
    #func_name = __name__ = 'UnitChanger'

    @property
    def __doc__(self):
        return "Change unit to %s" % self.unit.name

    def __init__(self, unit):
        self.unit = unit

    def __get__(self, ins, cls):
        if ins:
            return ins.switch_unit(self.unit)
        else:
            return self

    def __call__(self, x, y):
        pass

    def __set__(self, *args):
        raise AttributeError('Unable to set UnitChanger')

    def __repr__(self):
        return "Change units to %s" % self.unit.name


class Coord(_Coord):
    __slots__ = ()

    @property
    def base(self):
        return self.pt.point

    def switch_unit(self, unit):
        g = self.unit.to_pt
        f = unit.from_pt
        x, y = self.point
        return self._replace(
            point=self.point._replace(x=f(g(x)), y=f(g(y))),
            unit=unit
        )

    def __new__(cls, x=0, y=0):
        return _Coord.__new__(cls, point=Point(x, y),
                              units=DEFAULT_UNITS,
                              unit=DEFAULT_UNIT)

    def __repr__(self):
        return ('Coord((%g, %g) %s)' %
                (self.point.x, self.point.y, self.unit.name))

    def __call__(self, x, y):
        if x is not None and y is not None:
            return self._replace(point=Point(x, y))
        elif x is not None:
            _, cy = self.point
            return self._replace(point=Point(x, cy))
        elif y is not None:
            cx, _ = self.point
            return self._replace(point=Point(cx, y))
        else:
            return self._replace(point=Point(0, 0))


# Set all the UnitChangers on the usual Coord
for i, j in DEFAULT_UNITS.iteritems():
    setattr(Coord, i, UnitChanger(j))


# A Raw coordinate class
class RawCoord(_Coord):
    __slots__ = ()
    
    @property
    def base(self):
        return self.point

    def switch_unit(self, unit):
        raise AttributeError('Cannot switch unit')

    def __new__(cls, x=0, y=0):
        return _Coord.__new__(cls, point=Point(x, y),
                              units=None,
                              unit=None)

    def __repr__(self):
        return 'Coord(%g, %g)' % self.point

    def __call__(self, x, y):
        if x is not None and y is not None:
            return self._replace(point=Point(x, y))
        elif x is not None:
            _, cy = self.point
            return self._replace(point=Point(x, cy))
        elif y is not None:
            cx, _ = self.point
            return self._replace(point=Point(cx, y))
        else:
            return self._replace(point=Point(0, 0))

# Thing is that this is now easily verifiable. We would like to expose
# some of this magic to the user of the cursors, and we can now do that
# by composition rather than it being something built (quite horribly)
# into the system But now, how do we deal with alternative spaces?  See
# how simple? :)
