from dvidraw.cursor import Cursor, runner, bilin
from dviplot.boxes import Relations, Expand, Size
from dviplot.axis import possible_log_ticks, possible_lin_ticks
from operator import mul, itemgetter
from itertools import izip, imap, repeat
from dvidraw.bijections import logspace, linspace, separable
from dvidraw.units import RawCoord
from dviplot.symbols import cross_diag

# This needs a major refactoring.

# THIS WILL SOON BE DONE !
# ========================

# How many ticks can we specify?
# None --> fully automatic

# [float] --> automatic labelling, explicit ticks
# [(float, label)] --> Explicit ticks, explicit labels
# labeller --> Automatic ticks, explicit labelling

# we need to be careful: the user should be able to supply a generator and get
# back what they want.

# TODO: Design this part of the API
cursor = Cursor()


# There are four possible axes styles: fully explicit has to have 
def read_axis_explicit(axis):
    x, y, list(xs)

class StepData(object):
    def __init__(self, data):
        # Some fancy routine to read the data in.
        # TODO: allow other forms of unambiguous data (e.g. x, y)
        self.data = list(data)
        x_lows, x_highs, ys = zip(*self.data)

        # Guido got to this one before me! How do we chain errors idiomatically?
        # Well, python's dynamic, right?

        x_range = min(x for x in x_lows if x), max(x_highs)

        safe_ys = [y for y in ys if y > 0] 
        y_range = min(safe_ys), max(safe_ys)

        # let's just hard-code this as log-lin for now!
        # TODO: Allow arbitrary axes
        self.yticks, = possible_log_ticks(*y_range)
        self.y_range = self.yticks[0], self.yticks[-1]

        xticks = possible_lin_ticks(*x_range)
        xticks.sort(key=lambda x: abs(len(x) - 8))
        self.xticks = xticks[0]
        self.x_range = self.xticks[0], self.xticks[-1]
        
    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        linlog = separable(linspace(*self.x_range),
                           logspace(*self.y_range), RawCoord, RawCoord)

        cr.spaces['plt'] = linlog.inverse + cr.spaces['box']

        red = cr.rgb(0.8, 0, 0)
        cr.box(0, 0).to(1, 1).rect()
        with cr.clip as cr:
            x1, x2, y = self.data[0]
            y = max(y, 1e-10)
            cr.plt
            cr(x1, y).to(x2, y)
            for _, x2, y in self.data[1:]:
                y = max(y, 1e-10)
                cr.to(y=y).to(x=x2)
            cr.path().outline(red)
        plot = cr.spaces['plt']
        cr.unzoom()
        cr.spaces['plt'] = plot
    
    @property
    def pos(self):
        return self.frame.pos

    @property
    def size(self):
        return self.frame.size


import array
import itertools
class ImageData(object):
    def __init__(self,
                 nx, xlow, xhigh,
                 ny, ylow, yhigh,
                 data, color=lambda x: (x, x, x)):

        self.x_range = xlow, xhigh
        self.y_range = ylow, yhigh
        self.nx = nx
        self.ny = ny
        self.data = data
        self.xticks = [0, 1]
        self.yticks = [0, 1]
        self.color = color

    @property
    def pos(self):
        return self.frame.pos

    @property
    def size(self):
        return self.frame.size

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        linlin = separable(linspace(*self.x_range),
                           linspace(*self.y_range), RawCoord, RawCoord)
        cr.spaces['plt'] = linlin.inverse + cr.spaces['box']

        cr.box(0, 0).to(1, 1).rect()
        a = array.array(
            'B', itertools.chain(*map(self.color, self.data)))
        with cr.clip as cr:
            cr.plt(self.x_range[0], self.y_range[0]).to(
                self.x_range[1], self.y_range[1]).image(
                    a, self.nx, self.ny)

        plot = cr.spaces['plt']
        cr.unzoom()
        cr.spaces['plt'] = plot


class RatioData(object):
    def __init__(self, ratio_data):
        self.ratio_data = ratio_data
        self.xticks = self.ratio_data.xticks
        self.yticks = [0.6, 1.0, 1.4]
        self.x_range = self.ratio_data.x_range
        self.y_range = 0.2, 1.8

        # What does a ratio plot actually do?
        # I don't know, but we should pretend we do!

    @property
    def pos(self):
        return self.frame.pos

    @property
    def size(self):
        return self.frame.size

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        linlog = separable(linspace(*self.x_range),
                           linspace(*self.y_range), RawCoord, RawCoord)

        cr.spaces['plt'] = linlog.inverse + cr.spaces['box']

        cr.box(x=0).plt(y=1).to.box.right(1).path()

        plt = cr.spaces['plt']
        cr.unzoom()
        cr.spaces['plt'] = plt


class Plot(object):
    def __init__(self, data, title='', xtitle='', ytitle=''):
        # Need a way to manage the items as part of a box (TODO: tidy)
        relations = Relations()

        self.data = data
        xlabels = XLabels(data)
        ylabels = YLabels(data)
        title = PlotTitle(title)
        xtitle = XTitle(xtitle)
        ytitle = YTitle(ytitle)

        data.frame = frame = PlotFrame()
        frame.data = data

        ratio_data = RatioData(data)
        ratio_frame = ratio_data.frame = PlotFrame()
        ratio_frame.expand = ratio_frame.expand._replace(y=0.5)
        ratio_frame.data = ratio_data

        ratio_ytitle = YTitle('Ratio')
        ratio_ytitle.expand = ratio_ytitle.expand._replace(y=0.5)
        ratio_ylabels = YLabels(ratio_data)
        ratio_ylabels.expand = ratio_ylabels.expand._replace(y=0.5)

        self.layers = [title, xtitle, ytitle,
                       data, frame, xlabels, ylabels,
                       ratio_data, ratio_frame, ratio_ylabels, ratio_ytitle]

        # We only represent the "frame" here, since the data will pluck out the
        # frame's allocation when it comes to rendering.
        relations.right(ytitle, ylabels, frame)
        relations.right(ratio_ytitle, ratio_ylabels, ratio_frame)
        relations.down(title, frame, ratio_frame, xlabels, xtitle)

        self.lattice = relations.lattice()

    def log_y(self, log=True):
        self.yaxis = LogAxis if log else LinAxis

    def log_x(self, log=True):
        self.xaxis = LogAxis if log else LinAxis

    def size(self, width, height, margin=(10, 10)):
        self.margin = margin
        self.lattice.allocate(width - 2*margin[0],
                              height - 2*margin[1])
        self._size = Size(width, height)

    def draw(self, cr=None):
        cr = cr or Cursor()
        blk = cr.rgb(0, 0, 0)

        cr.default(outline=blk, weight=0.5)

        x, y = self.margin
        w, h = self._size

        cr.abs(x, y).to(w-x, w-y).zoom()

        for i in self.layers:
            i.draw(cr)
        cr.unzoom()

        return cr


class SimplePlot(Plot):
    def __init__(self, data, title='', xtitle='', ytitle=''):
        # Need a way to manage the items as part of a box (TODO: tidy)
        relations = Relations()

        self.data = data
        xlabels = XLabels(data)
        ylabels = YLabels(data)
        title = PlotTitle(title)
        xtitle = XTitle(xtitle)
        ytitle = YTitle(ytitle)

        data.frame = frame = PlotFrame()
        frame.data = data

        self.layers = [title, xtitle, ytitle,
                       data, frame, xlabels, ylabels]

        # We only represent the "frame" here, since the data will pluck out the
        # frame's allocation when it comes to rendering.
        relations.right(ytitle, ylabels, frame)
        relations.down(title, frame, xlabels, xtitle)

        self.lattice = relations.lattice()


class PlotObject(object):
    size = Size(0, 0)
    expand = Expand(1, 1)

    def alloc(self, x, y, w, h):
        self.size = Size(w, h)
        self.pos = x, y

    def draw(self, cr):
        cr.rel.pt(*self.pos).to.move(*self.size).rect()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.size)


class ColorPlot(Plot):
    def __init__(self, data, colorbar, title='', xtitle='', ytitle=''):
        # Need a way to manage the items as part of a box (TODO: tidy)
        relations = Relations()

        self.data = data
        xlabels = XLabels(data)
        ylabels = YLabels(data)

        title = PlotTitle(title)
        xtitle = XTitle(xtitle)
        ytitle = YTitle(ytitle)

        colorbar_ylabels = YLabels(colorbar, left=True)

        data.frame = frame = PlotFrame()
        frame.data = data

        self.layers = [title, xtitle, ytitle,
                       data, frame, xlabels, ylabels,
                       colorbar, colorbar_ylabels]

        # We only represent the "frame" here, since the data will pluck out the
        # frame's allocation when it comes to rendering.
        relations.right(ytitle, ylabels, frame,
                        colorbar, colorbar_ylabels)
        relations.down(title, frame, xlabels, xtitle)

        self.lattice = relations.lattice()


class ColorBar(PlotObject):
    size = Size(20, 0)
    lmargin = 7 
    rmargin = 0
    expand = Expand(0, 1)
    yticks = [0, 100]
    x_range = 0, 1
    y_range = 0, 100

    def __init__(self, stops):
        self.stops = stops

    def draw(self, cr):
        linlin = separable(linspace(*self.x_range),
                           linspace(*self.y_range),
                           RawCoord, RawCoord)


        dx, dy = self.size
        dx -= self.lmargin + self.rmargin

        cr.rel.pt(*self.pos).right(self.lmargin).to.move(dx, dy).zoom()

        cr.spaces['plt'] = linlin.inverse + cr.spaces['box']

        cr.box(0, 0).to(1, 1).rect()
        # The second one is for the clip

        cr.box(0, 0).to(1, 1).rect()

        with cr.clip as cr:
            cr.gradient(self.stops)

        plot = cr.spaces['plt']
        cr.unzoom()
        cr.spaces['plt'] = plot


# HACKY HAKCY HACKY HACKY! Make-plots has a much nicer solution!
def approx(x, y, delta=0.0001):
    return abs(x - y) <= delta


# Oh really. And where, exactly, does this data get set?!
class PlotFrame(PlotObject):
    size = Size(0, 0)
    expand = Expand(1, 1)

    def draw(self, cr):
        cr.rel.pt(*self.pos).to.move(*self.size).zoom()
        cr.box(0, 0).to(1, 1).rect()
        # The second one is for the clip
        cr.box(0, 0).to(1, 1).rect()
        
        with cr.clip as cr:
            x_min, x_max = self.data.x_range
            y_min, y_max = self.data.y_range
            # Need some way to dodge given regions
            for x in self.data.xticks:
                if (approx(x, x_min) or approx(x, x_max)):
                    continue
                cr.box(y=0).plt(x=x).to.pt.up(3).path()
                cr.box(y=1).plt(x=x).to.pt.down(3).path()

            for y in self.data.yticks:
                if (approx(y, y_min) or approx(y, y_max)):
                    continue
                cr.box(x=0).plt(y=y).to.pt.right(3).path()
                cr.box(x=1).plt(y=y).to.pt.left(3).path()
        cr.unzoom()


# Yticks
class YLabels(PlotObject):
    expand = Expand(0, 1)
    def __init__(self, data, xmargin=5, left=False):
        self.ticks = data.yticks
        self.xmargin = xmargin
        self.left = left

    def alloc(self, x, y, w, h):
        self.pos = x, y
        self.size = Size(w, h)

        if self.left:
            self.texts = [cursor.text("%g" % t, draw=False, anchor=(0, 0.5))
                          for t in self.ticks]
        else:
            self.texts = [cursor.text("%g" % t, draw=False, anchor=(1, 0.5))
                          for t in self.ticks]
        width = max(t.width for t in self.texts)
        self.size = Size(max(w, width + self.xmargin), h)

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        if self.left:
            cr.box(0, 0).rel.right(self.xmargin).plt
        else:
            cr.box(1, 0).rel.left(self.xmargin).plt

        for t, y in izip(self.texts, self.ticks):
            cr(y=y).draw_text(t)
        cr.unzoom()


# Ytitle
class YTitle(PlotObject):
    expand = Expand(0, 1)
    def __init__(self, ytitle, xmargin=2):
        self.ytitle = ytitle
        self.text = cursor.text(self.ytitle, draw=False,
                                anchor=(0.5, 1), angle=-90)
        self.xmargin = xmargin

    def alloc(self, x, y, w, h):
        self.pos = x, y
        self.size = Size(self.xmargin + self.text.width, h)

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        cr.box(0, 0.5).draw_text(self.text)
        cr.unzoom().rel


# Needs to draw itself
class XLabels(PlotObject):
    expand = Expand(1, 0)
    def __init__(self, data, ymargin=10):
        self.ticks = data.xticks
        self.ymargin = ymargin

    def alloc(self, x, y, w, h):
        self.texts = [cursor.text(r"%g" % t, draw=False,
                                  anchor=(0.5, 0.5))
                      for t in self.ticks]

        h = max(t.height for t in self.texts)
        self.pos = x, y
        self.size = Size(w, h + self.ymargin)

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom().box(0, 0.5).plt
        for t, x in izip(self.texts, self.ticks):
            cr(x=x).draw_text(t)
        cr.unzoom()


class XTitle(PlotObject):
    expand = Expand(1, 0)
    def __init__(self, xtitle, ymargin=5):
        self.xtitle = xtitle
        self.ymargin = ymargin
        self.text = cursor.text(self.xtitle, draw=False,
                                anchor=(1, 0))

    def alloc(self, x, y, w, h):
        self.size = Size(w, self.text.height + self.ymargin)
        self.pos = x, y

    def draw(self, cr):
        cr.rel(*self.pos).to.move(*self.size).zoom()
        cr.box(1, 0).draw_text(self.text)
        cr.unzoom().rel


class PlotTitle(PlotObject):
    expand = Expand(1, 0)
    def __init__(self, title, ymargin=5):
        # These actually have no effect, since not a box! Redo boxes.
        self.title = title
        self.ymargin = ymargin

    def alloc(self, x, y, w, h):
        self.text = cursor.text('\parbox{%g pt}{%s}' %
                                (w * 72.27 / 72.00, self.title),
                                draw=False, anchor=(0, 0))
        self.pos = x, y
        self.size = Size(w, self.text.height + self.ymargin)

    def draw(self, cr):
        cr.rel(*self.pos).up(self.ymargin).draw_text(self.text)


