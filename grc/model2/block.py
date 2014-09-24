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
from . port import PortBase


class Block(Element):

    KEY = 'key'
    NAME = 'label'

    SOURCES = None
    SINKS = None

    def __init__(self, parent):
        super(Block, self).__init__(parent)
        self._sources = self._instantiate_ports(self.SOURCES)
        self._sinks = self._instantiate_ports(self.SINKS)

    def _instantiate_ports(self, port_classes):
        ports = OrderedDict()
        for Port in (port_classes or []):
            if issubclass(Port, PortBase):
                port = Port(self)
                ports[port.key] = port
        return ports

    @property
    def key(self):
        """Get the key of this block (read-only)

        The key is a unique string that is a valid python variable name.
        """
        return self.KEY

    @property
    def name(self):
        """Get the name of this block (read-only)"""
        return self.NAME
