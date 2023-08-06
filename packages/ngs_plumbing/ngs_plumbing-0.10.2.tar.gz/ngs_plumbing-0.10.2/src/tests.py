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

import unittest

import ngs_plumbing.ngsp_string_test as string_test
from ngs_plumbing import dna_test
from ngs_plumbing import dnaqual_test
from ngs_plumbing import intervals_test
from ngs_plumbing import fasta_test
from ngs_plumbing import fastq_test
from ngs_plumbing import kmers_test
try:
    from ngs_plumbing import xsq_test
    has_xsq = True
except ImportError:
    import warnings
    warnings.warn("The package 'h5py' is missing. Functionalities related to it cannot be tested.")
    has_xsq = False
from ngs_plumbing import _libxsq_test
from ngs_plumbing import _libdna_test
from ngs_plumbing import _libdnaqual_test


def suite():
    suite_string = string_test.suite()
    suite_dna = dna_test.suite()
    suite_dnaqual = dnaqual_test.suite()
    suite_intervals = intervals_test.suite()
    suite_fasta = fasta_test.suite()
    suite_fastq = fastq_test.suite()
    suite_kmers = kmers_test.suite()
    if has_xsq:
        suite_xsq = xsq_test.suite()
    suite_libxsq = _libxsq_test.suite()
    suite_libdna = _libdna_test.suite()
    suite_libdnaqual = _libdnaqual_test.suite()

    l = [suite_string,
         suite_dna,
         suite_dnaqual,
         suite_intervals,
         suite_fasta,
         suite_fastq,
         suite_kmers,
         suite_libxsq,
         suite_libdna,
         suite_libdnaqual]
    if has_xsq:
        l.append(suite_xsq)
    alltests = unittest.TestSuite(l)
    return alltests


if __name__ == "__main__":
    unittest.main(defaultTest = "suite")
