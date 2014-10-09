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

from . import Element, exceptions


class BasePort(Element):
    """Common elements of stream and message ports"""

    # Consts for directions
    SINK = "sink"
    SOURCE = "source"

    # using class attributes isn't strictly ideal here. However, it allows
    # setting attribute default by subclassing
    name = ''
    direction = ''
    domain = ''
    key = None  # set by rewrite of block function  #todo: why keep this here?

    def __init__(self, parent, **kwargs):
        super(BasePort, self).__init__(parent)

        # overwrite class attribute defaults
        for key, value in kwargs.iteritems():
            if hasattr(self.__class__, key):
                setattr(self, key, value)

        self.rewrite_actions = {}

    @property
    def connections(self):
        """Iterator for the connections using this port"""
        for connection in self.parent_flowgraph.connections:
            if self in connection.ports:
                yield connection

    def rewrite(self):
        super(BasePort, self).rewrite()
        params = self.parent_block.params  # todo: replace by a dict with current param values
        for atrrib_name, callback in self.rewrite_actions.iteritems():
            try:
                value = callback(**params)
                setattr(self, atrrib_name, value)
            except Exception as e:
                raise exceptions.BlockException(e)

    def on_rewrite(self, **kwargs):
        for attr_name, callback in kwargs.iteritems():
            if attr_name in self.__dict__:
                self.rewrite_actions[attr_name] = callback


class StreamPort(BasePort):
    """Stream ports have a data type and vector length"""

    dtype = None
    vlen = 0

    def __init__(self, parent, dtype, vlen=1, **kwargs):
        super(StreamPort, self).__init__(parent, dtype=dtype, vlen=vlen, **kwargs)

    def validate(self):
        # todo: check dtype and vlen
        super(StreamPort, self).validate()


class MessagePort(BasePort):
    """Message ports usually have a fixed key"""

    def __init__(self, parent, key, **kwargs):
        super(MessagePort, self).__init__(parent, key=key, **kwargs)


class StreamSink(StreamPort):
    name = "in"
    direction = StreamPort.SINK


class StreamSource(StreamPort):
    name = "out"
    direction = StreamPort.SOURCE


class MessageSink(MessagePort):
    name = "in"
    direction = MessagePort.SINK


class MessageSource(MessagePort):
    name = "out"
    direction = MessagePort.SOURCE
