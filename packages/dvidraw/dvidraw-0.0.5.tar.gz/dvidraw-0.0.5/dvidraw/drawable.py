# Drawable objects are simply objects that are used for drawing to the screen.
# They have two purposes
# 1) To decouple rendering of objects from their creation
# 2) To allow for convenient reproduction of a figure and allow this
# representation to be serialised and restored.

class undef:
    pass

class Drawable(object):
    def fill(self, color=None):
        self.style = self.style._replace(fill=color)
        return self
    
    def outline(self, color=undef, weight=undef, join=undef, cap=undef):
        d = {}

        if weight is not undef: d['weight'] = weight
        if join is not undef: d['join'] = join
        if cap is not undef: d['cap'] = cap
        if color is not undef: d['outline'] = color

        self.style = self.style._replace(**d)
        return self


class Rectangle(Drawable):
    def __init__(self, a, b, style):
        self.a = a
        self.b = b
        self.style = style

    def extents(self):
        return self.a + self.b

class Gradient(Drawable):
    def __init__(self, a, b, stops):
        self.a = a
        self.b = b
        self.stops = stops

    def extents(self):
        return tuple(self.a) + tuple(self.b)

class Path(Drawable):
    def __init__(self, points, style, arrows=None):
        super(Path, self).__init__()
        self.style = style
        self.points = points
        self.arrows = arrows or []

    def __repr__(self):
        return "<Path(%s, %s)>" % (self.points, self.style)

    def extents(self):
        xs, ys = zip(*self.points)
        return min(xs), min(ys), max(xs), max(ys)

def combine_extents(extents):
    x0s, y0s, x1s, y1s = zip(*extents)
    return min(x0s), min(y0s), max(x1s), max(y1s)

class Picture(list):
    margin = 10, 10
    def extents(self):
        try:
            x0, y0, x1, y1 = combine_extents([i.extents() for i in self])
        except ValueError:
            x0, y0, x1, y1 = 0, 0, 0, 0
        mx, my = self.margin
        return x0 - mx, y0 - my, x1 + mx, y1 + my
    
    def append(self, arg):
        result = list.append(self, arg)
        self.on_update(self)
        return result

    def pop(self, ix=-1):
        result = list.pop(self, ix)
        self.on_update(self)
        return result

    @staticmethod
    def on_update(self):
        pass

class OpenPath(Path):
    pass

class ClosedPath(Path):
    pass

TP2PT = 72.00 / 72.27
from math import cos, sin

# There is a bug here.
class Text(Drawable):
    def __init__(self, tex, pos, style, anchor, angle):
        self.text = tex
        w, h = tex.size
        self.anchor = anchor
        self._width = w * TP2PT
        self._height = h * TP2PT
        self.pos = pos
        self.fill_color = style.fill
        self.angle = angle
        rx0, ry0, rx1, ry1 = self.extents()

        self.width = rx1 - rx0
        self.height = ry1 - ry0

    def fill(self, fill):
        self.fill_color = fill

    def extents(self):
        s = sin(self.angle)
        c = cos(self.angle)
        x, y = self.pos
        ax, ay = self.anchor
        w = self._width
        h = self._height
        # What is the unrotated bottom left?
        blx, bly = self.text.bl

        if ay is None:
            ay = bly

        x0 = - ax * w
        y0 = -ay * h
        x1 = (1-ax) * w
        y1 = (1-ay) * h

        rx0, ry0 = x + x0 * c - y0 * s, y + s * x0 + c * y0
        rx1, ry1 = x + x1 * c - y1 * s, y + s * x1 + c * y1

        return rx0, ry0, rx1, ry1

class Ellipse(Drawable):
    def __init__(self, a, b, root=(0, 0)):
        self.text = tex
        self.root = root
        self.axes = a, b


class Image(object):
    def __init__(self, data, p1, p2, width, height, filtering='nn'):
        self.data = data
        self.filtering = filtering
        self.width = width
        self.height = height
        self.p1 = p1
        self.p2 = p2

    def extents(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        return x1, y1, x2, y2

class Clip(object):
    def __init__(self, contents, region):
        self.contents = contents
        self.region = region

    def extents(self):
        return self.region.extents()

    def __repr__(self):
        return "Clip(contents=[...], region=%r)" % (self.region)


class Group(object):
    def __init__(self, contents):
        self._contents = contents

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, self.contents)

