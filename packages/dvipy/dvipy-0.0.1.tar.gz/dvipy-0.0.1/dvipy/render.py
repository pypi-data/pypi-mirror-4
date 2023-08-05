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

from collections import namedtuple

from dvipy.read import read_vf
from dvipy.font import kpse
from dvipy.fontmap import fntmap, load_requested, get_encoding
from dvipy.vf import VfState, vf_read_pre, vf_read_main
from dvipy.sizer import TexSizer


# The scaling does need to be done somewhere, to make sure that fonts etc. are
# the right. It would also be nice to have a test bed somewhere that can just 

DVI2TP = 2**-16

# When we sit and think for a while, the only thing we can have happen is a rule
# or a char, even with virtual fonts taken into consideration (yeah, this
# neglects specials)

Rule = namedtuple('Rule', ('x', 'y', 'w', 'h'))
Char = namedtuple('Char', ('x', 'y', 'char', 'font'))
Font = namedtuple('Font', ('filename', 'size'))

class T1Font(object):
    def __init__(self, filename, font, enc, scale=1.0):
        self.enc = enc
        self.fontcore = Font(filename, scale * font.size)

    def render(self, renderer, state, char):
        if self.enc:
            char = self.enc[char]
        c = Char(DVI2TP * state.h, DVI2TP * state.v, char, self.fontcore)
        renderer.page.append(c)

import operator



class VirtualFont(object):
    def __init__(self, filename, texfont,
                 read_pre=vf_read_pre, read_main=vf_read_main):
        self.state = VfState()

        with open(filename) as f:
            stream = iter(bytearray(f.read()))

        read_pre(stream, self.state)
        read_main(stream, self.state)

        self.font = self.state.fonts[0]
        self.texfont = texfont

        self.psfonts = psfonts = {}

        for i, j in self.state.fonts.iteritems():
            pfbs, encs = load_requested(fntmap[j.name])
            psname = pfbs[0]
            enc = get_encoding(encs[-1]) if encs else None
            psfonts[i] = T1Font(psname, j, enc, texfont.size)

    def render(self, renderer, state, i, read_vf=read_vf):
        renderer.in_vf=True
        stream = iter(bytearray(self.state.chars[i]))

        texfont = state.font
        texfonts = state.fonts
        font = renderer.font
        fonts = renderer.fonts

        state.fonts = self.state.fonts
        state.font = self.font
        renderer.fonts = self.psfonts
        renderer.font = self.psfonts[0]

        state.push()

        state.w = 0
        state.x = 0
        state.y = 0
        state.z = 0

        # This must be in a try block because the dvi commands can just exit
        # completely unexpectedly.
        try:
            read_vf(stream, state)
        except TypeError:
            pass
        except StopIteration:
            pass


        state.pop()

        state.font = texfont 
        state.fonts = texfonts
        renderer.font = font
        renderer.fonts = fonts
        renderer.in_vf = False

DviPage = namedtuple('DviPage', ('page', 'size', 'bl'))

class DviSlave():
    # Since we ignore specials and all that nonsense, we only need to store a
    # list of fonts, characters, and their positions. We can use a dispatcher
    # pattern to make this work -- have a heterogenous list with various objects
    # representing the renderings to perform. So really, all this does is handle
    # virtual fonts and compile things down into DVI objects. So for instance,
    # there will be lots and lots of tiny glyph objects.
    def __init__(self):
        self.fonts = {}
        self.page = []
        self.sizer = TexSizer()
        self.in_vf = False

    @property
    def callbacks(self):
        return dict(
            char = self.on_put_char,
            rule = self.on_put_rule,
            fnt = self.on_fnt,
            fnt_def = self.on_fnt_def
        )

    def clear_page(self):
        page = self.page
        (w, h), (b, l) = self.sizer.reset()
        size = DVI2TP * w, DVI2TP * h
        bl = DVI2TP * b, DVI2TP * l
        self.page = []
        return DviPage(page, size, bl)

    def on_put_char(self, state, i):
        self.font.render(self, state, i)
        # But if it's a virtual font how do we tell? ARRGH!
        # After about ~1min of thinking, this inelegant solution was proposed!
        if not self.in_vf:
            self.sizer.on_put_char(state, i)
        
    def on_fnt_def(self, texfont):
        r = fntmap.get(texfont.name)
        if r:
            pfbs, encs = load_requested(r)
            psname = pfbs[0]
            enc = get_encoding(encs[-1]) if encs else None
            font = T1Font(psname, texfont, enc)
        else:
            vffile = kpse('%s.vf' % texfont.name)
            font = VirtualFont(vffile, texfont)

        self.fonts[texfont.n] = font

    def on_fnt(self, state, fnt, k):
        self.font = self.fonts[k]

    def on_put_rule(self, s, a, b):
        self.page.append(Rule(DVI2PT * s.h, DVI2PT * s.v,
                              DVI2PT * b, DVI2PT * a))
        self.sizer.on_put_rule(s, a, b)
