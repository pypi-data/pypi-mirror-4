#!/usr/bin/env python

# Copyright (C) 2012 David Villa Alises
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from distutils.core import setup

setup(name         = 'python-bitbucket-api',
      version      = '0.20121010',
      description  = 'Bitbucket Python API and utilities',
      author       = 'David Villa Alises',
      author_email = '<David.Villa@gmail.com>',
      url          = 'https://bitbucket.org/DavidVilla/python-bitbucket-api',
      license      = 'GPL v2 or later',
      data_files   = [('/usr/bin', ['bin/bucket']),
                      ('/usr/lib/bucket', ['config.spec'])],
      packages     = ['bitbucket'],
      install_requires = ['python-commodity', 'requests']
      )
