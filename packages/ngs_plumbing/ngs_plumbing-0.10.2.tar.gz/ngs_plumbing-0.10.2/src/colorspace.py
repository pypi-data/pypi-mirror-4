from __future__ import absolute_import
import os, sys
import string
import itertools, warnings
import ngs_plumbing.fastq
from ngs_plumbing.fastq import write_fastq
from ngs_plumbing.fastq import read_fastq
from ngs_plumbing.fasta import write_fasta, write_qual


_DENCODE = string.maketrans('0123.', 'ATGCN')
_DDECODE = string.maketrans('ATGCNatgcn', '0123.0123.')


def dencode_seq(seq):
    return bytearray(seq)[1:].translate(_DENCODE)

def ddecode_seq(seq):
    return bytes(seq).translate(_DDECODE)
def ddecode_seq_T(seq):
    return b'T'+bytes(seq).translate(_DDECODE)
def ddecode_seq_G(seq):
    return b'G'+bytes(seq).translate(_DDECODE)

class FastqWriter(object):
    def __init__(self, fn, d):
        basename = fn[ : (fn.rfind('.'))]
        fn_seq = os.path.join(d, basename + '.FASTQ')
        if os.path.exists(fn_seq):
            sys.stderr.write('File %s already existing.\n' % fn_seq)
            sys.exit(1)
        self._buf = file(fn_seq, 'w')

    def write(self, entry, seq_proc = None, qual_proc = None):
        write_fastq(self._buf, entry, seq_proc = seq_proc, qual_proc = qual_proc)

    def close(self):
        self._buf.flush()
        self._buf.close()

    def flush(self):
        self._buf.flush()


class FastaqualWriter(object):
    def __init__(self, fn, d):
        basename = fn[ : (fn.rfind('.'))]
        fn_seq = os.path.join(d, basename + '.FASTA')
        fn_qual = os.path.join(d, basename + '.QUAL')
        if os.path.exists(fn_seq):
            sys.stderr.write('File %s already existing.\n' % fn_seq)
            sys.exit(1)
        if os.path.exists(fn_qual):
            sys.stderr.write('File %s already existing.\n' % fn_qual)
            sys.exit(1)
        self._buf_seq = file(fn_seq, 'w')        
        self._buf_qual = file(fn_qual, 'w')        

    def write(self, entry, seq_proc = None):
        write_fasta(self._buf_seq, entry, seq_proc = seq_proc)
        write_qual(self._buf_qual, entry, qual_proc = qual_proc)
        
    def close(self):
        self._buf_seq.flush()
        self._buf_seq.close()
        self._buf_qual.flush()
        self._buf_qual.close()

    def flush(self):
        self._buf_seq.flush()
        self._buf_qual.flush()

def _entry_fromfastaqual(fn):
    # fn: filename for the FASTA
    basename = fn[ : (fs.rfind('.'))]

    fn_qual = basename + '.QUAL'

    seq_iter = fasta.read_fasta(stream_seq)
    qual_iter = fasta.read_fasta(stream_qual)

    Entry = ngs_plumbing.fastq.Entry

    for s, q in itertools.izip(seq_iter, qual_iter):
        if s.header != q.header:
            warnings.warn('Mismatch between FASTA and QUAL headers')
        yield Entry(s.header, s.sequence, q.sequence)
    
def exec_code():
    import ngs_plumbing
    import io
    import argparse

    parser = argparse.ArgumentParser(
        description = 'Encode / decode files from color to base space.')
    parser.add_argument('paths', metavar='FILES', nargs='+',
                        help='Files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='directory in which resulting files should be put')
    parser.add_argument('-f', '--input-format-style',
                        dest = 'input_format',
                        choices = ('FASTA', 'FASTQ'),
                        help = "Style of the format for the input.")
    parser.add_argument('-F', '--output-format-style',
                        dest = 'output_format',
                        choices = ('FASTA', 'FASTQ'),
                        help = "Style of the format to output to.")
    parser.add_argument('-c', '--code-operation',
                        dest = 'code_operation',
                        choices = ('dencode', 'ddecode'),
                        help = 'double-encode (from color space to base space) or double-decode (the other way around)')
    parser.add_argument('-l', '--leading-base',
                        dest = 'leading_base',
                        choices = ('T', 'G'),
                        help = 'Leading base when going back to color space (T for F3, G for F5)')
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()
    
    for f in options.paths:
        if not os.path.exists(f):
            print('Error: Path "%s" does not exist' %f)
            sys.exit(1)
            
    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            print('Error: destination directory already existing (but not as a directory')
            sys.exit(1)
    else:
        warnings.warn('Warning: destination directory not existing; creating it.')
        os.mkdir(options.dest_dir)
        
    if options.input_format == 'FASTA':
        entry_iter = _entry_fromfastaqual
    else:
        entry_iter = read_fastq

    if options.code_operation == 'dencode':
        seq_proc = dencode_seq
        qual_proc = None
    else:
        if options.leading_base == 'T':
            seq_proc = ddecode_seq_T
        elif options.leading_base == 'G':
            seq_proc = ddecode_seq_G
        else:
            seq_proc = ddecode_seq
        qual_proc = None

    for f in options.paths:
        fn = os.path.basename(f)
        if options.output_format == 'FASTA':
            import ngs_plumbing.fasta
            entry_writer = FastaqualWriter(fn, options.dest_dir)
        else:
            import ngs_plumbing.fastq
            entry_writer = FastqWriter(fn, options.dest_dir)

        stream = io.OpenWrapper(f, 'r')
        progress = 0
        chunk = 10000
        for entry in entry_iter(stream):
            if (progress % chunk) == 0:
                sys.stdout.write('\r%s: %s entries processed.' % (f, '{:,}'.format(progress)))
                sys.stdout.flush()
            try:
                entry_writer.write(entry, seq_proc = seq_proc, qual_proc = qual_proc)
            except Exception as e:
                entry_writer.flush()
                sys.stdout.write('\r%s: %s entries processed.\n' % (f, '{:,}'.format(progress)))
                sys.stderr.write(str(e))
                sys.stdout.write('\n')
                sys.stderr.write(str(entry))
                sys.stdout.write('\n')
                sys.stdout.flush()
            progress += 1
        sys.stdout.write('\r%s: %s entries processed.\n' % (f, '{:,}'.format(progress)))
        sys.stdout.flush()
                
        stream.close()
        entry_writer.close()
