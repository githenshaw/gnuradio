"""
Copyright 2014 Free Software Foundation, Inc.
This file is part of GNU Radio

GNU Radio Companion is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GNU Radio Companion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from __future__ import absolute_import, division, print_function

from collections import MutableMapping

from . import exceptions
from . base import Element
from . import Block, Connection


class FlowGraph(Element):

    def __init__(self, parent=None):
        super(FlowGraph, self).__init__(parent)

        self.blocks = []
        self.connections = []
        self.variables = {}

        self.options = None
        self.namespace = _FlowGraphNamespace(self.variables)

    def add_block(self, key_or_block):
        """Add a new block to the flow-graph

        Args:
            key: the blocks key (a Block object can be passed as well)

        Raises:
            BlockException
        """
        if isinstance(key_or_block, str):
            try:
                block = self.platform.blocks[key_or_block](parent=self)
            except KeyError:
                raise exceptions.BlockException("Failed to add block '{}'".format(key_or_block))

        elif isinstance(key_or_block, Block):
            block = key_or_block

        else:
            raise exceptions.BlockException("")

        self.blocks.append(block)

    def make_connection(self, endpoint_a, endpoint_b):
        """Add a connection between flow-graphs

        """
        connection = Connection(self, endpoint_a, endpoint_b)
        self.connections.append(connection)

    def remove(self, elements):
        """

        """
        for element in elements:
            if isinstance(element, Block):
                # todo: remove connections to this block?
                self.blocks.remove(element)
            elif isinstance(element, Connection):
                self.connections.remove(element)
            self.children.remove(element)
            del element

    def rewrite(self):
        # todo: update blocks
        self.namespace.reset()
        super(FlowGraph, self).rewrite()

    def execute(self, expr):
        return eval(expr, None, self.namespace)


class _FlowGraphNamespace(MutableMapping):
    """A dict class that calls variables for missing items"""

    def __init__(self, variables, defaults=None):

        self.variables = variables
        self.defaults = defaults if defaults else {}

        self._namespace = dict(self.defaults)
        self._seen = set()

    def __getitem__(self, key):
        if key in set:
            raise RuntimeError("Circular dependency")
        try:
            value = self._namespace[key]
            self._seen.clear()

        except KeyError:
            if key in self.variables:
                self._seen.add(key)
                value = self.variables[key].value
            else:
                raise

        return value

    def __setitem__(self, key, value):
        self._namespace[key] = value

    def __delitem__(self, key):
        del self._namespace[key]

    def __len__(self):
        return len(self._namespace)

    def __iter__(self):
        return iter(self._namespace)

    def reset(self):
        self._namespace.clear()
        self._namespace.update(self.defaults)
