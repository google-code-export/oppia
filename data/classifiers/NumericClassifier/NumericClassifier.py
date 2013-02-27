# coding: utf-8
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

"""Numeric classifier rule definitions."""

__author__ = 'Sean Lip'


from data.classifiers import normalizers

# Normalizer to use for reader answers.
DEFAULT_NORMALIZER = normalizers.Number


def equals(val, x):
    """The given value should be equal to {{x}}."""
    return val == x


def is_less_than(val, x):
    """The given value should be less than {{x}}."""
    return val < x


def is_greater_than(val, x):
    """The given value should be greater than {{x}}."""
    return val > x


def is_less_than_or_equal_to(val, x):
    """The given value should be less than or equal to {{x}}."""
    return val <= x


def is_greater_than_or_equal_to(val, x):
    """The given value should be greater than or equal to {{x}}."""
    return val >= x


def is_inclusively_between(val, a, b):
    """The given value should be between {{a}} and {{b}}, inclusive."""
    return val >= a and val <= b


def is_within_tolerance(val, x, tol):
    """The given value should be within {{tol}} of {{x}}, inclusive."""
    return is_inclusively_between(val, x - tol, x + tol)