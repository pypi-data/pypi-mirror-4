# External modules
import collections
import colorsys

# Immutable colour system based around namedtuples.

_RGB = collections.namedtuple("RGB", ('r', 'g', 'b'))
_HSL = collections.namedtuple("HSL", ('h', 's', 'l'))

class HSL(_HSL):
    @property
    def hsl(self):
        return self

    @property
    def rgb(self):
        h, s, l = self
        return RGB(*colorsys.hls_to_rgb(h, l, s))

class RGB(_RGB):
    @property
    def hsl(self):
        h, l, s = colorsys.rgb_to_hls(*self)
        return HSL(h, s, l)

    @property
    def rgb(self):
        return self

# A general interpolator. This means that we can avoid handling rgb, hsl,
# (cielab) interpolations as special cases and just get on with things nicely.

def interpolate(patch, val):
    pass

def make_interpolator(frm, to):
    partial(interpolate, patch)


