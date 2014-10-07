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

from itertools import ifilter

from . import Element, FlowGraph

VALID_PORT_DIRECTIONS = ("sink", "source")


class Port(Element):
    """Simple Port class"""

    direction = None
    domain = None

    def __init__(self, parent, name, dtype, vlen=1, **kwargs):
        super(Port, self).__init__(parent)
        self._key = None
        self._name = name
        self._dtype = dtype
        self._vlen = vlen

    def setup(self, **kwargs):
        for var_name, value in kwargs.iteritems():
            for attrib_name in (var_name, '_' + var_name):
                if getattr(self, attrib_name):
                    setattr(self, attrib_name, value)

    @property
    def key(self):
        """ The key of a port is used in the connect function"""
        return self._key

    @key.setter
    def key(self, value):
        if self.dtype != "message" and not str(value).isdigit():
            raise ValueError("A stream port key must be numeric")

    @property
    def dtype(self):
        """The data type of this port"""
        return self._dtype

    @property
    def connections(self):
        """Iterator for the connections using this port"""
        for connection in self.parent_flowgraph.connections:
            if self in connection.ports:
                yield connection


class DynamicPort(Port):

    def __init__(self, parent, key, name, vlen=1, type_param_key='type', **kwargs):
        super(DynamicPort, self).__init__(parent, key, name, vlen, **kwargs)
        self._type_param_key = type_param_key

    def rewrite(self):
        super(DynamicPort, self).rewrite()
        self._dtype = self.parent.params[self._type_param_key]
