import argparse
import os
import sys

try:
    import ngs_plumbing.xsq
except ImportError:
    sys.stderr.write('Error: the Python package "h5py" is required but could not be imported.')
    sys.stderr.flush()



def main():
    parser = argparse.ArgumentParser(
        description = 'Convert XSQ files into less exotic (albeit sometimes also less efficient) formats.')
    parser.add_argument('paths', metavar='XSQ_FILE', nargs='*',
                        help='XSQ files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='directory in which resulting files should be put')
    parser.add_argument('-C', '--CSFASTA',
                        dest = 'to_csfasta',
                        action = 'store_true',
                        help = "output to CSFASTA + QUAL.")
    parser.add_argument('-Q', '-FASTQ',
                        dest = 'to_fastq',
                        action = 'store_true',
                        help = "output to FASTQ. If -E/--ECC, it will use the ECC base calls, otherwise it will do a naive conversion from the starting base.")
    parser.add_argument('-E', '--ECC',
                        dest = 'use_ecc',
                        action = 'store_true',
                        help = 'use ECC base calling whenever present (and conversion to FASTQ is asked).')
    parser.add_argument('-i', '--info',
                        dest = 'want_info',
                        action = 'store_true',
                        help = 'Print information about the XSQ file')
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()

