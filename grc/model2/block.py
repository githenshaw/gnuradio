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

from . import Element, Port, Param
from . param import IdParam


class BlockException(Exception):
    pass


class BlockSetupException(BlockException):
    pass


class BaseBlock(Element):

    key = 'key'  # key is a unique string that is a valid python variable name.
    name = 'label'
    domain = None

    def __init__(self, parent, **kwargs):
        super(BaseBlock, self).__init__(parent)

        self._ports = {  # the raw/unexpanded/hidden ports are held here
            'sources': OrderedDict(),  # a dict to hold the source ports this block, indexed by key
            'sinks': OrderedDict(),  # a dict to hold the sink ports this block, indexed by key
        }
        self.params = OrderedDict()
        self.add_param(IdParam(self))
        self.add_param(key='_enabled', name='Enabled', value_type=bool, default_value=True)

        # a list of sink ports currently visible (think hidden ports, bus ports, nports)
        # filled / updated by rewrite()
        self.sources = []
        self.sinks = []

        self.setup(**kwargs)

    def setup(self, **kwargs):
        """How to construct the block: sinks, sources, parameters"""
        # here block designers add code for ports and param
        raise NotImplementedError()

    @property
    def id(self):
        """unique identifier for this block within the flow-graph"""
        return self.params['id'].value

    def add_port(self, *args, **kwargs):
        """Add a port to this block

        Usage options:
            - a port object
            - kwargs for port construction
        """
        try:
            port = args[0] if args and isinstance(args[0], Port) else Port(*args, **kwargs)
            key = str(port.key)
            ports = self._ports[port.direction]
            if key in ports:
                raise BlockSetupException("Port key '{}' not unique".format(key))
            ports[key] = port
        except KeyError:
            raise BlockSetupException("Unknown port direction")
        # todo: catch and rethrow Port Exception

    def add_param(self, *args, **kwargs):
        """Add a param to this block

        Usage options:
            - a param object
            - kwargs for port construction
        """
        param = args[0] if args and isinstance(args[0], Param) else Param(*args, **kwargs)
        key = str(param.key)
        if key in self.params:
            raise BlockSetupException("Param key '{}' not unique".format(key))

    def rewrite(self):
        """Update the blocks ports"""
        super(BaseBlock, self).rewrite()
        # todo: expand nports, form busses, handle port hiding


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
