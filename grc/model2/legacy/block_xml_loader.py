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


def load_block_xml(xml_file):
    """Load block description from xml file"""
    # validate and import
    ParseXML.validate_dtd(xml_file, _block_dtd)
    n = ParseXML.from_file(xml_file).find('block')
    n['block_wrapper_path'] = xml_file  # inject block wrapper path
    # get block instance and add it to the list of blocks
    block = Block(None, n)
    key = block.get_key()
    #if key in self.get_block_keys():  # test against repeated keys
    #    print >> sys.stderr, 'Warning: Block with key "%s" already exists.\n\tIgnoring: %s' % (key, xml_file)
    return block


def load_category_tree_xml(xml_file):
    """Validate and parse category tree file and add it to list"""

    #recursive function to load categories and blocks
    def load_category(n, parent):
        name = n.find('name') or ''
        path = parent + [str(name)] if name else parent
        # load sub-categories
        for sub_n in n.findall('cat'):
            # yield from =)
            for block_key, path in load_category(sub_n, path):
                yield block_key, path
        #add blocks in this category
        for block_key in n.findall('block'):
            yield block_key, path

    ParseXML.validate_dtd(xml_file, BLOCK_TREE_DTD)
    category_tree_n = ParseXML.from_file(xml_file).find('cat')
    load_category(category_tree_n, [])
