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

"""
Tools to handle DNA.

When representing DNA as a string the use of storage is not optimal
as 8 bits (one byte) are used to store each base while there are
traditionnally only 4 possibilities for bases, 5 when considering
that 'N' can be used to signify that the base is not know / not defined
at a given position.

4 bases can be encoded with 2 bits, and 5 bases can be encoded with
3 bits.

The module contains the following lookup structure.
2-bit encoding:
_bit2_to_dna
_dna_to_bit2

3-bit encoding:
_bit3_to_dna
_dna_to_bit3

"""

from struct import pack, unpack
from array import array
from operator import or_
from io import IOBase, BytesIO
from ngs_plumbing._libdna import byte_frombit2bytearray, byte_frombit2bytes
from ngs_plumbing._libdna import slice_frombit2bytes
from ngs_plumbing._libdna import bit2_frombytes, bit2_frombytearray, bit2_frombuffer
from ngs_plumbing._libdna import bit2reverse_frombit2bytes, bit2complement_frombit2bytes, bit2reversecomplement_frombit2bytes
from ngs_plumbing.ngsp_string import sequentialfragments, sequentialfragments_iter, randomstring

# Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    xrange = range

# A: 0b00
# C: 0b01
# G: 0b10
# T: 0b11
_alphabet = b'ACGT'
_bit2_to_dna = _alphabet
# arbitrary: put an A when out of the alphabet
# error checking is assumed to take place upstream
_dna_to_bit2 = array('i', (0b00 for x in range(255)))

for val, b in enumerate(_bit2_to_dna):
    if sys.version_info[0] < 3:
        i = ord(b)
        _dna_to_bit2[i] = val
    else:
        _dna_to_bit2[b] = val
del(b, val)


# also store pairs (masking + lookups to be done divided by 2)
_bit2_to_dna2 = tuple(l1+l2 for i2,l2 in enumerate(_alphabet) \
                          for i1,l1 in enumerate(_alphabet))


_alphabet_n = b'ATGCN'
_alphabet_to_bits = {b'A': (0b000, ),
                     b'T': (0b001, ),
                     b'G': (0b110, ),
                     b'C': (0b111, ),
                     b'N': (0b010, 0b011, 0b100, 0b101)}

# setup byte<->integer mappings
_bit3_to_dna = list(b'N' * 8)
for k,v in _alphabet_to_bits.items():
    for i in v:
        _bit3_to_dna[i] = k
_bit3_to_dna = b''.join(_bit3_to_dna)
del(k, v, i)

_dna_to_bit3 = array('i', (_alphabet_to_bits[b'N'][0] for x in range(255)))
for val, b in enumerate(_bit3_to_dna):
    if sys.version_info[0] < 3:
        i = ord(b)
        _dna_to_bit3[i] = val
    else:
        _dna_to_bit3[b] = val
del(b, val)
# ---

def randomgenome(size):
    """ Make a random genome """
    return randomstring(size, _alphabet_n)


class PackedDNABytes(bytes):
    """
    Representation of a DNA string as an array of bytes
    """
    #__slots__ = ('__bits', '_get_bit_encoding', 'bit_encoding',
    #             'unpack')

    def _get_bit_encoding(self):
        return self.__bits
    bit_encoding = property(_get_bit_encoding,
                            None, None,
                            'Number of bits used for encoding')

    def __new__(cls, string='', bits = 2, dopack=True):
        if len(string) == 0:
            res = array('L')
        else:
            if bits == 2:
                if dopack:
                    res = bit2_frombytes(string)
                else:
                    res = string
            else:
                raise ValueError('Only 2-bit packing for now')
        obj = bytes.__new__(cls, res)
        return(obj)
        
    def __init__(self, string='', bits=2, dopack=True):
        self.__bits = bits
        if bits == 2:
            self.__unpack = byte_frombit2bytes
        elif bits == 3:
            raise ValueError('Only 2-bit packing for now')
        else:
            raise ValueError('The parameter "bits" can only take the value 2 or 3')

    def reversed(self):
        """ Return the reverse, still packed. """
        return PackedDNABytes(bit2reverse_frombit2bytes(self),
                              dopack=False)

    def complemented(self):
        """ Return the complement, still packed. """
        return PackedDNABytes(bit2complement_frombit2bytes(self), 
                              dopack=False)

    def reversecomplemented(self):
        """ Return the reverse complement, still packed. """
        return PackedDNABytes(bit2reversecomplement_frombit2bytes(self), 
                              dopack=False)

    def unpack(self):
        return self.__unpack(self)

    def unpack_slice(self, i=None, j=None):
        """ Get the unpacked a subsequence as bytes
        (zero-offset indexing, like other Python sequences)
        """
        res = slice_frombit2bytes(self, i, j)
        return res

# class KmerPosition(dict):
#     """
#     Given a sequence, or streamm, of DNA bases as bytes, build a Python dict
#     of bit representation for the Kmers.

#     KmerPosition(stream, K = 17, step = 1)
    
#     """

#     def __init__(self, stream, K = 17, step = 1):        

#         self.__K = K
#         self.__step = step

#         #FIXME: code duplication :/ refactor to avoid it without performance penalty
#         pos = long(0)
#         if isinstance(stream, bytes):
#             for i, chunk_bytes in enumerate(sequentialfragments(stream, K, step = step)):
#                 if chunk_bytes not in self:
#                     self[chunk_bytes] = [pos,]
#                 else:
#                     self[chunk_bytes].append(pos)
#                 pos += step
#         else:
#             iterator = sequentialfragments_iter
#             for i, chunk_bytes in enumerate(sequentialfragments_iter(stream, K, step = step)):
#                 b = chunk_bytes.tobytes()
#                 if b not in self:
#                     self[b] = [pos,]
#                 else:
#                     self[b].append(pos)
#                 pos += step


#     def _get_K(self):
#         return self.__K
#     def _set_K(self, K):
#         self.__K = K
#     K = property(_get_K, None, None, 'K for the K-mers')

#     def _get_step(self):
#         return self.__step
#     def _set_step(self, step):
#         self.__step = step
#     step = property(_get_step, None, None, 
#                     'Incremental step for the sliding window over the original sequence')
    

# class PackedPosition(KmerPosition):
#     """
#     Given a sequence, or streamm, of DNA bases as bytes, build a Python dict
#     of bit representation for the Kmers.

#     KmerPosition(stream, K = 17, step = 1, bits = 2)
    
#     """

#     def _get_bit_encoding(self):
#         return self.__bits
#     bit_encoding = property(_get_bit_encoding,
#                             None, None,
#                             'Number of bits used for encoding')
#     def _get_K(self):
#         return self.__K
#     def _set_K(self, K):
#         self.__K = K
#     K = property(_get_K, None, None, 'K for the K-mers')


#     def __init__(self, stream, K = 17, step = 1, bits = 2):        

#         assert(isinstance(K, long) or isinstance(K, int))
#         assert(isinstance(step, long) or isinstance(step, int))
#         self.__K = K
#         self.__step = step
#         self.__bits = bits

#         if bits == 2:
#             self.__int64_to_dna = bit2int64_to_dna
#         elif bits == 3:
#             self.__int64_to_dna = bit3int64_to_dna
#         else:
#             raise ValueError('The parameter "bits" can only take the value 2 or 3')

#         if isinstance(stream, bytes):
#             if bits == 2:
#                 iterator = dna_to_bit2int64
#             elif bits == 3:
#                 iterator = dna_to_bit3int64
#             else:
#                 raise ValueError('The parameter "bits" can only take the value 2 or 3')
#         else:
#             if bits == 2:
#                 iterator = dna_to_bit2int64_iter
#             elif bits == 3:
#                 iterator = dna_to_bit3int64_iter
#             else:
#                 raise ValueError('The parameter "bits" can only take the value 2 or 3')

#         pos = long(0)
#         for i, chunk_int in enumerate(iterator(stream, K = K, step = step)):
#             if chunk_int not in self:
#                 self[chunk_int] = [pos,]
#             else:
#                 self[chunk_int].append(pos)
#             pos += step

#     def keys_bytes(self):
#         """ Homologous to the method keys(),
#         except that it returns the keys as DNA bytes """
#         k = self.keys()
#         k = tuple(self.__int64_to_dna(k, self.__K))
#         return k

#     def iter_bytes(self):
#         return iter(self.__int64_to_dna(x) for x in iter(self))

