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
from itertools import chain

from . import Param, exceptions
from . element import Element
from . param import IdParam
from . port import BasePort, MessageSink, MessageSource, StreamSink, StreamSource


class BaseBlock(Element):

    key = 'key'  # key is a unique string
    name = 'label'

    def __init__(self, parent, **kwargs):
        super(BaseBlock, self).__init__(parent)

        self._ports = {  # the raw/unexpanded/hidden ports are held here
            'sources': [],  # a dict to hold the source ports this block, indexed by key
            'sinks': [],  # a dict to hold the sink ports this block, indexed by key
        }

        self.params = OrderedDict()
        self.add_param(IdParam(self))
        self.add_param(key='_enabled', name='Enabled', value_type=bool, default_value=True)

        self.params_namespace = {}  # dict of evaluated params

        # a list of sink ports currently visible (think hidden ports, bus ports, nports)
        self.sources = [] # filled / updated by rewrite()
        self.sinks = []

        # call user defined init
        self.setup(**kwargs)

    def setup(self, **kwargs):
        """How to construct the block: sinks, sources, parameters"""
        # here block designers add code for ports and params
        pass

    @property
    def id(self):
        """unique identifier for this block within the flow-graph"""
        return self.params['id'].value


    def add_port(self, port):
        """Add a port to this block

        Args:
            - port: instance of BasePort
        """
        if not isinstance(port, BasePort):
            raise ValueError("Excepted an instance of BasePort")
        try:
            self._ports[port.direction].append(port)
        except KeyError:
            raise exceptions.BlockSetupException("Unknown port direction")
        return port

    def add_stream_sink(self, **kwargs):
        return self.add_port(StreamSink(self, **kwargs))

    def add_stream_source(self, **kwargs):
        return self.add_port(StreamSource(self, **kwargs))

    def add_message_sink(self, **kwargs):
        return self.add_port(MessageSink(self, **kwargs))

    def add_message_source(self, **kwargs):
        return self.add_port(MessageSource(self, **kwargs))


    def add_param(self, *args, **kwargs):
        """Add a param to this block

        Usage options:
            - a param object
            - kwargs for port construction
        """
        param = args[0] if args and isinstance(args[0], Param) else Param(*args, **kwargs)
        key = str(param.key)
        if key in self.params:
            raise exceptions.BlockSetupException("Param key '{}' not unique".format(key))

    def rewrite(self):
        """Update the blocks ports"""
        # todo: evaluate params
        self.params_namespace.clear()
        for key, param in self.params.iteritems():
            self.params_namespace[key] = param.evaluated

        # todo: rewrite ports
        for port in chain(self._ports['sinks'], self._ports['sources']):
            port.rewrite()

        # todo: expand nports, form busses, handle port hiding

        #super(BaseBlock, self).rewrite()  # todo: should I even call this?


class Block(BaseBlock):
    """A regular block (not a pad, virtual sink/source, variable)"""

    def setup(self, **kwargs):
        super(Block, self).setup(**kwargs)

        self.add_param(key='alias', name='Block Alias', value_type=str, default_value=self.id)
        if self.sources or self.sinks:
            self.add_param(key='affinity', name='Core Affinity', value_type=list, default_value=[])
        if self.sources:
            self.add_param(key='minoutbuf', name='Min Output Buffer', value_type=int, default_value=0)
            self.add_param(key='maxoutbuf', name='Max Output Buffer', value_type=int, default_value=0)


class PadBlock(BaseBlock):
    pass
    # todo: add custom stuff


class VirtualSourceSinkBlock(BaseBlock):
    pass
    # todo: add custom stuff
