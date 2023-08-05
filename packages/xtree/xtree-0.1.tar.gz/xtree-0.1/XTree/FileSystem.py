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

import os
from shutil import rmtree


class FileSystem():

    def __init__(self):
        pass

    def checks(self):
        self.list_files()
        if not self.separator:
            files = [os.path.basename(f) for f in self.files]
            if len(files) != len(set(files)):
                print 'Duplicated file names found, use --separator option'
                exit()
        if self.separator:
            for f in self.files:
                if self.separator in f:
                    print '"%s" cannot be used as separator' % self.separator
                    exit()

    def cleanup(self):
        if self.base_dir:
            rmtree(self.base_dir)
        if self.purge:
            print 'Press any key to delete %s' % self.flat_dir
            raw_input()
            rmtree(self.flat_dir)

    def create_links(self):
        for src in self.files:
            if self.separator:
                dst = self.separator.join(src.split('/')[1:])
            else:
                dst = os.path.basename(src)
            os.link(src, os.path.join(self.flat_dir, dst))

    def directory_names(self):
        if os.path.isdir(self.archive):
            self.flat_dir = self.archive + '.flat'
        else:
            for elem in self.elements:
                if '/' in elem:
                    continue
                self.base_count += 1
                if elem not in self.files:
                    self.base_dir = elem
            if self.base_count > 1:
                self.base_dir = os.path.splitext(self.archive)[0]
                self.nopath = False
            self.flat_dir = self.base_dir + '.flat'

    def xtreeify(self):
        self.checks()
        self.directory_names()
        self.unpack()
        try:
            os.mkdir(self.flat_dir)
        except OSError:
            print 'Directory %s is already defined' % self.flat_dir
            exit()
        self.create_links()
        self.cleanup()
