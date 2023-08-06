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

from collections import namedtuple, OrderedDict

import io, array, math
import os, re
import sys
import h5py
import numpy
logical_and = numpy.logical_and
right_shift = numpy.right_shift
bitwise_and = numpy.bitwise_and

from ngs_plumbing.dnaqual import DnaQual
from ngs_plumbing._libxsq import colourqual_frombuffer, basequal_frombuffer, bytearray_phredtoascii, bytearray_addint

ColourQual = namedtuple('ColourQual', 'colour qual')

_ACGT = bytes('ACGT')
FRAGMENT_NAMES = ('F3', 'F5-DNA', 'F5-RNA', 'F5-BC', 'F5-2', 'R3', 'R5')
# F3: Forward strand. starts with a T
# F5/R3: Used to prime both F5-BC read and R3 or barcode. starts with a G
#
FRAGMENT_START = {'F3': b'T',
                  'F5-DNA': b'G',
                  'F5-RNA': b'G', # to be verified
                  'F5-BC': None,
                  'F5-2': None,
                  'R3': b'G',
                  'R5': None # I don't know
}

_pack_installdir = os.path.abspath(os.path.dirname(__file__))
testdata_dir = os.path.join(_pack_installdir, 'data')

def list_xsq(path):
    """ list XSQ (.xsq) files in a given directory """
    for path,dirs,files in os.walk(path):
        for f in files:
            if f.endswith('.xsq'):
                yield os.path.join(path,f)
                       
class FragmentError(KeyError):
    pass
class InvalidXSQError(ValueError):
    pass

        
class XSQFile(h5py.File):
    """
    Sequencing data from a run
    """

    @staticmethod
    def _valid_library_name(name, unclassified = False, unassigned = False):
        invalid_names = ('RunMetadata', 'Indexing')
        if name in invalid_names:
            return False
        if not unclassified and name == 'Unclassified':
            return False
        if not unassigned and name.startswith('Unassigned'):
            return False
        return True

    def _library_names_get(self):
        """ Names of the libraries in the file """
        
        return tuple(x for x in self.keys() if XSQFile._valid_library_name(x))
    library_names = property(_library_names_get, None, None,
                             """ Names of the libraries in the file (Ignoring the unclassifed and unassigned groups)""")

    def library(self, name, unclassified = False, unassigned = False):
        if not XSQFile._valid_library_name(name, unclassified = unclassified,
                                           unassigned = unassigned):
            raise ValueError("Invalid library name.")
        return XSQLibrary(self[name].id)

    def iter_lib(self):
        for lb_n in self.library_names:
            yield self.library(lb_n)

    def _run_metadata_get(self):
        """ Metadata about the run """
        if 'RunMetadata' not in self:
            raise KeyError("The file does not have meta-data.")
        res = self['RunMetadata']
        return XSQRunMetadata(res.id)

    run_metadata = property(_run_metadata_get, None, None,
                            """ Metadata about the run """)


class XSQLibrary(h5py._hl.group.Group):
    """
    Sequenced library in an XSQ file.
    """
    def _name_get(self):
        return self.attrs[u'LibraryName'][0]
    name = property(_name_get, None, None, 
                    'Library Name')

    def fragments(self):
        """ Fragments sequenced in this library """
        frags = set()
        for tile_n in self.keys():
            tile = super(XSQLibrary, self).__getitem__(tile_n)
            for k in tile.keys():
                if k in FRAGMENT_NAMES:
                    frags.add(k)
        return frags

    def readcount(self):
        """ Return the number of reads for the library
        """
        count = long(0)
        for number in self.keys():
            tmp = super(XSQLibrary, self).__getitem__(number)
            #FIXME: hack !
            for k in tmp.attrs.keys():
                if k.endswith('Count'):
                    ct = tmp.attrs[k]
                    if len(ct) != 1:
                        raise ValueError("Length of field expected to be 1.")
                    count += ct[0]
                    break
        return count

    def _readvalues(self, fragment, what):
        return _read_values(self, fragment, what)

    def iter_reads(self, fragment, what = 'BaseCallQV'):
        """ Iterator over the fragment 'fragment' for the data 'what' """
        if fragment not in FRAGMENT_NAMES:
            raise ValueError('Fragment "%s" not in %s' %(fragment, FRAGMENT_NAMES))
        for number in self.keys():
            num = super(XSQLibrary, self).__getitem__(number)
            if fragment not in num:
                raise FragmentError('No fragment "%s" in "%s".' %(fragment, number))
            frg = num[fragment]
            if what not in frg:
                raise FragmentError('No "%s" for fragment "%s" in "%s" (possible value(s): "%s").' %(what, fragment, number, '", "'.join(frg.keys())))
            ds = frg[what].value
            a = numpy.empty(shape = ds.shape, dtype=ds.dtype)
            a[:] = ds[:]
            for read in a:
                yield read

    def iter_colourqual(self, fragment):
        """ 
        Iterator over the sequence reads for the fragment 'fragment'.
        Each iteration returns a named tuple of length 2:

        - colour: the sequence of colours

        - qual: the quality for the sequence

        For a naive colour-to-sequence translation,
        the first base for the fragment
        should be used. It is in the dict FRAGMENT_START.
        """
        for read in self.iter_reads(fragment, what='ColorCallQV'):
            colour, qual = colourqual_frombuffer(read)
            yield ColourQual(colour, qual)


    def iter_dnaqual(self, fragment, numbase):
        """
        Iterator over the sequence reads for the fragment 'fragment'.
        Each iteration returns a tuple of length 2:

        - the sequence

        - the quality

        """
        #FIXME: automagic "numbase"
        return iter_fastq_reads(self, fragment, numbase)

def _read_values(group, fragment, what):
    """ Iterator over the fragment 'fragment' for the data 'what'
    """
    assert(fragment in FRAGMENT_NAMES)
    for number in group.keys():
        num = group[number]
        if fragment not in num:
            raise FragmentError('No such fragment "%s"' %fragment)
        ds = num[fragment][what].value
        yield ds

def tile_valuearray(tile, fragment, what):
    """ Get the array of values for a tile. """
    if fragment not in tile:
        raise FragmentError('No such fragment "%s"' %fragment)
    ds = tile[fragment][what].value
    a = numpy.empty(shape = ds.shape, dtype = ds.dtype)
        #FIXME: force copy into memory, presumably. Is this is always wise, or even true ?
    a[:] = ds[:]
    return a

def iter_valuearrays(group, fragment, what='BaseCallQV'):
    """ Iterator over the fragment 'fragment' for the data 'what'
    """
    assert(fragment in FRAGMENT_NAMES)
    for tile_n in group.keys():
        tile = group[tile_n]
        a = tile_valuearray(tile, fragment, what)
        tile_n = bytes(tile_n)
        yield (tile_n, a)

def iter_reads(group, fragment, what='BaseCallQV'):
    """ Iterator over the fragment 'fragment' for the data 'what'
    """
    assert(fragment in FRAGMENT_NAMES)
    for number in group.keys():
        num = group[number]
        if fragment not in num:
            raise FragmentError('No such fragment "%s"' %fragment)
        ds = num[fragment][what].value
        a = numpy.empty(shape = ds.shape, dtype = ds.dtype)
        a[:] = ds[:]
        for read in a:
            yield read


def iter_fastq_reads(group, fragment, numbase):
    """
    Iterator over reads in base space

    - group: HDF5 group

    - fragment: fragment name

    - numbase: number of bases (read length)
    """
    for tile_n, a in iter_valuearrays(group, fragment, what='BaseCallQV'):
        for row_i in xrange(a.shape[0]): 
            dna, qual = basequal_frombuffer(a[row_i])
            qual = bytearray_phredtoascii(qual)
            yield DnaQual(dna, qual)

def iter_csfasta_reads(group, fragment, numbase):
    """
    Iterator over reads in base space

    - group: HDF5 group

    - fragment: fragment name

    - numbase: number of bases (read length)
    """
    for tile_n, a in iter_valuearrays(group, fragment, what='ColorCallQV'):
        for row_i in xrange(a.shape[0]):
            colour, qual = colourqual_frombuffer(a[row_i])
            yield ColourQual(colour, qual)


class XSQRunMetadata(h5py._hl.group.Group):
    """
    Details about a sequencing run in an XSQ file.

    A run can have several libraries sequenced at once.
    """

    def _getattr(self, attr):
        try:
            return self.attrs[attr]
        except KeyError:
            return [None, ]

    def _tagdetails_get(self):
        return 

    tagdetails = property(lambda self: XSQTagDetailsList(self[u'TagDetails']).tags, 
                          None, None,
                          'Tag details')
    lanenumber = property(lambda self: self._getattr(u'LaneNumber')[0], None, None,
                          'Lane number')
    librarytype = property(lambda self: self._getattr(u'LibraryType')[0], None, None,
                           'Library type')
    hdfversion = property(lambda self: self._getattr(u'HDFVersion')[0], None, None,
                          'Version of the HDF5 file')
    fileversion = property(lambda self: self._getattr(u'FileVersion')[0], None, None,
                           'Version of the XSQ file')
    sequencingsamplename = property(lambda self: self._getattr(u'SequencingSampleName')[0], 
                                    None, None, 'Sequencing sample name')
    sequencingsampledescription = property(lambda self: self._getattr(u'SequencingSampleDescription')[0], None, None,
                                           'Sequencing sample description')
    runname = property(lambda self: self._getattr(u'RunName')[0], None, None,
                       'Name for the run')


class XSQInfo(OrderedDict):
    __ats = (('tagdetails', lambda x: ', '.join(x.tags)), 
             ('lanenumber', lambda x: x),
             ('hdfversion', lambda x: x),
             ('fileversion',lambda x: x),
             ('sequencingsamplename', lambda x: x),
             ('sequencingsampledescription', lambda x: x),
             ('runname',lambda x: x))

    def __init__(self):
        raise Error('')
    @classmethod
    def fromxsqfile_toordict(cls, xsqfile):
        assert(isinstance(xsqfile, XSQFile))
        res = OrderedDict()
        try:
            mtd = xsqfile.run_metadata
        except KeyError as ke:
            mtd = None
 
        for at, fun in cls.__ats:
            field = getattr(XSQRunMetadata, at).__doc__
            if mtd is None:
                res[field] = 'Missing'
                continue
            try:
                tmp = getattr(mtd, at)
                value = str(fun(tmp))
            except AttributeError:
                value = 'Error'
            res[field] = value
        return res
        
class XSQTagDetailsList(h5py._hl.group.Group):
    """
    """
    tags = property(lambda x: x.keys(), None, None,
                    'Sequencing tags. F3 is typically the forward strand for single read sequencing.')
    
    
class XSQTagDetails(h5py._hl.group.Group):
    def _numbasecalls_get(self):
        res = self.attrs['NumBaseCalls']
        if len(res) != 1:
            raise InvalidXSQError("Invalid XSQ file. NumBaseCalls should be of length 1.")
        return res
    numbasecalls = property(_numbasecalls_get, None, None,
                            'Number of bases called for the tag ("read length" for the tag)')
    def _isbasepresent_get(self):
        res = self.attrs['IsBasePresent']
        if len(res) != 1:
            raise InvalidXSQError("Invalid XSQ file. IsBasePresent should be of length 1.")
        if res == 1:
            return True
        elif res == 0:
            return False
        else:
            raise InvalidXSQError("Invalid XSQ file. IsBasePresent should 0 or 1 to represent a boolean.")
    isbasepresent = property(_isbasepresent_get, None, None,
                             'Is base information present ? When running a SOLiD, True likely means that ECC was run.')
    

def seqid_template(f, flowcell, tile):
    try:
        serial = f.run_metadata.attrs['InstrumentSerial'][0]
    except (AttributeError, KeyError) as ke:
        serial = 'UnknownSerial'
        
    seq_id = '@%s:%s:%s' %(serial, flowcell, tile) + ':%i:%i#0'
    return seq_id

def seqid_template_csfasta(flowcell, fragment):
    seq_id = '> %s' %(flowcell) + '_%i_%i_' + '%s' %fragment        
    return seq_id

def _progress_bar_iter(iterator, size = 20, out = sys.stdout, suffix = ''):
    n = len(iterator)
    ms = long(math.ceil(1.0 * n / size))
    for j, i in enumerate(iterator):
        if j % ms == 0:
            if os.isatty(out.fileno()):
                bar = '\r|%s%s|%s' %('\xe2\x96\x88' * min(size, (j / ms)), ' ' * (size - (j / ms)), suffix)
                out.write(bar)
                out.flush()
        yield i

def make_fastq(lib, fragment, buf, f, flowcell, numbase = None, 
               progress_mark = 50000, out=sys.stdout):
    n_count = long(0)
    n_perfect = long(0)
    read_count = long(0)
    inc = long(1)

    for tile_i, (tile_n, a) in enumerate(iter_valuearrays(lib, fragment, what='BaseCallQV')):
        if numbase is None:
            numbase = a.shape[1]

        seq_id = seqid_template(f, flowcell, tile_n)
        xyloc = lib[tile_n]['Fragments'][u'yxLocation'][:]

        read_count += xyloc.shape[0]
                
        ms = long(math.ceil((tile_i+1) * 1.0 * 20 / len(lib)))
        out.write('\r|%s%s|tile %i' %('\xe2\x96\x88' * min(20, ms), 
                                      ' ' * (20 - ms), tile_i+1))
        out.flush()

        for row_i in xrange(a.shape[0]):
            dna, qual = basequal_frombuffer(a[row_i])
            qual = bytearray_phredtoascii(qual)
            #yield DnaQual(dna, qual)

            n_count_read = dna.count(b'N')
            n_count += n_count_read
            if n_count_read == 0:
                n_perfect += inc
            dna_b = bytes(dna)
            x,y = xyloc[row_i]
            buf.writelines((seq_id %(x,y), '\n', dna_b, '\n+\n', qual, '\n'))

        #numbase = None

    if os.isatty(out.fileno()):
        out.write('\n')
    out.write("%i reads. ((%.3fGb, %.3f%% perfect , %.5f%% Ns)\n" %(read_count, 
                                                                    read_count*numbase / 1E9,
                                                                    100.0*n_perfect/read_count,  
                                                                    n_count * 100.0 / (read_count * len(dna))))
    out.flush()


def _xsqvalues_to_csfasta(xsqvalues, xyloc, buf_cs, buf_qual, seq_id, prefix):
    if xsqvalues.shape[1] == 0:
        sys.stderr.write('Reads of length 0 (!?)\n')
        sys.stderr.flush()
        return
    bases_i = range(xsqvalues.shape[1]-1)
    for row_i in xrange(xsqvalues.shape[0]): 
        seq, qual = colourqual_frombuffer(xsqvalues[row_i])
        x,y = xyloc[row_i]
        this_seq_id = seq_id % (x,y)
        buf_cs.writelines((this_seq_id, '\n', prefix, seq, '\n'))
        buf_qual.writelines((this_seq_id, '\n'))
        for q_i in bases_i:
            buf_qual.write('%i ' % qual[q_i])
        buf_qual.writelines((str(qual[len(bases_i)]), '\n'))


def make_csfasta(lib, fragment, buf_cs, buf_qual, f, flowcell, 
                 numbase = None, progress_mark = 50000, out=sys.stdout):
    read_count = long(0)
    inc = long(1)

    for tile_i, (tile_n, a) in enumerate(iter_valuearrays(lib, fragment, 
                                                          what='ColorCallQV')):
        if numbase is None:
            numbase = a.shape[1]
        seq_id = seqid_template_csfasta(flowcell, fragment)
        xyloc = lib[tile_n]['Fragments'][u'yxLocation'][:]
        read_count += xyloc.shape[0]
        prefix = FRAGMENT_START[fragment]

        ms = long(math.ceil((tile_i + 1) * 1.0 * 20 / len(lib)))
        out.write('\r|%s%s|tile %i' %('\xe2\x96\x88' * min(20, ms), 
                                      ' ' * (20 - ms), tile_i + 1))
        out.flush()

        _xsqvalues_to_csfasta(a, xyloc, buf_cs, buf_qual, seq_id, prefix)

    if os.isatty(out.fileno()):
        out.write('\n')
    out.write("%i reads (%.3fGb).\n" %(read_count, read_count*numbase / 1E9))
    out.flush()

def _xsqvalues_to_csfastq(xsqvalues, xyloc, buf, seq_id, prefix):
    for row_i in xrange(xsqvalues.shape[0]):
        seq, qual = colourqual_frombuffer(xsqvalues[row_i])
        seq = bytearray_addint(seq, 48)
        qual = bytearray_phredtoascii(qual)
        x,y = xyloc[row_i]
        buf.writelines((seq_id %(x,y), '\n', prefix, seq, '\n+\n', qual, '\n'))
        
def make_csfastq(lib, fragment, buf, f, flowcell, 
                 numbase = None, progress_mark = 50000, out=sys.stdout):
    read_count = long(0)
    inc = long(1)

    for tile_i, (tile_n, a) in enumerate(iter_valuearrays(lib, fragment, 
                                                          what='ColorCallQV')):
        if numbase is None:
            numbase = a.shape[1]
        seq_id = seqid_template(f, flowcell, tile_n)
        xyloc = lib[tile_n]['Fragments'][u'yxLocation'][:]
        read_count += xyloc.shape[0]
        prefix = FRAGMENT_START[fragment]

        ms = long(math.ceil((tile_i+1) * 1.0 * 20 / len(lib)))
        out.write('\r|%s%s|tile %i' %('\xe2\x96\x88' * min(20, ms), 
                                      ' ' * (20 - ms), tile_i + 1))
        out.flush()

        _xsqvalues_to_csfastq(a, xyloc, buf, seq_id, prefix)

    if os.isatty(out.fileno()):
        out.write('\n')
    out.write("%i reads (%.3fGb).\n" %(read_count, read_count*numbase / 1E9))
    out.flush()


def automagic_fastq(filename, path_out = '.', fragment = None, 
                    buf_size = long(2E6), extension = 'fq', out = sys.stdout,
                    cs = False,
                    want_unassigned = False):
    """ Extract sequence-space data into a FASTAQ file """

    if cs:
        maker = make_csfastq
    else:
        maker = make_fastq

    f = XSQFile(filename, 'r')
    p = re.compile('.+_([0-9]+)\.xsq')

    if want_unassigned:
        library_names = tuple(x for x in f.keys() if f._valid_library_name(x, unassigned = want_unassigned))
    else:
        library_names = f.library_names

    for i, lib_name in enumerate(library_names):
        out.write('%s (%i / %i)\n' %(lib_name, i+1, len(library_names)))
        out.flush()
        lib = f.library(lib_name, unassigned = want_unassigned)
        if fragment is None:
            fragment_list = tuple(lib.fragments())
        else:
            fragment_list = (fragment, )
        m = p.match(filename)
        flowcell = m.groups()[0]
        for frg in fragment_list:
            out.write('Fragment %s\n' %frg)
            out.flush()

            out_f = io.FileIO(os.path.join(path_out, "%s_%s.%s" %(lib_name, frg, extension)), "w")
            buf = io.BufferedWriter(out_f, buf_size)

            maker(lib, frg, buf, f, flowcell)                
            buf.flush()
            out_f.close()    
    f.close()

def automagic_csfasta(filename, path_out = '.', fragment = None, 
                      buf_size = long(2E6), out = sys.stdout,
                      want_unassigned = False):
    """ Extract sequence-space data into a FASTAQ file """

    assert((fragment is None) or (fragment in FRAGMENT_NAMES))

    f = XSQFile(filename, 'r')
    p = re.compile('.+_([0-9]+)\.xsq')

    if want_unassigned:
        library_names = tuple(x for x in f.keys() if f._valid_library_name(x, unassigned = want_unassigned))
    else:
        library_names = f.library_names
    
    for i, lib_name in enumerate(library_names):
        out.write('%s (%i / %i)\n' %(lib_name, i+1, len(library_names)))
        out.flush()
        lib = f.library(lib_name, unassigned = want_unassigned)
        if fragment is None:
            fragment_list = tuple(lib.fragments())
        else:
            fragment_list = (fragment, )
        m = p.match(filename)
        flowcell = m.groups()[0]

        for frg in fragment_list:
            out.write('Fragment %s\n' %frg)
            out.flush()
            out_cs = io.FileIO(os.path.join(path_out, "%s_%s.%s" %(lib_name, frg, 'csfasta')), "w")
            buf_cs = io.BufferedWriter(out_cs, buf_size)

            out_qual = io.FileIO(os.path.join(path_out, "%s_%s.%s" %(lib_name, frg, 'qual')), "w")
            buf_qual = io.BufferedWriter(out_qual, buf_size)

            #tagdetails = XSQTagDetails(lib.tagdetails.attrs[frg].id)
            #make_fastq(lib, fragment, tagdetails.numbasecalls, buf, seq_id)
            make_csfasta(lib, frg, buf_cs, buf_qual, f, flowcell)
            buf_cs.flush()
            out_cs.close()    
            buf_qual.flush()
            out_qual.close()

    f.close()

import random
def fastqual(xsqlib, fragment, what, sample = 0.05):
    """ Perform a FASTQUAL-type QC.
    - xsqlibn: the XSQ library
    - fragment: name of the frament
    - what: colour-space or base-space data
    - sample: proportion to sample in order to perform the QC; 1 is 100% """

    if sample <= 0 or sample > 1:
        raise ValueError("sample must be a number > 0 and <= 1")

    # determine the indices for the reads sampled
    nfragments = xsqlib.readcount()
    nsample = long(sample * nfragments)
    reads_idx = [None, ] * nsample
    for i in xrange(nsample):
        reads_idx[i] = random.randint(0, nfragments-1)
    reads_idx.sort()
    #reads_idx.reverse()

    # fetch the reads
    inc = int(1)
    #FIXME: read length hardcoded - fetch it from the XSQ
    readlength = 75
    maxval = 64
    vals = [ [None, ] * nsample for bp in range(readlength) ]
    s_i = reads_idx.pop()
    read_i_offset = 0
    read_m_iter = xsqlib._readvalues(fragment, what)
    read_m = read_m_iter.next()
    for read_i, read_idx in enumerate(reads_idx):
        while read_idx >= read_m.shape[0] + read_i_offset:
            read_i_offset += read_m.shape[0]
            read_m = read_m_iter.next()

        read = read_m[read_idx - read_i_offset, :]
        colour, qual = colourqual_frombuffer(read)
        for q_i, q in enumerate(qual):
            vals[q_i][read_i] = q
    for x in vals:
        x.sort()
    BoxplotInfo = namedtuple("BoxplotInfo", "p10 p25 p50 p75 p90")
    
    return tuple((BoxplotInfo(*(x[int(len(x) * p)] \
                                    for p in (.1, .25, .5, .75, .9))) \
                      for x in vals))


from ngs_plumbing import report
import csv, json
import jinja2

def make_htmlreport(xsqfile, directory = '.', verbose = True,
                    sample_percent = 0.05, data_type = 'json'):
    assert(isinstance(xsqfile, XSQFile))
    assert(data_type in ('json', 'csv'))
    pl = jinja2.PackageLoader('ngs_plumbing', 
                              package_path = os.path.join('data', 'html', 
                                                          'templates'));
    j_env = jinja2.Environment(loader = pl)
    template = j_env.get_template('xsqlibreport.html', 
                                  parent = os.path.join(_pack_installdir, 'data', 'html', 'templates'))
    # get information about the XSQ file
    xsqinfo = XSQInfo.fromxsqfile_toordict(xsqfile)
    LibReport = namedtuple("LibReport", 
                           "name lib_i readcount fragments")
    FragmentReport = namedtuple("FragmentReport",
                                "name varname data_fn")
    libs = list()
    for lib_i, lib in enumerate(xsqfile.iter_lib()):
        if verbose:
            sys.stdout.write('Processing library: %s.\n' % lib.name)
            sys.stdout.flush()
        frags = list()
        for fragment in lib.fragments():
            frg_varname = fragment.replace('-', '')
            #FIXME: only consider colour space for now
            fq = fastqual(lib, fragment, 'ColorCallQV', sample = sample_percent)
            # build the CSV file with quality
            data_fn = os.path.join(directory, 
                                  'fastqual_%s_%s_%i.%s' % (lib.name, frg_varname, lib_i, data_type))
            if verbose:
                sys.stdout.write('Creating file %s...' % data_fn)
            f = file(data_fn, mode = 'w')
            if data_type == 'csv':
                csv_w = csv.writer(f)
                for row in report.fastqual_tocsv_iter(fq):
                    csv_w.writerow(row)
            else:
                # json
                tmp = report.fastqual_tojson(fq)
                f.write('dataf_%i_%s = ' % (lib_i, frg_varname) )
                f.write(tmp)
                f.write(';')
            f.close()
            if verbose:
                sys.stdout.write('done.\n')
            frags.append(FragmentReport(fragment, frg_varname, os.path.relpath(data_fn, start = directory)))
        libs.append(LibReport(lib.name, lib_i, 
                              lib.readcount(), frags))
            
    # render the HTML
    rd = template.render(**{
            'basequal_max': 33,
            'data_type': data_type,
            'filename': os.path.basename(xsqfile.filename),
            'xsqinfo': tuple(xsqinfo.iteritems()),
            'libs': libs,
            'sample_percent': sample_percent})

    html_fn = os.path.join(directory, 
                           'fastqual_%s.html' % (os.path.basename(xsqfile.filename)))
    if verbose:
        sys.stdout.write('Creating file %s...' % html_fn)
    f = file(html_fn, mode = 'w')
    f.writelines(rd)            
    f.close()
    if verbose:
        sys.stdout.write('done.\n')
    # copy the javascript
    js_fn = os.path.join(_pack_installdir, 'data', 'html', 'readqual.js')
    jscp_fn = os.path.join(directory, 'readqual.js')
    if verbose:
        sys.stdout.write('Copying file %s...' % jscp_fn)
    f = file(js_fn, mode = 'r')
    f_cp = file(jscp_fn, mode = 'w')
    f_cp.writelines(row for row in f)
    f.close()
    f_cp.close()
    if verbose:
        sys.stdout.write('done.\n')

if __name__ == '__main__':
    pass
