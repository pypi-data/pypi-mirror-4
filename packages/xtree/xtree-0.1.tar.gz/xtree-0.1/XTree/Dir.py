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

from FileSystem import FileSystem


class Dir(FileSystem):

    def __init__(self, archive, separator='|', purge=False):
        self.archive = archive
        self.separator = separator
        self.purge = purge
        self.base_dir = None
        self.flat_dir = None
        self.files = []
        if not os.path.isdir(self.archive):
            print '%s is not a directory.' % self.archive
            exit()
        self.xtreeify()

    def list_files(self):
        for root, subfolders, files in os.walk(self.archive):
            for file in files:
                self.files.append(os.path.join(root, file))

    def unpack(self):
        pass
