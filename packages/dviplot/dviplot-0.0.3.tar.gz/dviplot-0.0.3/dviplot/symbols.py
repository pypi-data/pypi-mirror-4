# How to draw a *load* of symbols


# Circle, Square, Triangle, Rhombus, (star), Cross
# There's a load of these to get right

def cross_diag(cr, size=2.0):
    hs = 0.5 * size
    cr.rel.NW(hs).to.SE(size).path()
    cr.NW(hs).NE(hs).to.SW(size).path()
