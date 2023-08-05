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
"""Submit an email to a Patch Queue Manager"""

from bzrlib import (
    config as _mod_config,
    errors,
    gpg,
    osutils,
    urlutils,
    version_info as bzrlib_version,
    )
from bzrlib.branch import Branch
from bzrlib.email_message import EmailMessage
from bzrlib.smtp_connection import SMTPConnection
from bzrlib.trace import note


class BadCommitMessage(errors.BzrError):

    _fmt = "The commit message %(msg)r cannot be used by pqm."

    def __init__(self, msg):
        errors.BzrError.__init__(self)
        self.msg = msg


class NoPQMSubmissionAddress(errors.BzrError):

    _fmt = "No PQM submission email address specified for %(branch_url)s."

    def __init__(self, branch):
        if (branch is None) or (branch.base is None):
            branch_url = '(none)'
        else:
            branch_url = urlutils.unescape_for_display(branch.base, 'ascii')
        errors.BzrError.__init__(self, branch_url=branch_url)


class PQMEmailMessage(EmailMessage):
    """PQM doesn't support proper email subjects, so we hack around it."""

    def __init__(self, from_address, to_address, subject, body=None):
        EmailMessage.__init__(self, from_address=from_address,
                              to_address=to_address, subject=subject,
                              body=body)
        # Now override self.Subject to use raw utf-8
        self._headers['Subject'] = osutils.safe_unicode(subject).encode('UTF-8')


class PQMSubmission(object):
    """A request to perform a PQM merge into a branch."""

    def __init__(self, source_branch, public_location=None,
                 submit_location=None, message=None,
                 tree=None):
        """Create a PQMSubmission object.

        :param source_branch: the source branch for the merge
        :param public_location: the public location of the source branch
        :param submit_location: the location of the target branch
        :param message: The message to use when committing this merge
        :param tree: A WorkingTree or None. If not None the WT will be checked
            for uncommitted changes.

        If any of public_location, submit_location or message are
        omitted, they will be calculated from source_branch.
        """
        if source_branch is None and public_location is None:
            raise errors.NoMergeSource()
        self.source_branch = source_branch
        self.tree = tree

        if public_location is None:
            public_location = self.source_branch.get_public_branch()
            if public_location is None:
                raise errors.NoPublicBranch(self.source_branch)
        self.public_location = public_location

        if submit_location is None:
            if self.source_branch is None:
                raise errors.BzrError(
                    "Cannot determine submit location to use.")
            config = self.source_branch.get_config()
            submit_location = self.source_branch.get_submit_branch()

            if submit_location is None:
                raise errors.NoSubmitBranch(self.source_branch)
            # See if the submit_location has a public branch
            try:
                submit_branch = Branch.open(submit_location)
            except errors.NotBranchError:
                pass
            else:
                submit_public_location = submit_branch.get_public_branch()
                if submit_public_location is not None:
                    submit_location = submit_public_location
        self.submit_location = submit_location

        # Check that the message is okay to pass to PQM
        assert message is not None
        self.message = message.encode('utf8')
        if '\n' in self.message:
            raise BadCommitMessage(self.message)

    def check_tree(self):
        """Check that the working tree has no uncommitted changes."""
        if self.tree is None:
            return
        note('Checking the working tree is clean ...')
        self.tree.lock_read()
        try:
            basis_tree = self.tree.basis_tree()
            basis_tree.lock_read()
            try:
                for change in self.tree.iter_changes(basis_tree):
                    # If we have any changes, the tree is not clean
                    raise errors.UncommittedChanges(self.tree)
            finally:
                basis_tree.unlock()
        finally:
            self.tree.unlock()

    def check_public_branch(self):
        """Check that the public branch is up to date with the local copy."""
        note('Checking that the public branch is up to date at\n    %s',
             urlutils.unescape_for_display(self.public_location, 'utf-8'))
        local_revision = self.source_branch.last_revision()
        public_revision = Branch.open(self.public_location).last_revision()
        if local_revision != public_revision:
            raise errors.PublicBranchOutOfDate(
                self.public_location, local_revision)

    def to_lines(self):
        """Serialise as a list of lines."""
        return ['star-merge %s %s\n' % (self.public_location, self.submit_location)]

    def to_signed(self):
        """Serialize as a signed string."""
        unsigned_text = ''.join(self.to_lines())
        unsigned_text = unsigned_text.encode('ascii') #URLs should be ascii

        if bzrlib_version < (2, 5):
            if self.source_branch:
                config = self.source_branch.get_config()
            else:
                config = _mod_config.GlobalConfig()
        else:
            if self.source_branch:
                config = self.source_branch.get_config_stack()
            else:
                config = _mod_config.GlobalStack()
        strategy = gpg.GPGStrategy(config)
        return strategy.sign(unsigned_text)

    def to_email(self, mail_from, mail_to, sign=True):
        """Serialize as an email message.

        :param mail_from: The from address for the message
        :param mail_to: The address to send the message to
        :param sign: If True, gpg-sign the email
        :return: an email message
        """
        if sign:
            body = self.to_signed()
        else:
            body = ''.join(self.to_lines())
        message = PQMEmailMessage(mail_from, mail_to, self.message, body)
        return message


class StackedConfig(_mod_config.Config):

    def __init__(self):
        super(StackedConfig, self).__init__()
        self._sources = []

    def add_source(self, source):
        self._sources.append(source)

    def _get_user_option(self, option_name):
        """See Config._get_user_option."""
        for source in self._sources:
            value = source._get_user_option(option_name)
            if value is not None:
                return value
        return None

    def get(self, option_name):
        """Return an option exactly as bzrlib.config.Stack would.

        Since Stack allows the environment to override 'email', this uses the
        same logic.
        """
        if option_name == 'email':
            return self.username()
        else:
            return self._get_user_option(option_name)

    def _get_user_id(self):
        for source in self._sources:
            value = source._get_user_id()
            if value is not None:
                return value
        return None

    def set(self, name, value):
        self._sources[0].set_user_option(name, value)


def pqm_email(local_config, submit_location):
    """Determine the PQM email address.

    :param local_config: Config object for local branch
    :param submit_location: Location of submit branch
    """
    mail_to = local_config.get('pqm_email')
    if not mail_to:
        submit_branch = Branch.open(submit_location)
        submit_branch_config = get_stacked_config(submit_branch)
        mail_to = submit_branch_config.get('child_pqm_email')
        if mail_to is None:
            return None
    return mail_to.encode('utf8') # same here


def get_stacked_config(branch=None, public_location=None):
    """Return the relevant stacked config.

    If the branch is supplied, a branch stacked config is returned.
    Otherwise, if the public location is supplied, a stacked location config
    is returned.
    Otherwise, a global config is returned.

    For bzr versions earlier than 2.5, pqm_submit.StackedConfig is used.  For
    later versions, the standard stacked config is used.

    :param branch: The branch to retrieve the config for.
    :param public_location: The public location to retrieve the config for.
    """
    if bzrlib_version < (2, 5):
        config = StackedConfig()
        if branch:
            config.add_source(branch.get_config())
        else:
            if public_location:
                config.add_source(_mod_config.LocationConfig(public_location))
            config.add_source(_mod_config.GlobalConfig())
    else:
        if branch:
            config = branch.get_config_stack()
        elif public_location:
            config = _mod_config.LocationStack(public_location)
        else:
            config = _mod_config.GlobalStack()
    return config


def get_mail_from(config):
    """Return the email id that the email is from.

    :param config: The config to use for determining the from address.
    """
    mail_from = config.get('pqm_user_email')
    if not mail_from:
        mail_from = config.get('email')
    mail_from = mail_from.encode('utf8') # Make sure this isn't unicode
    return mail_from


def submit(branch, message, dry_run=False, public_location=None,
           submit_location=None, tree=None, ignore_local=False):
    """Submit the given branch to the pqm."""
    config = get_stacked_config(branch, public_location)
    submission = PQMSubmission(
        source_branch=branch, public_location=public_location, message=message,
        submit_location=submit_location,
        tree=tree)

    mail_from = get_mail_from(config)
    mail_to = pqm_email(config, submit_location)
    if not mail_to:
        raise NoPQMSubmissionAddress(branch)

    if not ignore_local:
        submission.check_tree()
        submission.check_public_branch()

    message = submission.to_email(mail_from, mail_to)

    mail_bcc = config.get('pqm_bcc')
    if mail_bcc is not None:
        message["Bcc"] = mail_bcc

    if dry_run:
        print message.as_string()
        return

    SMTPConnection(config).send_email(message)
