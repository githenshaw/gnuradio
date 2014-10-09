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

from . import ParseXML


BLOCK_TREE_DTD = 'block_tree.dtd'


def load_category_tree_xml(xml_file):
    """Validate and parse category tree file and add it to list"""

    #recursive function to load categories and blocks
    def _load_category(n, parent):
        name = n.get('name')
        path = parent + [str(name)] if name else parent
        # load sub-categories
        for sub_n in ParseXML.getall(n, 'cat'):
            for block_key, sub_categories in _load_category(sub_n, path):
                yield block_key, sub_categories  # yield from =)
        #add blocks in this category
        for block_key in ParseXML.getall(n, 'block'):
            yield block_key, path

    #ParseXML.validate_dtd(xml_file, BLOCK_TREE_DTD)
    category_tree_n = ParseXML.from_file(xml_file)['cat']
    # yield from =)
    for block_key, path in _load_category(category_tree_n, []):
        yield block_key, path
