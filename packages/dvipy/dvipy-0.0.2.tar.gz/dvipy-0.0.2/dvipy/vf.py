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

from dvipy.font import Font
from dvipy.dispatch import Dispatcher
from dvipy.stream import *

_, i1, i2, i3, i4 = signed
_, I1, I2, I3, I4 = unsigned

vf = Dispatcher()
with vf.op() as op:
    def _add_char(pl, cc, tfm, stream, state):
        dvi = read_string(stream, pl)
        state.chars[cc] = dvi

    @op(247)
    def pre(_, stream, state,
            read_string=read_string, 
            fmt1=fmt(I1, I1), fmt2=fmt(I4, I4)):
        i, k = fmt1(stream)
        x = read_string(stream, k)
        cs, ds = fmt2(stream)

    @op(0, 1)
    def short_char_i(pl, stream, state,
                     _add_char=_add_char,
                     fmt=fmt(I1, I3)):
        cc, tfm = fmt(stream)
        _add_char(pl, cc, tfm, stream, state)

    @op(242)
    def long_char_i(i, stream, state,
                    _add_char=_add_char,
                    fmt=fmt(I4, I4, I4)):
        pl, cc, tfm = fmt(stream)
        _add_char(pl, cc, tfm, stream, state)

    @op(243)
    def fnt_def(n, stream, state,
                fmt=fmt(I4, I4, I4, I1, I1)):

        k = unsigned[n](stream)
        c, s, d, a, l = fmt(stream)
        n = read_string(stream, a + l)
        state.fonts[k] = Font(n, s, d, k)

    @op(248)
    def post(_, stream, state):
        pass

    @op(249)
    def undef(i, stream, state):
        pass

class VfState(object):
    __slots__ = 'fonts', 'chars', 'scale'
    def __init__(self):
        self.fonts = {}
        self.chars = {}

vf_read_pre = vf.reader(whitelist=['pre'], end_on=['pre'])
vf_read_main = vf.reader(blacklist=['pre'], end_on=['post'])
