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

from dvipy.font import kpse
import re

fontmap = open(kpse('psfonts.map'))

#class FontCache(object):

def tokenize(line):
    # Words are separated by space or tabs, unless double quote in which
    # case extends to either next double quote or end of the line
    a = 0
    in_string = False
    for index, char in enumerate(line):
        if char == '"':
            if in_string:
                in_string = False
                yield line[a:index+1]
                a = index + 1
            else:
                in_string = True

        elif char == ' ' and not in_string:
            b = index
            if a < b:
                yield line[a:b]
            a = index + 1

    if a < index and not in_string:
        yield line[a:]

    if in_string:
        yield line[a:]

fntmap = {}

# Lazily fill the fontmap -- most fonts will never get used, so just do
# a pre-partition on them. This should speed up module loading, where
# 0.2s does make an appreciable difference.

for i in fontmap:
    a, _, r = i.strip().partition(' ')
    fntmap[a] = r

def load_requested(r):
    line = tuple(tokenize(r))
    encodings = []
    pfbs = []
    tfms = []
    in_gt = False
    for i in line:
        if in_gt:
            in_gt = False
            r = i
            if r.endswith('.enc'):
                encodings.append(r)
            elif r.endswith('.pfb'):
                pfbs.append(r)
        else:

            if i == '<':
                in_gt = True
                continue

            elif i.startswith('<<'):
                r = i[2:]
                if r.endswith('.pfb'):
                    pfbs.append(r)
                elif r.endswith('.pfa'):
                    pfbs.append(r)
                else:
                    raise RuntimeError('Incorrect psfont.map', i)

            elif i.startswith('<['):
                r = i[2:]
                encodings.append(r)

            elif i.startswith('<'):
                r = i[1:]
                if r.endswith('.enc'):
                    encodings.append(r)
                elif r.endswith('.pfb'):
                    pfbs.append(r)
                elif r.endswith('.pfa'):
                    pfbs.append(r)
                else:
                    raise RuntimeError('Incorrect psfont.map', i)

            elif i.startswith('<['):
                encodings.append(i[2:])

    return pfbs, encodings

#for i in fntmap:
#    print i, load_requested(fntmap, i)
#a, b, c = load_requested(fntmap, 'upplr8t')
#print fntmap

# AND IF THIS FAILS...

# -> lookup virtual font

encodings = {}

def get_encoding(enc):
    return encodings.get(enc) or _read_encoding(enc)


# This is one of the only instances where a regexp is okay
comment_re = re.compile(r'%.*')

def _read_encoding(enc):
    vector = []
    with open(kpse(enc)) as encfile:
        lines = (comment_re.sub('', line).strip() for line in encfile)
        lines = [i for i in lines if i]
    # One day, this will come back to haunt me, and do very nasty things to me
    # in my sleep. One day. But that day could be one day from now. It could be
    # ten years. That's just the kind of man I am.
    for line in lines[1:-1]:
        vector.extend(line.split())
    vector = [i.lstrip('/') for i in vector]
    encodings[enc] = vector
    return vector
