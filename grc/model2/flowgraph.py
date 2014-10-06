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

from . import Element, exceptions, Block, Connection


class FlowGraph(Element):

    def __init__(self, parent=None):
        super(FlowGraph, self).__init__(parent)

        self.blocks = []
        self.connections = []

        self.options = None

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

        self.blocks[block.id] = block

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
        # todo: update namespace
        super(FlowGraph, self).rewrite()
