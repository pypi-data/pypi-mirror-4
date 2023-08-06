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
import ngs_plumbing.ngsp_string as string
import io

# Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    long = int

class StringTestCase(unittest.TestCase):
    def test_randomstring(self):
        rna = string.randomstring(long(100), b'AUGC')
        self.assertEqual(100, len(rna))

    def test_randomfragments(self):
        rna = string.randomstring(long(100), b'AUGC')
        fragments = string.randomfragments(rna, 10, size = 5)
        self.assertEqual(len(fragments), 10)
        for f in fragments:
            self.assertEqual(len(f), 5)

    def test_sequentialfragments(self):
        quintuplets = (b'ATACG', b'CGGCT', b'GATCG')
        dna = b''.join(quintuplets)
        fragments = string.sequentialfragments(dna, 5, step = 5)
        for q,f in zip(quintuplets, fragments):
            self.assertEqual(q, f)

    def test_sequentialfragments_iter(self):
        quintuplets = (b'ATACG', b'CGGCT', b'GATCG')
        dna = b''.join(quintuplets)
        bio = io.BytesIO(dna)
        fragments = string.sequentialfragments_iter(bio, 5, step = 5)
        for q,f in zip(quintuplets, fragments):
            self.assertEqual(q, f)
        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(StringTestCase)
    return suite

def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

