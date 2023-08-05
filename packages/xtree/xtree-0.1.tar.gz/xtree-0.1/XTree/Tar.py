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

import tarfile

from FileSystem import FileSystem


class Tar(FileSystem):

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
            self.tarball = tarfile.open(self.archive)
        except (IOError, tarfile.ReadError):
            print '%s is not a tarball.' % self.archive
            exit()
        self.xtreeify()

    def list_files(self):
        self.elements = self.tarball.getnames()
        for member in self.tarball.getmembers():
            if member.isfile():
                self.files.append(member.name)

    def unpack(self):
        if self.nopath:
            path = '.'
        else:
            path = self.base_dir
        self.tarball.extractall(path = path)
