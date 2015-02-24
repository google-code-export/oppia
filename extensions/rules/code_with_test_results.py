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
# Unless required by applicable law or agreed to in writing, softwar
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Rules for CodeWithTestResults objects."""

__author__ = 'Sean Lip'

from extensions.rules import base


class TestSignatureMatches(base.CodeWithTestResultsRule):
    description = (
        'has test signatures matching {{x|ListOfUnicodeString}}')
    is_generic = False

    def _evaluate(self, subject):
        # Elements in self.x that are empty strings represent wildcards, and
        # they match anything.

        if len(self.x) != len(subject['testResults']):
            # TODO(sll): Should this throw an error, somehow -- or can we
            # verify that it never occurs?
            return False

        print self.x
        print subject['testResults']

        for ind, expected_result in enumerate(subject['testResults']):
            if not self.x[ind]:
                continue
            elif self.x[ind] != expected_result['result']:
                return False

        return True


class TestSignatureDoesNotMatch(base.CodeWithTestResultsRule):
    description = (
        'has test signatures that do not match {{x|ListOfUnicodeString}}')
    is_generic = False

    def _evaluate(self, subject):
        # Elements in self.x that are empty strings represent wildcards, and
        # the corresponding elements are not evaluated.

        if len(self.x) != len(subject['testResults']):
            # TODO(sll): Should this throw an error, somehow -- or can we
            # verify that it never occurs?
            return False

        fully_matches = True
        for ind, expected_result in enumerate(subject['testResults']):
            if not self.x[ind]:
                continue
            elif self.x[ind] != expected_result['result']:
                fully_matches = False

        return (not fully_matches)
