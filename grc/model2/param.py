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

from itertools import imap
from . import Element, FlowGraph


class Param(Element):

    def __init__(self, parent, name, key, value_type=None, default_value=None):
        super(Param, self).__init__(parent)
        self._name = name
        self._key = key

        self.value_type = value_type
        self.value = self.value_default = default_value
        self._evaluated = None

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def evaluated(self):
        return self._evaluated

    def rewrite(self):
        super(Param, self).rewrite()
        self._evaluated = self.parent_flowgraph.evaluate(self.value)

    def validate(self):
        super(Param, self).validate()
        # todo: check param validity


class IdParam(Param):
    """Parameter of a block used as a unique parameter within a flow-graph"""

    def __init__(self, parent):
        super(IdParam, self).__init__(
            parent, 'id', 'ID', str, default_value=self._get_unique_id()
        )

    def _get_unique_id(self):
        """get a unique block id within the flow-graph by trail&error"""
        block = self.parent_block
        blocks = self.parent_flowgraph.blocks
        for block_id in imap(lambda key: "{}_{}".format(key, block), range(len(blocks))):
            if block_id not in blocks:
                return block_id
