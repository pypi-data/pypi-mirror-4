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


class TexSizer():
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

    def on_put_char(self, s, i):
        st = s
        char = s.font.chars[i]
        w, h, d = char.width, char.height, char.depth
        self.left = min(self.left, st.h, st.h + w)
        self.right = max(self.right, st.h, st.h + w)

        self.top = min(self.top, st.v - h)
        self.bottom = max(self.bottom, st.v + d)

    def on_put_rule(self, s, a, b):
        v, h = s.v, s.h
        self.left = min(self.left, h, h + b)
        self.right = max(self.right, h, h + b)

        self.top = min(self.top, v, v + a)
        self.bottom = max(self.bottom, v, v + a)

    @property
    def size(self):
        return (self.right - self.left, self.bottom - self.top)

    @property
    def bl(self):
        return self.left, self.bottom


    def reset(self):
        size = self.size, self.bl
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        return size

