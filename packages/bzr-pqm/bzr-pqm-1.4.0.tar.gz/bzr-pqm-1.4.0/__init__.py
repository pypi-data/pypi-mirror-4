# Copyright (C) 2006-2012 by Canonical Ltd
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
"""Functionality for controlling a Patch Queue Manager (pqm).
"""

from __future__ import absolute_import

from bzrlib import version_info as bzrlib_version
from bzrlib.commands import plugin_cmds


version_info = (1, 4, 0, 'final', 0)

if version_info[3] == 'final':
    version_string = '%d.%d.%d' % version_info[:3]
else:
    version_string = '%d.%d.%d%s%d' % version_info
__version__ = version_string


plugin_cmds.register_lazy("cmd_pqm_submit", [], 'bzrlib.plugins.pqm.cmds')
plugin_cmds.register_lazy("cmd_lp_land", [], 'bzrlib.plugins.pqm.cmds')

if bzrlib_version >= (2, 5):
    from bzrlib import config as _mod_config
    _mod_config.option_registry.register_lazy('pqm_user_email',
        'bzrlib.plugins.pqm.config', 'pqm_user_email')
    _mod_config.option_registry.register_lazy('child_pqm_email',
        'bzrlib.plugins.pqm.config', 'child_pqm_email')
    _mod_config.option_registry.register_lazy('pqm_email',
        'bzrlib.plugins.pqm.config', 'pqm_email')
    _mod_config.option_registry.register_lazy('pqm_bcc',
        'bzrlib.plugins.pqm.config', 'pqm_bcc')


def test_suite():
    from bzrlib.tests import TestLoader
    from unittest import TestSuite

    from bzrlib.plugins.pqm.tests import test_lpland, test_pqm_submit

    loader = TestLoader()
    return TestSuite([
        loader.loadTestsFromModule(test_pqm_submit),
        loader.loadTestsFromModule(test_lpland),
        ])
