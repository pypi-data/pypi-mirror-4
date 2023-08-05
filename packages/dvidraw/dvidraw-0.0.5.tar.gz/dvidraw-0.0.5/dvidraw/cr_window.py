import gtk
import time
import __main__ as main

def refresh_gui(delay=0):
    while gtk.events_pending():
        gtk.main_iteration_do(block=False)
        time.sleep(delay)

class CairoDisplay(object):
    running = False
    def __init__(self, picture, render):
        self.picture = picture
        self.render = render

    def init_window(self):
        # The gtk and cairo modules are only imported here
        self.window = gtk.Window()
        self.da = gtk.DrawingArea()
        self.window.add(self.da)
        self.window.show_all()
        self.window.connect('delete-event', self.on_delete)
        self.da.connect('expose-event', self.on_expose)

    def on_delete(self, win, evt):
        gtk.main_quit()
        self.running = False
        del self.picture.on_update

    def on_expose(self, win, evt):
        cr = win.window.cairo_create()
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        x0, y0, x1, y1 = self.picture.extents()
        w = x1 - x0
        h = y1 - y0

        win_w, win_h = win.window.get_size()
        scale = min(win_w / w, win_h / h)

        nw, nh = scale * w, scale * h

        dx = 0.5 * (win_w - nw)
        dy = 0.5 * (win_h - nh)

        cr.translate(dx, dy)
        cr.scale(scale, scale)

        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        transform = lambda (x, y): (x - x0, h - (y - y0))
        self.render(self.picture, cr, transform)

        pass

    def redraw(self, _):
        self.da.queue_draw()

    def show(self, delay=0, block=None):
        if self.running:
            return

        self.init_window()
        self.running = True

        self.picture.on_update = self.redraw

        if block is None:
            block = hasattr(main, '__file__')

        if not block:
            refresh_gui()
        else:
            gtk.main()
