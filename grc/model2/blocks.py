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
from itertools import chain, ifilter, imap

from . import exceptions
from . base import Element
from . params import Param, IdParam
from . ports import BasePort, StreamPort, MessagePort


class BaseBlock(Element):
    uid = 'uid'     # a unique identifier for this block class
    name = 'label'  # the name of this block (label in the gui)

    import_template = ''
    make_template = ''

    def __init__(self, parent, **kwargs):
        super(BaseBlock, self).__init__(parent)

        self.params = OrderedDict()
        self.add_param(IdParam(self))
        self.add_param(name='Enabled', key='_enabled', vtype=bool, default=True)

        self.params_namespace = {}  # dict of evaluated params

        # the raw/unexpanded/hidden port objects are held here
        self._sources = []
        self._sinks = []

        # lists of ports currently visible (think hidden ports, bus ports, nports)
        self.sources = []  # filled / updated by rewrite()
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

    def add_port(self, cls, direction, *args, **kwargs):
        """Add a port to this block

        Args:
            - port_object_or_class: instance or subclass of BasePort
            - args, kwargs: arguments to pass the the port
        """
        if issubclass(cls, BasePort):
            port = cls(self, *args, **kwargs)
        elif isinstance(cls, BasePort):
            port = cls
        else:
            raise ValueError("Excepted an instance of BasePort")

        try:
            {
                'sink': self._sinks,
                'source': self._sources
            }[direction].append(port)
        except KeyError:
            raise exceptions.BlockSetupException("Unknown port direction")
        return port

    def add_stream_sink(self, name, enabled=True, nports=None, dtype=None, vlen=1):
        return self.add_port(
            StreamPort, 'sink', name, enabled, nports, dtype, vlen
        )

    def add_stream_source(self, name, enabled=True, nports=None, dtype=None, vlen=1):
        return self.add_port(
            StreamPort, 'source', name, enabled, nports, dtype, vlen
        )

    def add_message_sink(self, name, enabled=True, nports=None, key=None):
        return self.add_port(MessagePort, 'sink', name, enabled, nports, key)

    def add_message_source(self, name, enabled=True, nports=None, key=None):
        return self.add_port(MessagePort, 'source', name, enabled, nports, key)

    def add_param(self, *args, **kwargs):
        """Add a param to this block

        Usage options:
            - a param object
            - kwargs for port construction
        """
        if args and isinstance(args[0], Param):
            param = args[0]
        elif args and issubclass(args[0], Param):
            param = args[0](*args[1:], **kwargs)
        elif issubclass(kwargs.get('cls', object), Param):
            param = kwargs.pop('cls')(*args, **kwargs)
        else:
            param = Param(self, *args, **kwargs)
        key = str(param.key)
        if key in self.params:
            raise exceptions.BlockSetupException("Param key '{}' not unique".format(key))
        self.params[key] = param
        return param

    def rewrite(self):
        """Update the blocks ports"""
        self.params_namespace.clear()
        for key, param in self.params.iteritems():
            self.params_namespace[key] = param.evaluated

        port_list_mappings = ((self.sinks, self._sinks), (self.sources, self._sources))
        for ports, ports_raw in port_list_mappings:
            ports_current = list(ports)  # keep current list of ports
            del ports[:]  # reset list
            for port in ports_raw:
                port.rewrite()
                if port.enabled:
                    # re-add ports and their clones
                    ports.append(port)
                    ports += port.clones
                elif port in ports_current:
                    # remove connections from ports that were disabled
                    port.disconnect()

        # todo: form busses
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
