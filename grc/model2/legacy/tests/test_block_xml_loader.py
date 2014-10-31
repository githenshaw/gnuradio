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

from os import path
import glob

from .. import load_block_xml


def iter_test_files():
    test_file_dir = path.join(path.dirname(__file__), 'resources')
    for filename in glob.iglob(path.join(test_file_dir, '*.xml')):
        with open(filename) as fp:
            yield fp


def test_category_tree_xml():
    for fp in iter_test_files():
        BlockClass = load_block_xml(fp)
        print BlockClass

