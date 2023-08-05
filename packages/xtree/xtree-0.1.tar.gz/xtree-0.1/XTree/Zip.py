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

import zipfile
from os.path import isfile, join
from shutil import rmtree
from tempfile import mkdtemp

from FileSystem import FileSystem


class Zip(FileSystem):

    def __init__(self, archive, separator='|', purge=False):
        self.archive = archive
        self.separator = separator
        self.purge = purge
        self.base_count = 0
        self.base_dir = None
        self.flat_dir = None
        self.elements = []
        self.files = []
        self.nopath = True
        try:
            self.zipfile = zipfile.ZipFile(self.archive)
        except (IOError, RuntimeError):
            print '%s is not a zipfile.' % self.archive
            exit()
        self.xtreeify()

    def list_files(self):
        tmpdir = mkdtemp(prefix='xtree')
        for name in self.zipfile.namelist():
            self.elements.append(name.strip('/'))
        self.zipfile.extractall(tmpdir)
        for elem in self.elements:
             if isfile(join(tmpdir, elem)):
                 self.files.append(elem)
        rmtree(tmpdir)

    def unpack(self):
        if self.nopath:
            path = '.'
        else:
            path = self.base_dir
        self.zipfile.extractall(path = path)
