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


from .. import Block
from . import ParseXML



BLOCK_DTD = 'block.dtd'


def load_block_xml(xml_file):
    """Load block description from xml file"""

    # validate and import
    ParseXML.validate_dtd(xml_file, BLOCK_DTD)
    n = ParseXML.from_file(xml_file).find('block')


    n['block_wrapper_path'] = xml_file  # inject block wrapper path
    if not 'domain' in n:
        n['domain'] = None

    # get block instance and add it to the list of blocks
    block = construct_block_class_from_nested_data(n)

    return block

BLOCK_TEMPLATE = """\
class XMLBlock(Block):
    key    = "{{ n['key'] }}"
    name   = "{{ n['name'] }}"
    domain = "{{ n['domain'] }}"

    def setup(self, **kwargs):
        super(XMLBlock, self).setup(**kwargs)

        # params
        {% for param_n in n['params'] %}
        self.add_param(
            key = "{{ param_n['name'] }}",
            name = "{{ param_n['name'] }}",
            value_type = {{  }},
            default_value = {{ }},
        )
        {% endfor %}

        # sinks
        {% for sink_n in n['sink'] %}
        self.add_port(
            name = {{  }},
            type = {{  }},
            vlen = {{  }},
        )
        {% endfor %}

        # source
        {% for source_n in n['source'] %}
        self.add_port()
        {% endfor %}
"""


def construct_block_class_from_nested_data(nested_data):
    n = nested_data

    class XMLBlock(Block):
        key = n['key']
        name = n['name']
        domain = None


    return XMLBlock


def str_to_cls_name(name):
    return name

