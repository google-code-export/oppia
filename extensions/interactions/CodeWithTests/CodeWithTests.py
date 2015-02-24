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

from extensions.interactions import base


class CodeWithTests(base.BaseInteraction):
    """Interactive widget that allows programs to be input."""

    name = 'Code (learner writes a function)'
    category = 'Programming'
    description = 'Programming code widget with tests.'
    display_mode = base.DISPLAY_MODE_SUPPLEMENTAL
    _dependency_ids = ['jsrepl', 'codemirror']
    _handlers = [{
        'name': 'submit', 'obj_type': 'CodeWithTestResults'}]

    _customization_arg_specs = [{
        'name': 'language',
        'description': 'Programming language to evaluate the code in.',
        'schema': {
            'type': 'unicode',
            'choices': ['python']
        },
        'default_value': 'python'
    }, {
        'name': 'placeholder',
        'description': 'The initial code displayed in the code input field.',
        'schema': {
            'type': 'unicode',
            'ui_config': {
                'coding_mode': 'none',
            },
        },
        'default_value': (
            'def compute_result(arg):\n'
            '    """Adds 1 to the given arg."""\n'
            '\n'
            '    return arg - 1\n')
    }, {
        'name': 'tests',
        'description': (
            'The code snippets appended to the submission in order to test '
            'it'),
        'schema': {
            'type': 'list',
            'items': {
                'type': 'dict',
                'properties': [{
                    'name': 'label',
                    'schema': {
                        'type': 'unicode',
                    },
                }, {
                    'name': 'testCode',
                    'schema': {
                        'type': 'unicode',
                        'ui_config': {
                            'coding_mode': 'none',
                        },
                    },
                }],
            },
        },
        'default_value': [{
            'label': 'sample',
            'testCode': (
                '# Each testCode snippet should contain a function\n'
                '# run_test() which takes no arguments and returns a\n'
                '# two-element list. The first value in the returned list\n'
                '# should be a string representing the type of the test\n'
                '# result (e.g. \'success\', \'failure\', \'missed_base\n'
                '# case\', etc.) and the second value should be an optional\n'
                '# message meant for display to the learner.\n'
                '\n'
                'def run_test():\n'
                '    test_data = [(5, 6), (-1, 0), (2, 3)]\n'
                '    for test in test_data:\n'
                '        if compute_result(test[0]) != test[1]:\n'
                '            return [\'wrong\', (\n'
                '                \'Input data %s gives wrong answer\'\n'
                '                %% test[0])]\n'
                '\n'
                '    return [\'correct\', \'\']\n')
        }]
    }]
