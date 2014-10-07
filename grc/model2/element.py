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

from . import Block, FlowGraph, Platform


class Element(object):

    def __init__(self, parent):
        self._parent = parent
        self._children = []
        try:
            parent.children.append(self)
        except AttributeError:
            pass

    def _get_parent_by_class(self, cls):
        parent = self.parent
        return parent if isinstance(parent, cls) else \
            parent._get_parent_by_class(cls) if parent else None

    @property
    def parent(self):
        """Get the parent object"""
        return self._parent

    @property
    def parent_block(self):
        """Get the first block object in the ancestry

         Returns:
            a block object or None
        """
        return self._get_parent_by_class(Block)

    @property
    def parent_flowgraph(self):
        """Get the first flow-graph object in the ancestry

         Returns:
            a flow-graph object or None
        """
        return self._get_parent_by_class(FlowGraph)

    @property
    def platform(self):
        """Get the platform object from the ancestry

         Returns:
            a platform object or None
        """
        return self._get_parent_by_class(Platform)

    @property
    def children(self):
        return self._children

    def rewrite(self):
        """Rewrite object and all child object in this tree

        A rewrite shall be used to reevaluate variables, parameters, block surface (ports,...), ...
        The resulting values shall be cached for fast access
        """
        for child in self.children:
            child.rewrite()

    def validate(self):
        """Validate object and all child object in this tree

        Validation shall only check the validity of the flow-graph, not change any values
        """
        for child in self.children:
            child.rewrite()
