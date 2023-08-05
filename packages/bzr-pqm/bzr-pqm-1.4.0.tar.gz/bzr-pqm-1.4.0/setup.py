#!/usr/bin/env python2.4
# Copyright (C) 2005-2008 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""A plugin for Bazaar for submitting commands to a PQM service."""

from setuptools import setup
import os

# Get version number from this copy of bzr-pqm:
globals = {}
execfile(os.path.join(os.path.dirname(__file__), '__init__.py'), globals)
version = globals['__version__']
del globals

setup(
    name='bzr-pqm',
    version=version,
    maintainer='John Arbash Meinel',
    maintainer_email='john@arbash-meinel.com',
    description='bzr plugin to submit an email to a Patch Queue Manager',
    license='GNU GPL v2',
    url='https://launchpad.net/bzr-pqm',
    packages=['bzrlib.plugins.pqm', 'bzrlib.plugins.pqm.tests'],
    package_dir={'bzrlib.plugins.pqm': '.'},
    install_requires=[
        'bzr',
        'launchpadlib',
        ],
    extras_require = dict(
        test=[
            'testtools',
            ]
        ),
)

