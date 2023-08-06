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

import unittest
import io
import ngs_plumbing.intervals as intervals

class IntervalListTestCase(unittest.TestCase):
    
    def setUp(self):
        it1 = intervals.Interval(1, 7)
        it2 = intervals.Interval(3, 10)
        it3 = intervals.Interval(12, 16)        
        self.itl = intervals.IntervalList((it1, it3, it2))

    def test_initValid(self):
        itl = intervals.IntervalList()
        self.assertEqual(0, len(itl))
        it1 = intervals.Interval(1, 7)
        it2 = intervals.Interval(3, 10)
        itl = intervals.IntervalList((it1, it2))
        self.assertEqual(2, len(itl))

    def test_initInvalid(self):
        it1 = intervals.Interval(1, 7)
        it2 = intervals.Interval(3, 10)
        it3 = intervals.Interval(12, 16)
        self.assertRaises(AssertionError, intervals.IntervalList, (it1, it2, "foo", it3))

    def test_minmax(self):
        itl = self.itl
        ir = itl.minmax()
        self.assertEqual(1, ir.begin)
        self.assertEqual(16, ir.end)

    def test_collapse(self):
        itl = self.itl
        itl.sort()
        itl_c = intervals.IntervalList(intervals.IntervalList.collapse_iter(itl))
        self.assertEqual(2, len(itl_c))
        self.assertEqual(1, itl_c[0].begin)
        self.assertEqual(10, itl_c[0].end)

    def test_depthfilter(self):
        vals = ((1, 7), (2, 8), (3, 10), (12, 16), (11, 15),
                (20, 25))
        itl = intervals.IntervalList(intervals.Interval(x,y) for x,y in vals)
        itl.sort()
        tmp = intervals.IntervalList.depthfilter_iter(itl, 2)
        itl_f = intervals.IntervalList(tmp)
        self.assertEqual(2, len(itl_f))
        self.assertEqual(2, itl_f[0].begin)
        self.assertEqual(8, itl_f[0].end)
        self.assertEqual(12, itl_f[1].begin)
        self.assertEqual(15, itl_f[1].end)

        tmp = intervals.IntervalList.depthfilter_iter(itl, 3)
        itl_f = intervals.IntervalList(tmp)
        self.assertEqual(1, len(itl_f))
        self.assertEqual(3, itl_f[0].begin)
        self.assertEqual(7, itl_f[0].end)


        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(IntervalListTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

