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

"""Tests for classification of ListOfUnicodeString objects."""

__author__ = 'Sean Lip'

import extensions.rules.list_of_unicode_string as list_rules
import test_utils


class ListOfUnicodeStringRuleUnitTests(test_utils.GenericTestBase):
    """Tests for rules operating on ListOfUnicodeString objects."""

    def test_equals_rule(self):
        self.assertTrue(list_rules.Equals(['1', '3']).eval(['1', '3']))
        self.assertFalse(list_rules.Equals(['1', '3']).eval(['3', '1']))
        self.assertFalse(list_rules.Equals(['1']).eval(['3', '1']))

    def test_is_longer_than_rule(self):
        rule = list_rules.IsLongerThan(2)

        self.assertTrue(rule.eval(['a', 'b', 'c']))
        self.assertFalse(rule.eval(['b', 'b']))
        self.assertFalse(rule.eval([]))

    def test_has_length_inclusively_between_rule(self):
        with self.assertRaises(AssertionError):
            list_rules.HasLengthInclusivelyBetween(3, 1)

        rule = list_rules.HasLengthInclusivelyBetween(1, 3)
        self.assertTrue(rule.eval(['a', 'c', 'b']))
        self.assertTrue(rule.eval(['a', 'ab']))
        self.assertTrue(rule.eval(['a']))
        self.assertFalse(rule.eval([]))
        self.assertFalse(rule.eval(['a', 'b', 'c', 'd']))

    def test_equals_element_wise_rule(self):
        rule = list_rules.EqualsElementWise(0, 'abc')

        self.assertTrue(rule.eval(['abc']))
        self.assertTrue(rule.eval(['abc', 'def']))
        self.assertFalse(rule.eval(['cba']))
        self.assertFalse(rule.eval(['cba', 'abc', 'abc']))
        self.assertFalse(rule.eval([]))

    def test_has_elements_in_rule(self):
        rule = list_rules.HasElementsIn(['a', 'b'])

        self.assertTrue(rule.eval(['a', 'c', 'b']))
        self.assertTrue(rule.eval(['b']))
        self.assertFalse(rule.eval(['c']))
        self.assertFalse(rule.eval([]))

    def test_has_elements_not_in_rule(self):
        rule = list_rules.HasElementsNotIn(['a', 'b'])

        self.assertTrue(rule.eval(['a', 'c', 'b']))
        self.assertTrue(rule.eval(['c']))
        self.assertFalse(rule.eval(['a', 'b']))
        self.assertFalse(rule.eval(['a']))
        self.assertFalse(rule.eval([]))

    def test_omits_elements_in_rule(self):
        rule = list_rules.OmitsElementsIn(['a', 'b'])

        self.assertTrue(rule.eval(['c', 'ab']))
        self.assertTrue(rule.eval(['c']))
        self.assertTrue(rule.eval([]))
        self.assertTrue(rule.eval(['a']))

        self.assertFalse(rule.eval(['a', 'c', 'b']))
        self.assertFalse(rule.eval(['a', 'b']))

    def test_is_disjoint_from_rule(self):
        rule = list_rules.IsDisjointFrom(['a', 'b'])

        self.assertTrue(rule.eval(['c', 'ab']))
        self.assertTrue(rule.eval(['c']))
        self.assertTrue(rule.eval([]))

        self.assertFalse(rule.eval(['a', 'c', 'b']))
        self.assertFalse(rule.eval(['a', 'b']))
        self.assertFalse(rule.eval(['a']))
