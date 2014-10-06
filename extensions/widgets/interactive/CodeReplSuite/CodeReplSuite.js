// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Directive for the CodeRepl interactive widget.
 *
 * IMPORTANT NOTE: The naming convention for customization args that are passed
 * into the directive is: the name of the parameter, followed by 'With',
 * followed by the name of the arg.
 */
oppia.directive('oppiaInteractiveCodeReplSuite', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'interactiveWidget/CodeReplSuite',
      controller:  ['$scope', '$attrs', function($scope, $attrs) {
        $scope.tests = oppiaHtmlEscaper.escapedJsonToObj($attrs.testsWithValue);
        $scope.defaultAnswer = oppiaHtmlEscaper.escapedJsonToObj(
          $attrs.defaultAnswerWithValue);

        var LANGUAGE_PYTHON = 'python';

        // Keep the code string given by the user and the stdout from the evaluation
        // until sending them back to the server.
        $scope.code = ($scope.defaultAnswer || '');
        $scope.output = '';

        $scope.initCodeEditor = function(editor) {
          editor.setValue($scope.defaultAnswer);
          editor.setOption('lineNumbers', true);
          editor.setOption('indentUnit', 4);
          editor.setOption('indentWithTabs', true);
          editor.setOption('mode', LANGUAGE_PYTHON);

          // NOTE: this is necessary to avoid the textarea being greyed-out.
          setTimeout(function() {
            editor.refresh();
          }, 200);

          editor.on('change', function(instance, change) {
            $scope.code = editor.getValue();
          });
        };

        $scope.indentCodeByFourSpaces = function(code) {
          var result = '';
          var fragments = code.split('\n');
          for (var j = 0; j < fragments.length; j++) {
            result += ('    ' + fragments[j] + '\n');
          }
          return result;
        };

        // Set up the jsrepl instance with callbacks set.
        var jsrepl = new JSREPL({
          output: function(out) {
            // If evaluation is successful, this will be called before
            // 'result'.
            $scope.testResults = out.trim().split('\n');
          },
          result: function(res) {
            $scope.sendResponse(res, '');
          },
          error: function(err) {
            // TODO(sll): Rewrite this.
            var err = '';
            if ($scope.output) {
              err += $scope.output;
              $scope.output = '';
            }
            $scope.sendResponse('', err);
          },
          timeout: {
            time: 10000,
            callback: function() {
              $scope.sendResponse('', 'timeout');
            },
          },
        });

        jsrepl.loadLanguage(LANGUAGE_PYTHON, function() {
          console.log('Code REPL widget initialized.');
          $scope.$apply();
        });

        $scope.testResults = [];

        $scope.runCode = function(codeInput) {
          $scope.code = codeInput;
          $scope.output = '';
          $scope.testResults = [];

          for (var i = 0; i < $scope.tests.length; i++) {
            // Run the code for each test. This triggers one of the callbacks
            // set to jsrepl which then calls sendResponse with the result.
            var getTestCasesCode = (
              'def get_test_cases():\n' +
              $scope.indentCodeByFourSpaces($scope.tests[i].get_test_cases));

            var classifyTestcaseResultCode = (
              'def classify_testcase_result(test_data, learner_output):\n' +
              $scope.indentCodeByFourSpaces($scope.tests[i].classify_testcase_result));

            var learnerCode = (
              'def learner_code(test_data):\n' + $scope.indentCodeByFourSpaces(codeInput));

            var fullCode = (
              getTestCasesCode + '\n\n' + classifyTestcaseResultCode + '\n\n' + learnerCode);
            // This prints one classification code per line, in order.
            // TODO(sll): Handle the timeout and error cases.
            // TODO(sll): Handle the case where a learner prints a line; we don't want
            // to include this in the results.
            fullCode += (
              '_test_data = get_test_cases()\n' +
              'for datum in _test_data:\n' +
              '    print classify_testcase_result(datum, learner_code(datum[0]))\n');

            jsrepl.eval(fullCode);
          }
        };

        $scope.sendResponse = function(evaluation, err) {
          $scope.evaluation = (evaluation || '');
          $scope.err = (err || '');
          $scope.$parent.$parent.submitAnswer({
            code: $scope.code || '',
            test_results: [$scope.testResults]
          }, 'submit');
        };
      }]
    };
  }
]);


oppia.directive('oppiaResponseCodeReplSuite', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'response/CodeReplSuite',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        $scope.answer = oppiaHtmlEscaper.escapedJsonToObj($attrs.answer);
      }]
    };
  }
]);
