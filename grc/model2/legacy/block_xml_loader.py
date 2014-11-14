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
<%!
    def to_func_args(kwargs):
        return ", ".join(
            "{}={}".format(key, repr(value))
            for key, value in kwargs.iteritems()
        )
%>
<%def name="on_rewrite(rewrites)">\\
% if rewrites:
.on_rewrite(
            ${ to_func_args(rewrites) }
        )\\
% endif
</%def>
class XMLBlock(Block):
    key = "${ key }"
    name = "${ name }"

    import_template = "${ import_template }"
    make_template = "${ make_template }"

    def setup(self, **kwargs):
        super(XMLBlock, self).setup(**kwargs)

        # params
        % for kwargs, rewrites in params:
        self.add_param(${ to_func_args(kwargs) })${ on_rewrite(rewrites) }
        % endfor

        # sinks
        % for method, kwargs, rewrites in sinks:
        self.${ method }(${ to_func_args(kwargs) })${ on_rewrite(rewrites) }
        % endfor

        # sources
        % for method, kwargs, rewrites in sources:
        self.${ method }(${ to_func_args(kwargs) })${ on_rewrite(rewrites) }
        % endfor
""")


class Resolver(object):

    def __init__(self, block_n):
        self.params = {
            param_n['key'][0]: param_n['value'][0]
            for param_n in block_n.get('param', [])
        }
        self.collected_rewrites = {}

    def pop_rewrites(self):
        rewrites = self.collected_rewrites
        self.collected_rewrites = {}
        return rewrites

    def eval(self, key, expr):
        if '$' in expr:  # template
            try:
                param_key = expr[1:]
                default = self.params[param_key] # simple subst
                self.collected_rewrites[key] = param_key
                return default
            except KeyError:
                pass
            # todo parse/eval advanced template
        return expr

    def get(self, namespace, key, key2=None):
        expr = self.get_raw(namespace, key)
        return self.eval(key2 or key, expr) if expr else expr

    @staticmethod
    def get_raw(namespace, key):
        items = namespace.get(key, [None])
        if not isinstance(items, str):
            items = items[0]
        return items


def construct_block_class_from_nested_data(nested_data):
    block_n = nested_data
    resolver = Resolver(block_n)
    params_raw = {
        param_n['key'][0]: {
            key: value[0]
            for key, value in param_n.iteritems()
        } for param_n in block_n.get('param', [])
    }

    def set_optional(d, key, source, skey=None):
        value = source.get(skey or key, [None])[0]
        if value: d[key] = value

    params = []
    for key, param_n in params_raw.iteritems():
        kwargs = {}
        kwargs['key'] = resolver.get(param_n, 'key')
        kwargs['name'] = resolver.get(param_n, 'name')
        vtype = resolver.get(param_n, 'type', 'vtype')
        if vtype == 'enum':
            vtype = 'raw'
            kwargs['cls'] = 'OptionsParam'
            kwargs['options'] = [[
                option_n['key'][0], option_n['name'][0],
                dict(opt_n.split(':', 2)
                    for (opt_n,) in option_n.get('opt', []) if ':' in opt_n
                )
            ] for option_n in param_n.get('options', [])]
        kwargs['vtype'] = vtype or 'raw'

        kwargs['category'] = resolver.get(param_n, 'tab') or ''
        #todo: parse hide tag
        value = resolver.get_raw(param_n, 'value')
        if value:
            kwargs['value'] = value

        params.append((kwargs, resolver.pop_rewrites()))

    def get_ports(direction):
        ports = []
        for n in block_n.get(direction, []):
            method_name = "add_stream_" + direction
            kwargs = dict()

            kwargs['name'] = n['name'][0]

            dtype = resolver.get(n, 'type', 'dtype')
            if dtype == 'message':
                method_name = "add_message_" + direction
                kwargs['key'] = kwargs['name']
            else:
                kwargs['dtype'] = dtype
                vlen = resolver.get(n, 'vlen')
                if vlen:
                    kwargs['vlen'] = int(vlen)

            ports.append((method_name, kwargs, resolver.pop_rewrites()))
        return ports

    return BLOCK_TEMPLATE.render(
        key=block_n['key'][0],
        name=block_n['name'][0],

        make_template=block_n['make'][0],
        import_template=block_n['import'][0],

        params=params,
        sinks=get_ports('sink'),
        sources=get_ports('source'),
    )



def _parse_string_literal(value):
    try:
        evaluated = eval(value, [])
        if isinstance(evaluated, str):
            value = evaluated
    except:
        pass
    return '"{}"'.format(value.replace('"', '\\"'))
