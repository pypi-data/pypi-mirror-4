import unittest
import io, sys
import ngs_plumbing._libxsq as _libxsq

c2asc = ['']

class LibxsqTestCase(unittest.TestCase):
    
    def test_colourqual_frombytes(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombytes, 10)
        bt = b'AC$##HBD^%A'
        col, qual = _libxsq.colourqual_frombytes(bt)
        for i, x in enumerate(bt):
            # Python 3
            if sys.version_info[0] < 3:
                c = ord(x) & 0x3
            else:
                c = x & 0x3
            if qual[i] in (0,1,2,63):
                c = b'.'
            else:
                # Python 3
                if sys.version_info[0] < 3:
                    c = str(c)
                else:
                    c = bytes(str(c), 'ASCII')[0]
            self.assertEqual(c, col[i]);
        for i, x in enumerate(bt):
            # Python 3
            if sys.version_info[0] < 3:
                q = ord(x) >> 2
                self.assertEqual(q, ord(qual[i]));
            else:
                q = x >> 2
                self.assertEqual(q, qual[i]);

    def test_colourqual_frombytearray(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombytearray, 10)
        ba = bytearray(10)
        col,qual = _libxsq.colourqual_frombytearray(ba)

    def test_colourqual_frombuffer(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombuffer, 10)
        ba = bytearray(10)
        col,qual = _libxsq.colourqual_frombuffer(memoryview(ba))

    def test_basequal_frombytes(self):
        self.assertRaises(TypeError, _libxsq.basequal_frombytes, 10)
        bt = b'AC$##HBD^%A'
        base,qual = _libxsq.basequal_frombytes(bt)
        for i, x in enumerate(bt):
            # Python 3
            if sys.version_info[0] < 3:
                c = ord(x) & 0x3
            else:
                c = x & 0x3
            if base[i] in (0,1,2,63):
                c = b'N'
            else:
                c = b'ACGT'[c]
            self.assertEqual(c, base[i]);
        for i, x in enumerate(bt):
            # Python 3
            if sys.version_info[0] < 3:
                q = ord(x) >> 2
                self.assertEqual(q, ord(qual[i]));
            else:
                q = x >> 2
                self.assertEqual(q, qual[i]);


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(LibxsqTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)

