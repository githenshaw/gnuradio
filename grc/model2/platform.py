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

from __future__ import absolute_import, division, print_function

import os
from itertools import imap
from collections import defaultdict

from . _consts import BLOCK_CLASS_FILE_EXTENSION, BLOCK_XML_EXTENSION, BLOCK_TREE_EXTENSION
from . import legacy
from . types import ParamVType, PortDType


class BlockLoadException(Exception):
    pass


class Platform(object):

    param_vtypes = {}
    port_dtypes = {}

    def __init__(self, name, website, version, block_paths):
        """
        Make a platform from the arguments.

        Args:
            name: the platform name
            block_paths: the file paths to blocks in this platform
            license: a multi-line license (first line is copyright)
            website: the website url for this platform

        Returns:
            a platform object
        """
        self._name = name
        self._license = __doc__
        self._website = website

        self._version, self._version_major, self._version_api, self._version_minor = version
        self._version_short = version[1] + "." + version[2] + "." + version[3]

        self._block_paths = block_paths

        self.blocks = {}

    def load_blocks(self):
        """load the blocks and block tree from the search paths"""
        # reset
        self.blocks.clear()
        categories = defaultdict(set)
        # first, load category tree files
        for block_tree_file in self.iter_block_files(BLOCK_TREE_EXTENSION):
            try:
                for key, category in legacy.load_category_tree_xml(block_tree_file):
                    categories[key] += category
            except BlockLoadException:
                # TODO: better use warnings here?
                pass

        for block_class_file in self.iter_block_files():
            try:
                block = self.import_block_class_file(block_class_file)
                self.blocks[block.key] = block
                pass
            except BlockLoadException:
                # TODO: better use warnings here?
                pass

        for block_tree_file in self.iter_block_files(BLOCK_XML_EXTENSION):
            try:
                if block_tree_file.endswith(BLOCK_TREE_EXTENSION):
                    self.load_category_tree_xml(block_tree_file)
                else:
                    self.load_block_xml(block_tree_file)
            except BlockLoadException:
                # TODO: better use warnings here?
                pass

    def iter_block_files(self, suffix='grc.py'):
        """Iterator for block classes (legacy: block xml and category trees)"""
        get_path = lambda x: os.path.abspath(os.path.expanduser(x))
        for block_path in imap(get_path, self._block_paths):
            if os.path.isfile(block_path):
                yield block_path
            elif os.path.isdir(block_path):
                for dirpath, dirnames, filenames in os.walk(block_path):
                    for filename in sorted(filter(lambda f: f.endswith(suffix), filenames)):
                        yield os.path.join(dirpath, filename)

    def import_block_class_file(self, filename):
        """import filename and save all subclasses of Block in library"""
        block = NotImplemented
        return block

    def __repr__(self):
        return '{}(name="{}", ...)'.format(self.__class__.__name__, self.name)

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def version_short(self):
        return self._version_short

    @property
    def license(self):
        return self._license

    @property
    def website(self):
        return self._website

    @property
    def block_paths(self):
        return self._block_paths

    @classmethod
    def register_param_vtype(cls, param_type):
        if not isinstance(param_type, ParamVType):
            raise Exception("")

        for name in param_type.names:
            cls.param_vtypes[name] = param_type

    @classmethod
    def register_port_dtype(cls, port_dtype):
        if not isinstance(port_dtype, PortDType):
            raise Exception("")
        for name in port_dtype.names:
            cls.port_dtypes[name] = port_dtype
