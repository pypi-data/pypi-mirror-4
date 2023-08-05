from __future__ import division
import collections
import operator
from itertools import izip, chain, product
from operator import sub

Allocation = collections.namedtuple('Allocation', ('x', 'y', 'width', 'height'))
_Relation = collections.namedtuple('Relation', ('up', 'left', 'down', 'right'))
_DenseLattice = collections.namedtuple('DenseLattice', ('x', 'y'))
Dependency = collections.namedtuple('Dependency', ('ww', 'wh', 'hw', 'hh'))

class Relation(_Relation):
    def __new__(cls):
        return _Relation.__new__(cls, None, None, None, None)

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

inverse = dict(
    left = 'right',
    right = 'left',
    up = 'down',
    down = 'up'
)

directions = dict(
    up = (0, 1),
    down = (0, -1),
    left = (-1, 0),
    right = (1, 0)
)

class Relations(object):
    """Positional relations between things"""
    def __init__(self):
        self.relations = dict()

    def run(self, direction, *things):
        rs = self.relations
        for t, nt in izip(things, things[1:]):
            thing = rs.get(t, Relation())
            next_thing = rs.get(nt, Relation())
            
            rs[t] = thing._replace(**{direction : nt})
            rs[nt] = next_thing._replace(**{inverse[direction] : t})

    def right(self, *things):
        return self.run('right', *things)

    def across(self, *things):
        return self.run('right', *things)

    def down(self, *things):
        return self.run('down', *things)

    def up(self, *things):
        return self.run('up', *things)

    def left(self, *things):
        return self.run('left', *things)

    def _lattice(self, current, x, y, lattice):
        # First we'll transform to an intermediate representation, a dict of
        # positions
        if (x, y) in lattice:
            return

        lattice[(x, y)] = current

        current = self.relations[current]
        for d, n in izip(current._fields, current):
            if n:
                dx, dy = directions[d]
                self._lattice(n, x + dx, y + dy, lattice)

    def lattice(self):
        start = next(iter(self.relations))
        lattice = {}
        self._lattice(start, 0, 0, lattice)
        xs, ys = zip(*lattice)
        rx = range(min(xs), max(xs) + 1)
        ry = range(min(ys), max(ys) + 1)

        ys = [tuple(lattice.get((x, y), None) for x in rx) for y in ry]
        xs = zip(*ys)
        return DenseLattice(xs, ys)



Expand = collections.namedtuple('Expand', ('x', 'y'))
Size = collections.namedtuple('Size', ('w', 'h'))

# What about axes? What about titles? When you give them equal space,
class Plot(object):
    expand = Expand(1.0, 1.0)
    size = Size(0, 0)

    def alloc(self, x, y, w, h):
        pass

def cumulative(xs, xsum=0):
    rxs = []
    for x in xs:
        rxs.append(xsum)
        xsum += x
    return rxs



# The rules are relatively simple: If expand is set for any column of a row,
# then that entire row behaves as if it had expand set with the maximum value
# for that row.

class DenseLattice(_DenseLattice):
    def allocate(lattice, size_x, size_y, max_iterations=4):
        for _ in xrange(max_iterations):
            widths = [max(y.size.w for y in x if y) for x in lattice.x]
            heights = [max(x.size.h for x in y if x) for y in lattice.y]

            expand_x = [max(y.expand.x for y in x if y) for x in lattice.x]
            expand_y = [max(x.expand.y for x in y if x) for y in lattice.y]

            available_width = size_x - sum(
                w for w, e in izip(widths, expand_x) if not e)
            available_height = size_y - sum(
                h for h, e in izip(heights, expand_y) if not e)

            # Now we must try and give the row-cuts which make sense

            x_unit = available_width / sum(expand_x)
            y_unit = available_height / sum(expand_y)

            ws = [(e * x_unit) or w for e, w in izip(expand_x, widths)]
            hs = [(e * y_unit) or h for e, h in izip(expand_y, heights)]

            xs = cumulative(ws)
            ys = cumulative(hs)

            # If an alloc doesn't return anything, then it must be happy!
            happy = False
            for i, (w, h), (x, y) in izip(flatten(lattice.x),
                                  product(ws, hs),
                                  product(xs, ys)):
                if not i:
                    continue
                happy = not bool(i.alloc(x, y, w, h)) and happy

            if happy:
                return
