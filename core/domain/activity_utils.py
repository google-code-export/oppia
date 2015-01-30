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

"""Convenience methods for explorations and adventures."""

__author__ = 'Sean Lip'

import re
import string

import feconf
import utils


def require_valid_name(name, name_type):
    """Generic name validation (for titles or categories).

    Args:
      name: the name to validate.
      name_type: a human-readable string, like 'the exploration title' or
        'a state name'. This will be shown in error messages.
    """
    # This check is needed because state names are used in URLs and as ids
    # for statistics, so the name length should be bounded above.
    if len(name) > 50 or len(name) < 1:
        raise utils.ValidationError(
            'The length of %s should be between 1 and 50 '
            'characters; received %s' % (name_type, name))

    if name[0] in string.whitespace or name[-1] in string.whitespace:
        raise utils.ValidationError(
            'Names should not start or end with whitespace.')

    if re.search('\s\s+', name):
        raise utils.ValidationError(
            'Adjacent whitespace in %s should be collapsed.' % name_type)

    for c in feconf.INVALID_NAME_CHARS:
        if c in name:
            raise utils.ValidationError(
                'Invalid character %s in %s: %s' % (c, name_type, name))
