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
There are plenty of FASTA readers. This one is rather simple
but lets us limit dependencies on third-party packages
"""
import struct, io
from ngs_plumbing.dna import PackedDNABytes
from ngs_plumbing._libdna import byte_frombit2bytes

from collections import namedtuple

Entry = namedtuple('Entry', 'header sequence')

class FastaError(ValueError):
    pass

#Compatibility with Python 3
import sys
if sys.version_info[0] > 2:
    import _io
    file = _io.TextIOWrapper

class FastaFile(file):
    """ FASTA file.
    The default iterator will go through the entries in the file (not the rows). 
    """

    def __iter__(self):
        wrap = io.OpenWrapper(self.fileno(), closefd = False)
        return read_fasta(wrap)

class FastabError(ValueError):
    pass

class FastabFile(file):
    """ FASTAB file.
    The default iterator will go through the entries in the file (not the rows).
    """
    def __iter__(self):
        wrap = io.OpenWrapper(self.fileno(), mode = 'rb', closefd = False)
        return read_fastab(wrap)

    @staticmethod
    def from_fastafile(fin, fout):
        """ Create a FASTAB file from a FASTA file.

        - fin: FASTA input file
        
        - fout: FASTAB output file
        """

        if not isinstance(fin, file):
            close_fin = True
            fin = fasta.FastaFile(fn_in)
        else:
            close_fin = False

        if not isinstance(fout, io.BufferedIOBase):
            if isinstance(fout, str):
                fout = io.OpenWrapper(fout, 'wb', long(4E6))
                close_fout = True
            else:
                raise ValueError('fout should be an IO buffer or a string.')
        for i, entry in enumerate(fin):
            tofastab(entry, fout)

        if close_fin:
            fin.close()
            
        fout.flush()
        if close_fout:
            fout.close()


def read_fasta(stream):
    """ Return an iterator over FASTA entries in a stream
    (an iterable) """

    header = None
    sequence = list()
    for row in stream:
        row = row.rstrip()
        if row.startswith(b'>'):
            # header
            if header is not None:
                sequence = b''.join(sequence)
                yield Entry(header, sequence)
            #
            header = row
            sequence = list()
        else:
            # append sequence
            sequence.append(row)
    sequence = b''.join(sequence)
    if header is None:
        raise FastaError('Missing FASTA header.')
    yield Entry(header, sequence)

def write_fasta(buf, entry, seq_proc = None):
    if entry.header != b'>':
        buf.write(b'> ')
    buf.write(entry.header)
    buf.write(b'\n')
    if seq_proc is None:
        buf.write(entry.sequence)
    else:
        buf.write(seq_proc(entry.sequence))
    buf.write(b'\n')

def write_qual(buf, entry, qual_proc = None):
    buf.write(b'> ')
    buf.write(entry.header)
    buf.write(b'\n')
    if qual_proc is None:
        buf.write(entry.quality)
    else:
        buf.write(qual_proc(entry.sequence))

EntryBin = namedtuple('Entry', 'header sequence bits')

def tofastab(fasta, stream, force_upper = True):
    """
    Save a FASTA 'Entry' into a binary stream.
    'force_upper' will force the DNA sequence to be upper-case when True (which is the default).

    The format is as follows:

    - size of the sequence: 8 bytes as an unsigned long long

    - size of the header: 2 bytes as an unsigned short

    - a number of bytes equal to the size of the header (see above)

    - 2-bit encoded DNA

    """

    header = bytes(fasta.header)

    if len(header) > 256**2:
        raise ValueError("Header is too long")

    if force_upper:
        sequence = bytes(fasta.sequence.upper())
    else:
        sequence = bytes(fasta.sequence)
    vec = PackedDNABytes(sequence)

    stream.write(struct.pack('<QH%is%ss' %(len(header), str(len(vec))),
                             len(vec), len(header), header, vec))
    #print("%i %i" % (len(vec), len(header)))


def read_fastab(stream, maxhead = 500, maxseq = 100000):
    """
    Load a FASTA 'EntryBin' from a binary stream.

    - maxhead: maximum number of bytes for the head. If the header
    goes beyond it, an exception FastabError is raised.
    - maxseq: maximum number of bytes for the head. If the header
    goes beyond it, an exception FastabError is raised.

    The format is as follows:

    - size of the sequence: 8 bytes as an unsigned long long

    - size of the header: 2 bytes as an unsigned short

    - a number of bytes equal to the size of the header (see above)

    - 2-bit encoded DNA

    """

    while True:
        raw = stream.read(8+2)
        if len(raw) < 8+2:
            if len(raw) == 0:
                raise StopIteration()
            else:
                raise FastaError("Truncated FASTAB file (incomplete entry descriptor).")
        nseq, nhead = struct.unpack('<QH', raw)
        if nhead > maxhead:
            raise FastabError("Header size over the limit (%i > %i)" % (nhead, maxhead))
        if nseq > maxseq:
            raise FastabError("Sequence size over the limit (%i > %i)" % (nseq, maxseq))

        raw = stream.read(nhead)
        
        if len(raw) < nhead:
            raise FastaError("Truncated FASTAB file (incomplete entry descriptor).")
        header = struct.unpack('%is' %nhead, raw)[0]
        raw = stream.read(nseq)

        if len(raw) < (nseq):
            raise FastaError("Truncated FASTAB file (incomplete sequence).")
        vec = struct.unpack('%ss' %str(nseq), raw)[0]

        yield EntryBin(header, vec, int(2))


def skip_fastab(stream, skip=0):
    """
    """

    for i in xrange(skip):
        raw = stream.read(8+2)
        if len(raw) < 8+2:
            if len(raw) == 0:
                raise StopIteration()
            else:
                raise FastaError("Truncated FASTAB file (incomplete entry descriptor).")
        nseq, nhead = struct.unpack('<QH', raw)
        raw = stream.read(nhead)
        if len(raw) < nhead:
            raise FastaError("Truncated FASTAB file (incomplete entry descriptor).")
        raw = stream.read(nseq)
        if len(raw) < (nseq):
            raise FastaError("Truncated FASTAB file (incomplete sequence).")

        

