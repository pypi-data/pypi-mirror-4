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

from distutils.core import setup


setup(name='xtree',
      version='0.2',
      author='Luca Falavigna',
      author_email='dktrkranz@debian.org',
      description='Gather files scattered across several subdirectories',
      long_description='''\
xtree can easily convert an archive or a directory populated by a lot of
nested subdirectories into a flat tree structure, or the other way round.

This is particularly useful to move files scattered across a lot of
subdirectories into a single directory, or to move files grouped by a
common pattern into corresponding subdirectories.''',
      url='https://github.com/dktrkranz/xtree',
      license='GNU GPL',
      platforms='OS Independent',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: '
                      'GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Topic :: Utilities'],
      packages=['XTree'],
      scripts=['xtree'],
      data_files=[('share/man/man1', ['doc/xtree.1'])])
