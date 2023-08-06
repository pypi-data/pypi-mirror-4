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
Utilities around strings
"""

from random import randint
from io import IOBase

# Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    long = int
    xrange = range
    def randomstring(size, alphabet):
        """ Return a random string of length 'size', 
        using the given 'alphabet' of possible letters."""
        assert(isinstance(size, long) or isinstance(size, int))
        assert(isinstance(alphabet, bytes))
        # make a genome
        string = bytearray(size)
        for i in range(size):
            string[i] = alphabet[randint(0, 3)]
        return string
else:
    def randomstring(size, alphabet):
        """ Return a random string of length 'size', 
        using the given 'alphabet' of possible letters."""
        assert(isinstance(size, long) or isinstance(size, int))
        # make a genome
        string = b''.join(alphabet[randint(0, 3)] for x in xrange(size))
        return string

def randomfragments(string, n, size = 100):
    """ Make 'n' random, possibly overlapping, fragments
    of length 'fragment_len' from the given 'string'. """
    
    # make perfect reads
    assert(isinstance(string, str) or isinstance(string, bytes) or isinstance(string, bytearray))
    l = len(string)
    def f():
        y = randint(0, l - size)
        return string[y:(y + size)]
    reads = [f() for x in xrange(n)]
    return reads

def sequentialfragments(string, window_len, step = 1):
    """ Make sequential fragments from a string 'string', 
    moving by step 'step' between each fragment.
    """
    for i in xrange(0, len(string) - window_len + 1, step):
        chunk = string[i:(i + window_len)]
        yield chunk

def sequentialfragments_iter(stream, window_len, step = 1,
                             buffer_size = 2):
    """ Make an iterator of fragments from a stream 'stream', 
    moving by step 'step' between each fragment.

    Note: the fragments returned are memory views of a byte array, and
    as such as mutable. """

    buf = bytearray(window_len * buffer_size)
    buf_view = memoryview(buf)
    n = stream.readinto(buf_view[:window_len])
    #FIXME: check that n is ok
    yield buf_view[:window_len]
    bo = 0
    while True:
        if bo == (window_len * (buffer_size - 1)):
            buf_view[0:window_len] = buf_view[bo:(bo+window_len)]
            bo = 0
        else:
            bo = bo + step
        n = stream.readinto(buf_view[(window_len+bo):(window_len+bo+step)])
        if n < step:
            raise StopIteration("Could not read %i bytes from the stream." %n)
        yield buf_view[bo:(window_len + bo)]


def fragmentdict(string, window_len = 17, step = 1):
    """ For the given 'string', build a Python dict of keys
    corresponding to a sliding window of length 'window_len'
    and of incremental sliding step 'step'
    """
    # build the reference lookup
    d = dict()
    for i, chunk in enumerate(sequentialfragments(string, window_len, step = step)):
        if chunk not in d:
            d[chunk] = [i,]
        else:
            d[chunk].append(i)
    return d
