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

    for key in 'key name make import'.split():
        n[key] = n[key][0]

    params_raw = {
        param_n['key'][0]: {
            key: value[0]
            for key, value in params_n.iteritems()
        for params_n in n.get('params', [])
    }
    def resolve_template(expr):
        if '$' in expr:  # template
            try:
                param = params_raw[expr[1:]] # simple subst
                return param.get('value', None), param['key']
            except KeyError:
                pass
            # todo parse/eval advanced template
        return expr, None

    def set_optional(d, key, source, skey=None):
        value = source.get(skey or key, [None])[0]
        if value: d[key] = value

    params = []
    for key, param_n in params_raw.iteritems():
        param, rewrites = {}, {}
        param['key'] = param_n['key'][0]
        param['name'] = param_n['name'][0]
        vtype, set_from = resolve_template(param_n.get('type', ['raw'])[0])
        if vtype == 'enum':
            vtype = 'raw'
            param['cls'] = OptionsParam
            param['options'] = tuple(
                tuple(
                    option_n['key'][0],
                    option_n['name'][0],
                    dict(opt_n.split(':', 2)
                        for (opt_n,) in option_n.get('opt', []) if ':' in opt_n
                    )
                ) for option_n in params_.get(['options', [])
            )
        param['vtype'] = vtype or 'raw'
        if set_from: rewrites['vtype'] = set_from
        param['category'] = param_n.get('tab', [''])[0]
        #todo: parse hide tag
        value = param_n.get('value', None)[0]
        if value: param['value'] = value
        params.append(param)

    sinks = []
    for sink_n in n['sinks']:
        sink = {}
        sink['name'] = sink_n['name'][0]
        dtype, set_from = resolve_template(sink_n['type'][0])
        if dtype == 'message':
            sink['key'] = sink['name']
            sink['cls'] = MessageSink
        else:
            sink['dtype'] = dtype
            vlen = sink_n.get('vlen', [])[0]
            if vlen: sink['vlen'] = vlen

        sinks.append(sink)

    class XMLDefinedBlock(Block):
        key = n['key']
        name = n['name']

        make_template = n['make']
        import_templdate = n['import']

        def setup(self, **kwargs):
            super(XMLBlock, self).setup(**kwargs)

            for param, rewrites in params:
                self.add_param(**param).on_rewrite(*rewrites)

    return 1



def _parse_string_literal(value):
    try:
        evaluated = eval(value, [])
        if isinstance(evaluated, str):
            value = evaluated
    except:
        pass
    return '"{}"'.format(value.replace('"', '\\"'))
