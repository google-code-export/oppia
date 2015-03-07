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

"""Models for Oppia email notifications."""

__author__ = 'Sean Lip'

from core.platform import models
(base_models,) = models.Registry.import_models([models.NAMES.base_model])
import utils

from google.appengine.ext import ndb


_INTENT_INVITATION = 'invitation'
_INTENT_REMINDER = 'reminder'


def get_entity_id(enqueue_datetime, intent, to):
    """Returns the common id used for both an EmailNotificationModel and a
    EmailPayloadModel.
    """
    return '%s:%s:%s' % (
        to, intent, utils.get_time_in_millisecs(enqueue_datetime))


class EmailNotificationModel(base_models.BaseModel):
    """Settings and preferences for a particular user."""
    # Enqueue date of the notification.
    enqueue_datetime = ndb.DateTimeProperty(required=True)
    # Intent of the notification
    intent = ndb.StringProperty(required=True, choices=[
        _INTENT_INVITATION, _INTENT_REMINDER])
    # Email address used to send the notification.
    sender = ndb.StringProperty(required=True)
    # Subject line of the notification.
    subject = ndb.TextProperty(required=True)
    # Recipient of the notification.
    to = ndb.StringProperty(required=True)


class EmailPayloadModel(base_models.BaseModel):
    """The data payload of a Notification.

    We extract this data from Notification to increase the total size budget
    available to the user, which is capped at 1MB/entity.
    """
    # Enqueue date of the notification.
    enqueue_datetime = ndb.DateTimeProperty(required=True)
    # Body of the payload.
    body = ndb.TextProperty()
