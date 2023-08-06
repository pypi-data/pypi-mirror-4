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
""" Various utilities to report results / make reports with results """
from collections import OrderedDict
import json

def fastqual_tocsv_iter(fq):
    """ fq: result returned by xsq.fastqual() """
    
    header = tuple(['basepos',] +  list(fq[0]._fields))
    yield header
    for basepos, val in enumerate(fq):
        res = tuple( [basepos + 1, ] + [getattr(val, x) for x in fq[0]._fields])
        yield res

def fastqual_tojson(fq):
    """ fq: result returned by xsq.fastqual() """
    res = list()
    for basepos, val in enumerate(fq):
        od = OrderedDict()
        od['basepos'] = basepos +1
        for h,v in zip(fq[0]._fields, val):
            od[h] = v
        res.append(od)
    return json.dumps(res)
