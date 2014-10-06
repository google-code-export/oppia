from core.domain import widget_domain


class CodeReplSuite(widget_domain.BaseWidget):
    """Interactive widget that allows Python programs to be input and run
    against multiple test cases.
    """

    # The human-readable name of the widget.
    name = 'Code REPL with test suites'

    # The category the widget falls under in the widget repository.
    category = 'Custom'

    # A description of the widget.
    description = (
        'Programming code widget allowing code to be tested against multiple '
        'test cases.')

    # Customization args and their descriptions, schemas and default
    # values.
    _customization_arg_specs = [{
        'name': 'default_answer',
        'description': 'Default code to show in the input field.',
        'schema': {
            'type': 'unicode',
            'ui_config': {
                'coding_mode': 'python',
            }
        },
        'default_value': (
            '# Args:\n'
            '# - test_data: a positive integer less than 10.\n'
            '# Returns:\n'
            '#   \'prime\' if `test_data` is prime, and \'not prime\'\n'
            '#   otherwise.\n'
            '\n'
        ),
    }, {
        'name': 'tests',
        'description': 'Specifications for the test cases.',
        'schema': {
            'type': 'list',
            'items': {
                'type': 'dict',
                'properties': [{
                    'name': 'get_test_cases',
                    'schema': {
                        'type': 'unicode',
                        'ui_config': {
                            'coding_mode': 'python',
                        }
                    }
                }, {
                    'name': 'classify_testcase_result',
                    'schema': {
                        'type': 'unicode',
                        'ui_config': {
                            'coding_mode': 'python',
                        }
                    }
                }, {
                    'name': 'classification_choices',
                    'schema': {
                        'type': 'list',
                        'items': {
                            'type': 'unicode',
                        }
                    }
                }]
            }
        },
        'default_value': [{
            'get_test_cases': (
                '# This should return a list of 2-element tuples. Each\n'
                '# tuple contains the definition of one test case. The\n'
                '# first element is the test data and the second is\n'
                '# information needed to compute the expected result.\n'
                'return [(2, \'prime\'), (4, \'not prime\')]\n'),
            'classify_testcase_result': (
                '# This is the body of a function that takes two arguments:\n'
                '# - test_data: a test datum (a 2-tuple that is part of the\n'
                '#   output of get_test_cases())\n'
                '# - learner_output: the result of calling the learner\'s\n'
                '#   program on the test datum.\n'
                '# It should use these to determine and return a \n'
                '# classification for the student\'s response to this test\n'
                '# datum. This return value should be an element of\n'
                '# `classification_choices`.\n'
                'return (\'correct\' if test_data[1] == learner_output\n'
                '        else \'incorrect\')\n'),
            'classification_choices': [
                'correct',
                'incorrect'
            ]
        }]
    }]

    # Actions that the reader can perform on this widget which trigger a
    # feedback interaction, and the associated input types. Interactive widgets
    # must have at least one of these. This attribute name MUST be prefixed by
    # '_'.
    _handlers = [{
        'name': 'submit', 'obj_type': 'CodeSuiteEvaluation'
    }]

    # Additional JS library dependencies that should be loaded in pages
    # containing this widget. These should correspond to names of files in
    # feconf.DEPENDENCIES_TEMPLATES_DIR.
    _dependency_ids = ['jsrepl', 'codemirror']
