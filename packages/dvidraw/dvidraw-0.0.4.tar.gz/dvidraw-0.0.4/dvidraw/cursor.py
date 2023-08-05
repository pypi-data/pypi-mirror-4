#External modules
from math import hypot
from functools import partial
import contextlib
import collections

# Interstitial modules
import dvipy.runner

# Internal drawing modules
from dvidraw import color
from dvidraw.drawable import (OpenPath, ClosedPath,
                           Text, Clip, Rectangle, Picture, Image)
import dvidraw.cr_draw

# Internal spaces modules
from dvidraw.bijections import bilog, bilin
from dvidraw.units import (UnitChanger, Coord, RawCoord, Point, DEFAULT_UNITS,
                        DEFAULT_UNIT)


# Create the session runner. We rely on python to clean this up.
runner = dvipy.runner.TexRunner()

# Override the default types on bilog and bilin for the common case
bilog = partial(bilog, a=RawCoord, b=RawCoord)
bilin = partial(bilin, a=RawCoord, b=RawCoord)

Style = collections.namedtuple('Style', ('fill', 'outline', 'weight', 'cap',
                                         'join'))
def norm(x, y):
    """Normalise a 2d point"""
    h = 1.0 / hypot(x, y)
    return (x * h, y * h)


# A descriptor that just happens to return a callable that moves the cursor
# given distance.
class CursorMover(object):
    """Move a cursor"""
    __slots__ = ('pos', 'target','__doc__','name')

    def __init__(self, dx, dy, name):
        self.pos = norm(dx, dy)
        self.name = name

    def __set__(self, *args):
        raise AttributeError('Cannot set')

    @property
    def __doc__(self):
        x, y = self.pos
        return ("""Returns a callable f(d) which moves in the direction of
                (%.2g, %.2g) by d units upon calling"""
                % (x, y))

    def __get__(self, ins, cls):
        self.target = ins
        return self

    def __call__(self, d):
        dx, dy = self.pos
        self.target.move(dx, dy, d)
        return self.target

    def __repr__(self):
        x, y = self.pos
        return "CursorMover(%f, %f, %s)" % (x, y, self.name)

# For now, it will be *absolutely* easiest to just transform everything with
# great regularity. For instance, a zoom simply pops an intermediate layer
# atop every space. 

class SpaceChanger(object):
    """Change space"""
    __slots__ = 'unit', '__doc__'

    @property
    def __doc__(self):
        return "Change unit to %s" % self.unit.name

    def __init__(self, unit):
        self.unit = unit

    def __get__(self, ins, cls):
        if ins:
            return ins.switch_space(self.unit)
        else:
            return self

    def __set__(self, *args):
        raise AttributeError('Unable to set UnitChanger')
    def __repr__(self):
        return "Change units to %s" % self.unit.name

# There's a difference between *easy* and *good*. Easy would be to hack in the
# device transformation here (that is flip upside down).
# But the right thing to do is clearly to put this into the cairo renderer,
# which can pick up the size. :). In this way, madness is spared.

UNIT_BOXSPACE = bilin((0, 0), (1, 1), a=Coord, b=Coord)
class Cursor(object):
    box = SpaceChanger('box')
    abs = SpaceChanger('abs')
    rel = SpaceChanger('rel')
    plt = SpaceChanger('plt')
    runner = runner

    def __init__(self, x=0, y=0, unit='pt'):
        self.coord = Coord(x, y)
        self.unit = DEFAULT_UNIT
        self.stack = []

        self.spaces = {'abs' : UNIT_BOXSPACE }
        self.current = self.spaces['abs']
        self.space_stack = []

        self.picture = Picture()
        black = self.rgb(0, 0, 0)
        self.style = Style(None, black, 1.0, 'round', 'round')
        self.save = dvidraw.cr_draw.Saver(self.picture)

    # SPACE COMMANDS
    def switch_unit(self, unit=None):
        """Change the unit of the underlying coordate"""
        if unit:
            self.unit = unit

        if self.unit == self.coord.unit:
            return self

        try:
            self.coord = self.coord.switch_unit(self.unit)
            return self
        except AttributeError:
            # Do the right thing: switch to relative space or fail and
            # get the root space
            new_space = self.spaces.get('rel') or self.spaces.get('abs')
            return self._switch_space(new_space).switch_unit(unit)

    def switch_space(self, name):
        return self._switch_space(self.spaces[name])
    
    def move(self, dx=0, dy=0, d=1):
        """Move by the given amount"""
        x, y = self.coord.point
        return self(x + dx*d, y + dy*d)

    def _switch_space(self, new_space):
        self.coord = new_space.a(*new_space.ba(self.anchored))

        self.current = new_space

        if self.coord.units:
            self.switch_unit()

        return self


    def zoom(self):
        # Much of this problem comes from the fear of "changing things"
        a = self.stack.pop()
        b = self.anchored

        # But really all that we're doing is changing the relative and box
        # mappings. Plots will be largely unaffected.
        d = b - a
        
        # How do we transform from the current space into the zoomed region?
        box = bilin(a, b, b=Coord)
        rel = bilin((0, 0), d, b=Coord).inverse + box
        
        self.space_stack.append(self.spaces.copy())
        self.spaces.update(box = box, rel = rel)
        return self

    def unzoom(self):
        self.spaces = self.space_stack.pop()
        return self

    def __call__(self, x=None, y=None):
        self.coord = self.coord(x, y)
        return self

    @property
    def anchored(self):
        return Point._make(self.current(self.coord.base))

    @property
    def to(self):
        """Push current point to the stack"""
        self.stack.append(self.anchored)
        return self

    def __repr__(self):
        x, y = self.coord.point
        if self.coord.unit:
            return 'Cursor((%g, %g) %s)' % (x, y, self.coord.unit.name)
        else:
            return 'Cursor(%g, %g)' % (x, y)

    # Drawing commands
    def clear(self):
        self.picture.clear()
        self.stack = []

    def image(self, data, width, height, filtering='nn'):
        self.to
        p2 = self.stack.pop()
        p1 = self.stack.pop()
        self.picture.append(Image(data, p1, p2, width, height, filtering))

    def gradient(self, stops):
        self.to
        p2 = self.stack.pop()
        p1 = self.stack.pop()
        self.picture.append(Gradient(p1, p2, stops))


    def path(self, close=False):
        """
        Turn the stack into a path

        If close is true, close the path by joining the begging and the end.

        """
        self.to
        stack = self.stack

        self.stack = []

        if close:
            p = ClosedPath(stack, self.style)
        else:
            p = OpenPath(stack, self.style)
        self.picture.append(p)
        return p

    def rect(self):
        """
        Turn the stack into a path

        If close is true, close the path by joining the begging and the end.
=
        """
        stack = self.stack
        self.to
        b = stack.pop()
        a = stack.pop()
        r = Rectangle(a, b, self.style)
        self.picture.append(r)
        return r

    def draw_text(self, text):
        text.pos = self.anchored
        self.picture.append(text)

    def text(self, tex, anchor=(0, None), draw=True, angle=0,
             fill_color=color.RGB(0, 0, 0)):
        page = runner.page(tex)
        text = Text(page, self.anchored, self.style, anchor, angle)
        text.fill_color = fill_color
        if draw:
            self.picture.append(text)
        return text

    def undo(self):
        try:
            self.picture.pop()
        except IndexError:
            raise RuntimeError('No more undo levels')

    # Clipping is achieved by obtaining a context. When the context is released,
    # clipping is over. This means it's impossible to "forget" to release the
    # clip, or at least very difficult.

    @property
    @contextlib.contextmanager
    def clip(self):
        region = self.picture.pop()

        picture, self.picture = self.picture, Picture()
        yield self
        picture.append(Clip(self.picture, region))
        self.picture = picture

    # STYLES

    def default(self, **kwargs):
        self.style = self.style._replace(**kwargs)
        
        return self

    def rgb(self, r, g, b):
        return color.RGB(r, g, b)

    def hsl(self, h, s, l):
        return color.HSL(h, s, l)


for i, j in DEFAULT_UNITS.iteritems():
    setattr(Cursor, i, UnitChanger(j))

MOVERS = (
    (CursorMover(1, 0, 'right'), ('right', 'E')),
    (CursorMover(0, 1, 'up'), ('up', 'N')),
    (CursorMover(-1, 0, 'left'), ('left', 'W')),
    (CursorMover(0, -1, 'down'), ('down', 'S')),
    (CursorMover(-1, -1, 'South-West'), ('SW',)),
    (CursorMover(+1, -1, 'South-East'), ('SE',)),
    (CursorMover(-1, +1, 'North-West'), ('NW',)),
    (CursorMover(+1, +1, 'North-East'), ('NE',))
)


for mover, bindings in MOVERS:
    for b in bindings:
        setattr(Cursor, b, mover)
