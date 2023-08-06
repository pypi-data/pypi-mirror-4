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
import ngs_plumbing.dnaqual as dnaqual

class DnaQualTestCase(unittest.TestCase):

    def test_initMismatchingLength(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        quality = range(19)
        self.assertRaises(AssertionError, dnaqual.DnaQual, string, quality)

  
        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DnaQualTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

