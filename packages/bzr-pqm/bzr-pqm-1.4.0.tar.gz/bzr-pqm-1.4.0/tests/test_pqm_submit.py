# Copyright (C) 2006-2010, 2012 by Canonical Ltd
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
"""Test cases for pqm submit."""

import smtplib

from bzrlib import (
    config as _mod_config,
    errors,
    gpg,
    )
from bzrlib.plugins.pqm import pqm_submit
from bzrlib.tests import TestCaseWithMemoryTransport, TestCaseWithTransport


EMAIL = """\
From: "J. Random Hacker" <jrandom@example.com>
Subject: commit message
To: PQM <pqm@example.com>
User-Agent: Bazaar \(.*\)

-----BEGIN PSEUDO-SIGNED CONTENT-----
star-merge .*/public/ .*/submit/
-----END PSEUDO-SIGNED CONTENT-----
"""


class PQMSubmissionTests(TestCaseWithMemoryTransport):

    def test_no_source_branch(self):
        self.assertRaises(
            errors.NoMergeSource, pqm_submit.PQMSubmission,
            source_branch=None)

    def test_newlines_in_message(self):
        source_branch = self.make_branch('source')
        self.assertRaises(pqm_submit.BadCommitMessage,
                          pqm_submit.PQMSubmission,
                          source_branch=source_branch,
                          public_location='public-branch',
                          submit_location='submit-branch',
                          message='foo\nbar')

    def test_check_tree_clean(self):
        tree = self.make_branch_and_memory_tree('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=tree.branch,
            public_location=tree.branch.base,
            submit_location='submit-branch',
            message='not much to say',
            tree=tree,
            )
        submission.check_tree()

    def test_check_tree_no_tree(self):
        branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=branch,
            public_location=branch.base,
            submit_location='submit-branch',
            message='not much to say',
            tree=None,
            )
        submission.check_tree()

    def test_check_tree_dirty(self):
        tree = self.make_branch_and_memory_tree('source')
        tree.lock_write()
        try:
            tree.add('')

            submission = pqm_submit.PQMSubmission(
                source_branch=tree.branch,
                public_location=tree.branch.base,
                submit_location='submit-branch',
                message='not much to say',
                tree=tree,
                )
            self.assertRaises(errors.UncommittedChanges, submission.check_tree)
        finally:
            tree.unlock()

    def test_check_public_branch(self):
        tree = self.make_branch_and_memory_tree('source')
        source_branch = tree.branch
        public_branch = self.make_branch('public')

        # Commit something to the source branch
        tree.lock_write()
        tree.add('')
        tree.commit('message')
        tree.unlock()

        # Now the public branch is out of date:
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location=public_branch.base,
            submit_location='submit-branch',
            message='merge message')
        self.assertRaises(errors.PublicBranchOutOfDate,
                          submission.check_public_branch)

        # If we bring the public branch up to date, everything is fine.
        public_branch.pull(source_branch)
        submission.check_public_branch()

    def test_check_public_branch_missing(self):
        source_branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location=self.get_transport().abspath('public'),
            submit_location='submit-branch',
            message='merge message')
        self.assertRaises(errors.NotBranchError,
                          submission.check_public_branch)

    def test_ignore_local(self):
        submission = pqm_submit.PQMSubmission(
            source_branch=None,
            public_location='public-location',
            submit_location='submit-branch',
            message='merge message')
        message = submission.to_email('from@address', 'to@address', sign=False)
        self.assertContainsRe(
            message.as_string(), 'star-merge public-location submit-branch')

    def test_to_lines(self):
        source_branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public-branch',
            submit_location='submit-branch',
            message='commit message')
        lines = submission.to_lines()
        self.assertEqual(['star-merge public-branch submit-branch\n'], lines)

    def test_to_signed(self):
        source_branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public-branch',
            submit_location='submit-branch',
            message='commit message')
        old_strategy = gpg.GPGStrategy
        gpg.GPGStrategy = gpg.LoopbackGPGStrategy
        try:
            signed = submission.to_signed()
        finally:
            gpg.GPGStrategy = old_strategy
        self.assertEqual('-----BEGIN PSEUDO-SIGNED CONTENT-----\n'
                         'star-merge public-branch submit-branch\n'
                         '-----END PSEUDO-SIGNED CONTENT-----\n', signed)

    def test_to_email(self):
        source_branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public-branch',
            submit_location='submit-branch',
            message='commit message')
        message = submission.to_email('from@example.com', 'to@example.com',
                                      sign=False)
        self.assertEqual('from@example.com', message.get('From'))
        self.assertEqual('to@example.com', message.get('To'))
        self.assertEqual('commit message', message.get('Subject'))

    def test_to_unicode_email(self):
        """Subject has to be raw UTF-8 not email encoded."""
        source_branch = self.make_branch('source')
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public-branch',
            submit_location='submit-branch',
            message=u'Commit m\xe5ss\xb5ge')
        message = submission.to_email('from@example.com', 'to@example.com',
                                      sign=False)
        self.assertEqual('from@example.com', message.get('From'))
        self.assertEqual('to@example.com', message.get('To'))
        self.assertEqual('Commit m\xc3\xa5ss\xc2\xb5ge',
                         message.get('Subject'))

    def test_submit_branch_public_location(self):
        source_branch = self.make_branch('source')
        public_branch = self.make_branch('public')
        submit_branch = self.make_branch('submit')
        submit_public_branch = self.make_branch('submit_public')
        submit_branch.set_public_branch(submit_public_branch.base)
        source_branch.set_submit_branch(submit_branch.base)
        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public',
            message=u'Commit m\xe5ss\xb5ge')
        self.assertEqual(submit_public_branch.base, submission.submit_location)


class PQMSubmissionLocationsTests(TestCaseWithTransport):

    def test_find_public_branch(self):
        source_branch = self.make_branch('source')
        source_branch.set_public_branch('http://example.com/public')
        # Also set the deprecated public_repository config item to
        # show that public_branch is used in preference to it.
        source_branch.get_config().set_user_option(
            'public_repository', 'bad-value')

        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            submit_location='submit-branch',
            message='commit message')
        self.assertEqual('http://example.com/public',
                         submission.public_location)

    def test_find_public_branch_missing(self):
        source_branch = self.make_branch('source')
        self.assertRaises(
            errors.NoPublicBranch, pqm_submit.PQMSubmission,
            source_branch=source_branch,
            submit_location='submit-branch',
            message='commit message')

    def test_find_submit_branch(self):
        source_branch = self.make_branch('source')
        submit_transport = self.get_transport().clone('submit')
        submit_transport.ensure_base()
        source_branch.set_submit_branch(submit_transport.base)

        submission = pqm_submit.PQMSubmission(
            source_branch=source_branch,
            public_location='public-branch',
            message='commit message')
        self.assertEqual(submit_transport.base, submission.submit_location)

    def test_find_submit_branch_missing(self):
        source_branch = self.make_branch('source')
        self.assertRaises(
            errors.NoSubmitBranch, pqm_submit.PQMSubmission,
            source_branch=source_branch,
            public_location='public-branch',
            message='commit message')

    def run_bzr_fakemail(self, *args, **kwargs):
        # Run with fake smtplib and gpg stubs in place:
        sendmail_calls = []
        def sendmail(self, from_, to, message):
            sendmail_calls.append((self, from_, to, message))
        connect_calls = []
        def connect(self, host='localhost', port=0):
            connect_calls.append((self, host, port))
        def ehlo(self):
            return (200, 'Ok')
        def has_extn(self, extn):
            return False
        def starttls(self):
            pass
        old_sendmail = smtplib.SMTP.sendmail
        smtplib.SMTP.sendmail = sendmail
        old_connect = smtplib.SMTP.connect
        smtplib.SMTP.connect = connect
        old_ehlo = smtplib.SMTP.ehlo
        smtplib.SMTP.ehlo = ehlo
        old_has_extn = smtplib.SMTP.has_extn
        smtplib.SMTP.has_extn = has_extn
        old_starttls = smtplib.SMTP.starttls
        smtplib.SMTP.starttls = starttls
        old_strategy = gpg.GPGStrategy
        gpg.GPGStrategy = gpg.LoopbackGPGStrategy
        try:
            result = self.run_bzr(*args, **kwargs)
        finally:
            smtplib.SMTP.sendmail = old_sendmail
            smtplib.SMTP.connect = old_connect
            smtplib.SMTP.ehlo = old_ehlo
            smtplib.SMTP.has_extn = old_has_extn
            smtplib.SMTP.starttls = old_starttls
            gpg.GPGStrategy = old_strategy

        return result + (connect_calls, sendmail_calls)

    def test_pqm_submit(self):
        source_branch = self.make_branch('source')
        public_branch = self.make_branch('public')
        source_branch.set_public_branch(public_branch.base)
        submit_transport = self.get_transport().clone('submit')
        submit_transport.ensure_base()
        source_branch.set_submit_branch(submit_transport.base)
        config = source_branch.get_config()
        config.set_user_option('pqm_email', 'PQM <pqm@example.com>')
        config.set_user_option(
            'email', 'J. Random Hacker <jrandom@example.com>')

        out, err, connect_calls, sendmail_calls = \
            self.run_bzr_fakemail(['pqm-submit', '-m', 'commit message',
                                   './source'])
        self.assertEqual('', out)
        self.assertEqual(1, len(connect_calls))
        call = connect_calls[0]
        self.assertEqual(('localhost', 0), call[1:3])
        self.assertEqual(1, len(sendmail_calls))
        call = sendmail_calls[0]
        self.assertEqual(('jrandom@example.com', ['pqm@example.com']),
                         call[1:3])
        self.assertContainsRe(call[3], EMAIL)

    def test_pqm_submit_no_message(self):
        tree = self.make_branch_and_tree('source')
        tree.commit("one")
        out, err, connect_calls, sendmail_calls = \
            self.run_bzr_fakemail(['pqm-submit', './source'],
                                  retcode=3)
        self.assertContainsRe(err, 'You must supply a commit message')

    def test_dirty_pqm_submit(self):
        source_tree = self.make_branch_and_tree('source')
        self.build_tree(['source/foo'])
        source_tree.add(['foo'])

        public_branch = self.make_branch('public')
        source_tree.branch.set_public_branch(public_branch.base)
        submit_transport = self.get_transport().clone('submit')
        submit_transport.ensure_base()
        source_tree.branch.set_submit_branch(submit_transport.base)
        config = source_tree.branch.get_config()
        config.set_user_option('pqm_email', 'PQM <pqm@example.com>')
        config.set_user_option(
            'email', 'J. Random Hacker <jrandom@example.com>')

        out, err, connect_calls, sendmail_calls = \
            self.run_bzr_fakemail(['pqm-submit', '-m', 'commit message',
                                   './source'],
                                  retcode=3)
        self.assertContainsRe(err,
            r'Working tree ".*/source/" has uncommitted changes')

    def test_submit_subdir_of_branch(self):
        source_branch = self.make_branch('source')
        source_branch.set_submit_branch('http://example.com/submit')
        config = source_branch.get_config()
        out, err, connect_calls, sendmail_calls = \
            self.run_bzr_fakemail(['pqm-submit', '-m', 'commit message',
                                   './source/subdir'],
                                  retcode=3)
        self.assertContainsRe(err, 'bzr: ERROR: No working tree was found')

    def test_submit_branch(self):
        """Test that --submit-branch overrides local config."""
        source_branch = self.make_branch('source')
        public_branch = self.make_branch('public')
        source_branch.set_public_branch(public_branch.base)
        source_branch.set_submit_branch('http://a/very/different/branch')
        config = source_branch.get_config()
        config.set_user_option('pqm_email', 'PQM <pqm@example.com>')
        config.set_user_option(
            'email', 'J. Random Hacker <jrandom@example.com>')

        (out, err, connect_calls,
         sendmail_calls) = self.run_bzr_fakemail(
                ['pqm-submit', '-m', 'commit message',
                 '--submit-branch', 'http://example.com/submit/',
                 './source'
                ])
        self.assertEqual('', out)
        self.assertEqual(1, len(connect_calls))
        call = connect_calls[0]
        self.assertEqual(('localhost', 0), call[1:3])
        self.assertEqual(1, len(sendmail_calls))
        call = sendmail_calls[0]
        self.assertEqual(('jrandom@example.com', ['pqm@example.com']),
                         call[1:3])
        self.assertContainsRe(call[3], EMAIL)

    def test_ignore_local(self):
        """--ignore-local can submit a branch that isn't available locally.
        
        It will use the location config of the public location to determine the
        from and to email addresses.
        """
        config = _mod_config.LocationConfig('http://example.com/')
        config.set_user_option('pqm_email', 'PQM <pqm@example.com>')
        config.set_user_option(
            'pqm_user_email', 'J. Random Hacker <jrandom@example.com>')
        (out, err, connect_calls,
         sendmail_calls) = self.run_bzr_fakemail(
                ['pqm-submit', '-m', 'commit message',
                 '--submit-branch', 'http://example.com/submit/',
                 '--ignore-local', '--public-location',
                 'http://example.com/public/'
                ])
        self.assertEqual('', out)
        self.assertEqual(1, len(connect_calls))
        call = connect_calls[0]
        self.assertEqual(('localhost', 0), call[1:3])
        self.assertEqual(1, len(sendmail_calls))
        call = sendmail_calls[0]
        self.assertEqual(('jrandom@example.com', ['pqm@example.com']),
                         call[1:3])
        self.assertContainsRe(call[3], EMAIL)

    def test_ignore_local_global_config_fallback(self):
        """--ignore-local can submit a branch that isn't available locally.
        
        If there's no location config for the public location, it will
        determine the from and to email addresses from the global config.
        """
        config = _mod_config.GlobalConfig()
        config.set_user_option('pqm_email', 'PQM <pqm@example.com>')
        config.set_user_option(
            'pqm_user_email', 'J. Random Hacker <jrandom@example.com>')
        (out, err, connect_calls,
         sendmail_calls) = self.run_bzr_fakemail(
                ['pqm-submit', '-m', 'commit message',
                 '--submit-branch', 'http://example.com/submit/',
                 '--ignore-local', '--public-location',
                 'http://example.com/public/'
                ])
        self.assertEqual('', out)
        self.assertEqual(1, len(connect_calls))
        call = connect_calls[0]
        self.assertEqual(('localhost', 0), call[1:3])
        self.assertEqual(1, len(sendmail_calls))
        call = sendmail_calls[0]
        self.assertEqual(('jrandom@example.com', ['pqm@example.com']),
                         call[1:3])
        self.assertContainsRe(call[3], EMAIL)


class TestPqmEmail(TestCaseWithMemoryTransport):

    def test_child_pqm_email(self):
        local_branch = self.make_branch('local')
        local_config = pqm_submit.get_stacked_config(local_branch)
        submit_branch = self.make_branch('submit')
        submit_config = submit_branch.get_config()
        submit_config.set_user_option('child_pqm_email', 'child@example.org')
        result = pqm_submit.pqm_email(local_config, submit_branch.base)
        self.assertEqual('child@example.org', result)


class TestConfig(TestCaseWithMemoryTransport):

    def test_email_from_environ(self):
        """The config can get the email from the environ."""
        branch = self.make_branch('foo')
        config = pqm_submit.get_stacked_config(branch, None)
        self.assertEqual('jrandom@example.com', config.get('email'))
