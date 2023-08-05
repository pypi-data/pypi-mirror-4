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


from itertools import izip
from functools import partial
from operator import itemgetter
from contextlib import contextmanager
from collections import namedtuple

class Dispatcher(object):
    """Hides a _lot_ of the complexity / boilerplate"""
    def __init__(self):
        self.ops = {}
    
    # A contextmanager that returns a decorator. What could be simpler? :)
    @contextmanager
    def op(self):
        def op(*opcodes):
            """Add entry to the dispatcher"""
            def f(func):
                for opcode in opcodes:
                    self.ops[opcode] = func
                return func
            return f
        yield op
        self._make_tables()

    
    def _make_tables(self):
        # For efficiency and convenience, we define two tables at compile
        # (import) time. One is the lookup table, which returns a set for 
        ops = self.ops
        sorted_ops = sorted(ops.iteritems(), key=itemgetter(0))
        dispatch = dict()
        lookup = dict()

        for (a, func), (b, _) in izip(sorted_ops, sorted_ops[1:]):
            d = b - a

            if d > 1:
                for i, j in enumerate(xrange(a, b), 1):
                    dispatch[j] = partial(func, i)
            elif d == 1:
                dispatch[a] = partial(func, 0)
            elif d == 0:
                raise RuntimeError('Overlapping opcodes')

            fn = func.func_name
            s = lookup.get(fn, set())
            s.update(xrange(a, b))
            lookup[fn] = s
        self.lookup = lookup
        self.dispatch = dispatch


    def reader(self, whitelist=set(), blacklist=set(), end_on=set()):

        dispatch = self.dispatch
        lookup = self.lookup

        if whitelist and blacklist:
            raise RuntimeError(
                'Cannot have both whitelist and blacklist')

        end_on = set().union(*(lookup[i] for i in end_on))

        if whitelist:
            whitelist = set().union(*(lookup[i] for i in whitelist))
            return WhitelistReader(whitelist, end_on, dispatch)

        elif blacklist:
            blacklist = set().union(*(lookup[i] for i in blacklist))
            return BlacklistReader(blacklist, end_on, dispatch)

#Base classes -- get many nice defaults
_WhitelistReader = namedtuple('WhitelistReader', 
                              ('whitelist', 'end_on', 'dispatch'))

_BlacklistReader = namedtuple('BlacklistReader', 
                              ('blacklist', 'end_on', 'dispatch'))

class WhitelistReader(_WhitelistReader):
    def __call__(self, stream, state):
        dispatch = self.dispatch
        whitelist = self.whitelist
        end_on = self.end_on

        while True:
            opcode = next(stream)
            if opcode in whitelist:
                dispatch[opcode](stream, state)
            else:
                raise RuntimeError('Opcode %d not in whitelist' % opcode)

            if opcode in end_on:
                return

class BlacklistReader(_BlacklistReader):
    def __call__(self, stream, state):
        dispatch = self.dispatch
        blacklist = self.blacklist
        end_on = self.end_on

        while True:
            opcode = next(stream)
            if opcode not in blacklist:
                dispatch[opcode](stream, state)
            else:
                raise RuntimeError('Opcode %d in blacklist' % opcode)

            if opcode in end_on:
                return

__all__ = Dispatcher,
