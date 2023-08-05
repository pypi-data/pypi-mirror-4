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

import os
import sys
from shutil import rmtree

sys.path.append('.')


class Common:

    class Silence(object):

        def __enter__(self):
            self._stdout = sys.stdout
            self.null = open('/dev/null', 'wb')
            sys.stdout = self.null

        def __exit__(self, *ignored):
            sys.stdout = self._stdout

    def list_files(self, path):
        files = set()
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                files.add(os.path.join(dirname, filename))
        rmtree(path)
        return files
