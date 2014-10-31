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

from lxml import etree
from os import path
from mako.template import Template

from .. blocks import Block
from .. params import OptionsParam
from .. ports import MessageSink, StreamSink

from . block_category_loader import xml_to_nested_data

BLOCK_DTD = etree.DTD(path.join(path.dirname(__file__), 'block.dtd'))


def load_block_xml(xml_file):
    """Load block description from xml file"""
    try:
        xml = etree.parse(xml_file).getroot()
        BLOCK_DTD.validate(xml)
    except etree.LxmlError:
        return

    n = xml_to_nested_data(xml)[1]
    n['block_wrapper_path'] = xml_file  # inject block wrapper path

    return construct_block_class_from_nested_data(n)


BLOCK_TEMPLATE = Template("""\
class XMLBlock(Block):
    key = "${ key }"
    name = "${ name }"

    import_template = "${ import_template }"
    make_template = "${ make_template }"

    def setup(self, **kwargs):
        super(XMLBlock, self).setup(**kwargs)

        # params
        % for kwargs in params:
        self.add_param(${ repr(kwargs) })
        % endfor

        # sinks
        % for kwargs in sinks:
        self.add_port()
        % endfor

        # sources
""")


def construct_block_class_from_nested_data(nested_data):
    n = nested_data

    params_raw = {
        param_n['key'][0]: {
            key: value[0]
            for key, value in param_n.iteritems()
        } for param_n in n.get('param', [])
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
            param['options'] = [[
                option_n['key'][0], option_n['name'][0],
                dict(opt_n.split(':', 2)
                    for (opt_n,) in option_n.get('opt', []) if ':' in opt_n
                )
            ] for option_n in param_n.get('options', [])]
        param['vtype'] = vtype or 'raw'
        if set_from: rewrites['vtype'] = set_from
        param['category'] = param_n.get('tab', [''])[0]
        #todo: parse hide tag
        value = param_n.get('value', None)[0]
        if value:
            param['value'] = value

        params.append(param)

    sinks = []
    for sink_n in n.get('sinks', []):
        sink = dict()
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

    return BLOCK_TEMPLATE.render(
        key=n['key'][0],
        name=n['name'][0],

        make_template=n['make'][0],
        import_template=n['import'][0],

        params=params,
        sinks=[],
    )



def _parse_string_literal(value):
    try:
        evaluated = eval(value, [])
        if isinstance(evaluated, str):
            value = evaluated
    except:
        pass
    return '"{}"'.format(value.replace('"', '\\"'))
