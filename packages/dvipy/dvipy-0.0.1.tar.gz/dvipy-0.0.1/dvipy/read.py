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

#class Handler(object)
from dvipy.stream import *
from dvipy.font import Font
from dvipy.dispatch import Dispatcher

_, i1, i2, i3, i4 = signed
_, I1, I2, I3, I4 = unsigned

# A list of the opcodes we will use later. This follows an important
# convention, as follows: if there is an opcode, followed immediately by
# another opcode, it is interpreted as a single code. Otherwise, it is
# treated as a sequence, starting from one, which is passed as the first
# argument. Therefore, if an opcode actually begins with zero, we must
# pass first the one.

def default_char(state, char):
    pass

def default_rule(state, a, b):
    pass

def default_fnt_def(state, fnt, i):
    pass

def default_fnt(state, fnt, i):
    pass


class DviState(object):
    __slots__ = ('on_put_char', 'on_put_rule', 'on_fnt_def', 'on_fnt',
                 'fonts', 'font', 'stack', 'h', 'v', 'w', 'x', 'y', 'z',
                 'num', 'den', 'mag')
    def __init__(self):
        self.fonts = {}
        self.font = None
        self.set_callbacks()
        self.stack = []
        self.state = 0, 0, 0, 0, 0, 0

    def set_callbacks(self, char = default_char,
                      rule = default_rule,
                      fnt_def = default_fnt_def,
                      fnt = default_fnt):
        self.on_put_char = char
        self.on_put_rule = rule
        self.on_fnt_def = fnt_def
        self.on_fnt = fnt

    @property
    def state(self):
        return (self.h, self.v, self.w,
                self.x, self.y, self.z)

    @state.setter
    def state(self, (h, v, w, x, y, z)):
        self.h = h
        self.v = v
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def push(self):
        self.stack.append(self.state)
    
    def pop(self):
        self.state = self.stack.pop()

# This is probably the most complicated dispatcher. Dispatchers are objects that
# dispatch on an opcode, and loop until a certain final opcode is met. They can be
# operated on a whitelist or blacklist basis, thus tightening up parsing without
# exceptional logic. They operate based upon an internal dispatch dictionary,
# which maps from opcodes to the functions defined below. Function names are
# given here.

# Whilst this may seem slightly unorthodox (why not use a class?), done at a
# class level every method should really be a class method, as threading state
# creates a very limited parser which cannot be arbitrarily redirected.
# Furthermore, by explicitly passing the state object, less lookups have to be
# performed and namespace pollution is reduced.

# Mappings are created automatically based upon the following idea: opcodes
# spread to the next opcode, and a value starting from 1 is passed as the first
# argument. If an opcode is followed immediately by another, it must have value
# zero. As such, single operation opcodes get passed zero. This convention
# allows for a reduction of duplication, and still allows all the flexibility
# required.

dvi = Dispatcher()
with dvi.op() as op:

    @op(0, 1)
    def set_char_i(i, stream, state):
        """Typeset the character with code i and move right by its width"""
        state.on_put_char(state, i)
        state.h += state.font.chars[i].width

    @op(128)
    def set_char(n, stream, state,
                set_char_i=set_char_i,
                 unsigned=unsigned):
        """
        Typeset the character contained in the n-byte parameter and move
        right by its width

        """
        set_char_i(unsigned[n](stream), stream, state)

    @op(133)
    def put_char(n, stream, state,
                 unsigned=unsigned):
        state.on_put_char(state, unsigned[n](stream))

    @op(137)
    def put_rule(_, stream, state, fmt=fmt(i4, i4)):
        a, b = fmt(stream)
        state.on_put_rule(state, a, b)
        return b

    @op(132)
    def set_rule(_, stream, state, put_rule=put_rule):
        state.h += put_rule(_, stream, state)

    @op(138)
    def nop(_, stream, state):
        """By definition does nothing"""
        return

    @op(139)
    def bop(_, stream, state, i4=i4, I4=I4):
        c = read_array(stream, I4, 10)
        p = i4(stream)

    @op(140)
    def eop(_, stream, state):
        return

    @op(141)
    def push(_, stream, state):
        state.push()

    @op(142)
    def pop(_, stream, state):
        state.pop()

    @op(143)
    def right(n, stream, state, signed=signed):
        state.h += signed[n](stream)

    @op(147, 148)
    def w(n, stream, state, signed=signed):
        """Move right by w"""
        if n:
            state.w = signed[n](stream)
        state.h += state.w

    @op(152, 153)
    def x(n, stream, state, signed=signed):
        """Move right by x"""
        if n:
            state.x = signed[n](stream)
        state.h += state.x

    @op(157)
    def down(n, stream, state,signed=signed):
        state.v += signed[n](stream)

    @op(161, 162)
    def y(n, stream, state, signed=signed):
        """Move down by y"""
        if n:
            state.y = signed[n](stream)
        state.v += state.y

    @op(166, 167)
    def z(n, stream, state, signed=signed):
        if n:
            state.z = signed[n](stream)
        state.v += state.z

    @op(171, 172)
    def fnt_num_i(i, stream, state):
        state.font = state.fonts[i]
        state.on_fnt(state, state.font, i)

    @op(235)
    def fnt(n, stream, state, unsigned=unsigned):
        i = unsigned[n](stream)
        fnt_num_i(i, stream, state)

    @op(239)
    def xxx(n, stream, state, unsigned=unsigned, read_string=read_string):
        l = unsigned[n](stream)
        read_string(stream, l)

    @op(243)
    def fnt_def(n, stream, state,
                unsigned=unsigned,
                fmt=fmt(I4, I4, I4, I1, I1),
                Font=Font
               ):
        k = unsigned[n](stream)
        c, s, d, a, l = fmt(stream)
        name = read_string(stream, a + l)

        state.fonts[k] = font = Font(name, s, d, k)

        state.on_fnt_def(font)

    @op(247)
    def pre(_, stream, state,
            fmt=fmt(I1,I4,I4,I4,I1),
            read_string=read_string
           ):
        i, num, den, mag, k = fmt(stream)
        state.num = num
        state.den = den
        state.mag = mag
        x = read_string(stream, k)

    @op(248)
    def post(_, stream, state):
        # We really have no need to disturb the postamble, as we read in
        # files sequentially
        raise(RuntimeError, 'Postamble detected in unexpected place')

    @op(249)
    def post_post(_, stream, state):
        # Nor do we have reason to read in post post
        raise(RuntimeError, 'Post-postamble detected in unexpected place')

    @op(250)
    def undefined(_, stream, state):
        raise(RuntimeError, 'Undefined opcode')

read_pre = dvi.reader(whitelist=['pre', 'nop'], end_on=['pre'])

read_bop = dvi.reader(whitelist=['bop', 'nop', 'fnt_def'], end_on=['bop'])

read_eop = dvi.reader(blacklist=['pre', 'post', 'post_post'], end_on=['eop'])

read_vf = dvi.reader(blacklist=['pre', 'post', 'post_post'], end_on=['eop'])
