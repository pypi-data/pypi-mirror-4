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
import ngs_plumbing.fastq as fastq

class FastqTestCase(unittest.TestCase):

    def setUp(self):
        data = (b'@WXOVW:25:85', b'ATACGCGGCT'+b'GATCGTAGCG',
                b'+',
                b'@@))CCCCBB'+b'???ECCEECC',
                b'@WXOVW:26:89', b'GATCGCGGGG'+b'GATATATGCG',
                b'+',
                b'9.0*---))C'+b'+590<5>898',
                b'@WXOVW:33:89', b'GATAACGGGG'+b'GATAAATGCG',
                b'+',
                b'+.0*-BB))C'+b'+590<00898')

        self._data = data

    def test_read_fastq(self):
        data = self._data
        res = tuple(fastq.read_fastq(data))
        self.assertEqual(3, len(res))
        self.assertTrue(isinstance(res[0], fastq.Entry))
        self.assertTrue(isinstance(res[1], fastq.Entry))
        for i in range(3):
            self.assertEqual(data[i*4], res[i].header)
            self.assertEqual(data[(i*4)+1], res[i].sequence)
            self.assertEqual(data[(i*4)+3], res[i].quality)
 

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FastqTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

