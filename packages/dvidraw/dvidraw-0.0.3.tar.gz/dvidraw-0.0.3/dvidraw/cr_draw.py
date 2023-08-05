# External modules
import cairo
from functools import partial

# Internal modules
from dvidraw.drawable import *
from dvidraw.freetype import Cairo, freetype, ADOBE_CUSTOM, UNICODE

# Dvipy modules
from dvipy.render import Char, Rule
from dvipy.font import kpse

from math import radians

TP2PT = 7200.0 / 7227.0

caps = {
    'round':cairo.LINE_CAP_ROUND,
    'butt':cairo.LINE_CAP_BUTT
}

joins = {
    'round':cairo.LINE_JOIN_ROUND
}

def path(path, cr, transform, closed=False):
    points = path.points
    x, y = transform(points[0])
    cr.move_to(x, y)
    for p in points[1:]:
        cr.line_to(*transform(p))
    if closed:
        cr.close_path()
    # Path space
    # Path space

def clip(clip, target, transform):
    target.save()
    region = clip.region
    contents = clip.contents
    # and now the horrible hack
    dispatcher[region.__class__](region, target, transform)
    target.clip()
    target.new_path()
    render(contents, target, transform)
    target.restore()

def rect(rect, target, transform):
    x1, y1 = transform(rect.a)
    x2, y2 = transform(rect.b)
    dx, dy = x2 - x1, y2 - y1
    target.rectangle(x1, y1, dx, dy)

def group(members, target, transform):
    for member in members:
        render(member, target, transform)

def text(member, target, transform):
    print member.anchor
    # Text that isn't filled shouldn't be drawn. Should probably print a
    # warning when this happens.
    if not member.fill_color:
        return

    # Push current transformation to the stack
    target.save()
    target.translate(*transform(member.pos))
    target.scale(TP2PT, TP2PT)
    target.rotate(radians(member.angle))

    # Get the bottom left of the text
    blx, bly = member.text.bl
    ax, ay = member.anchor
    sx, sy = member.text.size

    if ay is None:
        target.translate(-blx - sx * ax, 0)
    else:
        target.translate(-blx - sx * ax, -bly + sy * ay)

    texes = member.text.page
    

    glyphs = [t for t in texes if t.__class__ is Char]
    rules = [t for t in texes if t.__class__ is Rule]

    getter = operator.itemgetter(3)

    glyphs.sort(key=getter)
    for font, texlets in groupby(glyphs, key=getter):
        filename = font.filename
        face = (ft_cache.get(filename) or
                freetype.new_face(kpse(filename)))
        ft_cache[filename] = face

        cairo_face = (cairo_cache.get(face) or
                      Cairo.cr_face_from_ft_face(face))
        cairo_cache[face] = cairo_face

        Cairo.set_font_face(target, cairo_face)
        target.set_font_size(font.size)

        face.select_charmap(ADOBE_CUSTOM)

        glyphs = []
        for x, y, char, f in texlets:
            if isinstance(char, basestring):
                c = face.get_name_index(char)
            else:
                c = face.get_char_index(char)
            glyphs.append((c, x, y))

        target.set_source_rgb(*member.fill_color.rgb)
        face.select_charmap(UNICODE)
        target.show_glyphs(glyphs)

    target.restore()

def picture(picture, target, transform):
    cr = target

    for member in picture:
        f = dispatcher[member.__class__]
        f(member, target, transform)

        if hasattr(member, 'style'):
            style = member.style

            if style.weight:
                cr.set_line_width(style.weight)
            if style.fill and style.outline and style.weight:
                cr.set_source_rgb(*style.fill.rgb)
                cr.fill_preserve()
            if style.outline and style.weight:
                cr.set_source_rgb(*style.outline.rgb)
                cr.set_line_cap(caps[style.cap])
                cr.set_line_join(caps[style.join])
                cr.stroke()
            elif style.fill:
                cr.set_source_rgb(*style.fill.rgb)
                cr.fill()


def image(im, target, transform):
    imsurf = cairo.ImageSurface.create_for_data(
        im.data, cairo.FORMAT_ARGB32,
        im.width, im.height)

    im.pattern = cairo.SurfacePattern(imsurf) 
    if im.filtering == 'nn':
        im.pattern.set_filter(cairo.FILTER_NEAREST)
    else:
        raise AttributeError(
            'Unknown filtering method proposed, %s' %
        im.filtering)

    x1, y1 = transform(im.p1)
    x2, y2 = transform(im.p2)
    dx, dy = abs(x2 - x1), abs(y2 - y1)

    target.save()
    target.translate(x1, y2)
    print dx, dy
    target.scale(dx / im.width, dy / im.height)
    target.set_source(im.pattern)

    target.paint()
    target.restore()
    

def gradient(gradient, target, transform):
    x1, y1 = transform(gradient.p1)
    x2, y2 = transform(gradient.p2)

    g = cairo.LinearGradient(1, abs(y2-y1))
    for x, c in gradient.stops:
        g.add_color_stop_rgb(x, *c)

    target.save()
    target.translate(x1, x2)

    target.paint()
    target.restore()


# Later we can make the picture actually something sensible. is it a container?
render = picture

# The cursor should hold a renderer. The default can be overwritten. Each cursor
# has a render attribute. cr.save.svg()

dispatcher = {
    Clip : clip,
    Group : group,
    Rectangle: rect,
    OpenPath : partial(path, closed=False),
    ClosedPath : partial(path, closed=True),
    Text : text,
    Picture : picture,
    Image : image,
    Gradient: Gradient,
}
# ==============
# Text rendering
# ==============

import os.path
from math import ceil

class Saver(object):
    def __init__(self, picture):
        self.picture = picture

    def png(self, filename, dpi=90):
        dpp = dpi / 72.0
        x0, y0, x1, y1 = self.picture.extents()
        w = x1 - x0
        h = y1 - y0

        transform = lambda (x, y): (x - x0, h - (y - y0))
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, int(ceil(w*dpp)),
                                  int(ceil(h*dpp)))
        cr = cairo.Context(surf)
        cr.scale(dpp, dpp)
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        picture(self.picture, cr, transform)
        surf.write_to_png(filename)


    def pdf(self, filename):
        x0, y0, x1, y1 = self.picture.extents()
        w = x1 - x0
        h = y1 - y0

        transform = lambda (x, y): (x - x0, h - (y - y0))
        surf = cairo.PDFSurface(filename, w, h)
        cr = cairo.Context(surf)
        picture(self.picture, cr, transform)
        surf.finish()

    def screen(self):
        from dvidraw.cr_window import CairoDisplay
        x0, y0, x1, y1 = self.picture.extents()
        screen = CairoDisplay(self.picture, render)
        screen.show()

    dispatch = {'png' : png,
                'pdf' : pdf}

    def __call__(self, fname, *args, **kwargs):
        base, ext = os.path.splitext(fname)
        ext = ext[1:]
        f = self.dispatch[ext](self, fname, *args, **kwargs)
    

ft_cache = {}
cairo_cache = {}

import operator
from itertools import groupby

