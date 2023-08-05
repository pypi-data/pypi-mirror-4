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

f = open('lol.out')


#lines = (line.strip() for line in f)

whitespace = set(' \t\n')
print whitespace

def read_intro(stream):
    for i in stream:
        print i

from ast import literal_eval
import Queue
queue = Queue.Queue()
for i in f:
    queue.put(literal_eval(i))

import functools

import itertools
def queue_iter(queue):
    queue_get = functools.partial(Queue.Queue.get, queue, timeout=1.0)
    return itertools.chain.from_iterable(iter(queue_get, None))

it = queue_iter(queue)

def read_error(stream):
    pass

in_page = False
in_error_type = False
in_error_body = 0

page = 0

from functools import partial
from itertools import groupby, izip, imap, repeat, tee, chain, ifilter
from operator import contains, itemgetter, ne

def lines(iterable):
    _is = partial(ne, '\n')
    groups = groupby(iterable, _is)
    return imap(''.join, imap(itemgetter(1), ifilter(itemgetter(0), groups)))

#for i, j in pairwise(it):
#    if in_error_type:
#        if j is not '\n':
#            error_type.append(j)
#        else:
#            error_type = ''.join(error_type)
#            in_error_type = False
#            in_error_body = 1
#
#    if in_error_body:
#        if j is '\n':
#            in_error_body += 1
#        else:
#            in_error_body += 1
#
#    elif i is '\n' and j is '!':
#        in_error_type = True
#        error_type = []
#    elif j is '[' and not in_page:
#        in_page = True
#        page = []
#    elif j.isdigit() and in_page:
#        page.append(j)
#    elif j is ']' and in_page:
#        in_page = False
#        print ''.join(page)
#
#
