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
import io, sys
import struct
import ngs_plumbing._libdna as _libdna

class BitPackingTestCase(unittest.TestCase):

    def test_dna_to_bit2_bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytes(string)
        string_back = _libdna.byte_frombit2bytes(vector)
        self.assertEqual(string, string_back)

    def test_dna_to_bit2_bytes_lowercase(self):
        string = b'atACGCGGct'+b'gaTCGTAGCG'
        vector = _libdna.bit2_frombytes(string)
        string_back = _libdna.byte_frombit2bytes(vector)
        self.assertEqual(string.upper(), string_back)

    def test_dna_to_bit2_bytearray(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytearray(bytearray(string))
        string_back = _libdna.byte_frombit2bytearray(vector)
        self.assertEqual(string, string_back)

    def test_slice_frombit2bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        packed = _libdna.bit2_frombytes(string)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 4)
        self.assertEqual(string[0:4], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 8)
        self.assertEqual(string[0:8], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 6)
        self.assertEqual(string[3:6], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 2, 4)
        self.assertEqual(string[2:4], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 11)
        self.assertEqual(string[0:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 11)
        self.assertEqual(string[3:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 4, 11)
        self.assertEqual(string[4:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 12)
        self.assertEqual(string[3:12], chunk)

        #self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
        #                 packed, -1, 3)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
                         packed, 1, 300)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
                         packed, 4, 3)

    def test_slicebit2_frombit2bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        packed = _libdna.bit2_frombytes(string)
        chunk = _libdna.slicebit2_frombit2bytes(packed, 0, 4)
        self.assertEqual(string[0:4], _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 0, 8)
        self.assertEqual(string[0:8], _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 3, 6)
        self.assertEqual(string[3:6] + b'A'*(4-(6-3)%4), _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 2, 4)
        self.assertEqual(string[2:4] + b'A'*(4-(4-2)%4), _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 0, 11)
        self.assertEqual(string[0:11] + b'A'*(4-(11-0)%4), 
                         _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 3, 11)
        self.assertEqual(string[3:11], 
                         _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 4, 11)
        self.assertEqual(string[4:11] + b'A'*(4-(11-4)%4), 
                         _libdna.byte_frombit2bytes(chunk))
        chunk = _libdna.slicebit2_frombit2bytes(packed, 3, 12)
        self.assertEqual(string[3:12] + b'A'*(4-(12-3)%4),
                         _libdna.byte_frombit2bytes(chunk))

        #self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
        #                 packed, -1, 3)
        self.assertRaises(IndexError, _libdna.slicebit2_frombit2bytes,
                         packed, 1, 300)
        self.assertRaises(IndexError, _libdna.slicebit2_frombit2bytes,
                         packed, 4, 3)

    def test_slice_frombit2bytearray(self):
        string = bytearray(b'ATACGCGGCT'+b'GATCGTAGCG')
        packed = _libdna.bit2_frombytearray(string)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 4)
        self.assertEqual(string[0:4], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 8)
        self.assertEqual(string[0:8], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 6)
        self.assertEqual(string[3:6], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 2, 4)
        self.assertEqual(string[2:4], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 11)
        self.assertEqual(string[0:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 11)
        self.assertEqual(string[3:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 4, 11)
        self.assertEqual(string[4:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 12)
        self.assertEqual(string[3:12], chunk)

        #self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
        #                 packed, -1, 3)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytearray,
                         packed, 1, 300)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytearray,
                         packed, 4, 3)

    def testBit2complement_frombit2bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytes(string)        
        vector_compl = _libdna.bit2complement_frombit2bytes(vector)
        self.assertEqual(len(vector), len(vector_compl))
        string_compl = _libdna.byte_frombit2bytes(vector_compl)
        self.assertEqual(b'TATGCGCCGACTAGCATCGC', string_compl)

    def testBit2complement_frombit2bytearray(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytearray(bytearray(string))
        vector_compl = _libdna.bit2complement_frombit2bytearray(vector)
        self.assertEqual(len(vector), len(vector_compl))
        string_compl = _libdna.byte_frombit2bytearray(vector_compl)
        self.assertEqual(b'TATGCGCCGACTAGCATCGC', string_compl)

    def testBit2reverse_frombit2bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytes(string)        
        vector_rev = _libdna.bit2reverse_frombit2bytes(vector)
        self.assertEqual(len(vector), len(vector_rev))
        string_rev = _libdna.byte_frombit2bytes(vector_rev)
        #Python 3:
        if sys.version_info[0] > 2:
            tmp = bytearray(len(string)-1)
            for i, j in enumerate(range(len(tmp), 0, -1)):
                tmp[i] = string[j]
        else:
            tmp = b''.join(string[x] for x in range(len(string)-1, -1, -1))
            self.assertEqual(tmp, string_rev)

    def testBit2reverse_frombit2bytearray(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytearray(bytearray(string))
        vector_rev = _libdna.bit2reverse_frombit2bytearray(vector)
        self.assertEqual(len(vector), len(vector_rev))
        string_rev = _libdna.byte_frombit2bytearray(vector_rev)
        #Python 3:
        if sys.version_info[0] > 2:
            tmp = bytearray(len(string)-1)
            for i, j in enumerate(range(len(tmp), 0, -1)):
                tmp[i] = string[j]
        else:
            tmp = b''.join(string[x] for x in range(len(string)-1, -1, -1))
            self.assertEqual(tmp, string_rev)

    def testBit2reversecomplement_frombit2bytes(self):
        string =    b'ATACGCGGCT'+b'GATCGTAGCG'
        string_c = b'TATGCGCCGA'+b'CTAGCATCGC'
        #Python 3:
        if sys.version_info[0] > 2:
            string_rc = bytearray(len(string))
            for i, j in enumerate(range(len(string_rc)-1, -1, -1)):
                string_rc[i] = string_c[j]
        else:
            string_rc = b''.join(string_c[x] for x in range(len(string)-1, -1, -1))
        vector = _libdna.bit2_frombytes(string)
        vector_rc = _libdna.bit2reversecomplement_frombit2bytes(vector)
        self.assertEqual(len(vector), len(vector_rc))
        string_back = _libdna.byte_frombit2bytes(vector_rc)
        self.assertEqual(string_rc, string_back)

    def testBit2reversecomplement_frombit2bytearray(self):
        string =    b'ATACGCGGCT'+b'GATCGTAGCG'
        string_c = b'TATGCGCCGA'+b'CTAGCATCGC'
        #Python 3:
        if sys.version_info[0] > 2:
            string_rc = bytearray(len(string))
            for i, j in enumerate(range(len(string_rc)-1, -1, -1)):
                string_rc[i] = string_c[j]
        else:
            string_rc = b''.join(string_c[x] for x in range(len(string)-1, -1, -1))
        vector = _libdna.bit2_frombytearray(bytearray(string))
        vector_rc = _libdna.bit2reversecomplement_frombit2bytearray(vector)
        self.assertEqual(len(vector), len(vector_rc))
        string_back = _libdna.byte_frombit2bytearray(vector_rc)
        self.assertEqual(string_rc, string_back)

        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(BitPackingTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

