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

""" """
from struct import unpack
from ngs_plumbing.dna import PackedDNABytes
from ngs_plumbing._libdna import slice_frombit2bytes, bit2_frombytes, bit2_frombytearray

# Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    xrange = range

def kmerbytearray_frombytes_iter(unpacked, K, step=1):
    v = bytearray(unpacked)
    for i in xrange(0, len(unpacked)-K+1, step):
        yield v[i:(i+K)]

def kmerbit2_frombytes_iter(unpacked, K, step=1):
    """ Return an iterator of bit2-packed segments from unpacked DNA """
    v = bytearray(unpacked)
    for i in xrange(0, len(unpacked)-K+1, step):
        yield bit2_frombytearray(v[i:(i+K)])

def kmerbytes_frombit2_iter(packed, K, step=1):
    """
    Return an iterator sliding a window of length K bases
    sliding over a sequence of 2-bit packed DNA

    - packed: a bytes of bit-packed DNA
    - K: size of k-mers
    - step: iterating step for the sliding window
    """
    #assert(isinstance(packed, PackedDNABytes))
    for i in xrange(0, len(packed)*4-K+1, step):
        res = slice_frombit2bytes(packed, i, i+K) 
        yield res


def kmerbit2_frombit2_iter(packed, K, step=1):
    """
    Return an iterator sliding a window of length K bases
    sliding over a sequence of 2-bit packed DNA
    """
    #assert(isinstance(packed, PackedDNABytes))
    for i in xrange(0, len(packed)*4-K+1, step):
        #print('slice %i:%i from %i' %(i, i+K, len(packed)))
        res = slice_frombit2bytes(packed, i, i+K)
        #FIXME: lousy hack - the right function is still missing from the API
        res = bit2_frombytes(res)
        yield res

def poskmerbit2_frombit2_iter(packed, K, step=1):
    """
    Return an iterator sliding a window of length K bases
    sliding over a sequence of 2-bit packed DNA
    """
    #assert(isinstance(packed, PackedDNABytes))
    for i in xrange(0, len(packed)*4-K+1, step):
        #print('slice %i:%i from %i' %(i, i+K, len(packed)))
        res = slice_frombit2bytes(packed, i, i+K)
        #FIXME: lousy hack - the right function is still missing from the API
        res = bit2_frombytes(res)
        yield (i, res)

            
    
