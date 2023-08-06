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
import ngs_plumbing.xsq as xsq

class XsqTestCase(unittest.TestCase):
    
    def setUp(self):
        fn = xsq.list_xsq(xsq.testdata_dir).next()
        xf = xsq.XSQFile(fn)
        self._fn = fn
        self._xf = xf

    def tearDown(self):
        self._xf.close()

    def testLibraryNames(self):
        xf = self._xf
        self.assertEqual(1, len(xf.library_names))
        self.assertEqual(u'DefaultLibrary', xf.library_names[0])

    def testRunMetaDataError(self):
        # Missing metadata. This can be the case when the 5500's software crashes and support
        # goes in to salvage data
        xf = self._xf
        self.assertRaises(KeyError, getattr, xf, 'run_metadata')
        
    def testLibrary(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        self.assertEqual('Dummy library for software testing', lb.name)

    def testIter_reads(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        f3_iter = lb.iter_reads('F3', 'ColorCallQV')
        f3 = list(f3_iter)

    def testIter_csfasta_reads(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        f3_iter = xsq.iter_csfasta_reads(lb, 'F3', 50)
        f3 = list(f3_iter)

    def testReadCount(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        self.assertEqual(4995, lb.readcount())

    def testMakeCSFASTA(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        fragment = 'F3'
        numbase = 50
        flowcell = '01'
        buf_cs = io.BytesIO()
        buf_qual = io.BytesIO()
        res = xsq.make_csfasta(lb, fragment, buf_cs, buf_qual, xf, flowcell)

    def testMakeCSFASTQ(self):
        xf = self._xf
        lb = xf.library(u'DefaultLibrary')
        fragment = 'F3'
        numbase = 50
        flowcell = '01'
        buf = io.BytesIO()
        res = xsq.make_csfastq(lb, fragment, buf, xf, flowcell)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(XsqTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

