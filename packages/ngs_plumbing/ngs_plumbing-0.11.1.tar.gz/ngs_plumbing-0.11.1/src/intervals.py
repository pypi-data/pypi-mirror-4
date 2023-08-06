# This file is part of ngs_plumbing.

# ngs_plumbing is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ngs_plumbing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2012 Laurent Gautier

from collections import namedtuple, deque
from operator import attrgetter
import sys, bisect

#FIXME: check that begin <= end
Interval = namedtuple('Interval', 'begin end')

# class BufferedpopList(list):

#     def __init__(self, bufsize = 100):
#         self._offset = 0
#         self._bufsize = bufsize

#     def pop(self, i):
#         if i < (self._bufsize - self._offset):
#             pass
#         res = super(BufferedpopList, self).pop(i+self._offset)
#         return res

#     def __getitem__(self, i):
#         return super(BufferedpopList, self).__getitem__(i+self._offset)

#     def __setitem__(self, i, val):
#         super(BufferedpopList, self).__setitem__(i+self._offset, val)

#     def insert(self, i, val):
#         super(BufferedpopList, self).insert(i+self._offset, val)

#     def __delitem__(self, i, val):
#         super(BufferedpopList, self).__delitem__(i+self._offset, val)

    
class IntervalList(list):
    """ List of intervals. """
    def __init__(*args):
        super(IntervalList, args[0]).__init__()
        if len(args) == 1:
            return
        if len(args) > 2:
            raise TypeError('IntervalList takes at most 2 argument (%i given)' %len(args))
        self, l = args
        for e in l:
            self.append(e)

    def append(self, x):
        #FIXME: change to an interval protocol ?
        assert(isinstance(x, Interval))
        super(IntervalList, self).append(x)

    def extend(self, l):
        assert(isinstance(l, IntervalList))
        super(IntervalList, self).extend(x)

    def __setitem__(self, i, x):
        #FIXME: change to an interval protocol ?
        assert(isinstance(x, Interval))
        super(IntervalList, self).__setitem__(i, x)

    def minmax(self):
        return IntervalList.minmax_iter(self)

    @staticmethod
    def minmax_iter(intervals):
        its = iter(intervals)
        it = next(its)
        mini = it.begin
        maxi = it.end
        for it in its:
            mini = min(mini, it.begin)
            maxi = max(maxi, it.end)
        return Interval(mini, maxi)

    def sort(self, key = attrgetter('begin'), reverse = False):
        """ in-place sorting on the "begin" attribute for the intervals """
        super(IntervalList, self).sort(key = key, reverse = reverse)

    @staticmethod
    def collapse_iter(intervals, action_merge = None):
        """ Collapse a (presumably sorted-on-begin) iterable of intervals. """
        its = enumerate(intervals)
        canopy = None
        for i, e in its:
            if canopy is None:
                canopy = e
                continue
            if canopy.end >= e.begin:
                canopy = Interval(canopy.begin, e.end)
                #canopy.end = e.end
                if action_merge is not None:
                    action_merge(intervals, i)
            else:
                yield canopy
                canopy = e
        if canopy is not None:
            yield canopy

    @staticmethod
    def depthfilter_iter(intervals, threshold):
        """ Filter a (presumably sorted-on-begin) iterable of intervals
        and return an interator of intervals for which the input
        intervals overlap at a given number of times.

        threshold: the number of times the intervals should overlap. """

        its = enumerate(intervals)
        inc = int(1)
        d = int(0)
        begin = None
        ends = list()
        for i, e in its:
            while (len(ends) > 0) and (ends[0] < e.begin):
                #FIXME: pop(0) is in O(n) :/
                end = ends.pop(0)
                if d == threshold:
                    # interval to be returned
                    #FIXME: pop(0) is in O(n) :/
                    itv = Interval(begin, end)  
                    yield itv
                d -= inc
            bisect.insort_left(ends, e.end)
            d += inc
            if d == threshold:
                begin = e.begin


