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

from collections import namedtuple

PortDType = namedtuple("PortDType", "name sizeof color")

stream_port_dtypes = {}

def add_port_dtype(name, sizeof, color, *keys):
    dtype = PortDType(name, sizeof, color)
    for key in keys:
        stream_port_dtypes[key] = dtype

# build-in types
add_port_dtype('Complex Float 64',   16, '#CC8C69', 'fc64')
add_port_dtype('Complex Float 32',    8, '#3399FF', 'fc64', 'complex')

add_port_dtype('Float 64' ,           8, '#66CCCC', 'f64')
add_port_dtype('Float 32' ,           4, '#FF8C69', 'f32', 'float')

add_port_dtype('Complex Integer 64', 16, '#66CC00', 'sc64')
add_port_dtype('Complex Integer 32',  8, '#33cc66', 'sc32')
add_port_dtype('Complex Integer 16',  4, '#cccc00', 'sc16')
add_port_dtype('Complex Integer 8' ,  2, '#cc00cc', 'sc8')

add_port_dtype('Integer 64',          8, '#99FF33', 's64')
add_port_dtype('Integer 32',          4, '#00FF99', 's32', 'int')
add_port_dtype('Integer 16',          2, '#FFFF66', 's16', 'short')
add_port_dtype('Integer 8' ,          1, '#FF66FF', 's8' , 'byte')  # uint?


class ParamType(object):

    def __init__(self, name, aliases):
        self.name = name
        self.aliases = aliases
