# Copyright (C) 2010-2012 by Canonical Ltd
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

"""Tools for landing branches with Launchpad."""

import os

from launchpadlib.launchpad import Launchpad
from launchpadlib.uris import (
    LPNET_SERVICE_ROOT,
    )
from lazr.uri import URI
from bzrlib import msgeditor
from bzrlib.errors import BzrCommandError
from bzrlib.plugins.pqm import pqm_submit
from bzrlib import smtp_connection
from bzrlib import ui


class MissingReviewError(Exception):
    """Raised when we try to get a review message without enough reviewers."""


class MissingBugsError(Exception):
    """Merge proposal has no linked bugs and no [no-qa] tag."""


class MissingBugsIncrementalError(Exception):
    """Merge proposal has the [incr] tag but no linked bugs."""


class LaunchpadBranchLander:

    name = 'launchpad-branch-lander'
    cache_dir = '~/.launchpadlib/cache'

    def __init__(self, launchpad):
        self._launchpad = launchpad

    @classmethod
    def load(cls, service_root=LPNET_SERVICE_ROOT):
        # XXX: JonathanLange 2009-09-24: No unit tests.
        cache_dir = os.path.expanduser(cls.cache_dir)
        # XXX: JonathanLange 2009-09-24 bug=435813: If cached data invalid,
        # there's no easy way to delete it and try again.
        launchpad = Launchpad.login_with(cls.name, service_root, cache_dir)
        return cls(launchpad)

    def load_merge_proposal(self, mp_url):
        """Get the merge proposal object for the 'mp_url'."""
        # XXX: JonathanLange 2009-09-24: No unit tests.
        web_mp_uri = URI(mp_url)
        api_mp_uri = self._launchpad._root_uri.append(
            web_mp_uri.path.lstrip('/'))
        return MergeProposal(self._launchpad.load(str(api_mp_uri)))

    def get_lp_branch(self, branch):
        """Get the launchpadlib branch based on a bzr branch."""
        # First try the public branch.
        branch_url = branch.get_public_branch()
        if branch_url:
            lp_branch = self._launchpad.branches.getByUrl(
                url=branch_url)
            if lp_branch is not None:
                return lp_branch
        # If that didn't work try the push location.
        branch_url = branch.get_push_location()
        if branch_url:
            lp_branch = self._launchpad.branches.getByUrl(
                url=branch_url)
            if lp_branch is not None:
                return lp_branch
        raise BzrCommandError(
            "No public branch could be found.  Please re-run and specify "
            "the URL for the merge proposal.")

    def get_merge_proposal_from_branch(self, branch):
        """Get the merge proposal from the branch."""

        lp_branch = self.get_lp_branch(branch)
        proposals = [
            mp for mp in lp_branch.landing_targets
            if mp.queue_status in ('Needs review', 'Approved')]
        if len(proposals) == 0:
            raise BzrCommandError(
                "The public branch has no active source merge proposals.  "
                "You must have a merge proposal before attempting to "
                "land the branch.")
        elif len(proposals) > 1:
            raise BzrCommandError(
                "The public branch has multiple active source merge "
                "proposals.  You must provide the URL to the one you wish to"
                " use.")
        return MergeProposal(proposals[0])


class MergeProposal:
    """Wrapper around launchpadlib `IBranchMergeProposal` for landing."""

    def __init__(self, mp):
        """Construct a merge proposal.

        :param mp: A launchpadlib `IBranchMergeProposal`.
        """
        self._mp = mp
        self._launchpad = mp._root

    @property
    def source_branch(self):
        """The push URL of the source branch."""
        return str(self._get_push_url(self._mp.source_branch)).rstrip('/')

    @property
    def target_branch(self):
        """The push URL of the target branch."""
        return str(self._get_push_url(self._mp.target_branch)).rstrip('/')

    @property
    def commit_message(self):
        """The commit message specified on the merge proposal."""
        return self._mp.commit_message

    @property
    def is_approved(self):
        """Is this merge proposal approved for landing."""
        return self._mp.queue_status == 'Approved'

    def get_stakeholder_emails(self):
        """Return a collection of people who should know about branch landing.

        Used to determine who to email with the ec2 test results.

        :return: A set of `IPerson`s.
        """
        # XXX: JonathanLange 2009-09-24: No unit tests.
        emails = set(
            map(get_email,
                [self._mp.source_branch.owner, self._launchpad.me]))
        emails.discard(None)
        return emails

    def get_reviews(self):
        """Return a dictionary of all Approved reviews.

        Used to determine who has actually approved a branch for landing. The
        key of the dictionary is the type of review, and the value is the list
        of people who have voted Approve with that type.

        Common types include 'code', 'db', 'ui' and of course `None`.
        """
        reviews = {}
        for vote in self._mp.votes:
            comment = vote.comment
            if comment is None or comment.vote != "Approve":
                continue
            reviewers = reviews.setdefault(vote.review_type, [])
            reviewers.append(vote.reviewer)
        if self.is_approved and not reviews:
            reviews[None] = [self._mp.reviewer]
        return reviews

    def get_bugs(self):
        """Return a collection of bugs linked to the source branch."""
        return self._mp.source_branch.linked_bugs

    def _get_push_url(self, branch):
        """Return the push URL for 'branch'.

        This function is a work-around for Launchpad's lack of exposing the
        branch's push URL.

        :param branch: A launchpadlib `IBranch`.
        """
        # XXX: JonathanLange 2009-09-24: No unit tests.
        return branch.composePublicURL(scheme="bzr+ssh")

    def get_commit_message(self, commit_text, testfix=False, no_qa=False,
                           incremental=False, rollback=None):
        """Get the Launchpad-style commit message for a merge proposal."""
        reviews = self.get_reviews()
        bugs = self.get_bugs()

        tags = ''.join([
            get_testfix_clause(testfix),
            get_reviewer_clause(reviews),
            get_bugs_clause(bugs),
            get_qa_clause(bugs, no_qa,
                incremental, rollback=rollback),
            ])

        return '%s %s' % (tags, commit_text)

class Submitter(object):
    """Class that submits a to PQM from a merge proposal."""

    def __init__(self, branch, mp, testfix=False, no_qa=False,
                 incremental=False, rollback=None):
        self.branch = branch
        self.mp = mp
        self.testfix = testfix
        self.no_qa = no_qa
        self.incremental = incremental
        self.rollback = rollback
        self.config = pqm_submit.get_stacked_config(self.branch, None)
        self.mail_from = pqm_submit.get_mail_from(self.config)

    @classmethod
    def from_cmdline(cls, location, testfix, no_qa, incremental, rollback):
        """Factory that returns a Submitter from commandline arguments."""
        from bzrlib import branch as _mod_branch
        branch = _mod_branch.Branch.open_containing('.')[0]
        lander = LaunchpadBranchLander.load()
        if location is None:
            mp = lander.get_merge_proposal_from_branch(branch)
        else:
            mp = lander.load_merge_proposal(location)
        return cls(branch, mp, testfix, no_qa, incremental, rollback)

    def submission(self):
        """Create a PQMSubmission for this Submitter."""
        submission = pqm_submit.PQMSubmission(self.branch,
            self.mp.source_branch, self.mp.target_branch, '')
        return submission

    @staticmethod
    def check_submission(submission):
        """Ensure the Submission is reasonable."""
        submission.check_tree()
        submission.check_public_branch()

    def set_message(self, submission):
        """Set the message of the Submission.

        This starts with automatic generation from merge proposal and branch
        properties, then allows the user to edit the values.
        """
        commit_message = self.mp.commit_message or ''
        start_message = self.mp.get_commit_message(commit_message,
            self.testfix, self.no_qa, self.incremental,
            rollback=self.rollback)
        prompt = ('Proposed commit message:\n%s\nEdit before sending'
                  % start_message)
        if commit_message == '' or ui.ui_factory.get_boolean(prompt):
            pqm_command = ''.join(submission.to_lines())
            unicode_message = msgeditor.edit_commit_message(
                'pqm command:\n%s' % pqm_command,
                start_message=start_message).rstrip('\n')
            message = unicode_message.encode('utf-8')
        else:
            message = start_message
        submission.message = message

    def make_submission_email(self, submission, sign=True):
        mail_to = pqm_submit.pqm_email(self.config, self.mp.target_branch)
        if not mail_to:
            raise pqm_submit.NoPQMSubmissionAddress(self.branch)
        return submission.to_email(self.mail_from, mail_to, sign=sign)

    def run(self, outf, sign=True):
        submission = self.submission()
        self.check_submission(submission)
        self.set_message(submission)
        email = self.make_submission_email(submission, sign=sign)
        if outf is not None:
            outf.write(email.as_string())
        else:
            smtp_connection.SMTPConnection(self.config).send_email(email)


def get_email(person):
    """Get the preferred email address for 'person'."""
    email_object = person.preferred_email_address
    # XXX: JonathanLange 2009-09-24 bug=319432: This raises a very obscure
    # error when the email address isn't set. e.g. with name12 in the sample
    # data. e.g. "httplib2.RelativeURIError: Only absolute URIs are allowed.
    # uri = tag:launchpad.net:2008:redacted".
    if email_object is None:
        return None # A team most likely.
    return email_object.email


def get_bugs_clause(bugs):
    """Return the bugs clause of a commit message.

    :param bugs: A collection of `IBug` objects.
    :return: A string of the form "[bug=A,B,C]".
    """
    if not bugs:
        return ''
    bug_ids = []
    for bug in bugs:
        for task in bug.bug_tasks:
            if (task.bug_target_name == 'launchpad'
                and task.status not in ['Fix Committed', 'Fix Released']):
                bug_ids.append(str(bug.id))
                break
    if not bug_ids:
        return ''
    return '[bug=%s]' % ','.join(bug_ids)


def get_testfix_clause(testfix=False):
    """Get the testfix clause."""
    if testfix:
        testfix_clause = '[testfix]'
    else:
        testfix_clause = ''
    return testfix_clause


def get_qa_clause(bugs, no_qa=False, incremental=False, rollback=None):
    """Check the no-qa and incremental options, getting the qa clause.

    The qa clause will always be or no-qa, or incremental, or no-qa and
    incremental, or a revno for the rollback clause, or no tags.

    See https://dev.launchpad.net/QAProcessContinuousRollouts for detailed
    explanation of each clause.
    """
    qa_clause = ""

    if not bugs and not no_qa and not incremental and not rollback:
        raise MissingBugsError

    if incremental and not bugs:
        raise MissingBugsIncrementalError

    if no_qa and incremental:
        qa_clause = '[no-qa][incr]'
    elif incremental:
        qa_clause = '[incr]'
    elif no_qa:
        qa_clause = '[no-qa]'
    elif rollback:
        qa_clause = '[rollback=%d]' % rollback
    else:
        qa_clause = ''

    return qa_clause


def get_reviewer_handle(reviewer):
    """Get the handle for 'reviewer'.

    The handles of reviewers are included in the commit message for Launchpad
    changes. Historically, these handles have been the IRC nicks. Thus, if
    'reviewer' has an IRC nickname for Freenode, we use that. Otherwise we use
    their Launchpad username.

    :param reviewer: A launchpadlib `IPerson` object.
    :return: unicode text.
    """
    irc_handles = reviewer.irc_nicknames
    for handle in irc_handles:
        if handle.network == 'irc.freenode.net':
            return handle.nickname
    return reviewer.name


def _comma_separated_names(things):
    """Return a string of comma-separated names of 'things'.

    The list is sorted before being joined.
    """
    return ','.join(sorted(thing.name for thing in things))


def get_reviewer_clause(reviewers):
    """Get the reviewer section of a commit message, given the reviewers.

    :param reviewers: A dict mapping review types to lists of reviewers, as
        returned by 'get_reviews'.
    :return: A string like u'[r=foo,bar][ui=plop]'.
    """
    # If no review type is specified it is assumed to be a code review.
    code_reviewers = reviewers.get(None, [])
    code_reviewers.extend(reviewers.get('', []))
    ui_reviewers = []
    rc_reviewers = []
    for review_type, reviewer in reviewers.items():
        if review_type is None:
            continue
        if review_type == '':
            code_reviewers.extend(reviewer)
        if 'code' in review_type or 'db' in review_type:
            code_reviewers.extend(reviewer)
        if 'ui' in review_type:
            ui_reviewers.extend(reviewer)
        if 'release-critical' in review_type:
            rc_reviewers.extend(reviewer)
    if not code_reviewers:
        raise MissingReviewError("Need approved votes in order to land.")
    if ui_reviewers:
        ui_clause = '[ui=%s]' % _comma_separated_names(ui_reviewers)
    else:
        ui_clause = ''
    if rc_reviewers:
        rc_clause = (
            '[release-critical=%s]' % _comma_separated_names(rc_reviewers))
    else:
        rc_clause = ''
    return '%s[r=%s]%s' % (
        rc_clause, _comma_separated_names(code_reviewers), ui_clause)
