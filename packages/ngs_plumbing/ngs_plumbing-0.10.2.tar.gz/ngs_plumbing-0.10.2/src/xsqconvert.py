#!/usr/bin/env python

#
#   XSQ converter
#

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

import argparse
import os
import sys
import functools

try:
    import ngs_plumbing.xsq
except ImportError:
    sys.stderr.write('Error: the Python package "h5py" is required but could not be imported. Bye.\n')
    sys.exit(1)
xsq = ngs_plumbing.xsq

def main():
    parser = argparse.ArgumentParser(
        description = '''Convert XSQ files into less exotic (albeit sometimes also less efficient) formats.

The overall idea is that XSQ files can be exported to two general types of files FASTA+QUAL or FASTQ,
and the exact file format for a given type will be depend on whether color-space or base-space data
are wanted. For example, the FASTQ general type would become CSFASTQ for color-space and
FASTQ for base-space.''')
    parser.add_argument('paths', metavar='XSQ_FILE', nargs='*',
                        help='XSQ files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='directory in which resulting files should be put')
    parser.add_argument('-f', '--format-style',
                        dest = 'output_format',
                        choices = ('FASTA', 'FASTQ'),
                        help = "Style of the format to output to.")
    parser.add_argument('-s', '--data-space',
                        dest = 'data_space',
                        choices = ('base', 'color'),
                        help = "Space to output the data into.")
    parser.add_argument('-E', '--ECC',
                        dest = 'use_ecc',
                        action = 'store_true',
                        help = 'use ECC to get data in base space.')
    parser.add_argument('--unassigned',
                        dest = 'want_unassigned',
                        action = 'store_true',
                        help = 'Also extract data from unassigned barcodes.')
    parser.add_argument('--buffer-size',
                        dest = 'buffer_size',
                        default = long(2E6),
                        type = long,
                        help = 'Buffer size in bytes. This can help with speed on some system or when files are accessed over NFS - default is set to 2000000 (2 Mb)')    
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()

    if not options.paths:
        sys.stderr.write('No input files. Goodbye.\n')
        sys.exit(1)

    if (not options.data_space) or (not options.output_format):
        sys.stderr.write('No output format or data space specified, so nothing was done. Goodbye.\n')
        sys.exit(1)

    if options.use_ecc and options.data_space == 'color':
        sys.stderr.write('Error: wanting data in color space is not compatible with wanting ECC data.\n')
        sys.exit(1)

    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            sys.stderr.write('Error: destination directory already existing (but not as a directory\n')
            sys.exit(1)
    else:
        sys.stderr.write('Warning: destination directory not existing; creating it.\n')
        os.mkdir(options.dest_dir)

    if options.output_format == 'FASTA':
        if options.data_space == 'color':
            conversion_function = functools.partial(xsq.automagic_csfasta,
                                  fragment = None, 
                                  buf_size = options.buffer_size, 
                                  out = sys.stdout,
                                  want_unassigned = options.want_unassigned)
        else:
            sys.stderr.write('Conversion to FASTA (base space) not yet implemented.\n')
            sys.exit(1)
    else:
        # FASTQ data
        if options.data_space == 'color':
            conversion_function = functools.partial(xsq.automagic_fastq,
                                fragment = None, 
                                buf_size = options.buffer_size, 
                                out = sys.stdout,
                                extension = 'csfq',
                                cs = True,
                                want_unassigned = options.want_unassigned)
        else:
            # base space
            if options.use_ecc:
                try:
                    conversion_function = functools.partial(xsq.automagic_fastq,
                                        fragment = None, 
                                        buf_size = options.buffer_size, 
                                        out = sys.stdout,
                                        cs = False,
                                        want_unassigned = options.want_unassigned)
                except KeyError as ke:
                    sys.stderr.write('\nError: No base calls for file "%s".\n' %f)
            else:
                sys.stderr.write('Conversion to FASTQ (base space) without ECC chemistry not yet implemented.\n')
                sys.exit(1)


    for f in options.paths:
        if not os.path.exists(f):
            sys.stderr.write('%s: No such file.\nSkipping...\n' % f)
            sys.stderr.flush()
            continue
            
        f_bn = os.path.basename(f)
        f_root, f_ext = os.path.splitext(f_bn)
        if f_ext.lower() != '.xsq':
            sys.stderr.write('%s: Extension \'.xsq\' expected.\nSkipping...\n' % f)
            sys.stderr.flush()
            continue
            
        dest_dir = os.path.join(options.dest_dir, f_root)
        os.mkdir(dest_dir)
        conversion_function(f,  path_out = dest_dir)

        
def htmlreport():
    import argparse

    parser = argparse.ArgumentParser(
        description = '''
Make an HTML report on the data quality in XSQ files.
''')
    parser.add_argument('paths', metavar='XSQ_FILE', nargs='*',
                        help='XSQ files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='Directory in which resulting files should be put')
    parser.add_argument('-f', '--force',
                        dest = 'force',
                        action = 'store_true',
                        help = 'Silently force actions such as overwriting files or creating missing directories.')
    parser.add_argument('-p', '--sampling-percentage',
                        dest = 'sample_percent',
                        default = 0.05,
                        type = float,
                        help = 'Percentage of the data to sample (a number between 0 and 1, default: 0.05, that is 5%%). An increased percentage is leading to an increased memory usage.')
    parser.add_argument('-t', '--data-type',
                        dest = 'data_type',
                        default = 'json',
                        help='Data type (default: json).')
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()

    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            print('Error: destination directory already existing (but not as a directory')
            sys.exit(1)
    else:
        if options.force:
            sys.stdout.write('Creating directory missing...')
            sys.stdout.flush()
            try:
                os.mkdir(options.dest_dir)
            except OSError as ose:
                sys.stderr.write('\n')
                sys.stderr.write(str(ose))
                sys.stderr.write('\n')
                sys.stderr.flush()
                sys.exit(1)
            sys.stdout.write('done.\n')
            sys.stdout.flush()
        else:
            print('Error: destination directory does not exist.')
            sys.exit(1)

    for f in options.paths:
        if not os.path.exists(f):
            print('%s: No such file.\nSkipping...' % f)
            continue
            
        f_bn = os.path.basename(f)
        f_root, f_ext = os.path.splitext(f_bn)
        if f_ext.lower() != '.xsq':
            print('%s: Extension \'.xsq\' expected.\nSkipping...' % f)
            continue
 
        dest_dir = os.path.join(options.dest_dir, f_root)
        try:
            os.mkdir(dest_dir)
        except OSError as ose:
            sys.stderr.write(str(ose))
            sys.stderr.write('\n')
            sys.exit(1)
            
        xf = xsq.XSQFile(f)
        xsq.make_htmlreport(xf, directory = dest_dir,
                            sample_percent = options.sample_percent,
                            data_type = options.data_type)
        xf.close()

if __name__ == '__main__':
    main()
