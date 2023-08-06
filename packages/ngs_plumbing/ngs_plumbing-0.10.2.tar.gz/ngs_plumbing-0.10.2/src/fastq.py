""" Yet another FASTQ parsing set of tools """

import io
from collections import namedtuple

Entry = namedtuple('Entry', 'header sequence quality')

class FastqError(ValueError):
    pass

class FastqFile(file):
    """ FASTQ file.
    The default iterator will go through the entries in the file (not the rows). 
    """
        
    def __iter__(self):
        wrap = io.OpenWrapper(self.fileno(), closefd = False)
        return read_fastq(wrap)

    def readcount(self):
        pos = self.tell()
        for i, entry in enumerate(read_fastq):
            pass
        return i+1

def read_fastq(stream):
    """ Return an iterator over FASTQ entries in a stream
    (an iterable) """

    sequence = list()
    quality = list()
    stream_iter = iter(stream)
    row = stream_iter.next()
    if row.startswith('@'):
        header = row.rstrip()
    else:
        raise FastqError('First row does not look like a Fastq header.')
    
    for row in stream_iter:
        row = row.rstrip()
        if header is not None:
            # sequence
            sequence.append(row)
            for row in stream_iter:
                row = row.rstrip()
                if row.startswith('+'):
                    if len(sequence) == 0:
                        raise FastqError('Empty Sequence')
                    break
                else:
                    sequence.append(row)
            # quality
            for row in stream_iter:
                row = row.rstrip()
                if row.startswith('@'):
                    if len(quality) == len(sequence):
                        break
                    else:
                        quality.append(row)
                elif row.startswith('+'):
                    if len(quality) >= len(sequence):
                        raise FastqError('Problem with the Fastq file '+\
                                         '(nearby header is %s)' % header)
                    else:
                        quality.append(row)
                else:
                    quality.append(row)
            sequence = ''.join(sequence)
            quality = ''.join(quality)
            yield Entry(header, sequence, quality)
            # reset for next round
            header = row
            sequence = list()
            quality = list()
    # do not miss the last entry
    sequence = ''.join(sequence)
    quality = ''.join(quality)
    if header is None:
        raise FastqError('Missing FASTQ header.')
    if row != header:
        yield Entry(header, sequence, quality)        

from ngs_plumbing import report
import csv
import jinja2

def make_htmlreport(fqfile, directory = '.', verbose = True,
                    sample_percent = 0.05):
    assert(isinstance(fqfile, FastqFile))
    pl = jinja2.PackageLoader('ngs_plumbing', 
                              package_path = os.path.join('data', 'html', 
                                                          'templates'));
    j_env = jinja2.Environment(loader = pl)
    template = j_env.get_template('fastqlibreport.html', 
                                  parent = os.path.join(_pack_installdir, 'data', 'html', 'templates'))
    # get information about the FASTQ file ?
    fn = os.path.basename(fqfile.filename)
    libs = list()
    csv_fn = os.path.join(directory, 
                          'fastqual_%s.csv' % fn)
    if verbose:
        sys.stdout.write('Creating file %s...' % csv_fn)
    f = file(csv_fn, mode = 'w')
    csv_w = csv.writer(f)
    for row in report.fastqual_tocsv_iter(fq):
        csv_w.writerow(row)
    f.close()
    if verbose:
        sys.stdout.write('done.\n')
    LibReport = namedtuple("LibReport", "readcount csv_fn")
    lib = LibReport(lib.readcount(), lib.csv_fn)        
    # render the HTML
    rd = template.render(**{
            'filename': fn,
            'fqinfo': tuple(),
            'lib': lib,
            'sample_percent': sample_percent})

    html_fn = os.path.join(directory, 
                           'fastqual_%s.html' % (fn))
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

def write_fastq(buf, entry, seq_proc = None, qual_proc = None):
    if entry.header[0] != '@':
        buf.write('@')
    buf.write(entry.header)
    buf.write('\n')
    if seq_proc is None:
        buf.write(entry.sequence)
    else:
        buf.write(seq_proc(entry.sequence))
    buf.write('\n+\n')
    if qual_proc is None:
        buf.write(entry.quality)
    else:
        buf.write(qual_proc(entry.quality))
    buf.write('\n')

if __name__ == '__main__':
    import sys, argparse
    from ngs_plumbing.utils import size_parser
    parser = argparse.ArgumentParser(
        description = 'Toolkit for FASTQ files')
    parser.add_argument('fn_in', metavar='<file name>', nargs='+',
                        help='FASTQ file')
    parser.add_argument('-c', '--count',
                        dest = 'count',
                        action = 'store_true',
                        help = 'Count the number of entries')
    parser.add_argument('-b', '--buffer',
                        dest = 'buffer',
                        default = '2Mb',
                        type = size_parser,
                        help = 'Buffer size (default: 2Mb)')
    parser.add_argument('-r', '--report',
                        dest = 'report',
                        action = 'store_true',
                        help = 'Make an HTML report about the content of the file')
        
    for fn_in in options.fn_in:
        sys.stdout.write('fn_in:\n')
        sys.stdout.flush()
        fq = FastqFile(fn_in)

        if options.count:
            rc = fq.readcount()
            sys.stdout.write('  # reads: %i\n' % rc)
            sys.stdout.flush()
