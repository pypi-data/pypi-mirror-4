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

import sys, os, re
cmd = 'scons -v'
s = os.popen(cmd, 'r')
p = re.compile('.+engine path: \[\'(.+)\'\].*')
for l in s:
    m = p.match(l)
    if m is not None:
        path = m.groups(0)[0]
        break
sys.path.append(os.path.dirname(path))

from SCons.Builder import Builder

def Mapper(*args, **kwargs):
    """ 
    Create a building mapping reads.

    - mapper: executable to the mapping program (e.g., bowtie, bwa, etc...)

    - mapper_opts: options for the mapper
    
    - reference: path to the reference 
    """
    extra = set(('mapper', 'mapper_opts', 'reference'))
    for x in extra:
        if x not in kwargs:
            raise ValueError('%s needed' %x)
    if 'action' in kwargs:
        raise ValueError('action should not be specified')

    kwargs['action'] = '{mapper} {mapper_opts} {reference} $SOURCE > $TARGET'.format(**kwargs)
    for x in extra:
        del(kwargs[x])
    return Builder(*args, **kwargs)

def Bowtie_build(*args, **kwargs):
    """
    
    """
    extra = set(('reference',))
    for x in extra:
        if x not in kwargs:
            raise ValueError('%s needed' %x)
    no_extra = set(('action', 'src_suffix'))
    for x in no_extra:
        if x in kwargs:
            raise ValueError('"%s" should not be specified' %x)

    kwargs['indexer'] = kwargs.get('indexer', 'bowtie-build')
    kwargs['indexer_opts'] = kwargs.get('indexer_opts', '-aB')
    kwargs['src_suffix'] = kwargs.get('src_suffix', 'fasta')
    kwargs['suffix'] = kwargs.get('suffix', 'ebwt')
    kwargs['action'] = '{indexer} {indexer_opts} $SOURCE > $TARGET'.format(**kwargs)
    for x in extra:
        del(kwargs[x])
    return Builder(*args, **kwargs)
    

def Bowtie_5500_ECC(*args, **kwargs):
    """ 
    See Mapper. Note that mapper_opts, suffix, and src_suffix should not be specified.

    - nproc : Number of processes (default to 1)

    """
    
    no_extra = set(('mapper_opts', 'suffix', 'src_suffix'))
    for x in no_extra:
        if x in kwargs:
            raise ValueError('"%s" should not be specified' %x)
    extra = set(('nproc', ))
    kwargs['mapper_opts'] = '--phred64-qual --sam -p %i' %kwargs.get('nproc', 1)
    kwargs['suffix'] = '.sam'
    kwargs['src_suffix'] = '.fq'
    return Mapper(*args, **kwargs)

def Bwa_build(*args, **kwargs):
    """
    - suffix: one of ('bwtsw', 'is', 'div')

    - indexer_opts: options to 'bwa index'

    """
    extra = set(('suffix', ))
    for x in extra:
        if x not in kwargs:
            raise ValueError('%s needed' %x)
    no_extra = set(('action', 'suffix'))
    for x in no_extra:
        if x in kwargs:
            raise ValueError('%s" should not be specified' %x)

    kwargs['indexer'] = kwargs.get('indexer', 'bwa index')
    kwargs['indexer_opts'] = kwargs.get('indexer_opts', '-c')
    kwargs['src_suffix'] = kwargs.get('src_suffix', 'fa')
    if kwargs['suffix'] not in ('bwtsw', 'is', 'div'):
        raise ValueError("suffix should be one of ('bwtsw', 'is', 'div')")
    
    kwargs['action'] = '{indexer} {indexer_opts} $SOURCE'.format(**kwargs)
    for x in extra:
        del(kwargs[x])
    return Builder(*args, **kwargs)


bowtie_exec = 'bowtie'
samtools_exec = 'samtools' 
        
#bowtie_5500_ecc = Bowtie_5500_ECC(mapper = bowtie_exec,
#                                  reference = '')

samtools_view = Builder(action = samtools_exec + ' view -bS ' + \
                            '-o $TARGET $SOURCE',
                        suffix = '.bam',
                        src_suffix = '.sam')

samtools_sort = Builder(action = samtools_exec + ' sort -o ' + \
                            '$SOURCE $TARGET',
                        suffix = '.sorted',
                        src_suffix = '.bam')
                            
samtools_index = Builder(action = samtools_exec + ' index ' + \
                             '$SOURCE > $TARGET',
                         suffix = '.bam.bai',
                         src_suffix = '.sorted')
                            
#env = Environment(BUILDERS = {'bowtie_5500_ecc': bowtie_5500_ecc,
#                              'samtools_view': samtools_view,
#                              'samtools_sort': samtools_sort,
#                              'samtools_index': samtools_index})



