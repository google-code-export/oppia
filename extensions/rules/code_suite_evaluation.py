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

"""Rules for CodeSuiteEvaluation objects."""

__author__ = 'Sean Lip'

from extensions.rules import base


class AllTestCasesHaveSameResult(base.CodeSuiteEvaluationRule):
    description = (
        'corresponds to all test cases having result {{x|UnicodeString}}')
    is_generic = False

    def _evaluate(self, subject):
        for suite in subject['test_results']:
            for testcase_result in suite:
                if testcase_result != self.x:
                    return False

        return True


class CodeContains(base.CodeSuiteEvaluationRule):
    description = 'contains {{x|UnicodeString}}'
    is_generic = False

    def _evaluate(self, subject):
        return self.x in subject['code']


class HasAtLeastOneResultOfType(base.CodeSuiteEvaluationRule):
    description = 'has at least one test case with result {{x|UnicodeString}}'
    is_generic = False

    def _evaluate(self, subject):
        for suite in subject['test_results']:
            for testcase_result in suite:
                if testcase_result == self.x:
                    return True

        return False
