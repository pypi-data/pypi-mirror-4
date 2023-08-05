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

from bzrlib.commands import Command
from bzrlib.option import Option
from bzrlib.errors import BzrCommandError


class cmd_pqm_submit(Command):
    """Submit the parent tree to the pqm.

    This acts like:
        $ echo "star-merge $PARENT $TARGET"
            | gpg --cl
            | mail pqm@somewhere -s "merge text"

    But it pays attention to who the local committer is
    (using their e-mail address), and uses the local
    gpg signing configuration. (As well as target pqm
    settings, etc.)

    The reason we use 'parent' instead of the local branch
    is that most likely the local branch is not a public
    branch. And the branch must be available to the pqm.

    This can be configured at the branch level using ~/.bazaar/locations.conf.
    Here is an example:
        [/home/emurphy/repo]
        pqm_email = PQM <pqm@example.com>
        pqm_user_email = User Name <user@example.com>
        submit_branch = http://code.example.com/code/project/devel
        # Set public_branch appropriately for all branches in repository:
        public_branch = http://code.example.com/code/emurphy/project
        public_branch:policy = appendpath
        [/home/emurphy/repo/branch]
        # Override public_branch for this repository:
        public_branch = http://alternate.host.example.com/other/public/branch

        smtp_server = host:port
        smtp_username =
        smtp_password =

    If you don't specify the smtp server, the message will be sent via localhost.
    """

    takes_args = ['location?']
    takes_options = [
        Option('message',
               help='Message to use on merge to pqm.  '
                    'Currently must be a single line because of pqm limits.',
               short_name='m',
               type=unicode),
        Option('dry-run', help='Print request instead of sending.'),
        Option('public-location', type=str,
               help='Use this url as the public location to the pqm.'),
        Option('submit-branch', type=str,
               help='Use this url as the target submission branch.'),
        Option('ignore-local', help='Do not check the local branch or tree.'),
        ]

    def run(self, location=None, message=None, public_location=None,
            dry_run=False, submit_branch=None, ignore_local=False):
        from bzrlib import bzrdir
        from bzrlib.plugins.pqm.pqm_submit import submit

        if ignore_local:
            tree, b, relpath = None, None, None
        else:
            if location is None:
                location = '.'
            tree, b, relpath = bzrdir.BzrDir.open_containing_tree_or_branch(
                location)
            if b is not None:
                b.lock_read()
                self.add_cleanup(b.unlock)
        if relpath and not tree and location != '.':
            raise BzrCommandError(
                'No working tree was found, but we were not given the '
                'exact path to the branch.\n'
                'We found a branch at: %s' % (b.base,))
        if message is None:
            raise BzrCommandError(
                'You must supply a commit message for the pqm to use.')
        submit(b, message=message, dry_run=dry_run,
               public_location=public_location,
               submit_location=submit_branch,
               tree=tree, ignore_local=ignore_local)

class cmd_lp_land(Command):
    """Land the merge proposal for this branch via PQM.

    The branch will be submitted to PQM according to the merge proposal.  If
    there is more than one one outstanding proposal for the branch, its
    location must be specified.
    """

    takes_args = ['location?']

    takes_options = [
        Option('dry-run', help='Display the PQM message instead of sending.'),
        Option(
            'testfix',
            help="This is a testfix (tags commit with [testfix])."),
        Option(
            'no-qa',
            help="Does not require QA (tags commit with [no-qa])."),
        Option(
            'incremental',
            help="Incremental to other bug fix (tags commit with [incr])."),
        Option(
            'rollback', type=int,
            help=(
                "Rollback given revision number. (tags commit with "
                "[rollback=revno]).")),
        ]

    def run(self, location=None, dry_run=False, testfix=False,
            no_qa=False, incremental=False, rollback=None):
        from bzrlib.plugins.pqm.lpland import Submitter
        from bzrlib.plugins.pqm.lpland import (
            MissingReviewError, MissingBugsError, MissingBugsIncrementalError)

        if dry_run:
            outf = self.outf
        else:
            outf = None
        if rollback and (no_qa or incremental):
            print "--rollback option used. Ignoring --no-qa and --incremental."
        try:
            submitter = Submitter.from_cmdline(
                location, testfix, no_qa, incremental,
                rollback=rollback).run(outf)
        except MissingReviewError:
            raise BzrCommandError(
                "Cannot land branches that haven't got approved code "
                "reviews. Get an 'Approved' vote so we can fill in the "
                "[r=REVIEWER] section.")
        except MissingBugsError:
            raise BzrCommandError(
                "Branch doesn't have linked bugs and doesn't have no-qa "
                "option set. Use --no-qa, or link the related bugs to the "
                "branch.")
        except MissingBugsIncrementalError:
            raise BzrCommandError(
                "--incremental option requires bugs linked to the branch. "
                "Link the bugs or remove the --incremental option.")
