#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
  

from distutils.core import setup
import os.path

description = file(os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="timeline",
      version="0.0.4",
      description="Timeline module for modelling a series of actions.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/python-timeline",
      packages=['timeline'],
      package_dir = {'':'.'},
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      install_requires = [
          'pytz',
          ],
      extras_require = dict(
          test=[
              'testtools',
              ]
          ),
      )
