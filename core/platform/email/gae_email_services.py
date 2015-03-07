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

"""Provides email-sending services."""

__author__ = 'Sean Lip'


import datetime

from core import counters
from core import jobs
from core.platform import models
(notification_models,) = models.Registry.import_models([
    models.NAMES.notification])
taskqueue_services = models.Registry.import_taskqueue_services()
import feconf
import logging

from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.api import mail_errors


class EmailSenderJobManager(jobs.BaseDeferredJobManager):

    @classmethod
    def _run(cls, additional_job_params):
        email_notification_id = additional_job_params['email_notification_id']
        email_payload_id = additional_job_params['email_payload_id']
        email_notification = (
            notification_models.EmailNotificationModel.get_by_id(
                email_notification_id))
        email_payload = notification_models.EmailPayloadModel.get_by_id(
            email_payload_id)

        if not email_notification:
            raise taskqueue_services.PermanentTaskFailure(
                'Email notification missing: ' + str(email_notification_id))

        if not email_payload:
            raise taskqueue_services.PermanentTaskFailure(
                'Payload missing: ' + str(email_payload_id))

        try:
            mail.send_mail(
                email_notification.sender, email_notification.to,
                email_notification.subject, email_payload.body)
        except Exception as e:
            raise taskqueue_services.PermanentTaskFailure(str(e))


def send_mail_to_admin(sender, subject, body):
    """Enqueues a 'send email' request with the GAE mail service.

    Args:
      - sender: str. the email address of the sender, usually in the form
          'SENDER NAME <EMAIL@ADDRESS.com>'.
      - subject: str. The subject line of the email.
      - body: str. The plaintext body of the email.
    """
    if feconf.CAN_SEND_EMAILS_TO_ADMIN:
        if not mail.is_email_valid(feconf.ADMIN_EMAIL_ADDRESS):
            raise Exception(
                'Malformed email address: %s' %
                feconf.ADMIN_EMAIL_ADDRESS)

        app_id = app_identity.get_application_id()
        body = '(Sent from %s)\n\n%s' % (app_id, body)

        mail.send_mail(sender, feconf.ADMIN_EMAIL_ADDRESS, subject, body)
        counters.EMAILS_SENT.inc()


def send_mail_async(to, sender, intent, subject, body):
    """Sends a notification asynchronously by email.

    Args:
    - to: str. Email address of the recipient.
    - sender: str. Email address of the sender. This must correspond to a
        valid sender at the time the deferred send_mail() call actually
        executes.
    - intent: str. Short string identifier of the intent of the
        notification (such as 'invitation' or 'reminder').
    - subject: str. Subject line for the email.
    - body: str. The email body. Must fit in a datastore entity.

    Raises:
      Exception: if the configuration in feconf.py forbids emails from being
        sent.
      ValueError: if 'to' or 'sender' is invalid, according to App Engine.
    """
    for email in (to, sender):
        if not mail.is_email_valid(email):
            raise ValueError('Malformed email address: %s' % email)

    if not feconf.CAN_SEND_EMAILS_TO_USERS:
        raise Exception('This app cannot send emails to users.')

    enqueue_datetime = datetime.datetime.utcnow()
    model_id = notification_models.get_entity_id(enqueue_datetime, intent, to)

    email_notification_model = notification_models.EmailNotificationModel(
        id=model_id, enqueue_datetime=enqueue_datetime, intent=intent,
        sender=sender, subject=subject, to=to)
    email_payload_model = notification_models.EmailPayloadModel(
        id=model_id, body=body, enqueue_datetime=enqueue_datetime)
    email_notification_model.put()
    email_payload_model.put()

    job_id = EmailSenderJobManager.create_new()
    EmailSenderJobManager.enqueue(job_id, additional_job_params={
        'email_notification_id': model_id,
        'email_payload_id': model_id,
    })
