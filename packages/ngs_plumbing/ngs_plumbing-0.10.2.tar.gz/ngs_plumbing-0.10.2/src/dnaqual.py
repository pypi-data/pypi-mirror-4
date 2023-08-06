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
Tools to handle DNA with base quality measures
"""

from collections import namedtuple
from ngs_plumbing.dna import _bit2_to_dna, _dna_to_bit2
from array import array
from ngs_plumbing._libdnaqual import bit2bytes_frombasequal
from ngs_plumbing._libxsq import basequal_frombytes

class DnaQual(object):
    """
    Given a sequence of bytes for the dna,
    and a sequence of integers for the quality,
    create an instance.
    """

    __slots___ = ('dna', 'qual', 
                  'tobit8')

    def __init__(self, dna, quality):
        assert(len(dna) == len(quality))
        self.dna = dna
        self.qual = quality

    def tobit8(self):
        """" Encode the DNA and quality information 
        into one bytes (8 bits) per DNA/quality pair. """
        return bit2bytes_frombasequal(self.dna, self.qual)

class DnaQualList(object):
    """
    Sequence of DnaQual instances
    """
    def __init__(self, sequence):
        dna_list = list()
        qual_list = list()
        for x in sequence:
            assert(isinstance(x, DnaQual))
            dna_list.append(x.dna)
            qual_list.append(x.qual)
        self._dna_list = dna_list
        self._qual_list = qual_list

    def __getitem__(self, i):
        return DnaQual(self._dna_list[i], self._qual_list[i])

    def __del__(self, i):
        del(self._dna_list[i])
        del(self._qual_list[i])

    def append(self, x):
        assert(isinstance(x, DnaQual))
        self._dna_list.append(x)
        self._qual_list.append(x)

    def to_bytes(self):
        pass

def bytes_to_dnaqual(bseq):
    """
    Take a sequence of bytes (bytes or bytearray)
    and return DNA and quality string.
    """
    dna, qual = basequal_frombytes(bseq)
    return DnaQual(dna, qual)


def halfbytes_to_dnaqual(bseq):
    """
    Take a sequence of half-bytes (bytes or bytearray)
    and return DNA and quality string.

    Note: only an even number of halfbytes is possible
    """

    dna = bytearray(len(bseq)*2)
    qual = bytearray(len(bseq)*2)
    for i, v in enumerate(bseq):
        d = _ACGT[v & 0b11]
        q = (v >> 2) & 0b11
        if q == 0:
            dna[i*2] = b'N'
        else:
            dna[i*2]
        qual[i*2] = q

        d = _dna_to_bit2[v & 0b11000000]
        q = (v >> 6) & 0b11
        if q == 0:
            dna[i*2+1] = b'N'
        else:
            dna[i*2+1]
        qual[i*2+1] = q
    
    return DnaQual(dna = dna,
                   qual = qual)


