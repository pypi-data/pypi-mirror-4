"""A library for executing running calculations.

A running calculation is an object that can be fed one value at a time. This
allows running several running calculations on a single iterator of values in
parallel. This isn't possible with the built-in variants of most calculations,
such as max() and heapq.nlargest().

Running calculation instances can be fed values directly, for example:

mean_rc, stddev_rc = RunningMean(), RunningStdDev()
for x in values:
    mean_rc.feed(x)
    stddev_rc.feed(x)
mean, stddev = mean_rc.value, stddev_rc.value

Additionally, the apply_in_parallel() function is supplied, which makes
performing several running calculations in parallel easy (and fast!).
For example:

mean, stddev = apply_in_parallel([RunningMean(), RunningStdDev()], values)
five_smallest, five_largest = apply_in_parallel([RunningNSmallest(5), RunningNLargest(5)], values)
"""

__all__ = [
	'apply_in_parallel',
    'RunningCalc',
	'RunningMax', 'RunningMin',
	'RunningCount',
	'RunningSum', 'RunningAverage', 'RunningMean',
	'RunningSumKahan', 'RunningAverageKahan', 'RunningMeanKahan',
    'RunningMSum', 'RunningLSum',
	'RunningVariance', 'RunningStandardDeviation', 'RunningStdDev',
	'RunningNLargest', 'RunningNSmallest',
	]

from itertools import islice

# Python 3 compatibility
import sys
if sys.version_info >= (3,):
    xrange = range
    long = int


def split_into_chunks(iterable, chunk_size):
    """Split the items in an iterable into chunks of a given size.
    
    If the number of items isn't a multiple of chunk_size, the last chunk will
    be smaller than chunk_size.
    
    This is like the grouper() recipe in the itertools documentation, except
    that no filler value is used, the code is more straightforward, and it
    is more efficient on sequences via special casing.
    """
    try:
        if int(chunk_size) != chunk_size or chunk_size < 1:
            raise ValueError('chunk_size must be an integer greater than zero!')
    except TypeError:
        raise ValueError('chunk_size must be an integer greater than zero!')
        
    try:
        # try efficient version for sequences
        n = len(iterable)
        if n == 0:
            pass
        elif chunk_size >= n:
            # just yield the given sequence
            # this avoids needlessly copying the entire sequence
            yield iterable
        else:
            for start in xrange(0, n, chunk_size):
                yield iterable[start:start+chunk_size]
    except (TypeError, AttributeError): # may be thrown by len() or the slicing
        # use generic version which works on all iterables
        iterator = iter(iterable)
        while True:
            chunk = list(islice(iterator, chunk_size))
            if not chunk:
                break
            yield chunk

def apply_in_parallel(running_calcs, iterable, chunk_size=1000):
    """Run several running calculations on a single iterable of values.
    
    The calculations are performed in parallel, so that the data is not kept
    in memory all at once.
    
    Note, however, that by default this will keep chunks of items in memory,
    one chunk at a time. This is done to allow running calculations to be
    performed faster. However, if keeping chunks of items in memory is
    problematic, set chunk_size appropriately or set it to one to disable
    splitting into chunks.
    """
    if chunk_size == 1:
        feed_funcs = [rcalc.feed for rcalc in running_calcs]
        for value in iterable:
            for rcalc_feed in feed_funcs:
                rcalc_feed(value)
    else:
        feed_funcs = [rcalc.feedMultiple for rcalc in running_calcs]
        for values_chunk in split_into_chunks(iterable, chunk_size):
            for rcalc_feed in feed_funcs:
                rcalc_feed(values_chunk)
        
    return tuple([rcalc.value for rcalc in running_calcs])


class RunningCalc(object):
    """A base class for running calculations.
    
    The interface is just that a 'feed' method must be implemented. This is
    the method which shall be called once for each value to be processed.
    
    A running calculation can initialize itself by implementing __init__.
    
    For optimization, a sub-class may override the feedMultiple method, which
    shall be called whenever several values are available for processing.
    """
    def feed(self, value):
        """Process a single value."""
        # All RunningCalc classes must implement this!
        raise NotImplementedError()

    def feedMultiple(self, values):
        """Process several values."""
        # This default implementation is naive; sub-classes are encouraged to
        # implement more efficient alternatives.
        for value in values:
            self.feed(value)


class RunningMax(RunningCalc):
    def __init__(self):
        self.value = None

    def feed(self, value):
        if self.value is None or value > self.value:
            self.value = value

    def feedMultiple(self, values):
        if values:
            self.feed(max(values))

class RunningMin(RunningCalc):
    def __init__(self):
        self.value = None

    def feed(self, value):
        if self.value is None or value < self.value:
            self.value = value

    def feedMultiple(self, values):
        if values:
            self.feed(min(values))

class RunningCount(RunningCalc):
    def __init__(self, initial_value=0):
        self.value = initial_value

    def feed(self, value):
        self.value += 1

    def feedMultiple(self, values):
        try:
            n = len(values)
        except TypeError:
            n = sum((1 for x in values))
        self.value += n

class RunningSum(RunningCalc):
    """naive running sum
    
    Note: this implementation is significantly numerically unstable!
    """
    def __init__(self, initial_value=0):
        self.value = initial_value

    def feed(self, value):
        self.value += value

    def feedMultiple(self, values):
        self.value += sum(values)

class RunningAverage(RunningCalc):
    """naive running average
    
    Note: this implementation is significantly numerically unstable!
    """
    def __init__(self):
        self.value = 0.0
        self.n = 0

    def feed(self, value):
        self.n += 1
        self.value += (value - self.value) / self.n


RunningMean = RunningAverage

def _kahan_running_sum(initial_value=0.0):
    """Generator function version of the Kahan summation algorithm.
    
    For internal use.
    """
    sum = initial_value
    c = 0.0
    while True:
        value = yield sum
        y = value - c
        t = sum + y
        c = (t-sum) - y
        sum = t

class RunningSumKahan(RunningCalc):
    """running sum using the Kahan summation algorithm"""
    def __init__(self, initial_value=0.0):
        self.kahan_sum = _kahan_running_sum(initial_value)
        self.value = next(self.kahan_sum)

    def feed(self, value):
        self.value = self.kahan_sum.send(value)

class RunningAverageKahan(RunningCalc):
    """running average using the Kahan summation algorithm"""
    def __init__(self):
        self.kahan_sum = _kahan_running_sum(0.0)
        next(self.kahan_sum)
        self.sum = None
        self.count = 0

    def feed(self, value):
        self.count += 1
        self.sum = self.kahan_sum.send(value)

    @property
    def value(self):
        return self.sum / self.count if self.sum is not None else 0

RunningMeanKahan = RunningAverageKahan

        
class RunningMSum(RunningCalc):
    """running full precision summation using multiple floats for intermediate values"""
    # based on ActiveState recipe #393090 by Raymod Hettinger
    # http://code.activestate.com/recipes/393090/

    def __init__(self):
        self.partials = [] # sorted, non-overlapping partial sums
        
    def feed(self, x):
        # Rounded x+y stored in hi with the round-off stored in lo.  Together
        # hi+lo are exactly equal to x+y.  The inner loop applies hi/lo summation
        # to each partial so that the list of partial sums remains exact.
        # Depends on IEEE-754 arithmetic guarantees.  See proof of correctness at:
        # www-2.cs.cmu.edu/afs/cs/project/quake/public/papers/robust-arithmetic.ps
        partials = self.partials
        i = 0
        for y in partials:
            if abs(x) < abs(y):
                x, y = y, x
            hi = x + y
            lo = y - (hi - x)
            if lo:
                partials[i] = lo
                i += 1
            x = hi
        partials[i:] = [x]

    @property
    def value(self):
        return sum(self.partials, 0.0)


from math import frexp
import operator

class RunningLSum(RunningCalc):
    """running full precision summation using long integers for intermediate values"""
    # based on ActiveState recipe #393090 by Raymod Hettinger
    # http://code.activestate.com/recipes/393090/

    def __init__(self):
        self.tmant = 0
        self.texp = 0

    def feed(self, value):
        # Transform (exactly) a float to m * 2 ** e where m and e are integers.
        # Adjust (tmant,texp) and (mant,exp) to make texp the common exponent.
        # Given a common exponent, the mantissas can be summed directly.
        mant, exp = frexp(value)
        mant, exp = long(mant * 2.0 ** 53), exp-53
        if self.texp > exp:
            self.tmant <<= self.texp - exp
            self.texp = exp
        else:
            mant <<= exp - self.texp
        self.tmant += mant

    def feedMultiple(self, values):
        # first calculate the minimal exponent, then shift all mantissas accordingly
        if values:
            exp_mant_pairs = [(exp-53, long(mant * 2.0 ** 53)) for (mant, exp) in map(frexp, values)] + [(self.tmant, self.texp)]
            self.texp = texp = min(map(operator.itemgetter(0), exp_mant_pairs))
            self.tmant = sum((mant << (exp-texp) for (exp, mant) in exp_mant_pairs))

    @property
    def value(self):
        return float(str(self.tmant)) * 2.0 ** self.texp


from math import sqrt

class RunningVariance(RunningCalc):
    """calculate a running variance using the Welford algorithm"""
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0

    def feed(self, value):
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.M2 += delta * (value - self.mean) # uses the new value of mean!

    @property
    def populationVariance(self):
        return (self.M2 / self.n) if self.n > 0 else 0

    @property
    def sampleVariance(self):
        return (self.M2 / (self.n - 1)) if self.n > 1 else 0

    @property
    def populationStandardDeviation(self):
        return sqrt(self.populationVariance)

    @property
    def sampleStandardDeviation(self):
        return sqrt(self.sampleVariance)

    value = populationVariance

class RunningStandardDeviation(RunningVariance):
    """calculate a running standard deviation using the Welford algorithm"""
    value = RunningVariance.populationStandardDeviation

class RunningSampleVariance(RunningVariance):
    """calculate a running sample variance using the Welford algorithm"""
    value = RunningVariance.sampleVariance

class RunningSampleStandardDeviation(RunningVariance):
    """calculate a running sample standard deviation using the Welford algorithm"""
    value = RunningVariance.sampleStandardDeviation

RunningStdDev = RunningStandardDeviation
RunningSampleStdDev = RunningSampleStandardDeviation


from heapq import heappush, heappushpop, heapify

class RunningNLargest(RunningCalc):
    def __init__(self, N):
        self.heap = []
        self.N = N

        # special case for N=0: self.value should always be []
        if self.N == 0:
            self.feed = lambda value: None
            self.feedMultiple = lambda values: None

    def feed(self, value):
        if len(self.heap) < self.N:
            heappush(self.heap, value)
        elif value > self.heap[0]:
            heappushpop(self.heap, value)

    def feedMultiple(self, values):
        # Note on efficiency: running nlargest() on the new values first is not
        # beneficial, since most values can be discarded immediately without
        # being added to the heap after just one comparison.
        heap = self.heap
        n_missing = self.N - len(heap)
        if n_missing > 0:
            values = iter(values)
            heap.extend(islice(values, n_missing))
            heapify(heap)
        try:
            sol = heap[0] # sol --> Smallest Of the Largest
        except IndexError:
            # heap is empty, which means no values were fed
            return
        for value in values:
            # heap[0] is always the smallest value in the heap
            if value > sol:
                heappushpop(heap, value)
                sol = heap[0]

    @property
    def value(self):
        return sorted(self.heap, reverse=True)

from _heapq import nsmallest
from itertools import chain
from bisect import insort_right
class RunningNSmallest(RunningCalc):
    def __init__(self, N):
        self.n_smallest = []
        self.N = N

        # special case for N=0: self.value should always be []
        if self.N == 0:
            self.feed = lambda value: None
            self.feedMultiple = lambda values: None

    def feed(self, value):
        if len(self.n_smallest) < self.N:
            insort_right(self.n_smallest, value)
        elif value < self.n_smallest[-1]:
            self.n_smallest.pop()
            insort_right(self.n_smallest, value)

    def feedMultiple(self, values):
        self.n_smallest = nsmallest(self.N, chain(self.n_smallest, values))

    @property
    def value(self):
        return self.n_smallest
