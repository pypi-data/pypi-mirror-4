#!/usr/bin/python
#
# Copyright (C) 2012 Luca Falavigna
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

import unittest

from common import Common
from XTree import Dir


class ZipFile(unittest.TestCase, Common):

    def test_dir(self):
        files = ('tests/dir/dir1.flat/bar|1|a',
                 'tests/dir/dir1.flat/bar|22|bb',
                 'tests/dir/dir1.flat/bar|333|ccc',
                 'tests/dir/dir1.flat/bar|foo1',
                 'tests/dir/dir1.flat/bar|foo2',
                 'tests/dir/dir1.flat/foo|bar1',
                 'tests/dir/dir1.flat/foo|bar2')
        with self.Silence():
            d = Dir.Dir('tests/dir/dir1')
            processed = self.list_files(d.flat_dir)
        self.assertEqual(set(files), processed)

    def test_dir_separator(self):
        files = ('tests/dir/dir1.flat/bar#1#a',
                 'tests/dir/dir1.flat/bar#22#bb',
                 'tests/dir/dir1.flat/bar#333#ccc',
                 'tests/dir/dir1.flat/bar#foo1',
                 'tests/dir/dir1.flat/bar#foo2',
                 'tests/dir/dir1.flat/foo#bar1',
                 'tests/dir/dir1.flat/foo#bar2')
        with self.Silence():
            d = Dir.Dir('tests/dir/dir1', '#')
            processed = self.list_files(d.flat_dir)
        self.assertEqual(set(files), processed)

    def test_dir_no_separator(self):
        files = ('tests/dir/dir1.flat/a',
                 'tests/dir/dir1.flat/bar1',
                 'tests/dir/dir1.flat/bar2',
                 'tests/dir/dir1.flat/bb',
                 'tests/dir/dir1.flat/ccc',
                 'tests/dir/dir1.flat/foo1',
                 'tests/dir/dir1.flat/foo2')
        with self.Silence():
            d = Dir.Dir('tests/dir/dir1', False)
            processed = self.list_files(d.flat_dir)
        self.assertEqual(set(files), processed)

    def test_dir_no_separator_exit(self):
        try:
            with self.Silence():
                d = Dir.Dir('tests/dir/dir2', False)
                processed = self.list_files(d.flat_dir)
        except SystemExit:
            pass
        else:
            self.fail('SystemExit exception expected')

    def test_dir_bad_separator(self):
        try:
            with self.Silence():
                d = Dir.Dir('tests/dir/dir3')
                processed = self.list_files(d.flat_dir)
        except SystemExit:
            pass
        else:
            self.fail('SystemExit exception expected')

    def test_dir_is_dir(self):
        try:
            with self.Silence():
                d = Dir.Dir('tests/tar/gzip1.tar.gz')
                processed = self.list_files(d.flat_dir)
        except SystemExit:
            pass
        else:
            self.fail('SystemExit exception expected')


if __name__ == '__main__':
    unittest.main()
