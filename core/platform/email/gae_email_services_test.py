# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the GAE mail API wrapper."""

__author__ = 'Sean Lip'

import datetime

from core.platform.email import gae_email_services
from core.tests import test_utils
import feconf


class EmailsToAdminTests(test_utils.GenericTestBase):
    """Tests for sending emails to the site admin."""

    def test_sending_email_to_admin(self):
        # Emails are not sent if the CAN_SEND_EMAILS_TO_ADMIN setting
        # is not turned on.
        with self.swap(feconf, 'CAN_SEND_EMAILS_TO_ADMIN', False):
            gae_email_services.send_mail_to_admin(
                'sender@example.com', 'subject', 'body')
            messages = self.mail_stub.get_sent_messages(
                to=feconf.ADMIN_EMAIL_ADDRESS)
            self.assertEqual(0, len(messages))

        with self.swap(feconf, 'CAN_SEND_EMAILS_TO_ADMIN', True):
            gae_email_services.send_mail_to_admin(
                'sender@example.com', 'subject', 'body')
            messages = self.mail_stub.get_sent_messages(
                to=feconf.ADMIN_EMAIL_ADDRESS)
            self.assertEqual(1, len(messages))
            self.assertEqual(feconf.ADMIN_EMAIL_ADDRESS, messages[0].to)
            self.assertIn(
                '(Sent from %s)' % self.EXPECTED_TEST_APP_ID,
                messages[0].body.decode())


class AsyncEmailTests(test_utils.GenericTestBase):

    _BODY = 'body'
    _INTENT = 'invitation'
    _SENDER = 'sender@example.com'
    _SUBJECT = 'subject'
    _TO = 'to@example.com'

    def setUp(self):
        super(AsyncEmailTests, self).setUp()
        self.now = datetime.datetime.utcnow()

    def test_can_send_emails_to_users_flag(self):
        # Emails are not sent if the CAN_SEND_EMAILS_TO_USERS setting
        # is not turned on.
        with self.swap(feconf, 'CAN_SEND_EMAILS_TO_USERS', False):
            with self.assertRaisesRegexp(Exception, 'cannot send emails'):
                gae_email_services.send_mail_async(
                    self._TO, self._SENDER, self._INTENT, self._SUBJECT,
                    self._BODY)

        with self.swap(feconf, 'CAN_SEND_EMAILS_TO_USERS', True):
            gae_email_services.send_mail_async(
                self._TO, self._SENDER, self._INTENT, self._SUBJECT,
                self._BODY)
            self.assertEqual(self.count_jobs_in_taskqueue(), 1)
            self.process_and_flush_pending_tasks()

            other_persons_messages = self.mail_stub.get_sent_messages(
                to=feconf.ADMIN_EMAIL_ADDRESS)
            self.assertEqual(0, len(other_persons_messages))

            messages = self.mail_stub.get_sent_messages(to=self._TO)
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].to, self._TO)
            self.assertEqual(messages[0].sender, self._SENDER)
            self.assertEqual(messages[0].subject, self._SUBJECT)
            self.assertEqual(messages[0].body.decode(), self._BODY)

    # TODO(sll): Test failure modes.
