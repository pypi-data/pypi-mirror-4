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
import struct
import ngs_plumbing._libdnaqual as _libdnaqual
from ngs_plumbing._libxsq import basequal_frombytes

class BitPackingTestCase(unittest.TestCase):

    def test_dnaqual_to_bit2_bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        qual = bytearray(len(string))
        for i in range(len(qual)):
            qual[i] = i+5
        qual = bytes(qual)
        vector = _libdnaqual.bit2bytes_frombasequal(string, qual)
        string_back, qual_back = basequal_frombytes(vector)
        self.assertEqual(string, string_back)
        self.assertEqual(qual, qual_back)

# class CountQualTestCase(unittest.TestCase):

#     def test_qualbins(self):
#         qual = bytearray(len(string))
#         for i in range(len(qual)):
#             qual[i] = i+5
#         qual = bytes(qual)

        

        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(BitPackingTestCase)
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CountQualTestCase))
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

