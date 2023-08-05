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

import collections
from itertools import groupby
from functools import partial

# This is a very simple (line-based) parser for the template format.
def scan_blockname(line):
    line = line.rstrip()
    if line.startswith('=') and line.endswith('='):
        p = line.strip('=').strip()
        if p.isalnum():
            return p


def scan_varname(line):
    if line.startswith('((') and line.endswith('))'):
        p = line.strip('()').strip()
        if p.isalnum():
            return p


def read_block_start(lines):
    for line in lines:
        block = scan_blockname(line)
        if block:
            return block

Var = collections.namedtuple('Var', ('name',))


def read_block_end(lines):
    for line in lines:
        l = line.rstrip()
        if line.startswith('=') and not l.strip('=').strip():
            break
        else:
            var = scan_varname(l)
            if var:
                yield Var(var)
            else:
                yield l


def isvar(x):
    return isinstance(x, Var)

def converge_content(content):
    for v, x in groupby(content, key=isvar):
        if v:
            for i in x:
                yield i
        else:
            yield '\n'.join(x)

def parse_template(lines):
    while True:
        block = read_block_start(lines)
        if block:
            content = list(converge_content(read_block_end(lines)))
            yield block, content
        else:
            return


# Each block maps to a very specific function.

class Template(object):
    def __init__(self, content):
        self.content = content
    
    @property
    def strings(self):
        return (t for t in self.content if not isvar(t))

    def render(self, **kwargs):
        return '\n'.join(kwargs.get(x.name, '') if isvar(x) else x for x in
                         self.content)

def read_templates(f):
    return dict((i, Template(j)) for i, j in parse_template(f))
