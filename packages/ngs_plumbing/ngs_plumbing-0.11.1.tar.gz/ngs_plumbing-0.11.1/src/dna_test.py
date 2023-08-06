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
import ngs_plumbing.dna as dna

#Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    long = int


def ascii_val(char):
    return struct.unpack('@b', char)[0]

class DNATestCase(unittest.TestCase):
    def test_randomgenome(self):
        genome = dna.randomgenome(long(100))
        self.assertEqual(100, len(genome))

    def test_PackedDNABytes(self):
        string = b'ATACGCGACT'+b'GATAGTAGCG'
        dna_compress = dna.PackedDNABytes(string)
        string_back = dna_compress.unpack()
        self.assertEqual(2, dna_compress.bit_encoding)
        self.assertEqual(string, string_back)
        #self.assertEqual(string[1:5], dna_compress.get_bytes(1, 5)[0])

    def test_PackedDNABytes_unpackslice(self):
        string = b'ATACGCGACT'+b'GATAGTAGCG'
        dna_compress = dna.PackedDNABytes(string)
        self.assertEqual(string[3:7], dna_compress.unpack_slice(3, 7))


        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DNATestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

