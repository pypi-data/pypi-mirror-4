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

import unittest
import io, struct
from ngs_plumbing.dna import PackedDNABytes
import ngs_plumbing.fasta as fasta

class FastaTestCase(unittest.TestCase):

    def setUp(self):
        data = (b'> S1', b'ATACGCGGCT'+b'GATCGTAGCG'+b'GATCGTAGCG'+b'AA',
                b'> S2', b'AGACGCGGCT'+b'GATCGTAGCG'+b'GATCGTAGCG'+b'CC',
                b'ACACGCGGCT'+b'GATCGTAGCG'+b'AGACGCGGCT'+b'GG')
        self._data = data

    def test_read_fasta(self):
        data = self._data
        res = tuple(fasta.read_fasta(data))
        self.assertEqual(2, len(res))
        self.assertTrue(isinstance(res[0], fasta.Entry))
        self.assertTrue(isinstance(res[1], fasta.Entry))
        self.assertEqual(data[0], res[0].header)
        self.assertEqual(data[1], res[0].sequence)
        self.assertEqual(data[2], res[1].header)
        self.assertEqual(b''.join(data[3:]), res[1].sequence)

    def test_read_fastab(self):
        data = tuple(fasta.read_fasta(self._data))
        bitpacked = PackedDNABytes(data[1].sequence)
        b = struct.pack('<QH%is%is' %(len(data[1].header), len(bitpacked)),
                        len(bitpacked), 
                        len(data[1].header), data[1].header,
                        bitpacked)
        stream = io.BytesIO(b)
        stream.flush()
        stream.seek(0)
        res = next(fasta.read_fastab(stream))
        self.assertEqual(data[1].header, res.header)
        self.assertEqual(len(bitpacked), len(res.sequence))
        for i in range(len(bitpacked)):
            self.assertEqual(bitpacked[i], res.sequence[i])

    def test_tofastab(self):
        data = tuple(fasta.read_fasta(self._data))
        stream = io.BytesIO()
        fasta.tofastab(data[1], stream)
        stream.flush()
        stream.seek(0)
        res = next(fasta.read_fastab(stream))
        self.assertEqual(data[1].header, res.header)
        bitpacked = PackedDNABytes(data[1].sequence)
        self.assertEqual(len(bitpacked), len(res.sequence))
        for i in range(len(bitpacked)):
            self.assertEqual(bitpacked[i], res.sequence[i])

  
        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FastaTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

