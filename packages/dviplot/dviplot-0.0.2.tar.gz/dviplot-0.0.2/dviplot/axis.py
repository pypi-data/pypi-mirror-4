from itertools import cycle
import random
import math

#data = [1.5 * random.random() for i in xrange(10)]

def possible_lin_ticks(low, high):
    """Obtain the possible ticks for a given set of axis measurements"""
    # Ones, twos and fives: this is what we like to work in, and is how it's
    # done in pyslha. But probably want something that is a bit more abstract
    # than pyslha.
    assert(high > low)
    d =  high - low

    # Now for some hardcore cheating: log function go!
    floor = 10**(math.floor(math.log10(d)) - 1)

    possible = [] 
    # We now use this scale...
    trials = (50, 20, 10, 5, 2, 1)
    for i in trials:
        da = floor * i
        a = int(math.floor(low / da))
        b = int(math.ceil(high / da))
        ticks = [da * x for x in xrange(a, b+1)]
        possible.append(ticks)

    return possible



# This might be a *little* easier
def possible_log_ticks(low, high):
    """Obtain the possible ticks for a given logarithmic axis"""
    assert low < high

    # There's really only one thing for log(10) plots
    low_log = int(math.floor(math.log10(low)))
    high_log = int(math.ceil(math.log10(high)))

    # Oh dear, this is rather simplistic!
    possible = [[10**i for i in xrange(low_log, 1+high_log)]]

    return possible

#tick_choices = list(possible_ticks(data))

# Let us introduce the concept of a "macro tick" -- that is, some kind of tick
# bigger than the major tick. This should obviously carry some kind of bonus,
# but not at the expense of everything else! Thing is that it should lie on
# ones, twos and fives. And this is pretty much what makes some things look
# weird when they're plotted. Strange scales.

# Minor ticks are going to be so much the same. Ten seems to be too many minor
# ticks in some cases, but it might give the best compromise. But five is
# probably going to be just right most of the time. Two is appropriate in some
# circumstances too.


# TODO: Make ticks have some cost value, pick the best one. Need to find a clean
# way of intefacing this with the rest of the code. Perhaps a callback
# mechanism is the least coupled. The main things we need to check are overlap
# of labels, overlap of legends etc.
