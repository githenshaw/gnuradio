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


from .. blocks import Block
from . import ParseXML



BLOCK_DTD = 'block.dtd'


def load_block_xml(xml_file):
    """Load block description from xml file"""

    # validate and import
    ParseXML.validate_dtd(xml_file, BLOCK_DTD)
    n = ParseXML.from_file(xml_file).find('block')


    n['block_wrapper_path'] = xml_file  # inject block wrapper path
    if 'domain' not in n:
        n['domain'] = None

    # get block instance and add it to the list of blocks
    block = construct_block_class_from_nested_data(n)

    return block

BLOCK_TEMPLATE = """\
class XMLBlock(Block):
    key    = "${ n['key'][0] }"
    name   = "${ n['name'][0] }"

    import_template = "${ n['import'][0] }"
    make_template   = "${ n['make'][0] }"

    def setup(self, **kwargs):
        super(XMLBlock, self).setup(**kwargs)

        # params
        % for param_n in n['params']:
        self.add_param(
            key = "${ param_n['key'] }",
            name = "${ param_n['name'] }",
            vtype = ${  },
            default = ${ param_n['value'] },
        )
        % endfor

        # sinks
        % for sink_n in n['sink']:
        self.add_port(
            name = ${  },
            type = ${  },
            vlen = ${  },
            nports = ${  },
            optional = ${  },
            hide = ${  },
        )
        % endfor

        # sources

"""


def construct_block_class_from_nested_data(nested_data):
    n = nested_data
    params = {params_n['key'][0]: params_n for params_n in n.get('params', [])}

    for key, params_n in params.iteritems():
        value = params_n['value'][0]
        vtype = params_n['type'][0]
        if '$' in vtype:
            print("Dynamic vtype for '{key:}': {vtype:}".format(**locals()))
        if vtype == 'str':
            value = _parse_string_literal(value)
    sinks = []
    for sink_n in n['sinks']:
        pass


    return 1



def _parse_string_literal(value):
    try:
        evaluated = eval(value, [])
        if isinstance(evaluated, str):
            value = evaluated
    except:
        pass
    return '"{}"'.format(value.replace('"', '\\"'))
