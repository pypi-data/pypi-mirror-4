# Copyright (C) 2011 by Canonical Ltd
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

from bzrlib.config import Option

pqm_user_email = Option('pqm_user_email',
    help='''\
From address to use for PQM submissions.

This defaults to the name and email address in the ``email`` setting.
''')
child_pqm_email = Option('child_pqm_email',
    help='''\
E-mail address for the PQM bot, for submissions of this branch.

See also the ``pqm_email`` setting.
''')
pqm_email = Option('pqm_email',
    help='''\
E-mail address of the PQM bot, for submissions from this branch.

This setting takes precedence over the ``child_pqm_email`` setting
in the submit branch.

See also the ``child_pqm_email` setting.
''')
pqm_bcc = Option('pqm_bcc',
    help='''\
List of addresses to BCC on PQM requests.
''')
