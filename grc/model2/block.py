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

from collections import OrderedDict

from . import Element
from . port import Port
from . param import Param


class BlockException(Exception):
    pass


class BlockSetupException(BlockException):
    pass


class Block(Element):

    key = 'key'  # key is a unique string that is a valid python variable name.
    name = 'label'

    def __init__(self, parent, **kwargs):
        super(Block, self).__init__(parent)

        self._ports = {  # the raw/unexpanded/hidden ports are help here
            'sources': OrderedDict(),  # a dict to hold the source ports this block, indexed by key
            'sinks': OrderedDict(),  # a dict to hold the sink ports this block, indexed by key
        }
        self.params = OrderedDict()

        # a list of sink ports currently visible (think hidden ports, bus ports, nports)
        # filled / updated by rewrite()
        self.sources = []
        self.sinks = []

        self.setup(**kwargs)

    def setup(self, **kwargs):
        """How to construct the block: sinks, sources, parameters"""
        # here block designers add code for ports and param
        raise NotImplementedError()

    def add_port(self, *args, **kwargs):
        """Add a port to this block
        Usage options:
            - a port object
            - kwargs for port construction
        """
        # get port object
        port = args[0] if args and isinstance(args[0], Port) else Port(*args, **kwargs)
        # check and add
        try:
            key = str(port.key)
            ports = self._ports[port.direction]
            if key in ports:
                raise BlockSetupException("Port key '{}' not unique")
            ports[key] = port
        except KeyError:
            raise BlockSetupException("Unknown port direction")

    def add_param(self, *args, **kwargs):
        # get param object
        if args and isinstance(args[0], Param):
            port = args[0]
        else:
            port = Port(*args, **kwargs
            )

    def rewrite(self):
        """Update the blocks ports"""
        super(Block, self).rewrite()
        # todo: expand nports, form busses, handle port hiding
