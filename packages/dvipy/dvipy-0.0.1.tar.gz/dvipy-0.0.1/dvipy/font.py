# Copyright 2012 David Mallows
#
# This file is part of dvipy.
# 
# Dvipy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dvipy.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import
from subprocess import Popen, PIPE
from collections import namedtuple
from itertools import islice, count
import struct

from dvipy.stream import *

def kpse(fname, Popen=Popen):
    query = 'kpsewhich', fname
    return Popen(query, stdout=PIPE).communicate()[0].strip()


Lengths = namedtuple('Lengths', (
    'lf', 'lh', 'bc', 'ec', 'nw', 'nh',
    'nd', 'ni', 'nl', 'nk', 'ne', 'np'))


Char = namedtuple('Char', (
    'width', 'height', 'depth',
    'italic', 'tag', 'remainder'))


def tfm_widths(stream, n, z, read_bytes_lazy=read_bytes_lazy):
    """
    Read in the widths from the TFM file, converting using the scaling factor
    given in the DVI file

    """
    alpha = 16
    while z >= 0o40000000:
        z //= 2
        alpha += alpha

    beta = 256 // alpha
    alpha *= z

    for b0, b1, b2, b3 in (read_bytes_lazy(stream, 4) for _ in xrange(n)):
        in_width = (((((b3 * z) // 0o400) + (b2 * z)) // 0o400) + (b1 * z)) // beta
        if b0 > 0:
            if b0 < 255:
                raise RuntimeError('Invalid width in TFM file')
            else:
                in_width -= alpha

        yield in_width


_, I1, I2, I3, I4 = unsigned
_, i1, i2, i3, i4 = signed

class Font(object):
    def __init__(self, fontname, scale, d=None, n=None):
        self.n = n
        self.d = d
        self.name = fontname

        filename = kpse('%s.tfm' % fontname)

        with open(filename, 'r') as f:
            stream = iter(bytearray(f.read()))

        lengths = Lengths._make(read_array(stream, I2, 12))

        header = read_array(stream, I4, lengths.lh)
        self.size = (header[1] / float(1<<20)) * (float(scale) / self.d)

        nc = 1 + lengths.ec - lengths.bc
        char_info = read_bytes(stream, 4 * nc)

        widths = list(tfm_widths(stream, lengths.nw, scale))
        heights = list(tfm_widths(stream, lengths.nh, scale))
        depths = list(tfm_widths(stream, lengths.nd, scale))
        italics = list(tfm_widths(stream, lengths.ni, scale))

        tables = widths, heights, depths, italics

        self.chars = chars = {}

        ci_iter = iter(char_info)
        for i in xrange(lengths.bc, lengths.ec+1):
            a, b, c, d = islice(ci_iter, 4)
            width_ix = a
            height_ix = (0xf0 & b) >> 4
            depth_ix = 0x0f & b
            italic_ix = (0xfc & c) >> 2
            tag = 0x03 & c
            remainder = d

            chars[i] = Char(
                widths[width_ix],
                heights[height_ix],
                depths[depth_ix],
                italics[italic_ix],
                tag, remainder)




if __name__=='__main__':
    f = Font('cmr12', 786432, 1, 1)
    for i, j in f.chars.iteritems():
        print chr(i), j
